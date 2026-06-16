"""无线杯/电信杯比赛管理"""

from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin, require_member
from app.models.competition_event import CompetitionEvent
from app.models.competition_event_topic import CompetitionEventTopic
from app.models.team import Team
from app.models.team_channel_config import TeamChannelConfig
from app.models.team_member import TeamMember
from app.models.topic_option import TopicOption
from app.models.user import User
from app.schemas.response import error_response, success_response

router = APIRouter()

UPLOAD_DIR = Path("uploads/competition_topics")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXT = {".pdf", ".doc", ".docx"}


class CompetitionEventCreateRequest(BaseModel):
    cup_type: str
    name: str
    portal_title: Optional[str] = None
    signup_start_at: Optional[datetime] = None
    signup_end_at: Optional[datetime] = None
    topic_open_at: Optional[datetime] = None
    topic_end_at: Optional[datetime] = None
    cycle_start_at: Optional[datetime] = None
    cycle_end_at: Optional[datetime] = None
    planned_topic_count: int = 0

    @field_validator("cup_type")
    @classmethod
    def validate_cup_type(cls, value: str) -> str:
        value = (value or "").strip().lower()
        if value not in {"wireless", "telecom"}:
            raise ValueError("cup_type 仅支持 wireless 或 telecom")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise ValueError("比赛名称不能为空")
        return value

    @field_validator("planned_topic_count")
    @classmethod
    def validate_topic_count(cls, value: int) -> int:
        if value < 0:
            raise ValueError("计划题目数量不能小于 0")
        return value


class CompetitionEventUpdateRequest(BaseModel):
    name: Optional[str] = None
    portal_title: Optional[str] = None
    signup_start_at: Optional[datetime] = None
    signup_end_at: Optional[datetime] = None
    topic_open_at: Optional[datetime] = None
    topic_end_at: Optional[datetime] = None
    cycle_start_at: Optional[datetime] = None
    cycle_end_at: Optional[datetime] = None
    planned_topic_count: Optional[int] = None

    @field_validator("name")
    @classmethod
    def validate_update_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("比赛名称不能为空")
        return value

    @field_validator("portal_title")
    @classmethod
    def validate_update_portal_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("报名页展示名称不能为空")
        return value

    @field_validator("planned_topic_count")
    @classmethod
    def validate_update_topic_count(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value < 0:
            raise ValueError("计划题目数量不能小于 0")
        return value


class CompetitionPortalConfigRequest(BaseModel):
    portal_title: str


class CompetitionEventNameUpdateRequest(BaseModel):
    name: str


class CompetitionActiveStateRequest(BaseModel):
    is_current: bool


def _build_module_key(cup_type: str) -> str:
    return f"{cup_type}_cup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"


def _event_to_dict(db: Session, event: CompetitionEvent) -> dict:
    team_count = db.query(func.count(Team.id)).filter(Team.module_key == event.module_key).scalar() or 0
    member_count = (
        db.query(func.count(TeamMember.id))
        .join(Team, TeamMember.team_id == Team.id)
        .filter(Team.module_key == event.module_key)
        .scalar()
        or 0
    )

    topic_team_count_rows = (
        db.query(Team.topic_id, func.count(Team.id))
        .filter(Team.module_key == event.module_key, Team.topic_id.isnot(None))
        .group_by(Team.topic_id)
        .all()
    )
    topic_team_count_map = {int(topic_id): int(count) for topic_id, count in topic_team_count_rows if topic_id is not None}

    topic_member_count_rows = (
        db.query(Team.topic_id, func.count(TeamMember.id))
        .join(TeamMember, TeamMember.team_id == Team.id)
        .filter(Team.module_key == event.module_key, Team.topic_id.isnot(None))
        .group_by(Team.topic_id)
        .all()
    )
    topic_member_count_map = {int(topic_id): int(count) for topic_id, count in topic_member_count_rows if topic_id is not None}

    return {
        "id": event.id,
        "cup_type": event.cup_type,
        "name": event.name,
        "portal_title": event.portal_title,
        "display_title": event.portal_title or event.name,
        "module_key": event.module_key,
        "signup_start_at": event.signup_start_at.isoformat() if event.signup_start_at else None,
        "signup_end_at": event.signup_end_at.isoformat() if event.signup_end_at else None,
        "topic_open_at": event.topic_open_at.isoformat() if event.topic_open_at else None,
        "topic_end_at": event.topic_end_at.isoformat() if event.topic_end_at else None,
        "cycle_start_at": event.cycle_start_at.isoformat() if event.cycle_start_at else None,
        "cycle_end_at": event.cycle_end_at.isoformat() if event.cycle_end_at else None,
        "is_current": bool(event.is_current),
        "planned_topic_count": event.planned_topic_count,
        "topic_count": len(event.topics),
        "team_count": int(team_count),
        "member_count": int(member_count),
        "total_people": int(team_count + member_count),
        "topics": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "document_name": t.document_name,
                "topic_option_id": t.topic_option_id,
                "selected_team_count": int(topic_team_count_map.get(t.topic_option_id or -1, 0)),
                "selected_member_count": int(topic_member_count_map.get(t.topic_option_id or -1, 0)),
                "selected_total_people": int(
                    topic_team_count_map.get(t.topic_option_id or -1, 0) +
                    topic_member_count_map.get(t.topic_option_id or -1, 0)
                ),
                "document_url": f"/uploads/competition_topics/{t.document_path}" if t.document_path else None,
            }
            for t in event.topics
        ],
        "created_at": event.created_at.isoformat(),
    }


