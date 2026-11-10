"""Public printer portal and authenticated administration.

Every mutation locks configuration then the machine row (MySQL FOR UPDATE).
SQLite takes a database write reservation before reading to provide equivalent
serialization across processes. All reservation intervals are [start, end).
"""
from contextlib import contextmanager
from datetime import datetime, date, time, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session, object_session
from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.security import create_access_token, decode_access_token

from app.core.limiter import limiter
from app.models.printer_booking import Printer, PrinterConfig, PrinterBooking, PrinterIncident
from app.models.team import Team, TeamStatus
from app.models.competition_event import CompetitionEvent
from app.schemas.response import success_response

router = APIRouter(prefix="/api/v1/printers", tags=["打印机预约"])
bearer = HTTPBearer(auto_error=False)
TZ = timezone(timedelta(hours=8))


def now():
    return datetime.now(TZ).replace(tzinfo=None)


def beijing_time(value):
    """Normalize aware instants to the database's naive Beijing-time convention."""
    return value.astimezone(TZ).replace(tzinfo=None) if value.tzinfo else value


def iso(value):
    return beijing_time(value).replace(tzinfo=TZ).isoformat() if value else None


def fail(code, message):
    raise HTTPException(code, message)


@contextmanager
def transaction(db):
    # Auth dependencies may have started a read transaction. Release it before
    # acquiring locks, so MySQL REPEATABLE READ sees the latest committed data.
    db.rollback()
    try:
        if db.get_bind().dialect.name == "sqlite":
            db.execute(text("BEGIN IMMEDIATE"))
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise


def config(db, lock=False):
    query = db.query(PrinterConfig).filter(PrinterConfig.id == 1)
    obj = (query.with_for_update() if lock else query).first()
    if obj is None:
        fail(503, "打印机系统未初始化，请管理员运行 init_printers.py")
    return obj


def machine(db, printer_id):
    obj = db.query(Printer).filter(Printer.id == printer_id).with_for_update().first()
    if obj is None:
        fail(404, "打印机不存在")
    return obj


def booking_data(b, private=False, current=None):
    # Status is a read-only schedule projection; actual use remains separately
    # audited by the raw status and explicit check-in/check-out timestamps.
    current = beijing_time(current if current is not None else now())
    status = b.status
    if status == "reserved":
        if current >= beijing_time(b.end_time):
            status = "completed"
        elif current >= beijing_time(b.start_time):
            status = "in_use"
    db = object_session(b) if hasattr(b, "_sa_instance_state") else None
    team_id = getattr(b, "competition_team_id", None)
    team = db.get(Team, team_id) if db is not None and team_id else None
    result = {"id": b.id, "printer_id": b.printer_id, "team_name": b.team_name,
              "captain_phone": team.captain_phone if team else None,
              "start_time": iso(b.start_time), "end_time": iso(b.end_time),
              "status": status, "usage_status": b.status,
              "checked_in_at": iso(b.checked_in_at), "checked_out_at": iso(b.checked_out_at)}
    if private:
        previous_id, previous_name = b.previous_booking_id, b.previous_team_name
        # Preview is live until actual check-in; check-in fixes the historical snapshot.
        if b.status == "reserved" and b.checked_in_at is None and db is not None:
            previous = db.query(PrinterBooking).filter(PrinterBooking.printer_id == b.printer_id, PrinterBooking.checked_in_at.isnot(None), PrinterBooking.checked_in_at <= current).order_by(PrinterBooking.checked_in_at.desc(), PrinterBooking.id.desc()).first()
            previous_id, previous_name = (previous.id, previous.team_name) if previous else (None, None)
        result.update(purpose=b.purpose, previous_booking_id=previous_id, previous_team_name=previous_name)
    return result


