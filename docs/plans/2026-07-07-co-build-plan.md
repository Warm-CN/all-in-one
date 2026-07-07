# 共建页面 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为社团管理系统新增"共建"模块,允许成员对任意页面提出带截图批注的建设意见,管理员可管理状态流转并查看文字清单。

**Architecture:** 后端 FastAPI + SQLAlchemy 新增 Suggestion/Screenshot/Annotation/StatusChange/Reply/Endorsement 六张表和对应 API;前端 Vue3 + Element Plus + Tailwind 新增 CoBuild 页面,用 html2canvas 一次性截图 + Canvas 2D 绘制批注(零 DOM 重排保证性能);不使用 OCR,用户框选时直接输入文字说明。

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, Vue 3, Element Plus, Tailwind CSS, html2canvas, Canvas 2D API

**Spec:** `docs/specs/2026-07-07-co-build-design.md`

---

## File Structure

### 后端新增

| 文件 | 职责 |
|------|------|
| `app/models/suggestion.py` | Suggestion/Screenshot/Annotation/StatusChange/Reply/Endorsement 六个 SQLAlchemy 模型 |
| `app/schemas/suggestion.py` | Pydantic 请求/响应 schema |
| `app/api/v1/suggestions.py` | 6 个 API 端点 |

### 后端修改

| 文件 | 改动 |
|------|------|
| `app/models/__init__.py` | 导出新模型 |
| `app/main.py` | 注册 suggestions 路由 |

### 前端新增

| 文件 | 职责 |
|------|------|
| `frontend/src/views/CoBuild.vue` | 共建主页(意见列表+页面选择+提建议) |
| `frontend/src/components/cobuild/ScreenshotLauncher.vue` | 页面下拉选择+前往截图按钮 |
| `frontend/src/components/cobuild/ScreenshotCanvas.vue` | Canvas 画布(矩形/任意形状/文字绘制) |
| `frontend/src/components/cobuild/AnnotationEditor.vue` | 批注编辑器(截图+Canvas+工具栏+表单) |
| `frontend/src/components/cobuild/SuggestionCard.vue` | 意见列表卡片 |
| `frontend/src/components/cobuild/SuggestionDetail.vue` | 意见详情(文字清单+讨论区) |
| `frontend/src/components/cobuild/DiscussionThread.vue` | 讨论区(回复+复议) |
| `frontend/src/api/suggestion.js` | API 封装 |

### 前端修改

| 文件 | 改动 |
|------|------|
| `frontend/src/router/index.js` | 新增 /co-build 路由 |
| `frontend/src/layout/MainLayout.vue` | 侧边栏新增"共建"菜单项 |

---

## Task 1: 后端数据模型

**Files:**
- Create: `app/models/suggestion.py`
- Modify: `app/models/__init__.py`

- [ ] **Step 1: 创建 suggestion.py 模型文件**

```python
"""
共建意见模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, LargeBinary
from app.models.base import BaseModel


class Suggestion(BaseModel):
    """建设意见"""
    __tablename__ = "suggestions"

    title = Column(String(200), nullable=False, comment="标题")
    description = Column(Text, nullable=False, comment="描述")
    category = Column(String(20), nullable=False, default="other", comment="分类: layout/feature/bug/other")
    status = Column(String(20), nullable=False, default="received", comment="状态: received/pending_fix/fixing/wont_fix/done")
    page_url = Column(String(500), nullable=True, comment="关联页面URL")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="提出者")
    done_at = Column(DateTime, nullable=True, comment="完成时间")
    done_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="修改人")


class Screenshot(BaseModel):
    """截图"""
    __tablename__ = "screenshots"

    suggestion_id = Column(Integer, ForeignKey("suggestions.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联意见")
    image_data = Column(LargeBinary, nullable=False, comment="JPEG压缩数据")
    width = Column(Integer, nullable=False, comment="原图宽度")
    height = Column(Integer, nullable=False, comment="原图高度")


class Annotation(BaseModel):
    """批注"""
    __tablename__ = "annotations"

    screenshot_id = Column(Integer, ForeignKey("screenshots.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联截图")
    type = Column(String(20), nullable=False, comment="类型: rect/freehand/text")
    coords = Column(JSON, nullable=False, comment="坐标 rect:{x,y,w,h} freehand:{points:[[x,y],...]} text:{x,y}")
    text = Column(String(500), nullable=False, comment="文字批注内容")
    color = Column(String(20), nullable=False, default="#EF4444", comment="颜色")


class StatusChange(BaseModel):
    """状态变更记录"""
    __tablename__ = "status_changes"

    suggestion_id = Column(Integer, ForeignKey("suggestions.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联意见")
    from_status = Column(String(20), nullable=True, comment="原状态")
    to_status = Column(String(20), nullable=False, comment="新状态")
    reason = Column(Text, nullable=True, comment="说明/不予修改原因")
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="操作人")


class Reply(BaseModel):
    """讨论回复"""
    __tablename__ = "replies"

    suggestion_id = Column(Integer, ForeignKey("suggestions.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联意见")
    parent_id = Column(Integer, ForeignKey("replies.id", ondelete="CASCADE"), nullable=True, comment="父回复(支持嵌套)")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="作者")
    content = Column(Text, nullable=False, comment="内容")
    endorse_count = Column(Integer, nullable=False, default=0, comment="复议数")


class Endorsement(BaseModel):
    """复议记录"""
    __tablename__ = "endorsements"

    reply_id = Column(Integer, ForeignKey("replies.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联回复")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="复议用户")
```

