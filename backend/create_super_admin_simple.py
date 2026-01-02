#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建超级管理员用户脚本（简化版，直接使用pymysql）
"""
import pymysql
from passlib.context import CryptContext
import os

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_super_admin():
    """创建超级管理员用户"""
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
            # 先创建users表
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    status INT DEFAULT 1,  -- 1: 启用, 0: 禁用
                    is_super_admin BOOLEAN DEFAULT FALSE,
                    activity_query BOOLEAN DEFAULT FALSE,  -- 活动查询权限
                    activity_monitor BOOLEAN DEFAULT FALSE,  -- 活动监控权限
                    copy_trade BOOLEAN DEFAULT FALSE,  -- 跟单交易权限
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_table_sql)
            print("users表创建成功！")
            
            # 创建activity_record表
            create_activity_table_sql = """
                CREATE TABLE IF NOT EXISTS activity_record (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    task_id VARCHAR(100),
                    target_user VARCHAR(100) NOT NULL,
                    transaction_hash VARCHAR(100),
                    timestamp INT NOT NULL,
                    asset VARCHAR(50),
                    side VARCHAR(10),
                    size FLOAT,
                    price FLOAT,
                    unique_key VARCHAR(100) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_activity_table_sql)
            print("activity_record表创建成功！")
            
            # 现在检查是否已存在超级管理员用户
            cursor.execute("SELECT * FROM users WHERE is_super_admin = 1")
            existing_super_admin = cursor.fetchone()
            if existing_super_admin:
                print("超级管理员用户已存在，无需重复创建")
                print(f"用户名: {existing_super_admin[1]}")
                return
            
            # 超级管理员信息
            username = 'admin'
            password = 'Admin123!'
            hashed_password = pwd_context.hash(password)
            
            # 检查用户名是否已存在
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                print(f"用户名 '{username}' 已存在，请修改配置或删除现有用户")
                return
            
            # 插入超级管理员用户
            insert_sql = """
                INSERT INTO users (
                    username, password, status, is_super_admin,
                    activity_query, activity_monitor, copy_trade
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                username, hashed_password, 1, True,  # status=1（启用）, is_super_admin=True
                True, True, True  # 所有模块权限都设置为True
            ))
            
            # 提交事务
            connection.commit()
            
            print("超级管理员用户创建成功！")
            print(f"用户名: {username}")
            print(f"密码: {password}")
            print("请妥善保存此信息，首次登录后建议修改密码")
            
    except pymysql.MySQLError as e:
        print(f"数据库错误: {e}")
    except Exception as e:
        print(f"创建超级管理员用户失败: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()


if __name__ == '__main__':
    create_super_admin()
