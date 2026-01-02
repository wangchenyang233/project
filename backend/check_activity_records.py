import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'vue_flask_db',
    'charset': 'utf8mb4'
}

def check_activity_records():
    """检查活动记录"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 检查所有活动记录
    print("=== 所有活动记录 ===")
    cursor.execute("SELECT id, task_id, target_user, timestamp, asset, side, size, price, created_at FROM activity_record ORDER BY created_at DESC LIMIT 10")
    records = cursor.fetchall()
    for record in records:
        print(f"ID: {record[0]}, task_id: {record[1]}, target_user: {record[2]}, timestamp: {record[3]}, asset: {record[4]}, side: {record[5]}, size: {record[6]}, price: {record[7]}, created_at: {record[8]}")
    
    # 检查有task_id的记录
    print("\n=== 有task_id的活动记录 ===")
    cursor.execute("SELECT id, task_id, target_user, timestamp, asset, side, size, price, created_at FROM activity_record WHERE task_id IS NOT NULL ORDER BY created_at DESC")
    records = cursor.fetchall()
    print(f"总数: {len(records)}")
    for record in records:
        print(f"ID: {record[0]}, task_id: {record[1]}, target_user: {record[2]}, timestamp: {record[3]}, asset: {record[4]}, side: {record[5]}, size: {record[6]}, price: {record[7]}, created_at: {record[8]}")
    
    # 检查有target_user的记录
    print("\n=== 有target_user的活动记录 ===")
    cursor.execute("SELECT id, task_id, target_user, timestamp, asset, side, size, price, created_at FROM activity_record WHERE target_user IS NOT NULL ORDER BY created_at DESC LIMIT 10")
    records = cursor.fetchall()
    print(f"总数: {len(records)}")
    for record in records:
        print(f"ID: {record[0]}, task_id: {record[1]}, target_user: {record[2]}, timestamp: {record[3]}, asset: {record[4]}, side: {record[5]}, size: {record[6]}, price: {record[7]}, created_at: {record[8]}")
    
    conn.close()

if __name__ == "__main__":
    check_activity_records()
