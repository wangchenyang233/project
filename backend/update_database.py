from app import create_app
from app.extensions import db
from app.models import CopyTradeRecord

# 创建Flask应用实例
app = create_app()

with app.app_context():
    # 获取数据库连接
    connection = db.engine.connect()
    
    try:
        # 检查并添加event_title字段
        result = connection.execute(db.text("SHOW COLUMNS FROM copy_trade_record LIKE 'event_title'"))
        if not result.fetchone():
            connection.execute(db.text("ALTER TABLE copy_trade_record ADD COLUMN event_title VARCHAR(255) NULL"))
            print("Added column event_title")
        
        # 检查并添加event_slug字段
        result = connection.execute(db.text("SHOW COLUMNS FROM copy_trade_record LIKE 'event_slug'"))
        if not result.fetchone():
            connection.execute(db.text("ALTER TABLE copy_trade_record ADD COLUMN event_slug VARCHAR(255) NULL"))
            print("Added column event_slug")
        
        print("Database updated successfully!")
        
    except Exception as e:
        print(f"Error updating database: {str(e)}")
    finally:
        connection.close()