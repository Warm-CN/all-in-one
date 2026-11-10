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
from passlib.hash import pbkdf2_sha256
from sqlalchemy.orm import Session, object_session
from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.security import create_access_token, decode_access_token

# PBKDF2 accepts Unicode without bcrypt's 72-byte truncation pitfall.
get_password_hash = pbkdf2_sha256.hash
verify_password = pbkdf2_sha256.verify
from app.core.limiter import limiter
from app.models.printer_booking import Printer, PrinterConfig, PrinterTeam, PrinterBooking, PrinterIncident
from app.schemas.response import success_response

router = APIRouter(prefix="/api/v1/printers", tags=["打印机预约"])
bearer = HTTPBearer(auto_error=False)
TZ = timezone(timedelta(hours=8))


def now():
    return datetime.now(TZ).replace(tzinfo=None)


def iso(value):
    return value.replace(tzinfo=TZ).isoformat() if value else None


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


def booking_data(b, private=False):
    result = {"id": b.id, "printer_id": b.printer_id, "team_name": b.team_name,
              "start_time": iso(b.start_time), "end_time": iso(b.end_time), "status": b.status,
              "checked_in_at": iso(b.checked_in_at), "checked_out_at": iso(b.checked_out_at)}
    if private:
        previous_id, previous_name = b.previous_booking_id, b.previous_team_name
        # Preview is live until actual check-in; check-in fixes the historical snapshot.
        if b.status == "reserved" and b.checked_in_at is None:
            db = object_session(b)
            previous = db.query(PrinterBooking).filter(PrinterBooking.printer_id == b.printer_id, PrinterBooking.checked_in_at.isnot(None), PrinterBooking.checked_in_at <= now()).order_by(PrinterBooking.checked_in_at.desc(), PrinterBooking.id.desc()).first()
            previous_id, previous_name = (previous.id, previous.team_name) if previous else (None, None)
        result.update(purpose=b.purpose, previous_booking_id=previous_id, previous_team_name=previous_name)
    return result


def team_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer), db: Session = Depends(get_db)):
    payload = decode_access_token(credentials.credentials) if credentials else None
    if not payload or payload.get("scope") != "printer_team":
        fail(401, "请先验证打印队伍身份")
    team = db.get(PrinterTeam, payload.get("printer_team_id"))
    cfg = config(db)
    if not team or team.module_key != cfg.module_key:
        fail(401, "队伍凭据已失效，请重新验证")
    return team.id


def identity(db, team):
    return {"token": create_access_token({"sub": "0", "printer_team_id": team.id, "scope": "printer_team"}, timedelta(hours=8)),
            "team": {"id": team.id, "team_name": team.team_name},
            "bookings": [booking_data(b, True) for b in db.query(PrinterBooking).filter_by(team_id=team.id).order_by(PrinterBooking.start_time.desc()).all()]}


class Identify(BaseModel):
    captain_student_id: str = Field(min_length=1, max_length=30)
    captain_phone: str = Field(pattern=r"^1[3-9]\d{9}$")
    access_code: str = Field(min_length=8, max_length=72)


