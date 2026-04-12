"""
重建数据库脚本 - 删除所有旧表并按新模型重新创建

警告：此操作将删除所有现有数据！
使用前请确保已备份重要数据。

用法：
    python scripts/rebuild_database.py
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.core.database import engine, Base
from app.models import *  # 导入所有模型


def rebuild_database():
    """
    重建数据库
    1. 删除所有现有表
    2. 根据新模型创建所有表
    """
    
    print("⚠️  警告：此操作将删除所有现有数据库表！")
    print("=" * 60)
    
    # 二次确认
    confirm = input("请输入 'YES' 继续，或按Enter取消: ")
    if confirm != "YES":
        print("❌ 操作已取消")
        return
    
    print("\n🗑️  正在删除所有现有表...")
    
    try:
        # 删除所有表（按依赖关系反向删除）
        Base.metadata.drop_all(bind=engine)
        print("✅ 旧表已删除")
        
        print("\n📦 正在创建新表...")
        # 根据新模型创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 新表创建成功")
        
        # 显示创建的表
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            
        print(f"\n📋 已创建 {len(tables)} 个表：")
        for table in tables:
            print(f"   ✓ {table}")
        
        print("\n" + "=" * 60)
        print("✅ 数据库重建完成！")
        print("\n下一步：运行 python scripts/init_admin.py 创建管理员账号")
        
    except Exception as e:
        print(f"\n❌ 重建失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    rebuild_database()