def selected_event(db, cfg):
    # Explicit binding always wins. Auto-detect only an unambiguous Bambu event.
    event = db.query(CompetitionEvent).filter_by(module_key=cfg.module_key).first() if cfg.module_key else None
    if event:
        return event
    if cfg.module_key and cfg.module_key != "bambu_cup":
        return None
    candidates = [e for e in db.query(CompetitionEvent).all() if is_bambu(e)]
    current = [e for e in candidates if e.is_current]
    return current[0] if len(current) == 1 else (candidates[0] if len(candidates) == 1 else None)


def is_bambu(event):
    return event.cup_type == "bambu" or "拓竹" in (event.name or "") or "拓竹" in (event.portal_title or "")


def active_team(db, cfg, sid=None, team_id=None):
    event = selected_event(db, cfg)
    if not event:
        fail(409, "尚未绑定拓竹杯赛事，请联系管理员")
    query = db.query(Team).filter(Team.module_key == event.module_key, Team.status != TeamStatus.CANCELLED, Team.delete_requested == False)
    if sid is not None:
        query = query.filter(Team.captain_student_id == sid)
    if team_id is not None:
        query = query.filter(Team.id == team_id)
    teams = query.all()
    if len(teams) != 1:
        fail(404 if not teams else 409, "未找到该赛事的有效队长队伍，请先报名或联系管理员")
    return teams[0]


def team_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer), db: Session = Depends(get_db)):
    payload = decode_access_token(credentials.credentials) if credentials else None
    if not payload or payload.get("scope") != "printer_team" or not payload.get("competition_team_id"):
        fail(401, "请先输入队长学号查询队伍")
    cfg = config(db)
    team = active_team(db, cfg, team_id=payload["competition_team_id"])
    if payload.get("module_key") != team.module_key or payload.get("captain_student_id") != team.captain_student_id:
        fail(401, "队伍所属赛事已变化，请重新查询")
    return team.id


def identity(db, team):
    current = now()
    return {"token": create_access_token({"sub": "0", "competition_team_id": team.id, "module_key": team.module_key, "captain_student_id": team.captain_student_id, "scope": "printer_team"}, timedelta(hours=8)),
            "team": {"id": team.id, "team_name": team.team_name},
            "bookings": [booking_data(b, True, current) for b in db.query(PrinterBooking).filter_by(competition_team_id=team.id).order_by(PrinterBooking.start_time.desc()).all()]}


