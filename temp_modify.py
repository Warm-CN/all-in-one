import re

with open('app/api/v1/signups.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We want to replace everything from "from pydantic import BaseModel" to the end of submit_application
replacement = """from pydantic import BaseModel

class ApplyRequest(BaseModel):
    signup_config_id: int
    student_id: str
    form_data: Dict[str, Any]

class UpdateApplyRequest(BaseModel):
    form_data: Dict[str, Any]

@router.post("/apply", response_model=dict, summary="提交报名表单")
async def submit_application(
    req: ApplyRequest,
    db: Session = Depends(get_db)
):
    \"\"\"
    场景 A（公开）：提交报名表单 (无需登录)
    \"\"\"
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
        status=ApplicationStatus.SUBMITTED
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
"""

# Let's replace the whole submitting logic
# Find @router.post("/apply" up to @router.get("/applications"
pattern = re.compile(r"from pydantic import BaseModel.*?@router\.get\(\"/applications\"", re.DOTALL)

new_content = pattern.sub(replacement + "\n\n@router.get(\"/applications\"", content)

# Now, we also need to update query-status endpoint
query_status_replacement = """class StatusQueryRequest(BaseModel):
    student_id: str
    phone: str

@router.post("/query-status", response_model=dict, summary="查询报名状态与面试信息（公开）")
async def query_application_status(
    req: StatusQueryRequest,
    db: Session = Depends(get_db)
):
    \"\"\"
    场景 A（公开）：公开查询入口
    \"\"\"
    apps = db.query(Application).filter(
        Application.student_id == req.student_id,
        Application.phone == req.phone
    ).order_by(Application.created_at.desc()).all()
    
    if not apps:
        return error_response(404, "未找到该同学的报名记录，请检查学号和手机号是否正确")
        
    results = []
    for app in apps:
        status_map = {
            "submitted": "已提交，筛选中",
            "reviewing": "面试/筛选进行中",
            "accepted": "已录用",
            "rejected": "未通过",
            "cancelled": "已取消"
        }
        status_desc = status_map.get(app.status.value, "未知状态")
        
        results.append({
            "id": app.id,
            "activity_title": app.signup_config.title if app.signup_config else "招新活动",
            "status": app.status.value,
            "status_desc": status_desc,
            "form_data": app.form_data,
            "notes": app.review_notes or "暂无通知，请稍后再次查询或关注短信",
            "interview_time": app.interview_time,
            "interview_location": app.interview_location,
            "submitted_at": app.created_at.isoformat()
        })
        
    return success_response(data=results, msg="查询成功")"""

query_pattern = re.compile(r"class StatusQueryRequest\(BaseModel\):.*", re.DOTALL)

if "class StatusQueryRequest" in new_content:
    new_content = query_pattern.sub(query_status_replacement, new_content)
else:
    new_content += "\n\n" + query_status_replacement

with open('app/api/v1/signups.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done updating signups.py")
