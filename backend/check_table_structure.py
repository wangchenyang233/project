import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'vue_flask_db',
    'charset': 'utf8mb4'
}

def check_table_structure():
    """检查表结构"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 检查 activity_record 表结构
    print("=== activity_record 表结构 ===")
    cursor.execute("DESCRIBE activity_record")
    columns = cursor.fetchall()
    for col in columns:
        print(f"字段: {col[0]}, 类型: {col[1]}, 允许NULL: {col[2]}, 键: {col[3]}, 默认值: {col[4]}, 额外: {col[5]}")
    
    # 检查 monitor_task 表结构
    print("\n=== monitor_task 表结构 ===")
    cursor.execute("DESCRIBE monitor_task")
    columns = cursor.fetchall()
    for col in columns:
        print(f"字段: {col[0]}, 类型: {col[1]}, 允许NULL: {col[2]}, 键: {col[3]}, 默认值: {col[4]}, 额外: {col[5]}")
    
    conn.close()

if __name__ == "__main__":
    check_table_structure()
