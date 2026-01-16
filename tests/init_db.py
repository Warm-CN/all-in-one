"""
数据库初始化脚本
创建所有表并添加初始管理员账号
"""
from app.core.database import engine, Base, SessionLocal
from app.models import User, UserRole, UserStatus
from app.core.security import get_password_hash


def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建所有表
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功！")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print(f"⚠️  管理员账号已存在: {existing_admin.real_name} (学号: {existing_admin.student_id})")
            return
        
        # 创建管理员账号
        print("\n创建管理员账号...")
        admin_user = User(
            real_name="系统管理员",
            password_hash=get_password_hash("123456"),
            student_id="admin",
            phone="13800138000",
            email="admin@example.com",
            department="技术部",
            position="系统管理员",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ 管理员账号创建成功！")
        print(f"   姓名: {admin_user.real_name}")
        print(f"   学号: {admin_user.student_id}")
        print(f"   密码: 123456")
        print(f"   角色: {admin_user.role.value}")
        print(f"   状态: {admin_user.status.value}")
        
    except Exception as e:
        print(f"❌ 创建管理员失败: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n🎉 数据库初始化完成！")


if __name__ == "__main__":
    init_database()