- [ ] **Step 2: 在 models/__init__.py 中导出新模型**

在 `app/models/__init__.py` 末尾(`__all__` 列表之前)添加导入:

```python
from app.models.suggestion import Suggestion, Screenshot, Annotation, StatusChange, Reply, Endorsement
```

并在 `__all__` 列表中追加:

```python
    "Suggestion",
    "Screenshot",
    "Annotation",
    "StatusChange",
    "Reply",
    "Endorsement",
```

- [ ] **Step 3: 重启后端验证建表**

Run: 重启 uvicorn,观察日志中无建表错误
Expected: 启动成功,数据库新增 6 张表

- [ ] **Step 4: Commit**

```bash
git add app/models/suggestion.py app/models/__init__.py
git commit -m "feat: 共建模块数据模型"
```

---

## Task 2: 后端 Pydantic Schema

**Files:**
- Create: `app/schemas/suggestion.py`

- [ ] **Step 1: 创建 schema 文件**

```python
"""
共建意见 Pydantic Schema
"""
from typing import Optional, List, Any
from pydantic import BaseModel


class AnnotationCreate(BaseModel):
    type: str   # rect / freehand / text
    coords: dict
    text: str
    color: str = "#EF4444"


class ScreenshotCreate(BaseModel):
    image_data: str  # base64
    width: int
    height: int
    annotations: List[AnnotationCreate] = []


class SuggestionCreate(BaseModel):
    title: str
    description: str
    category: str = "other"
    page_url: str = ""
    screenshots: List[ScreenshotCreate] = []


class ReplyCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None


class StatusUpdate(BaseModel):
    status: str  # pending_fix / fixing / wont_fix / done
    reason: Optional[str] = None
```

- [ ] **Step 2: Commit**

```bash
git add app/schemas/suggestion.py
git commit -m "feat: 共建模块 Pydantic schema"
```

---

## Task 3: 后端 API 端点

**Files:**
- Create: `app/api/v1/suggestions.py`
- Modify: `app/main.py`

- [ ] **Step 1: 创建 suggestions.py 路由**

```python
"""
共建意见 API
"""
import base64
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_member, require_admin
from app.models.user import User
from app.models.suggestion import (
    Suggestion, Screenshot, Annotation, StatusChange, Reply, Endorsement
)
from app.schemas.suggestion import (
    SuggestionCreate, ReplyCreate, StatusUpdate
)
from app.schemas.response import success_response, error_response

router = APIRouter(prefix="/api/v1/suggestions", tags=["共建意见"])


# ==================== 状态流转校验 ====================

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
        img_bytes = base64.b64decode(sc.image_data.split(",")[-1]) if "," in sc.image_data else base64.b64decode(sc.image_data)
        shot = Screenshot(suggestion_id=sug.id, image_data=img_bytes, width=sc.width, height=sc.height)
        db.add(shot)
        db.flush()
        for an in sc.annotations:
            ann = Annotation(
                screenshot_id=shot.id, type=an.type, coords=an.coords,
                text=an.text, color=an.color
            )
            db.add(ann)
    # 记录初始状态
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


# ==================== 图片接口 ====================

@router.get("/screenshots/{screenshot_id}/image", summary="获取截图图片")
async def get_screenshot_image(
    screenshot_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    from fastapi import Response
    shot = db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
    if not shot:
        return error_response(404, "截图不存在")
    return Response(content=shot.image_data, media_type="image/jpeg")


# ==================== 辅助函数 ====================

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
```

- [ ] **Step 2: 在 main.py 注册路由**

在 `app/main.py` 顶部导入行添加:

```python
from app.api.v1 import auth, signups, room_bookings, admin, users, admin_bookings, schedules, admin_schedules, teams, competitions, suggestions
```

在路由注册区(约第197行后)添加:

```python
# 共建意见路由
app.include_router(
    suggestions.router,
    tags=["共建意见"]
)
```

- [ ] **Step 3: 重启后端验证 API 文档**

Run: 重启 uvicorn,访问 http://localhost:8001/docs
Expected: 看到"共建意见"分组下有 7 个端点

- [ ] **Step 4: Commit**

```bash
git add app/api/v1/suggestions.py app/main.py
git commit -m "feat: 共建模块后端 API"
```

---

## Task 4: 前端 API 封装

**Files:**
- Create: `frontend/src/api/suggestion.js`

- [ ] **Step 1: 创建 API 封装文件**

```javascript
import request from './request'

// 意见列表
export function getSuggestions(params = {}) {
  return request.get('/api/v1/suggestions', { params })
}

// 提交意见
export function createSuggestion(data) {
  return request.post('/api/v1/suggestions', data)
}

// 意见详情
export function getSuggestionDetail(id) {
  return request.get(`/api/v1/suggestions/${id}`)
}

// 更新状态(管理员)
export function updateSuggestionStatus(id, data) {
  return request.patch(`/api/v1/suggestions/${id}/status`, data)
}

// 追加意见/评论
export function createReply(id, data) {
  return request.post(`/api/v1/suggestions/${id}/replies`, data)
}

// 复议/取消复议
export function toggleEndorse(replyId) {
  return request.post(`/api/v1/suggestions/replies/${replyId}/endorse`)
}

// 截图图片 URL
export function screenshotImageUrl(screenshotId) {
  return `/api/v1/suggestions/screenshots/${screenshotId}/image`
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api/suggestion.js
git commit -m "feat: 共建模块前端 API 封装"
```