def _sync_channel_config_by_event(db: Session, event: CompetitionEvent) -> None:
    cfg = db.query(TeamChannelConfig).filter(TeamChannelConfig.module_key == event.module_key).first()
    if not cfg:
        cfg = TeamChannelConfig(module_key=event.module_key)
        db.add(cfg)

    cfg.signup_close_at = event.signup_end_at
    cfg.topic_close_at = event.topic_end_at


@router.get("/competitions/current-event", response_model=dict, summary="获取当前进行中的比赛（公开）")
async def get_current_event(db: Session = Depends(get_db)):
    event = (
        db.query(CompetitionEvent)
        .filter(CompetitionEvent.is_current == 1)
        .order_by(CompetitionEvent.updated_at.desc())
        .first()
    )
    if not event:
        return success_response(data=None, msg="当前无进行中比赛")
    return success_response(data=_event_to_dict(db, event), msg="获取成功")


@router.get("/competitions/events", response_model=dict, summary="获取比赛历史列表")
async def list_events(
    cup_type: str,
    current_user: User = Depends(require_member),
    db: Session = Depends(get_db),
):
    cup_type = (cup_type or "").strip().lower()
    if cup_type not in {"wireless", "telecom"}:
        return error_response(400, "cup_type 仅支持 wireless 或 telecom")

    events = (
        db.query(CompetitionEvent)
        .filter(CompetitionEvent.cup_type == cup_type)
        .order_by(CompetitionEvent.created_at.desc())
        .all()
    )
    return success_response(data=[_event_to_dict(db, e) for e in events], msg=f"获取成功，共 {len(events)} 条")


@router.get("/competitions/events/{event_id}", response_model=dict, summary="获取比赛详情")
async def get_event_detail(
    event_id: int,
    current_user: User = Depends(require_member),
    db: Session = Depends(get_db),
):
    event = db.query(CompetitionEvent).filter(CompetitionEvent.id == event_id).first()
    if not event:
        return error_response(404, "比赛不存在")
    return success_response(data=_event_to_dict(db, event), msg="获取成功")


