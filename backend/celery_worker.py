import os
import sys
import time
import logging
from celery import Celery
from app.extensions import db
from app.models import ActivityRecord, MonitorTask, CopyTradeConfig
from app.utils.request_util import fetch_latest_trades
from app.utils.dedup_util import get_unique_key, deduplicate_data
from app.utils.encrypt_util import decrypt_str
from app.utils.sign_util import init_clob_client

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入Flask应用
from app import create_app

# 创建Flask应用上下文
app = create_app()

# 初始化Celery
celery = Celery(
    __name__,
    broker=app.config['REDIS_URL'],
    backend=app.config['REDIS_URL']
)

# 更新Celery配置
celery.conf.update(app.config)

# 配置任务
@celery.task(name='monitor_user_activity')
def monitor_user_activity(target_user, poll_seconds=5):
    """监控用户活动
    
    轮询Polymarket API获取最新交易数据，数据去重后持久化到activity_record表
    
    参数：
        target_user: 目标用户钱包地址
        poll_seconds: 轮询间隔（秒）
    """
    task_id = monitor_user_activity.request.id
    logger.info(f"Starting activity monitoring for user {target_user}, task_id: {task_id}, poll interval: {poll_seconds}s")
    
    try:
        # 更新任务状态
        with app.app_context():
            task = MonitorTask.query.filter_by(task_id=task_id).first()
            if task:
                task.status = 'running'
                db.session.commit()
        
        # 持续监控
        while True:
            try:
                # 获取最新交易数据
                logger.debug(f"Fetching latest trades for user {target_user}")
                params = {'user': target_user, 'limit': 100}
                trades_data = fetch_latest_trades(params)
                
                # 数据去重
                unique_trades = deduplicate_data(trades_data)
                
                if unique_trades:
                    logger.info(f"Found {len(unique_trades)} unique trades for user {target_user}")
                    
                    # 持久化数据
                    with app.app_context():
                        saved_count = 0
                        for trade in unique_trades:
                            # 生成唯一标识
                            unique_key = get_unique_key(trade)
                            
                            # 检查记录是否已存在
                            existing_record = ActivityRecord.query.filter_by(unique_key=unique_key).first()
                            if existing_record:
                                logger.debug(f"Record already exists: {unique_key}")
                                continue
                            
                            # 创建新记录
                            record = ActivityRecord(
                                task_id=task_id,
                                target_user=target_user,
                                transaction_hash=trade.get('transactionHash'),
                                timestamp=trade.get('timestamp'),
                                asset=trade.get('asset'),
                                side=trade.get('side'),
                                size=trade.get('size'),
                                price=trade.get('price'),
                                unique_key=unique_key
                            )
                            
                            # 添加到数据库
                            db.session.add(record)
                            saved_count += 1
                        
                        if saved_count > 0:
                            db.session.commit()
                            logger.info(f"Saved {saved_count} new activity records")
            
            except Exception as e:
                logger.error(f"Error in monitor_user_activity: {str(e)}")
            
            # 检查任务是否被终止
            with app.app_context():
                task = MonitorTask.query.filter_by(task_id=task_id).first()
                if not task or task.status != 'running':
                    logger.info(f"Monitoring task {task_id} stopped by user")
                    return
            
            # 等待下一次轮询
            time.sleep(poll_seconds)
    
    except Exception as e:
        logger.error(f"Monitoring task failed: {str(e)}")
        # 更新任务状态为失败
        with app.app_context():
            task = MonitorTask.query.filter_by(task_id=task_id).first()
            if task:
                task.status = 'failed'
                db.session.commit()
        raise

@celery.task(name='auto_copy_trade')
def auto_copy_trade(user_id):
    """自动跟单
    
    监控目标用户活动，自动复制交易
    
    参数：
        user_id: 用户ID
    """
    task_id = auto_copy_trade.request.id
    logger.info(f"Starting auto copy trade for user {user_id}, task_id: {task_id}")
    
    try:
        # 获取用户配置
        with app.app_context():
            config = CopyTradeConfig.query.filter_by(user_id=user_id).first()
            if not config:
                logger.error(f"Copy trade config not found for user {user_id}")
                return
            
            # 更新配置
            config.task_id = task_id
            config.status = 'running'
            db.session.commit()
            
            # 解密私钥
            pk = decrypt_str(config.pk_encrypted)
            
            # 初始化CLOB客户端
            client = init_clob_client(pk, config.my_proxy_wallet)
    
        # 持续监控和跟单
        while True:
            try:
                # 检查配置状态
                with app.app_context():
                    config = CopyTradeConfig.query.filter_by(user_id=user_id).first()
                    if not config or config.status != 'running' or config.task_id != task_id:
                        logger.info(f"Auto copy trade task {task_id} stopped")
                        return
                
                # 获取目标用户的最新交易
                logger.debug(f"Fetching latest trades for target user {config.target_user}")
                params = {'user': config.target_user, 'limit': 50}
                trades_data = fetch_latest_trades(params)
                
                # 数据去重
                unique_trades = deduplicate_data(trades_data)
                
                if unique_trades:
                    logger.info(f"Found {len(unique_trades)} unique trades for target user {config.target_user}")
                    
                    # 这里应该实现跟单逻辑
                    # 由于没有具体的CLOB API文档，这里只做模拟
                    for trade in unique_trades:
                        logger.info(f"Copying trade: {trade}")
                        # 这里应该调用client.place_order()等方法
                        # 但由于没有具体API，这里只做日志记录
            
            except Exception as e:
                logger.error(f"Error in auto_copy_trade: {str(e)}")
            
            # 等待下一次轮询
            time.sleep(5)
    
    except Exception as e:
        logger.error(f"Auto copy trade failed: {str(e)}")
        # 更新配置状态为失败
        with app.app_context():
            config = CopyTradeConfig.query.filter_by(user_id=user_id).first()
            if config and config.task_id == task_id:
                config.status = 'failed'
                db.session.commit()
        raise

if __name__ == '__main__':
    # 启动Celery worker
    celery.start()