---

## Task 5: 前端路由与菜单

**Files:**
- Modify: `frontend/src/router/index.js`
- Modify: `frontend/src/layout/MainLayout.vue`

- [ ] **Step 1: 在 router/index.js 添加路由**

在 `children` 数组中(约第113行 `contacts` 路由之后)添加:

```javascript
            {
                path: 'co-build',
                name: 'CoBuild',
                component: () => import('@/views/CoBuild.vue'),
                meta: { title: '共建', requiresAuth: true }
            },
```

- [ ] **Step 2: 在 MainLayout.vue 侧边栏添加菜单项**

找到"协会资源"分组的菜单列表,在其中添加"共建"菜单项。菜单项格式参照同组其他项:

```html
<el-menu-item index="/co-build">
  <el-icon><EditPen /></el-icon>
  <span>共建</span>
</el-menu-item>
```

确保 `EditPen` 图标已在 script 中导入。

- [ ] **Step 3: 验证页面可访问**

Run: 访问 http://localhost:3000/co-build
Expected: 页面空白(组件尚未创建),但不报 404

- [ ] **Step 4: Commit**

```bash
git add frontend/src/router/index.js frontend/src/layout/MainLayout.vue
git commit -m "feat: 共建模块路由与菜单"
```

---

## Task 6: ScreenshotCanvas 组件(Canvas 批注画布)

**Files:**
- Create: `frontend/src/components/cobuild/ScreenshotCanvas.vue`

- [ ] **Step 1: 创建 Canvas 画布组件**

```vue
<template>
  <div class="relative" ref="containerRef">
    <img
      ref="imgRef"
      :src="imageSrc"
      class="block max-w-full select-none"
      @load="onImageLoad"
      draggable="false"
    />
    <canvas
      ref="canvasRef"
      class="absolute top-0 left-0"
      :width="canvasWidth"
      :height="canvasHeight"
      @mousedown="onMouseDown"
      @mousemove="onMouseMove"
      @mouseup="onMouseUp"
      :style="{ cursor: cursorStyle }"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'

const props = defineProps({
  imageSrc: String,
  tool: { type: String, default: 'rect' }, // rect / freehand / text
  annotations: { type: Array, default: () => [] }
})
const emit = defineEmits(['add-annotation'])

const containerRef = ref(null)
const imgRef = ref(null)
const canvasRef = ref(null)
const canvasWidth = ref(0)
const canvasHeight = ref(0)
const isDrawing = ref(false)
const startPos = ref(null)
const currentPath = ref([])
const cursorStyle = ref('crosshair')

function onImageLoad() {
  nextTick(() => {
    const img = imgRef.value
    canvasWidth.value = img.clientWidth
    canvasHeight.value = img.clientHeight
    redraw()
  })
}

function getCtx() {
  return canvasRef.value.getContext('2d')
}

function redraw() {
  const ctx = getCtx()
  if (!ctx) return
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  for (const ann of props.annotations) {
    drawAnnotation(ctx, ann)
  }
  // 绘制当前进行中的形状
  if (isDrawing.value) {
    if (props.tool === 'rect' && startPos.value) {
      // 虚线预览
      ctx.strokeStyle = '#3B82F6'
      ctx.lineWidth = 2
      ctx.setLineDash([6, 4])
      const s = startPos.value
      ctx.strokeRect(s.x, s.y, currentPath.value[0] - s.x, currentPath.value[1] - s.y)
      ctx.setLineDash([])
    } else if (props.tool === 'freehand' && currentPath.value.length > 1) {
      ctx.strokeStyle = '#3B82F6'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(currentPath.value[0][0], currentPath.value[0][1])
      for (let i = 1; i < currentPath.value.length; i++) {
        ctx.lineTo(currentPath.value[i][0], currentPath.value[i][1])
      }
      ctx.stroke()
    }
  }
}

function drawAnnotation(ctx, ann) {
  ctx.strokeStyle = ann.color
  ctx.fillStyle = ann.color
  ctx.lineWidth = 2
  ctx.font = '14px sans-serif'
  if (ann.type === 'rect') {
    const c = ann.coords
    ctx.strokeRect(c.x, c.y, c.w, c.h)
    // 标注序号
    const label = ann._label || ''
    ctx.fillStyle = ann.color
    ctx.fillRect(c.x, c.y - 20, 24, 20)
    ctx.fillStyle = '#fff'
    ctx.fillText(label, c.x + 4, c.y - 6)
    ctx.fillStyle = ann.color
  } else if (ann.type === 'freehand') {
    const pts = ann.coords.points
    if (!pts || pts.length < 2) return
    ctx.beginPath()
    ctx.moveTo(pts[0][0], pts[0][1])
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1])
    ctx.closePath()
    ctx.stroke()
    const label = ann._label || ''
    ctx.fillStyle = ann.color
    ctx.fillRect(pts[0][0], pts[0][1] - 20, 24, 20)
    ctx.fillStyle = '#fff'
    ctx.fillText(label, pts[0][0] + 4, pts[0][1] - 6)
    ctx.fillStyle = ann.color
  } else if (ann.type === 'text') {
    const c = ann.coords
    ctx.fillStyle = 'rgba(255,255,255,0.85)'
    const w = ctx.measureText(ann.text).width + 12
    ctx.fillRect(c.x - 6, c.y - 14, w, 22)
    ctx.fillStyle = ann.color
    ctx.fillText(ann.text, c.x, c.y + 2)
  }
}

function getPos(e) {
  const rect = canvasRef.value.getBoundingClientRect()
  return { x: e.clientX - rect.left, y: e.clientY - rect.top }
}

function onMouseDown(e) {
  const pos = getPos(e)
  if (props.tool === 'text') {
    // 文字工具:直接弹出输入(由父组件处理)
    emit('add-annotation', { type: 'text', coords: { x: pos.x, y: pos.y } })
    return
  }
  isDrawing.value = true
  startPos.value = pos
  if (props.tool === 'freehand') {
    currentPath.value = [[pos.x, pos.y]]
  } else {
    currentPath.value = [pos.x, pos.y]
  }
}

function onMouseMove(e) {
  if (!isDrawing.value) return
  const pos = getPos(e)
  if (props.tool === 'freehand') {
    currentPath.value.push([pos.x, pos.y])
  } else {
    currentPath.value = [pos.x, pos.y]
  }
  redraw()
}

function onMouseUp(e) {
  if (!isDrawing.value) return
  isDrawing.value = false
  const pos = getPos(e)
  if (props.tool === 'rect') {
    const s = startPos.value
    const w = pos.x - s.x
    const h = pos.y - s.y
    if (Math.abs(w) > 5 && Math.abs(h) > 5) {
      emit('add-annotation', {
        type: 'rect',
        coords: { x: Math.min(s.x, pos.x), y: Math.min(s.y, pos.y), w: Math.abs(w), h: Math.abs(h) }
      })
    }
  } else if (props.tool === 'freehand') {
    if (currentPath.value.length > 2) {
      emit('add-annotation', {
        type: 'freehand',
        coords: { points: [...currentPath.value] }
      })
    }
  }
  startPos.value = null
  currentPath.value = []
  redraw()
}

watch(() => props.annotations, () => {
  nextTick(redraw)
}, { deep: true })

onMounted(() => {
  nextTick(redraw)
})
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/cobuild/ScreenshotCanvas.vue
git commit -m "feat: Canvas 批注画布组件"
```