class Identify(BaseModel):
    captain_student_id: str = Field(min_length=1, max_length=20)

    @field_validator("captain_student_id")
    @classmethod
    def nonblank(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("请输入队长学号")
        return value


class BookingCreate(BaseModel):
    printer_id: int = Field(ge=1, le=3)
    start_time: datetime
    end_time: datetime
    purpose: str = Field(default="", max_length=500)

    @field_validator("start_time", "end_time")
    @classmethod
    def local_time(cls, value):
        # Naive input is explicitly interpreted as Beijing time.
        return value.astimezone(TZ).replace(tzinfo=None) if value.tzinfo else value


class IncidentCreate(BaseModel):
    description: str = Field(min_length=3, max_length=3000)

    @field_validator("description")
    @classmethod
    def nonblank(cls, value):
        if len(value.strip()) < 3:
            raise ValueError("请具体描述异常")
        return value.strip()


class OpeningHour(BaseModel):
    weekday: int = Field(ge=0, le=6)
    start: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")


class ConfigUpdate(BaseModel):
    event_id: Optional[int] = Field(default=None, ge=1)
    module_key: Optional[str] = Field(default=None, max_length=80)
    opening_hours_enabled: bool = False
    opening_hours: list[OpeningHour] = Field(default_factory=list, max_length=28)
    admin_contact: Optional[str] = Field(default=None, max_length=300)


class AdminBookingCreate(BookingCreate):
    captain_student_id: str = Field(min_length=1, max_length=20)


class MachineUpdate(BaseModel):
    status: str = Field(pattern=r"^(available|maintenance)$")


class Resolve(BaseModel):
    resolution: str = Field(min_length=3, max_length=3000)


def public_config(db, admin=False):
    cfg = config(db)
    event = selected_event(db, cfg)
    result = {"printers": [{"id": p.id, "name": p.name, "status": p.status} for p in db.query(Printer).order_by(Printer.id)],
              "opening_hours_enabled": cfg.opening_hours_enabled, "opening_hours": cfg.opening_hours,
              "admin_contact": cfg.admin_contact,
              "timezone": "Asia/Shanghai", "module_key": event.module_key if event else None,
              "event": {"id": event.id, "name": event.portal_title or event.name, "module_key": event.module_key} if event else None,
              "signup_url": f"/team-portal?event_id={event.id}" if event else "/team-portal"}
    if admin:
        result["events"] = [{"id": e.id, "name": e.portal_title or e.name, "module_key": e.module_key, "is_bambu": is_bambu(e)} for e in sorted(db.query(CompetitionEvent).all(), key=lambda e: (not is_bambu(e), -e.id))]
    return result


@router.get("/config")
def get_config(db: Session = Depends(get_db)):
    return success_response(public_config(db))


@router.post("/identify")
@limiter.limit("30/minute")
def identify(request: Request, data: Identify, db: Session = Depends(get_db)):
    return success_response(identity(db, active_team(db, config(db), sid=data.captain_student_id)))


@router.get("/bookings")
def list_bookings(date: date, db: Session = Depends(get_db)):
    start = datetime.combine(date, time.min)
    rows = db.query(PrinterBooking).filter(PrinterBooking.start_time < start + timedelta(days=1), PrinterBooking.end_time > start).order_by(PrinterBooking.start_time).all()
    current = now()
    return success_response([booking_data(b, current=current) for b in rows])


@router.get("/my-bookings")
def my_bookings(team_id: int = Depends(team_auth), db: Session = Depends(get_db)):
    current = now()
    return success_response([booking_data(b, True, current) for b in db.query(PrinterBooking).filter_by(competition_team_id=team_id).order_by(PrinterBooking.start_time.desc()).all()])


def add_booking(db, data, team):
    cfg = config(db, True)
    # Revalidate existing team within the transaction; no approval state required.
    team = active_team(db, cfg, team_id=team.id)
    p = machine(db, data.printer_id)
    if p.status != "available":
        fail(409, "打印机停机维护中")
    if data.start_time < now() or data.end_time <= data.start_time:
        fail(400, "预约开始不能早于当前时间，结束必须晚于开始")
    if cfg.opening_hours_enabled and not any(h["weekday"] == data.start_time.weekday() and h["start"] <= data.start_time.strftime("%H:%M") < h["end"] for h in cfg.opening_hours):
        fail(400, "预约开始时间须在办公室开放时段内")
    if db.query(PrinterBooking).filter(PrinterBooking.printer_id == p.id, PrinterBooking.status != "cancelled", PrinterBooking.start_time < data.end_time, PrinterBooking.end_time > data.start_time).with_for_update().first():
        fail(409, "该打印机此时段已被预约")
    b = PrinterBooking(printer_id=p.id, competition_team_id=team.id, team_name=team.team_name, captain_name=team.captain_name,
                       captain_student_id=team.captain_student_id, start_time=data.start_time, end_time=data.end_time, purpose=data.purpose)
    db.add(b)
    db.flush()
    return booking_data(b, True)


@router.post("/bookings")
def create_booking(data: BookingCreate, team_id: int = Depends(team_auth), db: Session = Depends(get_db)):
    with transaction(db):
        result = add_booking(db, data, db.get(Team, team_id))
    return success_response(result, "预约成功")


def owned_booking(db, booking_id, team_id):
    b = db.get(PrinterBooking, booking_id)
    if b is None:
        fail(404, "预约不存在")
    if b.competition_team_id != team_id:
        fail(403, "只能操作本队预约")
    return b


@router.post("/bookings/{booking_id}/cancel")
def cancel(booking_id: int, team_id: int = Depends(team_auth), db: Session = Depends(get_db)):
    with transaction(db):
        config(db, True)
        b = owned_booking(db, booking_id, team_id)
        machine(db, b.printer_id)
        if b.status != "reserved" or b.start_time <= now():
            fail(409, "只能取消尚未开始的预约")
        b.status = "cancelled"
        result = booking_data(b, True)
    return success_response(result)


@router.post("/bookings/{booking_id}/check-in")
def check_in(booking_id: int, team_id: int = Depends(team_auth), db: Session = Depends(get_db)):
    with transaction(db):
        config(db, True)
        b = owned_booking(db, booking_id, team_id)
        p = machine(db, b.printer_id)
        current = now()
        if p.status != "available" or b.status != "reserved" or not b.start_time <= current < b.end_time:
            fail(409, "当前不可签到，请确认预约时间与机器状态")
        if db.query(PrinterBooking).filter_by(printer_id=p.id, status="in_use").first():
            fail(409, "上一队伍尚未签退，请先完成交接")
        prev = db.query(PrinterBooking).filter(PrinterBooking.printer_id == p.id, PrinterBooking.checked_in_at.isnot(None), PrinterBooking.checked_in_at <= current).order_by(PrinterBooking.checked_in_at.desc(), PrinterBooking.id.desc()).first()
        b.previous_booking_id = prev.id if prev else None
        b.previous_team_name = prev.team_name if prev else None
        b.checked_in_at, b.status = current, "in_use"
        result = booking_data(b, True)
    return success_response(result)


@router.post("/bookings/{booking_id}/check-out")
def check_out(booking_id: int, team_id: int = Depends(team_auth), db: Session = Depends(get_db)):
    with transaction(db):
        config(db, True)
        b = owned_booking(db, booking_id, team_id)
        machine(db, b.printer_id)
        if b.status != "in_use":
            fail(409, "仅使用中的预约可以签退")
        b.checked_out_at, b.status = now(), "completed"
        result = booking_data(b, True)
    return success_response(result)


@router.post("/bookings/{booking_id}/incidents")
def incident(booking_id: int, data: IncidentCreate, team_id: int = Depends(team_auth), db: Session = Depends(get_db)):
    with transaction(db):
        config(db, True)
        b = owned_booking(db, booking_id, team_id)
        p = machine(db, b.printer_id)
        current = now()
        if b.status == "reserved" and b.start_time <= current < b.end_time:
            if db.query(PrinterBooking).filter_by(printer_id=p.id, status="in_use").first():
                fail(409, "上一队伍尚未签退，请先联系管理员完成交接")
            previous = db.query(PrinterBooking).filter(PrinterBooking.printer_id == p.id, PrinterBooking.checked_in_at.isnot(None), PrinterBooking.checked_in_at <= current).order_by(PrinterBooking.checked_in_at.desc(), PrinterBooking.id.desc()).first()
            b.previous_booking_id = previous.id if previous else None
            b.previous_team_name = previous.team_name if previous else None
        elif b.status == "in_use":
            previous = db.get(PrinterBooking, b.previous_booking_id) if b.previous_booking_id else None
        else:
            fail(409, "仅可在预约时段检查机器或实际使用中报告异常")
        row = PrinterIncident(printer_id=p.id, booking_id=b.id, reporter_team_name=b.team_name,
                              previous_booking_id=b.previous_booking_id, responsible_team_name=previous.team_name if previous else None,
                              responsible_captain_name=previous.captain_name if previous else None, description=data.description)
        db.add(row)
        p.status = "maintenance"
        db.flush()
        result = {"id": row.id, "previous_booking_id": row.previous_booking_id, "responsible_team_name": row.responsible_team_name}
    return success_response(result, "异常已记录，机器已暂停使用，待管理员核查")


@router.get("/admin/config")
def admin_config(admin=Depends(require_admin), db: Session = Depends(get_db)):
    return success_response(public_config(db, True))


@router.put("/admin/config")
def update_config(data: ConfigUpdate, admin=Depends(require_admin), db: Session = Depends(get_db)):
    if any(h.start >= h.end for h in data.opening_hours):
        fail(400, "开放时段结束必须晚于开始；跨午夜请拆成两段")
    if data.opening_hours_enabled and not data.opening_hours:
        fail(400, "启用开始限制时至少配置一个开放时段")
    with transaction(db):
        cfg = config(db, True)
        if data.event_id is not None or data.module_key is not None:
            event = db.get(CompetitionEvent, data.event_id) if data.event_id else db.query(CompetitionEvent).filter_by(module_key=data.module_key).first()
            if event is None:
                fail(404, "请选择已有赛事")
            cfg.module_key = event.module_key
        cfg.opening_hours_enabled = data.opening_hours_enabled
        cfg.opening_hours = [h.model_dump() for h in data.opening_hours]
        if data.admin_contact is not None:
            cfg.admin_contact = data.admin_contact.strip()
    return success_response(public_config(db, True))


@router.get("/admin/bookings")
def admin_bookings(date: Optional[date] = None, admin=Depends(require_admin), db: Session = Depends(get_db)):
    query = db.query(PrinterBooking)
    if date:
        start = datetime.combine(date, time.min)
        query = query.filter(PrinterBooking.start_time < start + timedelta(days=1), PrinterBooking.end_time > start)
    current = now()
    return success_response([{**booking_data(b, True, current), "captain_name": b.captain_name, "captain_student_id": b.captain_student_id,
                              "competition_team_id": b.competition_team_id, "deleted_by": b.deleted_by}
                             for b in query.order_by(PrinterBooking.start_time.desc()).all()])


@router.post("/admin/bookings")
def admin_create_booking(data: AdminBookingCreate, admin=Depends(require_admin), db: Session = Depends(get_db)):
    with transaction(db):
        cfg = config(db, True)
        team = active_team(db, cfg, sid=data.captain_student_id.strip())
        result = add_booking(db, data, team)
    return success_response(result, "预约已添加")


@router.delete("/admin/bookings/{booking_id}")
def admin_delete_booking(booking_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    admin_id = admin.id
    with transaction(db):
        config(db, True)
        b = db.get(PrinterBooking, booking_id)
        if b is None:
            fail(404, "预约不存在")
        machine(db, b.printer_id)
        if b.status == "in_use":
            b.checked_out_at = now()
        b.status, b.deleted_by = "cancelled", admin_id
        result = booking_data(b, True)
    return success_response(result, "预约已删除，历史使用及异常记录保留")


@router.put("/admin/printers/{printer_id}")
def update_machine(printer_id: int, data: MachineUpdate, admin=Depends(require_admin), db: Session = Depends(get_db)):
    with transaction(db):
        config(db, True)
        p = machine(db, printer_id)
        if data.status == "available" and db.query(PrinterIncident).filter_by(printer_id=p.id, resolved_at=None).first():
            fail(409, "请先处理该机器所有未解决异常")
        p.status = data.status
    return success_response({"id": printer_id, "status": data.status})


@router.get("/admin/incidents")
def list_incidents(admin=Depends(require_admin), db: Session = Depends(get_db)):
    return success_response([{"id": r.id, "printer_id": r.printer_id, "booking_id": r.booking_id,
                              "reporter_team_name": r.reporter_team_name, "previous_booking_id": r.previous_booking_id,
                              "responsible_team_name": r.responsible_team_name, "responsible_captain_name": r.responsible_captain_name,
                              "description": r.description, "resolution": r.resolution, "created_at": iso(r.created_at), "resolved_at": iso(r.resolved_at)}
                             for r in db.query(PrinterIncident).order_by(PrinterIncident.id.desc()).all()])


@router.post("/admin/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: int, data: Resolve, admin=Depends(require_admin), db: Session = Depends(get_db)):
    with transaction(db):
        config(db, True)
        row = db.get(PrinterIncident, incident_id)
        if not row:
            fail(404, "异常记录不存在")
        machine(db, row.printer_id)
        if row.resolved_at:
            fail(409, "异常已经处理")
        row.resolution, row.resolved_at, row.resolved_by = data.resolution.strip(), now(), admin.id
    return success_response(msg="已记录核查结果，请确认设备安全后手动恢复")
