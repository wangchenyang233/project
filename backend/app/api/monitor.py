from flask import request, jsonify, current_app
from . import monitor_bp
from app.utils.auth_util import require_login, require_module_permission
from app.models import MonitorTask, ActivityRecord
from app.extensions import db
from app.utils.request_util import fetch_latest_trades
from app.utils.dedup_util import get_unique_key, deduplicate_data
import logging
import threading
import time
import uuid

# 设置日志记录器
logger = logging.getLogger(__name__)

# 内存中的监控任务字典
monitoring_tasks = {}
# 监控任务线程字典
monitoring_threads = {}

def monitor_worker(task_id, target_user, poll_seconds):
    """监控工作线程
    
    持续轮询Polymarket API获取最新交易数据，数据去重后持久化到activity_record表
    
    参数：
        task_id: 任务ID
        target_user: 目标用户钱包地址
        poll_seconds: 轮询间隔（秒）
    """
    # 延迟导入避免循环依赖
    from app import create_app
    
    # 创建Flask应用实例（用于线程中的应用上下文）
    flask_app = create_app()
    
    # 在Flask应用上下文中运行
    with flask_app.app_context():
        logger.info(f"Starting activity monitoring for user {target_user}, task_id: {task_id}, poll interval: {poll_seconds}s")
        
        # 初始化：读取当前记录，建立"已见集合"
        try:
            params = {'user': target_user, 'type': 'TRADE', 'limit': 100, 'sortBy': 'TIMESTAMP', 'sortDirection': 'DESC'}
            activity_list = fetch_latest_trades(params)
            
            # 用 transactionHash 去重
            seen = set()
            for it in activity_list:
                tx = it.get('transactionHash')
                if tx:
                    seen.add(tx)
                else:
                    seen.add((it.get('timestamp'), it.get('asset'), it.get('side'), it.get('size'), it.get('price')))
            
            logger.info(f"Initialized. Loaded {len(activity_list)} latest trades. Start monitoring...")
            
            # 持续轮询
            while monitoring_tasks.get(task_id, {}).get('status') == 'running':
                try:
                    # 获取最新交易数据
                    params = {'user': target_user, 'type': 'TRADE', 'limit': 100, 'sortBy': 'TIMESTAMP', 'sortDirection': 'DESC'}
                    new_list = fetch_latest_trades(params)
                    
                    # 找出新记录
                    new_items = []
                    for it in new_list:
                        tx = it.get('transactionHash')
                        key = tx if tx else (it.get('timestamp'), it.get('asset'), it.get('side'), it.get('size'), it.get('price'))
                        if key not in seen:
                            new_items.append(it)
                    
                    # 有新记录就保存到数据库
                    if new_items:
                        new_items.sort(key=lambda x: x.get('timestamp', 0))
                        saved_count = 0
                        
                        for it in new_items:
                            # 生成唯一标识
                            unique_key = get_unique_key(it)
                            
                            # 检查记录是否已存在
                            existing_record = ActivityRecord.query.filter_by(unique_key=unique_key).first()
                            if existing_record:
                                continue
                            
                            # 创建新记录
                            record = ActivityRecord(
                                task_id=task_id,
                                target_user=target_user,
                                transaction_hash=it.get('transactionHash'),
                                timestamp=it.get('timestamp'),
                                asset=it.get('asset'),
                                side=it.get('side'),
                                size=it.get('size'),
                                price=it.get('price'),
                                unique_key=unique_key
                            )
                            
                            # 添加到数据库
                            db.session.add(record)
                            saved_count += 1
                            
                            # 更新 seen
                            tx = it.get('transactionHash')
                            if tx:
                                seen.add(tx)
                            else:
                                seen.add((it.get('timestamp'), it.get('asset'), it.get('side'), it.get('size'), it.get('price')))
                        
                        if saved_count > 0:
                            db.session.commit()
                            logger.info(f"Saved {saved_count} new activity records for task {task_id}")
                    
                    time.sleep(poll_seconds)
                
                except Exception as e:
                    logger.error(f"Error in monitor_worker for task {task_id}: {str(e)}")
                    time.sleep(poll_seconds * 2)
            
            logger.info(f"Monitoring task {task_id} stopped")
        
        except Exception as e:
            logger.error(f"Monitoring task {task_id} failed: {str(e)}")
            # 更新任务状态为失败
            try:
                task = MonitorTask.query.filter_by(task_id=task_id).first()
                if task:
                    task.status = 'failed'
                    db.session.commit()
            except:
                pass