---

## Task 7: AnnotationEditor 组件(批注编辑器)

**Files:**
- Create: `frontend/src/components/cobuild/AnnotationEditor.vue`

- [ ] **Step 1: 创建批注编辑器组件**

```vue
<template>
  <div class="fixed inset-0 z-50 flex bg-black/60" v-if="visible">
    <!-- 左侧:截图+Canvas -->
    <div class="flex-1 overflow-auto p-6">
      <div class="mx-auto" style="max-width: 900px;">
        <ScreenshotCanvas
          :image-src="currentScreenshot.imageSrc"
          :tool="activeTool"
          :annotations="currentAnnotations"
          @add-annotation="onAddAnnotation"
        />
      </div>
    </div>
    <!-- 右侧:工具栏+表单 -->
    <div class="w-96 shrink-0 overflow-y-auto bg-white p-6 shadow-xl">
      <h3 class="mb-4 text-lg font-bold">批注工具</h3>
      <div class="mb-4 flex gap-2">
        <el-button :type="activeTool === 'rect' ? 'primary' : 'default'" @click="activeTool = 'rect'">矩形框选</el-button>
        <el-button :type="activeTool === 'freehand' ? 'primary' : 'default'" @click="activeTool = 'freehand'">任意形状</el-button>
        <el-button :type="activeTool === 'text' ? 'primary' : 'default'" @click="activeTool = 'text'">文字标注</el-button>
      </div>
      <el-button @click="undoLast" class="mb-2">撤销</el-button>
      <el-button @click="clearAll" class="mb-2">清空</el-button>

      <!-- 截图列表 -->
      <h4 class="mb-2 mt-4 text-sm font-bold">截图列表 ({{ screenshots.length }})</h4>
      <div class="flex flex-wrap gap-2 mb-4">
        <div
          v-for="(sc, idx) in screenshots"
          :key="idx"
          @click="switchScreenshot(idx)"
          :class="['cursor-pointer rounded border-2 p-1', idx === currentIndex ? 'border-blue-500' : 'border-gray-200']"
        >
          <img :src="sc.imageSrc" class="h-12 w-16 object-cover" />
          <div class="text-center text-xs">图{{ idx + 1 }}</div>
        </div>
      </div>
      <el-button @click="$emit('add-screenshot')" class="mb-4">+ 添加下一张</el-button>

      <!-- 批注清单 -->
      <h4 class="mb-2 text-sm font-bold">批注清单</h4>
      <div class="mb-4 space-y-2">
        <div v-for="(ann, idx) in currentAnnotations" :key="idx" class="rounded border p-2 text-sm">
          <span class="font-bold">框{{ idx + 1 }}</span>
          <span class="text-gray-500">({{ ann.type }})</span>
          <p>{{ ann.text }}</p>
          <el-button link type="danger" size="small" @click="removeAnnotation(idx)">删除</el-button>
        </div>
        <p v-if="currentAnnotations.length === 0" class="text-xs text-gray-400">暂无批注</p>
      </div>

      <!-- 意见表单 -->
      <h4 class="mb-2 text-sm font-bold">意见信息</h4>
      <el-form label-position="top">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" class="w-full">
            <el-option label="布局美化" value="layout" />
            <el-option label="功能优化" value="feature" />
            <el-option label="Bug反馈" value="bug" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="详细描述" />
        </el-form-item>
        <el-button type="primary" @click="onSubmit" :disabled="!canSubmit" class="w-full">提交意见</el-button>
        <el-button @click="$emit('cancel')" class="mt-2 w-full">取消</el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ScreenshotCanvas from './ScreenshotCanvas.vue'

const props = defineProps({
  visible: Boolean,
  screenshots: Array, // [{ imageSrc, width, height, annotations: [] }]
  pageUrl: String
})
const emit = defineEmits(['cancel', 'submit', 'add-screenshot'])

const activeTool = ref('rect')
const currentIndex = ref(0)
const form = ref({ title: '', category: 'other', description: '' })

const currentScreenshot = computed(() => props.screenshots[currentIndex.value] || { imageSrc: '' })
const currentAnnotations = computed(() => currentScreenshot.value.annotations || [])

const canSubmit = computed(() => form.value.title && form.value.description)

function switchScreenshot(idx) {
  currentIndex.value = idx
}

function onAddAnnotation(ann) {
  // 弹出输入框要求用户输入文字
  ElMessageBox.prompt('请输入该批注的文字说明', '批注说明', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValidator: (val) => !!val || '必须输入文字说明'
  }).then(({ value }) => {
    ann.text = value
    ann.color = '#EF4444'
    currentScreenshot.value.annotations.push(ann)
  }).catch(() => {})
}

function removeAnnotation(idx) {
  currentScreenshot.value.annotations.splice(idx, 1)
}

function undoLast() {
  currentScreenshot.value.annotations.pop()
}

function clearAll() {
  currentScreenshot.value.annotations = []
}

function onSubmit() {
  emit('submit', {
    title: form.value.title,
    description: form.value.description,
    category: form.value.category,
    page_url: props.pageUrl,
    screenshots: props.screenshots
  })
}

// 监听 visible 重置
watch(() => props.visible, (v) => {
  if (v) {
    currentIndex.value = 0
    form.value = { title: '', category: 'other', description: '' }
  }
})
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/cobuild/AnnotationEditor.vue
git commit -m "feat: 批注编辑器组件"
```

