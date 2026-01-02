#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证超级管理员用户是否已创建的脚本
"""
import pymysql


def verify_super_admin():
    """验证超级管理员用户是否已创建"""
    # 数据库连接配置
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '123456',  # 用户提供的密码
        'database': 'vue_flask_db',
        'charset': 'utf8mb4'
    }
    
    try:
        # 连接数据库
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # 查询超级管理员用户
            cursor.execute("SELECT * FROM users WHERE is_super_admin = 1")
            super_admin = cursor.fetchone()
            
            if super_admin:
                print("✅ 超级管理员用户已成功创建！")
                print(f"   ID: {super_admin[0]}")
                print(f"   用户名: {super_admin[1]}")
                print(f"   状态: {'启用' if super_admin[3] == 1 else '禁用'}")
                print(f"   创建时间: {super_admin[9]}")
                print("   权限: 超级管理员")
                return True
            else:
                print("❌ 未找到超级管理员用户")
                
                # 查询所有用户
                cursor.execute("SELECT id, username, is_super_admin, status FROM users")
                all_users = cursor.fetchall()
                
                if all_users:
                    print("当前数据库中的用户:")
                    for user in all_users:
                        print(f"   ID: {user[0]}, 用户名: {user[1]}, 角色: {'超级管理员' if user[2] else '普通用户'}, 状态: {'启用' if user[3] == 1 else '禁用'}")
                else:
                    print("当前数据库中没有用户")
                return False
            
    except pymysql.MySQLError as e:
        print(f"数据库错误: {e}")
    except Exception as e:
        print(f"验证失败: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()


if __name__ == '__main__':
    verify_super_admin()