"""
初始化默认招新活动配置（可重复执行，幂等）

用法：
    .venv/Scripts/python.exe scripts/init_signup_config.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.models.signup import SignupConfig


def init_signup_config() -> None:
    db = SessionLocal()
    try:
        now = datetime.now()

        existing = db.query(SignupConfig).filter(
            SignupConfig.is_active == True,
            SignupConfig.start_time <= now,
            SignupConfig.end_time >= now,
            SignupConfig.category.in_(["recruitment", "招新"])
        ).first()

        if existing:
            print(f"已存在开放中的招新活动: {existing.title} (id={existing.id})")
            return

        config = SignupConfig(
            title="2026 春季协会招新",
            description="欢迎报名协会，提交后可在公开页面查询进度与面试安排。",
            start_time=now - timedelta(days=1),
            end_time=now + timedelta(days=20),
            max_participants=None,
            is_active=True,
            category="recruitment",
            form_fields=[
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
        )

        db.add(config)
        db.commit()
        db.refresh(config)
        print(f"已创建默认招新活动: {config.title} (id={config.id})")
    except Exception as exc:
        db.rollback()
        print(f"初始化失败: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_signup_config()