---

## Task 8: SuggestionCard 和 SuggestionDetail 组件

**Files:**
- Create: `frontend/src/components/cobuild/SuggestionCard.vue`
- Create: `frontend/src/components/cobuild/SuggestionDetail.vue`
- Create: `frontend/src/components/cobuild/DiscussionThread.vue`

- [ ] **Step 1: 创建 SuggestionCard 组件**

```vue
<template>
  <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md">
    <div class="mb-2 flex items-center justify-between">
      <span class="rounded-full px-2 py-1 text-xs font-semibold" :class="categoryClass">{{ categoryLabel }}</span>
      <span class="rounded-full px-2 py-1 text-xs" :class="statusClass">{{ statusLabel }}</span>
    </div>
    <h3 class="mb-1 font-bold text-slate-800">{{ suggestion.title }}</h3>
    <p class="mb-2 line-clamp-2 text-sm text-slate-500">{{ suggestion.description }}</p>
    <div class="flex items-center justify-between text-xs text-slate-400">
      <span>{{ suggestion.created_at }}</span>
      <el-button link type="primary" @click="$emit('view', suggestion.id)">查看详情</el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ suggestion: Object })
defineEmits(['view'])

const categoryLabel = computed(() => ({ layout: '布局美化', feature: '功能优化', bug: 'Bug反馈', other: '其他' }[props.suggestion.category] || '其他'))
const categoryClass = computed(() => ({
  layout: 'bg-blue-50 text-blue-600', feature: 'bg-green-50 text-green-600',
  bug: 'bg-red-50 text-red-600', other: 'bg-gray-100 text-gray-600'
}[props.suggestion.category] || 'bg-gray-100 text-gray-600'))

const statusLabel = computed(() => ({
  received: '已收到', pending_fix: '等待修改', fixing: '修改中',
  wont_fix: '不予修改', done: '修改成功'
}[props.suggestion.status] || '已收到'))
const statusClass = computed(() => ({
  received: 'bg-gray-100 text-gray-600', pending_fix: 'bg-amber-50 text-amber-600',
  fixing: 'bg-blue-50 text-blue-600', wont_fix: 'bg-red-50 text-red-600',
  done: 'bg-green-50 text-green-600'
}[props.suggestion.status] || 'bg-gray-100 text-gray-600'))
</script>
```

- [ ] **Step 2: 创建 DiscussionThread 组件**

