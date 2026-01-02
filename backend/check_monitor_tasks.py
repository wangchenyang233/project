import os
import sys

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import MonitorTask
from app.extensions import db

def check_and_fix_monitor_tasks():
    """检查并修复监控任务"""
    app = create_app()
    
    with app.app_context():
        # 查询所有监控任务
        tasks = MonitorTask.query.all()
        
        print(f"总共找到 {len(tasks)} 个监控任务:")
        
        for task in tasks:
            print(f"\n任务ID: {task.task_id}")
            print(f"目标用户: {task.target_user}")
            print(f"状态: {task.status}")
            print(f"轮询间隔: {task.poll_seconds}秒")
            print(f"创建时间: {task.created_at}")
            
            # 检查目标用户是否为有效的钱包地址
            if task.target_user and not task.target_user.startswith('0x'):
                print(f"警告: 目标用户 '{task.target_user}' 不是有效的钱包地址")
                
                # 停止并删除错误的任务
                task.status = 'stopped'
                db.session.commit()
                print(f"已停止任务 {task.task_id}")
        
        # 查询所有运行中的任务
        running_tasks = MonitorTask.query.filter_by(status='running').all()
        print(f"\n\n当前运行中的任务数量: {len(running_tasks)}")
        
        for task in running_tasks:
            print(f"- 任务ID: {task.task_id}, 目标用户: {task.target_user}")
        
        db.session.commit()
        print("\n数据库检查和修复完成")

if __name__ == '__main__':
    check_and_fix_monitor_tasks()
