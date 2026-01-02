#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试密码哈希验证机制的脚本
"""
import pymysql
from passlib.context import CryptContext

# 密码加密上下文（与项目中使用的一致）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_password_verification():
    """测试密码哈希验证机制"""
    # 数据库连接配置
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': 'vue_flask_db',
        'charset': 'utf8mb4'
    }
    
    try:
        # 连接数据库
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # 获取超级管理员用户
            cursor.execute("SELECT username, password FROM users WHERE is_super_admin = 1")
            super_admin = cursor.fetchone()
            
            if super_admin:
                username, hashed_password = super_admin
                print(f"获取到超级管理员用户: {username}")
                print(f"密码哈希值: {hashed_password}")
                
                # 测试密码验证
                test_password = 'Admin123!'
                print(f"\n测试密码: {test_password}")
                
                try:
                    is_valid = pwd_context.verify(test_password, hashed_password)
                    print(f"密码验证结果: {'✅ 密码正确' if is_valid else '❌ 密码错误'}")
                    
                    # 尝试重新哈希相同的密码，看看是否使用相同的算法
                    new_hash = pwd_context.hash(test_password)
                    print(f"\n重新哈希的密码: {new_hash}")
                    print(f"哈希算法是否匹配: {'✅ 匹配' if new_hash.startswith('$2b$') and hashed_password.startswith('$2b$') else '❌ 不匹配'}")
                    
                    return is_valid
                except Exception as e:
                    print(f"❌ 密码验证时出错: {e}")
                    return False
            else:
                print("❌ 未找到超级管理员用户")
                return False
    
    except Exception as e:
        print(f"❌ 连接数据库时出错: {e}")
        return False

if __name__ == '__main__':
    print("=== 密码哈希验证测试 ===")
    test_password_verification()