```vue
<template>
  <div class="space-y-3">
    <div v-for="reply in replies" :key="reply.id" class="rounded-lg bg-slate-50 p-3">
      <div class="mb-1 flex items-center justify-between">
        <span class="text-xs font-semibold text-slate-600">用户{{ reply.author_id }}</span>
        <span class="text-xs text-slate-400">{{ reply.created_at }}</span>
      </div>
      <p class="mb-2 text-sm text-slate-700">{{ reply.content }}</p>
      <el-button link size="small" :type="reply.endorsed ? 'primary' : 'default'" @click="$emit('endorse', reply.id)">
        复议 ({{ reply.endorse_count }})
      </el-button>
    </div>
    <div v-if="replies.length === 0" class="py-4 text-center text-sm text-slate-400">暂无讨论</div>
    <!-- 发表评论 -->
    <div class="flex gap-2">
      <el-input v-model="content" placeholder="发表评论..." />
      <el-button type="primary" @click="submit">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const props = defineProps({ replies: Array })
const emit = defineEmits(['endorse', 'reply'])
const content = ref('')
function submit() {
  if (!content.value.trim()) return
  emit('reply', content.value)
  content.value = ''
}
</script>
```

- [ ] **Step 3: 创建 SuggestionDetail 组件**

```vue
<template>
  <el-drawer v-model="visible" :title="detail?.title || '详情'" size="60%">
    <div v-if="detail">
      <!-- 基本信息 -->
      <el-descriptions :column="2" border class="mb-4">
        <el-descriptions-item label="分类">{{ categoryLabel }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusType">{{ statusLabel }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ detail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="关联页面">{{ detail.page_url }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ detail.description }}</el-descriptions-item>
      </el-descriptions>

      <!-- 批注文字清单 -->
      <h4 class="mb-2 font-bold">批注文字清单</h4>
      <div class="mb-4 space-y-1">
        <div v-for="sc in detail.screenshots" :key="sc.id" class="rounded border p-2">
          <p class="text-xs font-semibold text-slate-500">截图 {{ sc.index }}</p>
          <div v-for="ann in sc.annotations" :key="ann.id" class="text-sm">
            框 {{ ann.index }} ({{ ann.type }}): {{ ann.text }}
          </div>
        </div>
      </div>

      <!-- 截图缩略图 -->
      <h4 class="mb-2 font-bold">截图</h4>
      <div class="mb-4 flex flex-wrap gap-2">
        <div v-for="sc in detail.screenshots" :key="sc.id">
          <img :src="screenshotImageUrl(sc.id)" class="h-24 rounded border" />
        </div>
      </div>

      <!-- 状态管理(管理员) -->
      <template v-if="isAdmin">
        <h4 class="mb-2 font-bold">状态管理</h4>
        <div class="mb-4 flex gap-2">
          <el-select v-model="newStatus" placeholder="选择状态" class="w-40">
            <el-option label="等待修改" value="pending_fix" />
            <el-option label="修改中" value="fixing" />
            <el-option label="不予修改" value="wont_fix" />
            <el-option label="修改成功" value="done" />
          </el-select>
          <el-input v-model="statusReason" placeholder="说明/原因" class="w-60" />
          <el-button type="primary" @click="onStatusUpdate">更新</el-button>
        </div>
      </template>

      <!-- 讨论区 -->
      <h4 class="mb-2 font-bold">讨论区</h4>
      <DiscussionThread
        :replies="detail.replies"
        @endorse="onEndorse"
        @reply="onReply"
      />
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import DiscussionThread from './DiscussionThread.vue'
import { updateSuggestionStatus, createReply, toggleEndorse, screenshotImageUrl } from '@/api/suggestion'

const props = defineProps({
  modelValue: Boolean,
  detail: Object,
  isAdmin: Boolean
})
const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})
const newStatus = ref('')
const statusReason = ref('')

const categoryLabel = computed(() => ({ layout: '布局美化', feature: '功能优化', bug: 'Bug反馈', other: '其他' }[props.detail?.category] || ''))
const statusLabel = computed(() => ({ received: '已收到', pending_fix: '等待修改', fixing: '修改中', wont_fix: '不予修改', done: '修改成功' }[props.detail?.status] || ''))
const statusType = computed(() => ({ received: 'info', pending_fix: 'warning', fixing: 'primary', wont_fix: 'danger', done: 'success' }[props.detail?.status] || 'info'))

async function onStatusUpdate() {
  if (!newStatus.value) return ElMessage.warning('请选择状态')
  try {
    await updateSuggestionStatus(props.detail.id, { status: newStatus.value, reason: statusReason.value })
    ElMessage.success('状态已更新')
    newStatus.value = ''
    statusReason.value = ''
    emit('refresh')
  } catch (e) { ElMessage.error('更新失败') }
}

async function onEndorse(replyId) {
  try {
    await toggleEndorse(replyId)
    emit('refresh')
  } catch (e) { ElMessage.error('操作失败') }
}

async function onReply(content) {
  try {
    await createReply(props.detail.id, { content })
    ElMessage.success('评论成功')
    emit('refresh')
  } catch (e) { ElMessage.error('评论失败') }
}
</script>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/cobuild/SuggestionCard.vue frontend/src/components/cobuild/SuggestionDetail.vue frontend/src/components/cobuild/DiscussionThread.vue
git commit -m "feat: 意见卡片/详情/讨论组件"
```

---

## Task 9: CoBuild 主页面

