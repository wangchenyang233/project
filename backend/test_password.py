import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath('.'))

from app.utils.encrypt_util import verify_pwd
from app.config import Config

# 测试密码
password = Config.SUPER_ADMIN_PASSWORD
# 从数据库中获取的密码哈希
hashed_password = '$2b$12$yqEu2LPHaqixz92U08sE2ujTkQnZehf2HnjFvUGwtia7Yewa1XlEC'

print(f"测试密码: {password}")
print(f"密码哈希: {hashed_password}")
print(f"密码验证结果: {verify_pwd(hashed_password, password)}")