class Register(Identify):
    team_name: str = Field(min_length=1, max_length=100)
    captain_name: str = Field(min_length=1, max_length=50)
    registration_code: str = Field(min_length=8, max_length=72)

    @field_validator("team_name", "captain_name", "captain_student_id")
    @classmethod
    def nonblank(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("不能为空")
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
    module_key: str = Field(default="bambu_cup", pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    opening_hours_enabled: bool = False
    opening_hours: list[OpeningHour] = Field(default_factory=list, max_length=28)
    registration_code: Optional[str] = Field(default=None, min_length=8, max_length=72)
    registration_enabled: Optional[bool] = None


class MachineUpdate(BaseModel):
    status: str = Field(pattern=r"^(available|maintenance)$")


class Resolve(BaseModel):
    resolution: str = Field(min_length=3, max_length=3000)


def public_config(db):
    cfg = config(db)
    return {"printers": [{"id": p.id, "name": p.name, "status": p.status} for p in db.query(Printer).order_by(Printer.id)],
            "opening_hours_enabled": cfg.opening_hours_enabled, "opening_hours": cfg.opening_hours,
            "timezone": "Asia/Shanghai", "module_key": cfg.module_key,
            "registration_enabled": cfg.registration_enabled and bool(cfg.registration_code_hash)}


@router.get("/config")
def get_config(db: Session = Depends(get_db)):
    return success_response(public_config(db))


@router.post("/teams")
@limiter.limit("5/minute")
def register(request: Request, data: Register, db: Session = Depends(get_db)):
    with transaction(db):
        cfg = config(db, True)
        if not cfg.registration_enabled or not cfg.registration_code_hash or not verify_password(data.registration_code, cfg.registration_code_hash):
            fail(403, "报名邀请码无效或登记尚未开放")
        if db.query(PrinterTeam).filter_by(module_key=cfg.module_key, captain_student_id=data.captain_student_id).first():
            fail(409, "该队长已登记，请直接验证身份")
        team = PrinterTeam(module_key=cfg.module_key, team_name=data.team_name, captain_name=data.captain_name,
                           captain_student_id=data.captain_student_id, captain_phone_hash=get_password_hash(data.captain_phone),
                           access_code_hash=get_password_hash(data.access_code))
        db.add(team)
        db.flush()
        result = identity(db, team)
    return success_response(result, "队伍登记成功")


@router.post("/identify")
@limiter.limit("10/minute")
def identify(request: Request, data: Identify, db: Session = Depends(get_db)):
    cfg = config(db)
    team = db.query(PrinterTeam).filter_by(module_key=cfg.module_key, captain_student_id=data.captain_student_id).first()
    if not team or not verify_password(data.access_code, team.access_code_hash) or not verify_password(data.captain_phone, team.captain_phone_hash):
        fail(401, "队长信息或队伍口令不正确")
    return success_response(identity(db, team))


@router.get("/bookings")
def list_bookings(date: date, db: Session = Depends(get_db)):
    start = datetime.combine(date, time.min)
    rows = db.query(PrinterBooking).filter(PrinterBooking.start_time < start + timedelta(days=1), PrinterBooking.end_time > start).order_by(PrinterBooking.start_time).all()
    return success_response([booking_data(b) for b in rows])


@router.get("/my-bookings")
def my_bookings(team_id: int = Depends(team_auth), db: Session = Depends(get_db)):
    return success_response([booking_data(b, True) for b in db.query(PrinterBooking).filter_by(team_id=team_id).order_by(PrinterBooking.start_time.desc()).all()])


@router.post("/bookings")
def create_booking(data: BookingCreate, team_id: int = Depends(team_auth), db: Session = Depends(get_db)):
    with transaction(db):
        cfg = config(db, True)
        p = machine(db, data.printer_id)
        if p.status != "available":
            fail(409, "打印机停机维护中")
        if data.start_time < now() or data.end_time <= data.start_time:
            fail(400, "预约开始不能早于当前时间，结束必须晚于开始")
        if cfg.opening_hours_enabled and not any(h["weekday"] == data.start_time.weekday() and h["start"] <= data.start_time.strftime("%H:%M") < h["end"] for h in cfg.opening_hours):
            fail(400, "预约开始时间须在办公室开放时段内")
        conflict = db.query(PrinterBooking).filter(PrinterBooking.printer_id == p.id, PrinterBooking.status != "cancelled", PrinterBooking.start_time < data.end_time, PrinterBooking.end_time > data.start_time).first()
        if conflict:
            fail(409, "该打印机此时段已被预约")
        team = db.get(PrinterTeam, team_id)
        b = PrinterBooking(printer_id=p.id, team_id=team.id, team_name=team.team_name, captain_name=team.captain_name,
                           captain_student_id=team.captain_student_id, start_time=data.start_time, end_time=data.end_time, purpose=data.purpose)
        db.add(b)
        db.flush()
        result = booking_data(b, True)
    return success_response(result, "预约成功")


def owned_booking(db, booking_id, team_id):
    b = db.get(PrinterBooking, booking_id)
    if b is None:
        fail(404, "预约不存在")
    if b.team_id != team_id:
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
    return success_response(public_config(db))


@router.put("/admin/config")
def update_config(data: ConfigUpdate, admin=Depends(require_admin), db: Session = Depends(get_db)):
    if any(h.start >= h.end for h in data.opening_hours):
        fail(400, "开放时段结束必须晚于开始；跨午夜请拆成两段")
    if data.opening_hours_enabled and not data.opening_hours:
        fail(400, "启用开始限制时至少配置一个开放时段")
    with transaction(db):
        cfg = config(db, True)
        cfg.module_key = data.module_key
        cfg.opening_hours_enabled = data.opening_hours_enabled
        cfg.opening_hours = [h.model_dump() for h in data.opening_hours]
        if data.registration_code:
            cfg.registration_code_hash = get_password_hash(data.registration_code)
            cfg.registration_enabled = True
        if data.registration_enabled is not None:
            if data.registration_enabled and not cfg.registration_code_hash:
                fail(400, "请先设置报名邀请码")
            cfg.registration_enabled = data.registration_enabled
    return success_response(public_config(db))


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
