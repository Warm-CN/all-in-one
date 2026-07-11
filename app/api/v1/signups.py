"""
报名系统路由
场景 A：公开接口 - 提交报名表单（无需登录）
"""
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
from io import BytesIO
from urllib.parse import quote

from fastapi.responses import Response
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font

from app.core.database import get_db
from app.core.dependencies import require_admin, require_member
from app.models.signup import SignupConfig
from app.models.application import Application, ApplicationStatus, InterviewStage
from app.models.user import User
from app.schemas.response import success_response, error_response

router = APIRouter()


STAGE_LABEL_MAP = {
    InterviewStage.FIRST_ROUND: "第一轮面试",
    InterviewStage.SECOND_ROUND: "第二轮面试",
    InterviewStage.ACCEPTED: "已录用",
    InterviewStage.REJECTED: "已淘汰",
}

APPLICATION_STATUS_LABELS = {
    ApplicationStatus.SUBMITTED: "已提交",
    ApplicationStatus.REVIEWING: "审核中",
    ApplicationStatus.ACCEPTED: "已通过",
    ApplicationStatus.REJECTED: "未通过",
    ApplicationStatus.CANCELLED: "已取消",
}

FIXED_SIGNUP_CATEGORIES = ["recruitment", "wireless_cup", "telecom_cup"]

FIXED_SIGNUP_DEFAULTS = {
    "recruitment": {
        "title": "协会招新",
        "description": "协会招新报名",
    },
    "wireless_cup": {
        "title": "无线杯",
        "description": "无线杯报名",
    },
    "telecom_cup": {
        "title": "电信杯",
        "description": "电信杯报名",
    },
}

DEFAULT_FORM_FIELDS = [
    {"name": "姓名", "type": "text", "required": True},
    {"name": "手机号", "type": "text", "required": True},
    {"name": "邮箱", "type": "text", "required": True},
    {"name": "学院", "type": "text", "required": True},
    {"name": "专业班级", "type": "text", "required": True},
    {"name": "第一志愿", "type": "select", "required": True},
    {"name": "第二志愿", "type": "select", "required": False},
    {"name": "服从调剂", "type": "radio", "required": True},
    {"name": "自我介绍", "type": "textarea", "required": False}
]

EXCEL_TEMPLATE_HEADERS = [
    "姓名", "学号", "手机号", "邮箱", "学院", "专业班级", "第一志愿", "第二志愿", "服从调剂", "自我介绍",
    "一面时间", "一面地点", "二面部门", "二面时间", "二面地点", "备注"
]


def stage_to_label(stage: Optional[InterviewStage]) -> str:
    if not stage:
        return STAGE_LABEL_MAP[InterviewStage.FIRST_ROUND]
    return STAGE_LABEL_MAP.get(stage, STAGE_LABEL_MAP[InterviewStage.FIRST_ROUND])


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value).strip()


def excel_header_map(sheet) -> Dict[str, int]:
    return {
        normalize_text(cell.value): index
        for index, cell in enumerate(sheet[1])
        if normalize_text(cell.value)
    }


def excel_cell_value(row, header_map: Dict[str, int], names, fallback_index: Optional[int] = None) -> str:
    for name in names:
        index = header_map.get(name)
        if index is not None and index < len(row):
            return normalize_text(row[index])

    if fallback_index is not None and fallback_index < len(row):
        return normalize_text(row[fallback_index])

    return ""


def ensure_fixed_signup_configs(db: Session):
    now = datetime.now()
    for category in FIXED_SIGNUP_CATEGORIES:
        existing = db.query(SignupConfig).filter(SignupConfig.category == category).first()
        if existing:
            continue

        defaults = FIXED_SIGNUP_DEFAULTS[category]
        config = SignupConfig(
            title=defaults["title"],
            description=defaults["description"],
            category=category,
            start_time=now,
            end_time=now,
            max_participants=None,
            is_active=False,
            current_stage="registration",
            form_fields=DEFAULT_FORM_FIELDS,
        )
        db.add(config)

    db.commit()


