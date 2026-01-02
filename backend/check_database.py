import pymysql
import json

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'vue_flask_db',
    'charset': 'utf8mb4'
}

def check_database():
    """检查数据库中的数据"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 检查监控任务
    print("=== 监控任务 ===")
    cursor.execute("SELECT * FROM monitor_task ORDER BY created_at DESC LIMIT 5")
    tasks = cursor.fetchall()
    if tasks:
        columns = [desc[0] for desc in cursor.description]
        for task in tasks:
            task_dict = dict(zip(columns, task))
            print(f"任务ID: {task_dict.get('id')}, 用户: {task_dict.get('user_address')}, 状态: {task_dict.get('status')}, 创建时间: {task_dict.get('created_at')}")
    else:
        print("没有监控任务")
    
    # 检查活动记录
    print("\n=== 活动记录 ===")
    cursor.execute("SELECT COUNT(*) FROM activity_record")
    count = cursor.fetchone()[0]
    print(f"活动记录总数: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM activity_record ORDER BY created_at DESC LIMIT 5")
        records = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        for record in records:
            record_dict = dict(zip(columns, record))
            print(f"ID: {record_dict.get('id')}, 任务ID: {record_dict.get('task_id')}, 用户: {record_dict.get('user_address')}, 时间戳: {record_dict.get('timestamp')}, 资产: {record_dict.get('asset')}, 方向: {record_dict.get('direction')}, 金额: {record_dict.get('amount')}, 价格: {record_dict.get('price')}")
    
    conn.close()

if __name__ == "__main__":
    check_database()
