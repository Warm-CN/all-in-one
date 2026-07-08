"""
共建意见 API
"""
import base64
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_admin
from app.models.user import User
from app.models.suggestion import (
    Suggestion, Screenshot, Annotation, StatusChange, Reply, Endorsement
)
from app.schemas.suggestion import SuggestionCreate, ReplyCreate, StatusUpdate
from app.schemas.response import success_response, error_response

router = APIRouter(prefix="/api/v1/suggestions", tags=["共建意见"])

VALID_TRANSITIONS = {
    "received": ["pending_fix", "wont_fix"],
    "pending_fix": ["fixing", "wont_fix"],
    "fixing": ["done", "wont_fix"],
    "done": [],
    "wont_fix": ["pending_fix"],
}


@router.get("", summary="获取意见列表")
async def get_suggestions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Suggestion)
    if status_filter:
        query = query.filter(Suggestion.status == status_filter)
    if category:
        query = query.filter(Suggestion.category == category)
    total = query.count()
    items = query.order_by(desc(Suggestion.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    data = [_suggestion_summary(s) for s in items]
    return success_response(data={"items": data, "total": total, "page": page, "page_size": page_size})


@router.post("", summary="提交意见")
async def create_suggestion(
    body: SuggestionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    sug = Suggestion(
        title=body.title,
        description=body.description,
        category=body.category,
        status="received",
        page_url=body.page_url,
        author_id=current_user.id
    )
    db.add(sug)
    db.flush()
    for sc in body.screenshots:
        raw = sc.image_data
        if "," in raw:
            raw = raw.split(",", 1)[1]
        img_bytes = base64.b64decode(raw)
        shot = Screenshot(suggestion_id=sug.id, image_data=img_bytes, width=sc.width, height=sc.height)
        db.add(shot)
        db.flush()
        for an in sc.annotations:
            ann = Annotation(
                screenshot_id=shot.id, type=an.type, coords=an.coords,
                text=an.text, color=an.color
            )
            db.add(ann)
    sc0 = StatusChange(suggestion_id=sug.id, from_status=None, to_status="received", reason=None, operator_id=current_user.id)
    db.add(sc0)
    db.commit()
    db.refresh(sug)
    return success_response(data={"id": sug.id}, msg="提交成功")


@router.get("/{suggestion_id}", summary="意见详情")
async def get_suggestion_detail(
    suggestion_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    sug = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    if not sug:
        return error_response(404, "意见不存在")
    shots = db.query(Screenshot).filter(Screenshot.suggestion_id == suggestion_id).all()
    shot_list = []
    for idx, sh in enumerate(shots):
        anns = db.query(Annotation).filter(Annotation.screenshot_id == sh.id).all()
        shot_list.append({
            "index": idx + 1,
            "id": sh.id,
            "width": sh.width,
            "height": sh.height,
            "annotations": [
                {"index": i + 1, "id": a.id, "type": a.type, "coords": a.coords, "text": a.text, "color": a.color}
                for i, a in enumerate(anns)
            ]
        })
    replies = db.query(Reply).filter(Reply.suggestion_id == suggestion_id).order_by(Reply.created_at).all()
    reply_list = [_reply_dict(r, current_user.id, db) for r in replies]
    status_history = db.query(StatusChange).filter(StatusChange.suggestion_id == suggestion_id).order_by(StatusChange.created_at).all()
    return success_response(data={
        "id": sug.id, "title": sug.title, "description": sug.description,
        "category": sug.category, "status": sug.status, "page_url": sug.page_url,
        "author_id": sug.author_id, "created_at": _fmt(sug.created_at),
        "done_at": _fmt(sug.done_at), "done_by": sug.done_by,
        "screenshots": shot_list, "replies": reply_list,
        "status_history": [{"from": s.from_status, "to": s.to_status, "reason": s.reason, "operator_id": s.operator_id, "created_at": _fmt(s.created_at)} for s in status_history]
    })


@router.patch("/{suggestion_id}/status", summary="更新状态(管理员)")
async def update_status(
    suggestion_id: int,
    body: StatusUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    sug = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    if not sug:
        return error_response(404, "意见不存在")
    old = sug.status
    if body.status not in VALID_TRANSITIONS.get(old, []):
        return error_response(400, f"非法状态流转: {old} → {body.status}")
    if body.status == "wont_fix" and not body.reason:
        return error_response(400, "不予修改必须填写原因")
    sug.status = body.status
    if body.status == "done":
        sug.done_at = datetime.now()
        sug.done_by = current_user.id
    sc = StatusChange(suggestion_id=suggestion_id, from_status=old, to_status=body.status, reason=body.reason, operator_id=current_user.id)
    db.add(sc)
    db.commit()
    return success_response(msg="状态已更新")


@router.post("/{suggestion_id}/replies", summary="追加意见/评论")
async def create_reply(
    suggestion_id: int,
    body: ReplyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    sug = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    if not sug:
        return error_response(404, "意见不存在")
    reply = Reply(suggestion_id=suggestion_id, parent_id=body.parent_id, author_id=current_user.id, content=body.content)
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return success_response(data={"id": reply.id}, msg="回复成功")


@router.post("/replies/{reply_id}/endorse", summary="复议/取消复议")
async def toggle_endorse(
    reply_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    reply = db.query(Reply).filter(Reply.id == reply_id).first()
    if not reply:
        return error_response(404, "回复不存在")
    existing = db.query(Endorsement).filter(Endorsement.reply_id == reply_id, Endorsement.user_id == current_user.id).first()
    if existing:
        db.delete(existing)
        reply.endorse_count = max(0, reply.endorse_count - 1)
        endorsed = False
    else:
        e = Endorsement(reply_id=reply_id, user_id=current_user.id)
        db.add(e)
        reply.endorse_count += 1
        endorsed = True
    db.commit()
    return success_response(data={"endorsed": endorsed, "count": reply.endorse_count})


@router.get("/screenshots/{screenshot_id}/image", summary="获取截图图片")
async def get_screenshot_image(
    screenshot_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    shot = db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
    if not shot:
        return error_response(404, "截图不存在")
    return Response(content=shot.image_data, media_type="image/jpeg")


def _suggestion_summary(s: Suggestion) -> dict:
    return {
        "id": s.id, "title": s.title, "category": s.category,
        "status": s.status, "author_id": s.author_id,
        "created_at": _fmt(s.created_at),
        "done_at": _fmt(s.done_at), "done_by": s.done_by,
    }


def _reply_dict(r: Reply, current_user_id: int, db: Session) -> dict:
    my_endorse = db.query(Endorsement).filter(Endorsement.reply_id == r.id, Endorsement.user_id == current_user_id).first()
    return {
        "id": r.id, "parent_id": r.parent_id, "author_id": r.author_id,
        "content": r.content, "endorse_count": r.endorse_count,
        "endorsed": my_endorse is not None,
        "created_at": _fmt(r.created_at),
    }


def _fmt(dt) -> Optional[str]:
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None