def fill_export_sheet(sheet, applications):
    sheet.append(EXCEL_TEMPLATE_HEADERS)

    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for app in applications:
        form_data = app.form_data or {}
        sheet.append([
            app.name,
            app.student_id,
            app.phone,
            form_data.get("邮箱", ""),
            form_data.get("学院", ""),
            form_data.get("专业班级", ""),
            form_data.get("第一志愿", ""),
            form_data.get("第二志愿", ""),
            form_data.get("服从调剂", ""),
            form_data.get("自我介绍", ""),
            app.first_choice_interview_time or "",
            app.first_choice_interview_location or "",
            app.second_round_department or "",
            app.second_round_interview_time or "",
            app.second_round_interview_location or "",
            app.review_notes or "",
        ])

    column_widths = {
        "A": 12,
        "B": 16,
        "C": 16,
        "D": 24,
        "E": 16,
        "F": 18,
        "G": 14,
        "H": 14,
        "I": 12,
        "J": 34,
        "K": 20,
        "L": 20,
        "M": 14,
        "N": 20,
        "O": 20,
        "P": 30,
    }
    for col, width in column_widths.items():
        sheet.column_dimensions[col].width = width


def fill_example_sheet(sheet):
    sheet.append(EXCEL_TEMPLATE_HEADERS)
    sheet.append([
        "张三",
        "202600000001",
        "13800000000",
        "example@example.com",
        "信息学院",
        "计科2601",
        "科创部",
        "宣传部",
        "是",
        "喜欢技术实践，参加过校内项目。",
        "2026-06-20 19:00",
        "创新楼 A101",
        "科创部",
        "2026-06-27 19:00",
        "创新楼 A102",
        "请提前 10 分钟到场",
    ])

    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")

    column_widths = {
        "A": 12,
        "B": 16,
        "C": 16,
        "D": 24,
        "E": 16,
        "F": 18,
        "G": 14,
        "H": 14,
        "I": 12,
        "J": 34,
        "K": 20,
        "L": 20,
        "M": 14,
        "N": 20,
        "O": 20,
        "P": 30,
    }
    for col, width in column_widths.items():
        sheet.column_dimensions[col].width = width


@router.get("/configs", response_model=dict, summary="获取活跃的报名配置列表")
async def get_active_signup_configs(
    category: str = None,
    db: Session = Depends(get_db)
):
    """
    场景 A（公开）：获取当前可报名的活动列表
    
    无需登录即可访问
    """
    ensure_fixed_signup_configs(db)
    now = datetime.now()

    query = db.query(SignupConfig).filter(
        SignupConfig.is_active == True,
        SignupConfig.category.in_(FIXED_SIGNUP_CATEGORIES)
    )

    # 按分类筛选
    if category:
        query = query.filter(SignupConfig.category == category)

    # 只显示报名时间内的活动
    query = query.filter(
        SignupConfig.start_time <= now,
        SignupConfig.end_time >= now
    )

    configs = query.all()
    
    return success_response(
        data=[{
            "can_submit": bool(c.is_active and c.start_time <= now <= c.end_time),
            "id": c.id,
            "is_active": c.is_active,
            "title": c.title,
            "description": c.description,
            "category": c.category,
            "start_time": c.start_time.isoformat(),
            "end_time": c.end_time.isoformat(),
            "max_participants": c.max_participants,
            "form_fields": c.form_fields
        } for c in configs],
        msg="获取成功"
    )


from pydantic import BaseModel

class ApplyRequest(BaseModel):
    signup_config_id: int
    student_id: str
    form_data: Dict[str, Any]

class UpdateApplyRequest(BaseModel):
    form_data: Dict[str, Any]


class AdminUpdateApplicationRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    review_notes: Optional[str] = None
    interview_time: Optional[str] = None
    interview_location: Optional[str] = None
    first_choice_interview_time: Optional[str] = None
    first_choice_interview_location: Optional[str] = None
    second_choice_interview_time: Optional[str] = None
    second_choice_interview_location: Optional[str] = None
    second_round_department: Optional[str] = None
    second_round_interview_time: Optional[str] = None
    second_round_interview_location: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None


class AdminSignupConfigRequest(BaseModel):
    title: str
    category: str
    start_time: datetime
    end_time: datetime
    is_active: bool = True
    description: Optional[str] = None
    max_participants: Optional[int] = None


class AdminSignupConfigUpdateRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    max_participants: Optional[int] = None


