"""
初始化管理员账户脚本

用法：
    python scripts/init_admin.py
    
功能：
    创建学号为 110，密码为 654321 的管理员账户
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash


def init_admin_account():
    """
    初始化管理员账户
    - 学号: 110
    - 密码: 654321
    - 姓名: 系统管理员
    - 角色: admin
    - 状态: active
    """
    
    # 创建所有表
    print("📦 正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成\n")
    
    # 创建数据库会话
    db: Session = SessionLocal()
    
    try:
        # 检查管理员账号是否已存在
        existing_admin = db.query(User).filter(User.student_id == "110").first()
        
        if existing_admin:
            print("⚠️  管理员账号已存在:")
            print(f"   学号: {existing_admin.student_id}")
            print(f"   姓名: {existing_admin.full_name}")
            print(f"   角色: {existing_admin.role}")
            print(f"   状态: {existing_admin.status}")
            
            # 询问是否重置密码
            response = input("\n是否重置密码为 654321? (y/n): ")
            if response.lower() == 'y':
                existing_admin.password_hash = get_password_hash("654321")
                existing_admin.role = 'admin'
                existing_admin.status = 'active'
                db.commit()
                print("✅ 密码已重置，角色和状态已更新")
            else:
                print("❌ 操作已取消")
            return
        
        # 创建新管理员账号
        admin_user = User(
            student_id="110",
            password_hash=get_password_hash("654321"),
            full_name="系统管理员",
            phone=None,
            email="admin@system.com",
            department="系统部门",
            position="管理员",
            role='admin',
            status='active'
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ 管理员账号创建成功！")
        print("\n📋 账号信息:")
        print(f"   学号: {admin_user.student_id}")
        print(f"   密码: 654321")
        print(f"   姓名: {admin_user.full_name}")
        print(f"   邮箱: {admin_user.email}")
        print(f"   部门: {admin_user.department}")
        print(f"   职位: {admin_user.position}")
        print(f"   角色: {admin_user.role}")
        print(f"   状态: {admin_user.status}")
        print(f"   创建时间: {admin_user.created_at}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 创建失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 初始化管理员账户")
    print("=" * 50)
    print()
    
    init_admin_account()
    
    print()
    print("=" * 50)
    print("✨ 完成")
    print("=" * 50)
