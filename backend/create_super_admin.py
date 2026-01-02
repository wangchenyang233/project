#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建超级管理员用户脚本
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.utils.encrypt_util import encrypt_pwd
from app.config import config


def create_super_admin():
    """创建超级管理员用户"""
    # 创建Flask应用实例
    app = create_app(config_name='development')
    
    with app.app_context():
        try:
            # 检查是否已存在超级管理员用户
            existing_super_admin = User.query.filter_by(is_super_admin=True).first()
            if existing_super_admin:
                print("超级管理员用户已存在，无需重复创建")
                print(f"用户名: {existing_super_admin.username}")
                return
            
            # 从配置中获取超级管理员信息
            username = app.config.get('SUPER_ADMIN_USERNAME', 'admin')
            password = app.config.get('SUPER_ADMIN_PASSWORD', 'Admin123!')
            
            # 检查用户名是否已存在
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"用户名 '{username}' 已存在，请修改配置或删除现有用户")
                return
            
            # 创建超级管理员用户
            super_admin = User(
                username=username,
                password=encrypt_pwd(password),
                status=1,  # 启用状态
                is_super_admin=True,
                activity_query=True,  # 赋予所有模块权限
                activity_monitor=True,
                copy_trade=True
            )
            
            # 添加到数据库
            db.session.add(super_admin)
            db.session.commit()
            
            print("超级管理员用户创建成功！")
            print(f"用户名: {username}")
            print(f"密码: {password}")
            print("请妥善保存此信息，首次登录后建议修改密码")
            
        except Exception as e:
            print(f"创建超级管理员用户失败: {str(e)}")
            db.session.rollback()


if __name__ == '__main__':
    create_super_admin()