**Files:**
- Create: `frontend/src/views/CoBuild.vue`

- [ ] **Step 1: 创建 CoBuild.vue 主页面**

```vue
<template>
  <div class="flex h-full flex-col gap-4 p-4 lg:p-6">
    <!-- 顶部标题区 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 shadow-sm">
          <el-icon :size="16"><EditPen /></el-icon>
        </div>
        <h1 class="text-xl font-bold text-slate-800">共建</h1>
      </div>
      <el-button type="primary" @click="showLauncher = true">提建议</el-button>
    </div>

    <!-- 意见列表 -->
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <SuggestionCard
        v-for="s in suggestions"
        :key="s.id"
        :suggestion="s"
        @view="openDetail"
      />
    </div>
    <div v-if="suggestions.length === 0" class="py-12 text-center text-slate-400">
      暂无意见,点击"提建议"提交第一条
    </div>

    <!-- 截图启动器 -->
    <ScreenshotLauncher
      v-model:visible="showLauncher"
      @start-screenshot="startScreenshot"
    />

    <!-- 批注编辑器 -->
    <AnnotationEditor
      :visible="showEditor"
      :screenshots="editorScreenshots"
      :page-url="currentPageUrl"
      @cancel="showEditor = false"
      @add-screenshot="addScreenshot"
      @submit="submitSuggestion"
    />

    <!-- 意见详情 -->
    <SuggestionDetail
      v-model="showDetail"
      :detail="currentDetail"
      :is-admin="userStore.isAdmin"
      @refresh="loadDetail"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { EditPen } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { getSuggestions, getSuggestionDetail, createSuggestion } from '@/api/suggestion'
import ScreenshotLauncher from '@/components/cobuild/ScreenshotLauncher.vue'
import AnnotationEditor from '@/components/cobuild/AnnotationEditor.vue'
import SuggestionCard from '@/components/cobuild/SuggestionCard.vue'
import SuggestionDetail from '@/components/cobuild/SuggestionDetail.vue'

const userStore = useUserStore()
const suggestions = ref([])
const showLauncher = ref(false)
const showEditor = ref(false)
const showDetail = ref(false)
const currentDetail = ref(null)
const currentPageUrl = ref('')
const editorScreenshots = ref([])

onMounted(loadList)

async function loadList() {
  try {
    const res = await getSuggestions({ page: 1, page_size: 50 })
    if (res.code === 200) suggestions.value = res.data.items
  } catch (e) { ElMessage.error('加载列表失败') }
}

function startScreenshot(pageUrl) {
  currentPageUrl.value = pageUrl
  editorScreenshots.value = []
  showLauncher.value = false
  // 新标签打开目标页面并进入截图模式
  const url = `${window.location.origin}${pageUrl}?screenshot=1`
  window.open(url, '_blank')
  // 监听截图完成消息
  window.addEventListener('message', onScreenshotMessage, { once: true })
  showEditor.value = true
}

function onScreenshotMessage(e) {
  if (e.data?.type === 'screenshot') {
    editorScreenshots.value.push({
      imageSrc: e.data.imageSrc,
      width: e.data.width,
      height: e.data.height,
      annotations: []
    })
  }
}

function addScreenshot() {
  const url = `${window.location.origin}${currentPageUrl.value}?screenshot=1`
  window.open(url, '_blank')
  window.addEventListener('message', onScreenshotMessage, { once: true })
}

async function openDetail(id) {
  showDetail.value = true
  await loadDetail(id)
}

async function loadDetail(id) {
  try {
    const res = await getSuggestionDetail(id || currentDetail.value?.id)
    if (res.code === 200) currentDetail.value = res.data
  } catch (e) { ElMessage.error('加载详情失败') }
}

async function submitSuggestion(formData) {
  try {
    // 将 imageSrc(base64) 转换为提交格式
    const payload = {
      title: formData.title,
      description: formData.description,
      category: formData.category,
      page_url: formData.page_url,
      screenshots: formData.screenshots.map(sc => ({
        image_data: sc.imageSrc,
        width: sc.width,
        height: sc.height,
        annotations: sc.annotations
      }))
    }
    const res = await createSuggestion(payload)
    if (res.code === 200) {
      ElMessage.success('提交成功')
      showEditor.value = false
      loadList()
    }
  } catch (e) { ElMessage.error('提交失败') }
}
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/CoBuild.vue
git commit -m "feat: 共建主页面"
```

---

## Task 10: ScreenshotLauncher 组件

**Files:**
- Create: `frontend/src/components/cobuild/ScreenshotLauncher.vue`

- [ ] **Step 1: 创建截图启动器组件**