@router.get("/admin/configs", response_model=dict, summary="管理员查看报名配置")
async def get_admin_signup_configs(
    category: str = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    ensure_fixed_signup_configs(db)
    query = db.query(SignupConfig).filter(SignupConfig.category.in_(FIXED_SIGNUP_CATEGORIES))
    if category:
        query = query.filter(SignupConfig.category == category)

    configs = query.order_by(SignupConfig.created_at.desc()).all()
    return success_response(
        data=[{
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "category": c.category,
            "start_time": c.start_time.isoformat(),
            "end_time": c.end_time.isoformat(),
            "max_participants": c.max_participants,
            "is_active": c.is_active,
            "form_fields": c.form_fields
        } for c in configs],
        msg=f"获取成功，共 {len(configs)} 条"
    )


@router.post("/admin/configs", response_model=dict, summary="管理员新建报名配置")
async def create_signup_config(
    req: AdminSignupConfigRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return error_response(400, "后台管理已固定为招新、无线杯、电信杯三类活动，不支持新建")


@router.put("/admin/configs/{config_id}", response_model=dict, summary="管理员修改报名配置")
async def update_signup_config(
    config_id: int,
    req: AdminSignupConfigUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    config = db.query(SignupConfig).filter(SignupConfig.id == config_id).first()
    if not config:
        return error_response(404, "配置不存在")
    if config.category not in FIXED_SIGNUP_CATEGORIES:
        return error_response(400, "仅允许修改固定活动配置")

    next_start = req.start_time if req.start_time is not None else config.start_time
    next_end = req.end_time if req.end_time is not None else config.end_time
    if next_start >= next_end:
        return error_response(400, "开始时间必须早于截止时间")

    if req.title is not None:
        config.title = req.title
    if req.category is not None and req.category != config.category:
        return error_response(400, "固定活动不允许修改分类")
    if req.start_time is not None:
        config.start_time = req.start_time
    if req.end_time is not None:
        config.end_time = req.end_time
    if req.is_active is not None:
        config.is_active = req.is_active
    if req.description is not None:
        config.description = req.description
    if req.max_participants is not None:
        config.max_participants = req.max_participants
    db.commit()
    return success_response(msg="修改成功")

@router.post("/apply", response_model=dict, summary="提交报名表单")
async def submit_application(
    req: ApplyRequest,
    db: Session = Depends(get_db)
):
    """
    场景 A（公开）：提交报名表单 (无需登录)
    """
    config = db.query(SignupConfig).filter(SignupConfig.id == req.signup_config_id).first()
    if not config:
        return error_response(404, "报名活动不存在")
    if not config.is_active:
        return error_response(400, "该活动已关闭报名")
        
    now = datetime.now()
    if now < config.start_time:
        return error_response(400, "报名尚未开始")
    if now > config.end_time:
        return error_response(400, "报名已结束")
        
    # 检查是否已报名
    existing = db.query(Application).filter(
        Application.student_id == req.student_id,
        Application.signup_config_id == req.signup_config_id
    ).first()
    if existing:
        return error_response(400, "您已经报名过该活动了")
        
    if config.max_participants:
        current_count = db.query(Application).filter(
            Application.signup_config_id == req.signup_config_id
        ).count()
        if current_count >= config.max_participants:
            return error_response(400, "报名人数已满")

    application = Application(
        signup_config_id=req.signup_config_id,
        student_id=req.student_id,
        name=req.form_data.get("姓名", "未知"),
        phone=req.form_data.get("手机号", "未知"),
        form_data=req.form_data,
        status=ApplicationStatus.SUBMITTED,
        current_stage=InterviewStage.FIRST_ROUND
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return success_response(data={"application_id": application.id}, msg="报名成功！")

@router.put("/apply/{application_id}", response_model=dict, summary="修改表单数据")
async def update_application(
    application_id: int,
    req: UpdateApplyRequest,
    db: Session = Depends(get_db)
):
    app_record = db.query(Application).filter(Application.id == application_id).first()
    if not app_record:
        return error_response(404, "记录不存在")
    
    if app_record.status != ApplicationStatus.SUBMITTED:
        return error_response(400, "当前状态不允许修改报名信息")
        
    app_record.form_data = req.form_data
    app_record.name = req.form_data.get("姓名", app_record.name)
    app_record.phone = req.form_data.get("手机号", app_record.phone)
    
    db.commit()
    return success_response(msg="修改成功")


@router.get("/applications", response_model=dict, summary="获取报名列表（仅管理员）")
async def get_applications(
    signup_config_id: int = None,
    status: str = None,
    keyword: str = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    场景 C（管理）：查看所有报名记录
    
    **仅限 Admin** - 导出数据
    """
    query = db.query(Application)
    
    if signup_config_id:
        query = query.filter(Application.signup_config_id == signup_config_id)
    
    if status:
        query = query.filter(Application.status == status)
    
    if keyword:
        query = query.filter(
            (Application.student_id.contains(keyword)) |
            (Application.name.contains(keyword)) |
            (Application.phone.contains(keyword))
        )

    applications = query.order_by(Application.created_at.desc()).all()
    
    return success_response(
        data=[{
            "id": app.id,
            "user_id": app.user_id,
            "signup_config_id": app.signup_config_id,
            "activity_title": app.signup_config.title if app.signup_config else "招新活动",
            "student_id": app.student_id,
            "name": app.name,
            "phone": app.phone,
            "form_data": app.form_data,
            "status": app.status.value,
            "current_stage": app.current_stage.value if app.current_stage else "first_round",
            "current_stage_desc": stage_to_label(app.current_stage),
            "review_notes": app.review_notes,
            "interview_time": app.interview_time,
            "interview_location": app.interview_location,
            "first_choice_interview_time": app.first_choice_interview_time,
            "first_choice_interview_location": app.first_choice_interview_location,
            "second_choice_interview_time": app.second_choice_interview_time,
            "second_choice_interview_location": app.second_choice_interview_location,
            "second_round_department": app.second_round_department,
            "second_round_interview_time": app.second_round_interview_time,
            "second_round_interview_location": app.second_round_interview_location,
            "created_at": app.created_at.isoformat()
        } for app in applications],
        msg=f"获取成功，共 {len(applications)} 条"
    )


@router.get("/applications/internal", response_model=dict, summary="内部查看报名列表（成员可见）")
async def get_internal_applications(
    keyword: str = None,
    department: str = None,
    current_user: User = Depends(require_member),
    db: Session = Depends(get_db)
):
    query = db.query(Application)

    if keyword:
        query = query.filter(
            (Application.student_id.contains(keyword)) |
            (Application.name.contains(keyword)) |
            (Application.phone.contains(keyword))
        )

    applications = query.order_by(Application.created_at.desc()).all()

    if department:
        applications = [
            app for app in applications
            if (app.form_data or {}).get("第一志愿") == department or (app.form_data or {}).get("第二志愿") == department
        ]

    return success_response(
        data=[{
            "id": app.id,
            "student_id": app.student_id,
            "name": app.name,
            "phone": app.phone,
            "first_choice": (app.form_data or {}).get("第一志愿", ""),
            "second_choice": (app.form_data or {}).get("第二志愿", ""),
            "form_data": app.form_data,
            "current_stage": app.current_stage.value if app.current_stage else "first_round",
            "current_stage_desc": stage_to_label(app.current_stage),
            "college": (app.form_data or {}).get("学院", ""),
            "major": (app.form_data or {}).get("专业班级", ""),
            "adjust": (app.form_data or {}).get("服从调剂", ""),
            "email": (app.form_data or {}).get("邮箱", ""),
            "intro": (app.form_data or {}).get("自我介绍", ""),
            "first_choice_interview_time": app.first_choice_interview_time,
            "first_choice_interview_location": app.first_choice_interview_location,
            "second_choice_interview_time": app.second_choice_interview_time,
            "second_choice_interview_location": app.second_choice_interview_location,
            "second_round_department": app.second_round_department,
            "second_round_interview_time": app.second_round_interview_time,
            "second_round_interview_location": app.second_round_interview_location,
            "review_notes": app.review_notes,
        } for app in applications],
        msg=f"获取成功，共 {len(applications)} 条"
    )


@router.get("/applications/export", summary="导出报名表（仅管理员）")
async def export_applications(
    keyword: str = None,
    department: str = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Application)

    if keyword:
        query = query.filter(
            (Application.student_id.contains(keyword)) |
            (Application.name.contains(keyword)) |
            (Application.phone.contains(keyword))
        )

    applications = query.order_by(Application.created_at.desc()).all()

    if department:
        applications = [
            app for app in applications
            if (app.form_data or {}).get("第一志愿") == department or (app.form_data or {}).get("第二志愿") == department
        ]

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "招新报名信息"
    fill_export_sheet(sheet, applications)

    example_sheet = workbook.create_sheet("填写示例")
    fill_example_sheet(example_sheet)

    help_sheet = workbook.create_sheet("填写说明")
    help_sheet.append(["字段", "说明"])
    help_sheet.append(["一面时间/地点", "第一次面试安排，可按示例格式填写"])
    help_sheet.append(["二面部门", "第二次面试对应部门"])
    help_sheet.append(["二面时间/地点", "第二次面试安排，可按示例格式填写"])
    help_sheet.append(["备注", "会写入系统通知信息"])
    help_sheet.append(["导入规则", "只更新 Excel 中填写了内容的单元格；留空不会清空系统里已有安排"])
    for cell in help_sheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    help_sheet.column_dimensions["A"].width = 28
    help_sheet.column_dimensions["B"].width = 64

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    filename = f"recruitment_applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    encoded_filename = quote(filename)
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
    }
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )


@router.get("/applications/import-template", summary="下载面试安排导入模板（仅管理员）")
async def download_import_template(
    current_user: User = Depends(require_admin),
):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "面试安排导入"
    sheet.append(EXCEL_TEMPLATE_HEADERS)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    column_widths = {"A": 12, "B": 12, "C": 15, "D": 22, "E": 15, "F": 15, "G": 15, "H": 18, "I": 12, "J": 30, "K": 18, "L": 18, "M": 15, "N": 18, "O": 18, "P": 25}
    for col, width in column_widths.items():
        sheet.column_dimensions[col].width = width

    help_sheet = workbook.create_sheet("填写说明")
    help_sheet.append(["字段", "说明"])
    help_sheet.append(["姓名/学号", "用于匹配报名人，至少填一项"])
    help_sheet.append(["一面时间/地点", "第一次面试安排，如：2026-07-15 14:00 / 教学楼A301"])
    help_sheet.append(["二面部门", "第二次面试对应部门"])
    help_sheet.append(["二面时间/地点", "第二次面试安排"])
    help_sheet.append(["导入规则", "只更新 Excel 中填写了内容的单元格；留空不会清空已有安排"])
    for cell in help_sheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    help_sheet.column_dimensions["A"].width = 28
    help_sheet.column_dimensions["B"].width = 64

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    filename = "面试安排导入模板.xlsx"
    encoded_filename = quote(filename)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )


@router.post("/applications/import", response_model=dict, summary="导入面试安排（仅管理员）")
async def import_applications_interview_info(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        return error_response(400, "请上传 xlsx 文件")

    content = await file.read()
    if not content:
        return error_response(400, "上传文件为空")

    try:
        workbook = load_workbook(BytesIO(content), data_only=True)
    except Exception:
        return error_response(400, "Excel 文件解析失败，请检查模板格式")

    sheet = workbook.active
    header_map = excel_header_map(sheet)
    rows = list(sheet.iter_rows(min_row=2, values_only=True))
    if not rows:
        return error_response(400, "Excel 中没有可导入的数据")

    updated = 0
    skipped = 0
    unchanged = 0

    for row in rows:
        student_id = excel_cell_value(row, header_map, ["学号", "student_id"], 1)
        if not student_id:
            skipped += 1
            continue

        app_record = db.query(Application).filter(
            Application.student_id == student_id
        ).order_by(Application.created_at.desc()).first()
        if not app_record:
            skipped += 1
            continue

        row_changed = False
        field_updates = {
            "first_choice_interview_time": excel_cell_value(row, header_map, ["一面时间", "第一次面试时间", "一面-第一志愿时间", "first_choice_interview_time"], 10),
            "first_choice_interview_location": excel_cell_value(row, header_map, ["一面地点", "第一次面试地点", "一面-第一志愿地点", "first_choice_interview_location"], 11),
            "second_round_department": excel_cell_value(row, header_map, ["二面部门", "第二次面试部门", "second_round_department"], 12),
            "second_round_interview_time": excel_cell_value(row, header_map, ["二面时间", "第二次面试时间", "second_round_interview_time"], 13),
            "second_round_interview_location": excel_cell_value(row, header_map, ["二面地点", "第二次面试地点", "second_round_interview_location"], 14),
        }

        # 更安全的导入策略：只有 Excel 中明确填写的字段才会覆盖数据库中的现有值。
        for field_name, field_value in field_updates.items():
            if not field_value:
                continue
            if getattr(app_record, field_name) != field_value:
                setattr(app_record, field_name, field_value)
                row_changed = True

        notes_text = excel_cell_value(row, header_map, ["备注", "通知备注", "review_notes"], 15)
        if notes_text and app_record.review_notes != notes_text:
            app_record.review_notes = notes_text
            row_changed = True

        # 历史字段兼容：仅在一面被明确填写时才同步默认展示字段，避免空单元格误清空。
        first_choice_time = field_updates["first_choice_interview_time"]
        if first_choice_time and app_record.interview_time != app_record.first_choice_interview_time:
            app_record.interview_time = app_record.first_choice_interview_time
            row_changed = True

        first_choice_location = field_updates["first_choice_interview_location"]
        if first_choice_location and app_record.interview_location != app_record.first_choice_interview_location:
            app_record.interview_location = app_record.first_choice_interview_location
            row_changed = True

        if row_changed:
            updated += 1
        else:
            unchanged += 1

    db.commit()
    return success_response(
        data={"updated": updated, "skipped": skipped, "unchanged": unchanged},
        msg=f"导入完成：更新 {updated} 条，跳过 {skipped} 条，未改动 {unchanged} 条"
    )


@router.put("/applications/{application_id}/admin", response_model=dict, summary="管理员修改报名记录")
async def admin_update_application(
    application_id: int,
    req: AdminUpdateApplicationRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    app_record = db.query(Application).filter(Application.id == application_id).first()
    if not app_record:
        return error_response(404, "记录不存在")

    if req.name is not None:
        app_record.name = req.name
    if req.phone is not None:
        app_record.phone = req.phone
    if req.status is not None:
        app_record.status = req.status
    if req.review_notes is not None:
        app_record.review_notes = req.review_notes
    if req.interview_time is not None:
        app_record.interview_time = req.interview_time
    if req.interview_location is not None:
        app_record.interview_location = req.interview_location
    if req.first_choice_interview_time is not None:
        app_record.first_choice_interview_time = req.first_choice_interview_time
    if req.first_choice_interview_location is not None:
        app_record.first_choice_interview_location = req.first_choice_interview_location
    if req.second_choice_interview_time is not None:
        app_record.second_choice_interview_time = req.second_choice_interview_time
    if req.second_choice_interview_location is not None:
        app_record.second_choice_interview_location = req.second_choice_interview_location
    if req.second_round_department is not None:
        app_record.second_round_department = req.second_round_department
    if req.second_round_interview_time is not None:
        app_record.second_round_interview_time = req.second_round_interview_time
    if req.second_round_interview_location is not None:
        app_record.second_round_interview_location = req.second_round_interview_location
    if req.form_data is not None:
        app_record.form_data = req.form_data

    if req.first_choice_interview_time is not None:
        app_record.interview_time = req.first_choice_interview_time
    if req.first_choice_interview_location is not None:
        app_record.interview_location = req.first_choice_interview_location

    db.commit()
    db.refresh(app_record)

    return success_response(msg="修改成功")


@router.delete("/applications/{application_id}", response_model=dict, summary="管理员删除报名记录")
async def admin_delete_application(
    application_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    app_record = db.query(Application).filter(Application.id == application_id).first()
    if not app_record:
        return error_response(404, "记录不存在")

    db.delete(app_record)
    db.commit()
    return success_response(msg="删除成功")

class StatusQueryRequest(BaseModel):
    student_id: str
    phone: str

@router.post("/query-status", response_model=dict, summary="查询报名状态与面试信息（公开）")
async def query_application_status(
    req: StatusQueryRequest,
    db: Session = Depends(get_db)
):
    """
    场景 A（公开）：公开查询入口
    """
    apps = db.query(Application).filter(
        Application.student_id == req.student_id,
        Application.phone == req.phone
    ).order_by(Application.created_at.desc()).all()
    
    if not apps:
        return error_response(404, "未找到该同学的报名记录，请检查学号和手机号是否正确")
        
    results = []
    for app in apps:
        status_desc = APPLICATION_STATUS_LABELS.get(app.status, app.status.value)
        interview_time = app.first_choice_interview_time or app.interview_time
        interview_location = app.first_choice_interview_location or app.interview_location
        
        results.append({
            "id": app.id,
            "activity_title": app.signup_config.title if app.signup_config else "招新活动",
            "status": app.status.value,
            "current_stage": app.current_stage.value if app.current_stage else "first_round",
            "status_desc": status_desc,
            "form_data": app.form_data,
            "notes": app.review_notes or "暂无通知，请稍后再次查询或关注短信",
            "interview_time": interview_time,
            "interview_location": interview_location,
            "first_choice_interview_time": app.first_choice_interview_time,
            "first_choice_interview_location": app.first_choice_interview_location,
            "second_choice_interview_time": app.second_choice_interview_time,
            "second_choice_interview_location": app.second_choice_interview_location,
            "second_round_department": app.second_round_department,
            "second_round_interview_time": app.second_round_interview_time,
            "second_round_interview_location": app.second_round_interview_location,
            "submitted_at": app.created_at.isoformat()
        })
        
    return success_response(data=results, msg="查询成功")
