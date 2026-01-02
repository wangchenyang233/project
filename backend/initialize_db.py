#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化数据库结构脚本
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, ActivityRecord
from app.config import config


def initialize_database():
    """初始化数据库结构"""
    # 创建Flask应用实例
    app = create_app(config_name='development')
    
    with app.app_context():
        try:
            # 创建所有表
            db.create_all()
            print("数据库表创建成功！")
            
        except Exception as e:
            print(f"初始化数据库失败: {str(e)}")


if __name__ == '__main__':
    initialize_database()
