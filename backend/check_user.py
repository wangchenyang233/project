import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath('.'))

from app import create_app
from app.models import User

# 创建Flask应用实例
app = create_app()

# 在应用上下文中查询用户信息
with app.app_context():
    # 查询超级管理员用户
    user = User.query.filter_by(is_super_admin=True).first()
    
    if user:
        print(f"用户ID: {user.id}")
        print(f"用户名: {user.username}")
        print(f"密码哈希: {user.password}")
        print(f"超级管理员: {user.is_super_admin}")
        print(f"状态: {user.status}")
    else:
        print("未找到超级管理员用户")
        # 查询所有用户
        all_users = User.query.all()
        print(f"所有用户 ({len(all_users)}):")
        for u in all_users:
            print(f"  ID: {u.id}, 用户名: {u.username}, 超级管理员: {u.is_super_admin}")