```vue
<template>
  <el-dialog v-model="visible" title="选择截图页面" width="400px">
    <p class="mb-3 text-sm text-slate-500">选择要反馈的页面,点击后将在新标签页打开并进入截图模式</p>
    <el-select v-model="selectedPage" placeholder="请选择页面" class="w-full mb-4">
      <el-option v-for="p in pages" :key="p.url" :label="p.label" :value="p.url" />
    </el-select>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :disabled="!selectedPage" @click="onStart">前往截图</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ visible: Boolean })
const emit = defineEmits(['update:visible', 'start-screenshot'])

const visible = computed({
  get: () => props.visible,
  set: (v) => emit('update:visible', v)
})
const selectedPage = ref('')

const pages = [
  { label: '首页概览', url: '/home' },
  { label: '会议室预约', url: '/rooms' },
  { label: '招新面试', url: '/recruitment' },
  { label: '竞赛队伍', url: '/teams-center' },
  { label: '通讯录', url: '/contacts' },
  { label: '账号设置', url: '/settings' },
  { label: '成员管理', url: '/users' },
  { label: '日程管理', url: '/admin/schedule' },
  { label: '会议室管理', url: '/admin/rooms' },
  { label: '招新管理', url: '/admin/recruitment' },
  { label: '赛事管理', url: '/admin/events' },
]

function onStart() {
  emit('start-screenshot', selectedPage.value)
  visible.value = false
}
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/cobuild/ScreenshotLauncher.vue
git commit -m "feat: 截图启动器组件"
```

---

## Task 11: 截图模式注入(html2canvas)

**Files:**
- Modify: `frontend/src/layout/MainLayout.vue`

- [ ] **Step 1: 在 MainLayout.vue 中注入截图模式逻辑**

在 `<script setup>` 中添加截图模式检测和 html2canvas 调用逻辑:

```javascript
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import html2canvas from 'html2canvas'

const screenshotMode = ref(false)

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  if (params.get('screenshot') === '1') {
    screenshotMode.value = true
    document.body.style.cursor = 'crosshair'
    // 添加暗色遮罩
    const overlay = document.createElement('div')
    overlay.id = 'screenshot-overlay'
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.3);z-index:9999;pointer-events:none;'
    document.body.appendChild(overlay)
    // 监听框选
    startScreenshotSelection()
  }
})

function startScreenshotSelection() {
  let isSelecting = false
  let startX = 0, startY = 0
  let selectionBox = null

  document.addEventListener('mousedown', async (e) => {
    if (!screenshotMode.value) return
    isSelecting = true
    startX = e.clientX
    startY = e.clientY
    selectionBox = document.createElement('div')
    selectionBox.style.cssText = `position:fixed;border:2px solid #3B82F6;background:rgba(59,130,246,0.1);z-index:10000;left:${startX}px;top:${startY}px;`
    document.body.appendChild(selectionBox)
  })

  document.addEventListener('mousemove', (e) => {
    if (!isSelecting || !selectionBox) return
    const w = e.clientX - startX
    const h = e.clientY - startY
    selectionBox.style.width = Math.abs(w) + 'px'
    selectionBox.style.height = Math.abs(h) + 'px'
    selectionBox.style.left = Math.min(startX, e.clientX) + 'px'
    selectionBox.style.top = Math.min(startY, e.clientY) + 'px'
  })

  document.addEventListener('mouseup', async (e) => {
    if (!isSelecting || !selectionBox) return
    isSelecting = false
    const w = Math.abs(e.clientX - startX)
    const h = Math.abs(e.clientY - startY)
    if (w < 10 || h < 10) {
      selectionBox.remove()
      return
    }
    // 执行截图
    const x = Math.min(startX, e.clientX)
    const y = Math.min(startY, e.clientY)
    selectionBox.remove()
    await captureScreenshot(x, y, w, h)
  })
}

async function captureScreenshot(x, y, w, h) {
  try {
    const canvas = await html2canvas(document.body, {
      x: x + window.scrollX,
      y: y + window.scrollY,
      width: w,
      height: h,
      useCORS: true,
      scale: 1
    })
    // 压缩为 JPEG
    const dataUrl = canvas.toDataURL('image/jpeg', 0.7)
    // 发送给父窗口
    window.opener?.postMessage({
      type: 'screenshot',
      imageSrc: dataUrl,
      width: w,
      height: h
    }, '*')
    // 关闭当前标签
    window.close()
  } catch (err) {
    ElMessage.error('截图失败,请重试')
  }
}
```

注意:在模板末尾添加 `<div v-if="screenshotMode" class="fixed inset-0 z-[9998] bg-black/30 pointer-events-none" />` 作为暗色遮罩的 Vue 版本(替代手动 DOM 创建)。

- [ ] **Step 2: 安装 html2canvas 依赖**

Run: `cd frontend && npm install html2canvas`

- [ ] **Step 3: Commit**

```bash
git add frontend/src/layout/MainLayout.vue frontend/package.json frontend/package-lock.json
git commit -m "feat: 截图模式注入(html2canvas)"
```

---

## Task 12: 集成测试与收尾

**Files:**
- All created files

- [ ] **Step 1: 验证前端编译无错误**

Run: `cd frontend && npm run build`
Expected: 构建成功无报错

- [ ] **Step 2: 验证后端启动无错误**

Run: 重启 uvicorn
Expected: 启动成功,6 张新表已建

- [ ] **Step 3: 端到端测试流程**

1. 访问 /co-build → 看到空列表
2. 点"提建议" → 选择"首页概览" → 点"前往截图"
3. 新标签打开首页 → 暗色遮罩 + 十字光标
4. 拖框选区域 → 松开 → 截图传回共建页
5. 在批注编辑器中框选 + 输入文字 → 填表单 → 提交
6. 意见列表出现新卡片 → 点查看详情
7. 管理员看到批注文字清单 + 状态管理

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: 共建模块集成完成"
```