@router.post("/competitions/events", response_model=dict, summary="新建比赛")
async def create_event(
    req: CompetitionEventCreateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    event = CompetitionEvent(
        cup_type=req.cup_type,
        name=req.name,
        portal_title=(req.portal_title or req.name).strip(),
        module_key=_build_module_key(req.cup_type),
        signup_start_at=req.signup_start_at,
        signup_end_at=req.signup_end_at,
        topic_open_at=req.topic_open_at,
        topic_end_at=req.topic_end_at,
        cycle_start_at=req.cycle_start_at,
        cycle_end_at=req.cycle_end_at,
        planned_topic_count=req.planned_topic_count,
        is_current=0,
    )
    db.add(event)
    db.flush()
    _sync_channel_config_by_event(db, event)
    db.commit()
    db.refresh(event)
    return success_response(data={"event_id": event.id, "module_key": event.module_key}, msg="比赛创建成功")


@router.put("/competitions/events/{event_id}", response_model=dict, summary="更新比赛基础信息")
async def update_event(
    event_id: int,
    req: CompetitionEventUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    event = db.query(CompetitionEvent).filter(CompetitionEvent.id == event_id).first()
    if not event:
        return error_response(404, "比赛不存在")

    fields_set = req.model_fields_set

    if "name" in fields_set:
        if req.name is None:
            return error_response(400, "比赛名称不能为空")
        event.name = req.name

    if "portal_title" in fields_set:
        event.portal_title = req.portal_title

    date_fields = [
        "signup_start_at",
        "signup_end_at",
        "topic_open_at",
        "topic_end_at",
        "cycle_start_at",
        "cycle_end_at",
    ]
    for field in date_fields:
        if field in fields_set:
            setattr(event, field, getattr(req, field))

    if "planned_topic_count" in fields_set and req.planned_topic_count is not None:
        event.planned_topic_count = req.planned_topic_count

    _sync_channel_config_by_event(db, event)
    db.commit()
    db.refresh(event)
    return success_response(data=_event_to_dict(db, event), msg="比赛信息更新成功")


@router.put("/competitions/events/{event_id}/portal-config", response_model=dict, summary="设置报名页显示名称")
async def update_portal_config(
    event_id: int,
    req: CompetitionPortalConfigRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    event = db.query(CompetitionEvent).filter(CompetitionEvent.id == event_id).first()
    if not event:
        return error_response(404, "比赛不存在")

    title = (req.portal_title or "").strip()
    if not title:
        return error_response(400, "报名页显示名称不能为空")

    event.portal_title = title
    db.commit()
    return success_response(msg="报名页显示名称更新成功")


@router.put("/competitions/events/{event_id}/name", response_model=dict, summary="修改比赛名称")
async def update_event_name(
    event_id: int,
    req: CompetitionEventNameUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    event = db.query(CompetitionEvent).filter(CompetitionEvent.id == event_id).first()
    if not event:
        return error_response(404, "比赛不存在")

    name = (req.name or "").strip()
    if not name:
        return error_response(400, "比赛名称不能为空")

    event.name = name
    # 默认保持展示标题与比赛名称一致，避免管理页和公开页显示不一致。
    event.portal_title = name
    db.commit()
    return success_response(msg="比赛名称更新成功")


@router.put("/competitions/events/{event_id}/active-state", response_model=dict, summary="切换比赛进行中状态")
async def update_active_state(
    event_id: int,
    req: CompetitionActiveStateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    event = db.query(CompetitionEvent).filter(CompetitionEvent.id == event_id).first()
    if not event:
        return error_response(404, "比赛不存在")

    if req.is_current:
        db.query(CompetitionEvent).update({CompetitionEvent.is_current: 0}, synchronize_session=False)
        event.is_current = 1
    else:
        event.is_current = 0

    db.commit()
    return success_response(msg="状态切换成功")


@router.post("/competitions/events/{event_id}/topics", response_model=dict, summary="添加选题")
async def add_event_topic(
    event_id: int,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    document: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    event = db.query(CompetitionEvent).filter(CompetitionEvent.id == event_id).first()
    if not event:
        return error_response(404, "比赛不存在")

    title = (title or "").strip()
    if not title:
        return error_response(400, "选题名称不能为空")

    document_name = None
    document_path = None
    if document and document.filename:
        ext = Path(document.filename).suffix.lower()
        if ext not in ALLOWED_EXT:
            return error_response(400, "仅支持 pdf/doc/docx 文件")
        safe_name = f"{event_id}_{uuid4().hex[:10]}{ext}"
        save_path = UPLOAD_DIR / safe_name
        content = await document.read()
        save_path.write_bytes(content)
        document_name = document.filename
        document_path = safe_name

    index = db.query(func.count(CompetitionEventTopic.id)).filter(CompetitionEventTopic.event_id == event.id).scalar() or 0
    topic_code = f"{event.module_key}_T{index + 1:02d}"[:50]

    topic_option = TopicOption(
        code=topic_code,
        title=title,
        module_key=event.module_key,
        description=(description or "").strip() or None,
        is_active=True,
        max_teams=None,
    )
    db.add(topic_option)
    db.flush()

    topic = CompetitionEventTopic(
        event_id=event.id,
        title=title,
        description=(description or "").strip() or None,
        document_name=document_name,
        document_path=document_path,
        topic_option_id=topic_option.id,
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)

    return success_response(
        data={
            "id": topic.id,
            "title": topic.title,
            "description": topic.description,
            "document_name": topic.document_name,
            "topic_option_id": topic.topic_option_id,
            "document_url": f"/uploads/competition_topics/{topic.document_path}" if topic.document_path else None,
        },
        msg="选题添加成功",
    )


@router.put("/competitions/events/{event_id}/topics/{topic_id}", response_model=dict, summary="修改选题")
async def update_event_topic(
    event_id: int,
    topic_id: int,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    document: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    event = db.query(CompetitionEvent).filter(CompetitionEvent.id == event_id).first()
    if not event:
        return error_response(404, "比赛不存在")

    topic = (
        db.query(CompetitionEventTopic)
        .filter(CompetitionEventTopic.id == topic_id, CompetitionEventTopic.event_id == event_id)
        .first()
    )
    if not topic:
        return error_response(404, "选题不存在")

    title = (title or "").strip()
    if not title:
        return error_response(400, "选题名称不能为空")

    topic.title = title
    topic.description = (description or "").strip() or None

    if document and document.filename:
        ext = Path(document.filename).suffix.lower()
        if ext not in ALLOWED_EXT:
            return error_response(400, "仅支持 pdf/doc/docx 文件")
        safe_name = f"{event_id}_{uuid4().hex[:10]}{ext}"
        save_path = UPLOAD_DIR / safe_name
        content = await document.read()
        save_path.write_bytes(content)
        topic.document_name = document.filename
        topic.document_path = safe_name

    if topic.topic_option_id:
        topic_option = db.query(TopicOption).filter(TopicOption.id == topic.topic_option_id).first()
        if topic_option:
            topic_option.title = topic.title
            topic_option.description = topic.description
            topic_option.module_key = event.module_key

    db.commit()
    db.refresh(topic)

    return success_response(
        data={
            "id": topic.id,
            "title": topic.title,
            "description": topic.description,
            "document_name": topic.document_name,
            "topic_option_id": topic.topic_option_id,
            "document_url": f"/uploads/competition_topics/{topic.document_path}" if topic.document_path else None,
        },
        msg="选题修改成功",
    )