@monitor_bp.route('/start', methods=['POST'])
@require_login
@require_module_permission('activity_monitor')
def start_monitor():
    """开始监控用户活动
    
    参数：
        user: 目标用户钱包地址
        poll_seconds: 轮询间隔（秒）
    
    返回：
        任务ID和监控状态
    """
    try:
        # 获取请求参数
        data = request.get_json()
        target_user = data.get('user')
        poll_seconds = data.get('poll_seconds', 5)
        if poll_seconds is not None:
            poll_seconds = int(poll_seconds)
        else:
            poll_seconds = 5
        
        # 参数验证
        if not target_user:
            return jsonify({
                'code': 400,
                'msg': 'user参数不能为空'
            }), 400
            
        if poll_seconds <= 0 or poll_seconds > 300:
            return jsonify({
                'code': 400,
                'msg': 'poll_seconds参数必须在1-300之间'
            }), 400
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 保存任务信息到数据库
        monitor_task = MonitorTask(
            task_id=task_id,
            target_user=target_user,
            poll_seconds=poll_seconds,
            status='running'
        )
        db.session.add(monitor_task)
        db.session.commit()
        
        # 保存任务到内存
        monitoring_tasks[task_id] = {
            'target_user': target_user,
            'poll_seconds': poll_seconds,
            'status': 'running',
            'created_at': time.time()
        }
        
        # 启动监控线程
        thread = threading.Thread(target=monitor_worker, args=(task_id, target_user, poll_seconds), daemon=True)
        thread.start()
        monitoring_threads[task_id] = thread
        
        logger.info(f"Started monitoring task {task_id} for user {target_user}, poll every {poll_seconds} seconds")
        
        return jsonify({
            'code': 200,
            'msg': '监控任务已启动',
            'data': {
                'task_id': task_id,
                'target_user': target_user,
                'status': 'running'
            }
        })
        
    except Exception as e:
        logger.error(f"Start monitor failed: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': '监控任务启动失败',
            'error': str(e)
        }), 500

@monitor_bp.route('/stop', methods=['POST'])
@require_login
@require_module_permission('activity_monitor')
def stop_monitor():
    """停止监控任务
    
    参数：
        task_id: 任务ID
    
    返回：
        任务状态
    """
    try:
        # 获取请求参数
        data = request.get_json()
        task_id = data.get('task_id')
        
        # 参数验证
        if not task_id:
            return jsonify({
                'code': 400,
                'msg': 'task_id参数不能为空'
            }), 400
        
        # 查找任务
        task = MonitorTask.query.filter_by(task_id=task_id).first()
        if not task:
            return jsonify({
                'code': 404,
                'msg': '监控任务不存在'
            }), 404
        
        # 更新内存中的任务状态
        if task_id in monitoring_tasks:
            monitoring_tasks[task_id]['status'] = 'stopped'
        
        # 更新数据库中的任务状态
        task.status = 'stopped'
        db.session.commit()
        
        logger.info(f"Stopped monitoring task {task_id}")
        
        return jsonify({
            'code': 200,
            'msg': '监控任务已停止',
            'data': {
                'task_id': task_id,
                'status': 'stopped'
            }
        })
        
    except Exception as e:
        logger.error(f"Stop monitor failed: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': '监控任务停止失败',
            'error': str(e)
        }), 500

@monitor_bp.route('/logs', methods=['GET'])
@require_login
@require_module_permission('activity_monitor')
def get_monitor_logs():
    """获取监控日志
    
    参数：
        task_id: 任务ID
    
    返回：
        监控日志列表
    """
    try:
        # 获取请求参数
        task_id = request.args.get('task_id')
        
        # 参数验证
        if not task_id:
            return jsonify({
                'code': 400,
                'msg': 'task_id参数不能为空'
            }), 400
        
        # 查找监控任务
        task = MonitorTask.query.filter_by(task_id=task_id).first()
        if not task:
            return jsonify({
                'code': 404,
                'msg': '监控任务不存在'
            }), 404
        
        # 获取监控日志（activity_record表数据）
        logs = ActivityRecord.query.filter_by(task_id=task_id).order_by(ActivityRecord.created_at.desc()).all()
        
        # 转换为字典列表
        log_list = []
        for log in logs:
            log_dict = log.to_dict()
            # 添加前端需要的字段
            log_dict['level'] = 'info'
            log_dict['message'] = f"{log.side} {log.size} {log.asset} @ {log.price}"
            log_dict['user_address'] = log.target_user
            log_list.append(log_dict)
        
        logger.info(f"Retrieved {len(log_list)} logs for task {task_id}")
        
        return jsonify({
            'code': 200,
            'msg': '日志获取成功',
            'data': {
                'task_id': task_id,
                'target_user': task.target_user,
                'logs': log_list,
                'total': len(log_list)
            }
        })
        
    except Exception as e:
        logger.error(f"Get monitor logs failed: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '日志获取失败',
            'error': str(e)
        }), 500