import pymysql
import time

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'vue_flask_db',
    'charset': 'utf8mb4'
}

def monitor_database():
    """持续监控数据库变化"""
    print("开始监控数据库变化...")
    last_count = 0
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        while True:
            # 检查活动记录总数
            cursor.execute("SELECT COUNT(*) FROM activity_record")
            count = cursor.fetchone()[0]
            
            # 检查有task_id的记录数
            cursor.execute("SELECT COUNT(*) FROM activity_record WHERE task_id IS NOT NULL")
            task_count = cursor.fetchone()[0]
            
            # 检查最新的记录
            cursor.execute("SELECT id, task_id, target_user, timestamp, created_at FROM activity_record ORDER BY created_at DESC LIMIT 1")
            latest = cursor.fetchone()
            
            print(f"[{time.strftime('%H:%M:%S')}] 总记录数: {count}, 有task_id的记录数: {task_count}")
            if latest:
                print(f"  最新记录: ID={latest[0]}, task_id={latest[1]}, target_user={latest[2]}, timestamp={latest[3]}, created_at={latest[4]}")
            
            if count > last_count:
                print(f"  新增了 {count - last_count} 条记录")
                last_count = count
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n停止监控")
    finally:
        conn.close()

if __name__ == "__main__":
    monitor_database()
