from flask import request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from . import copy_trade_bp
from app.utils.auth_util import require_login, require_module_permission
from app.utils.encrypt_util import encrypt_str, decrypt_str
from app.models import CopyTradeConfig, CopyTradeRecord
from app.extensions import db
from app.utils.request_util import fetch_latest_trades
import logging
import threading
import time
import uuid

# 设置日志记录器
logger = logging.getLogger(__name__)

# 内存中的跟单任务字典
copy_trade_tasks = {}
# 跟单任务线程字典
copy_trade_threads = {}

def copy_trade_worker(task_id, target_user, my_proxy_wallet, pk, poll_seconds=1):
    """自动跟单工作线程
    
    持续监控目标用户的交易活动，自动进行跟单
    
    参数：
        task_id: 任务ID
        target_user: 目标用户钱包地址
        my_proxy_wallet: 我的代理钱包地址
        pk: 私钥
        poll_seconds: 轮询间隔（秒）
    """
    from app import create_app
    from py_clob_client.client import ClobClient
    from py_clob_client.clob_types import OrderArgs, OrderType
    from py_clob_client.order_builder.constants import BUY, SELL
    from py_clob_client.exceptions import PolyApiException
    import requests
    
    # 创建Flask应用实例（用于线程中的应用上下文）
    flask_app = create_app()
    
    # 在Flask应用上下文中运行
    with flask_app.app_context():
        logger.info(f"Starting copy trade for user {target_user}, task_id: {task_id}, poll interval: {poll_seconds}s")
        
        try:
            # 初始化 CLOB 客户端
            client = ClobClient(
                "https://clob.polymarket.com",
                key=pk,
                chain_id=137,
                signature_type=2,
                funder=my_proxy_wallet,
            )
            client.set_api_creds(client.create_or_derive_api_creds())
            
            # 初始化：读取当前记录，建立"已见集合"
            seen = set()
            params = {'user': target_user, 'type': 'TRADE', 'limit': 100, 'sortBy': 'TIMESTAMP', 'sortDirection': 'DESC'}
            activity_list = fetch_latest_trades(params)
            
            for it in activity_list:
                tx = it.get('transactionHash')
                if tx:
                    seen.add(tx)
            
            logger.info(f"Initialized copy trade. Loaded {len(activity_list)} latest trades. Start monitoring...")
            
            # 持续轮询
            while copy_trade_tasks.get(task_id, {}).get('status') == 'running':
                try:
                    # 获取最新交易数据
                    params = {'user': target_user, 'type': 'TRADE', 'limit': 100, 'sortBy': 'TIMESTAMP', 'sortDirection': 'DESC'}
                    new_list = fetch_latest_trades(params)
                    
                    # 找出新记录
                    new_items = []
                    for it in new_list:
                        tx = it.get('transactionHash')
                        if tx and tx not in seen:
                            new_items.append(it)
                            seen.add(tx)
                    
                    # 有新记录就处理跟单
                    if new_items:
                        new_items.sort(key=lambda x: x.get('timestamp', 0))
                        for it in new_items:
                            try:
                                # 从 activity 提取字段
                                target_price = float(it["price"])
                                target_size = float(it["size"])
                                target_side = it["side"]
                                token_id = str(it["asset"])
                                target_tx_hash = it.get("transactionHash", "")
                                
                                # 构造跟单参数
                                order_args = OrderArgs(
                                    price=target_price,
                                    size=target_size,
                                    side=SELL if target_side == "SELL" else BUY,
                                    token_id=token_id,
                                )
                                
                                # 创建并提交订单
                                signed = client.create_order(order_args)
                                resp = client.post_order(signed, OrderType.GTC)
                                
                                # 记录交易结果
                                tx_hash = resp.get('orderID', f"tx_{uuid.uuid4()}")
                                status = resp.get('status', 'unknown')
                                
                                # 保存到数据库
                                record = CopyTradeRecord(
                                    task_id=task_id,
                                    target_user=target_user,
                                    target_tx_hash=target_tx_hash,
                                    tx_hash=tx_hash,
                                    amount=target_price * target_size,
                                    price=target_price,
                                    size=target_size,
                                    side=target_side,
                                    token_id=token_id,
                                    event_title=it.get('title', ''),
                                    event_slug=it.get('slug', ''),
                                    status='success' if status in ['live', 'matched'] else 'failed'
                                )
                                db.session.add(record)
                                db.session.commit()
                                
                                logger.info(f"Copy trade completed: target={target_user}, tx={target_tx_hash}, status={status}")
                                
                            except PolyApiException as e:
                                logger.error(f"Copy trade failed (PolyApiException): {str(e)}")
                                # 记录失败交易
                                record = CopyTradeRecord(
                                    task_id=task_id,
                                    target_user=target_user,
                                    target_tx_hash=it.get("transactionHash", ""),
                                    tx_hash=f"failed_{uuid.uuid4()}",
                                    amount=0,
                                    price=float(it.get("price", 0)),
                                    size=float(it.get("size", 0)),
                                    side=it.get("side", ""),
                                    token_id=str(it.get("asset", "")),
                                    event_title=it.get('title', ''),
                                    event_slug=it.get('slug', ''),
                                    status='failed'
                                )
                                db.session.add(record)
                                db.session.commit()
                            except Exception as e:
                                logger.error(f"Copy trade failed (Exception): {str(e)}")
                                # 记录失败交易
                                record = CopyTradeRecord(
                                    task_id=task_id,
                                    target_user=target_user,
                                    target_tx_hash=it.get("transactionHash", ""),
                                    tx_hash=f"failed_{uuid.uuid4()}",
                                    amount=0,
                                    price=float(it.get("price", 0)),
                                    size=float(it.get("size", 0)),
                                    side=it.get("side", ""),
                                    token_id=str(it.get("asset", "")),
                                    event_title=it.get('title', ''),
                                    event_slug=it.get('slug', ''),
                                    status='failed'
                                )
                                db.session.add(record)
                                db.session.commit()
                    
                    time.sleep(poll_seconds)
                
                except Exception as e:
                    logger.error(f"Error in copy_trade_worker for task {task_id}: {str(e)}")
                    time.sleep(poll_seconds * 2)
            
            logger.info(f"Copy trade task {task_id} stopped")
            
        except Exception as e:
            logger.error(f"Copy trade task {task_id} failed: {str(e)}")
            # 更新任务状态为失败
            try:
                config = CopyTradeConfig.query.filter_by(task_id=task_id).first()
                if config:
                    config.status = 'failed'
                    db.session.commit()
            except:
                pass

@copy_trade_bp.route('/config', methods=['POST'])
@require_login
@require_module_permission('copy_trade')
def save_copy_trade_config():
    """保存自动跟单配置
    
    参数：
        target_user: 目标用户钱包地址
        wallet_address: 我的钱包地址
        private_key: 私钥（将被加密存储）
    
    返回：
        配置保存结果
    """
    try:
        # 获取请求参数
        data = request.get_json()
        target_user = data.get('target_user')
        wallet_address = data.get('wallet_address')
        private_key = data.get('private_key')
        
        # 参数验证
        if not all([target_user, wallet_address, private_key]):
            return jsonify({
                'code': 400,
                'msg': 'target_user、wallet_address和private_key参数不能为空'
            }), 400
        
        # 加密私钥
        private_key_encrypted = encrypt_str(private_key)
        
        # 保存配置（如果已存在则更新）
        user_id = get_jwt_identity()
        config = CopyTradeConfig.query.filter_by(user_id=user_id).first()
        if config:
            # 更新现有配置
            config.target_user = target_user
            config.my_proxy_wallet = wallet_address
            config.pk_encrypted = private_key_encrypted
            config.status = 'stopped'  # 重置状态
            config.task_id = None  # 清除任务ID
            logger.info(f"Updated copy trade config for user {config.user_id}")
        else:
            # 创建新配置
            config = CopyTradeConfig(
                user_id=user_id,
                target_user=target_user,
                my_proxy_wallet=wallet_address,
                pk_encrypted=private_key_encrypted
            )
            db.session.add(config)
            logger.info(f"Created new copy trade config for user {config.user_id}")
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '配置保存成功',
            'data': {
                'target_user': target_user,
                'wallet_address': wallet_address
            }
        })
        
    except Exception as e:
        logger.error(f"Save copy trade config failed: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': '配置保存失败',
            'error': str(e)
        }), 500

@copy_trade_bp.route('/start', methods=['POST'])
@require_login
@require_module_permission('copy_trade')
def start_copy_trade():
    """启动自动跟单任务
    
    返回：
        任务启动结果
    """
    try:
        # 获取当前登录用户
        user_id = get_jwt_identity()
        
        # 查找跟单配置
        config = CopyTradeConfig.query.filter_by(user_id=user_id).first()
        if not config:
            return jsonify({
                'code': 404,
                'msg': '未找到跟单配置，请先设置配置'
            }), 404
            
        # 检查配置状态
        if config.status == 'running':
            return jsonify({
                'code': 400,
                'msg': '跟单任务已在运行中'
            }), 400
        
        # 解密私钥
        pk = decrypt_str(config.pk_encrypted)
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 更新配置
        config.task_id = task_id
        config.status = 'running'
        db.session.commit()
        
        # 保存任务到内存
        copy_trade_tasks[task_id] = {
            'target_user': config.target_user,
            'my_proxy_wallet': config.my_proxy_wallet,
            'status': 'running',
            'created_at': time.time()
        }
        
        # 启动跟单线程
        thread = threading.Thread(
            target=copy_trade_worker, 
            args=(task_id, config.target_user, config.my_proxy_wallet, pk), 
            daemon=True
        )
        thread.start()
        copy_trade_threads[task_id] = thread
        
        logger.info(f"Started copy trade task {task_id} for user {user_id}")
        
        return jsonify({
            'code': 200,
            'msg': '跟单任务已启动',
            'data': {
                'task_id': task_id,
                'target_user': config.target_user,
                'status': 'running'
            }
        })
        
    except Exception as e:
        logger.error(f"Start copy trade failed: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': '跟单任务启动失败',
            'error': str(e)
        }), 500

@copy_trade_bp.route('/stop', methods=['POST'])
@require_login
@require_module_permission('copy_trade')
def stop_copy_trade():
    """停止自动跟单任务
    
    返回：
        任务停止结果
    """
    try:
        # 获取当前登录用户
        user_id = get_jwt_identity()
        
        # 查找配置
        config = CopyTradeConfig.query.filter_by(user_id=user_id).first()
        if not config or not config.task_id:
            return jsonify({
                'code': 404,
                'msg': '未找到对应的跟单任务'
            }), 404
        
        task_id = config.task_id
        
        # 更新内存中的任务状态
        if task_id in copy_trade_tasks:
            copy_trade_tasks[task_id]['status'] = 'stopped'
        
        # 更新数据库中的任务状态
        config.status = 'stopped'
        config.task_id = None
        db.session.commit()
        
        logger.info(f"Stopped copy trade task {task_id}")
        
        return jsonify({
            'code': 200,
            'msg': '跟单任务已停止',
            'data': {
                'task_id': task_id,
                'status': 'stopped'
            }
        })
        
    except Exception as e:
        logger.error(f"Stop copy trade failed: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': '跟单任务停止失败',
            'error': str(e)
        }), 500

@copy_trade_bp.route('/stat', methods=['GET'])
@require_login
@require_module_permission('copy_trade')
def get_copy_trade_stat():
    """获取跟单统计信息
    
    返回：
        跟单统计数据
    """
    try:
        # 获取当前登录用户
        user_id = get_jwt_identity()
        
        # 查找配置
        config = CopyTradeConfig.query.filter_by(user_id=user_id).first()
        if not config:
            return jsonify({
                'code': 404,
                'msg': '未找到跟单配置'
            }), 404
        
        # 查询交易记录获取统计信息
        total_trades = CopyTradeRecord.query.filter_by(task_id=config.task_id).count()
        success_trades = CopyTradeRecord.query.filter_by(task_id=config.task_id, status='success').count()
        failed_trades = CopyTradeRecord.query.filter_by(task_id=config.task_id, status='failed').count()
        
        logger.info(f"Retrieved copy trade stats for user {user_id}")
        
        return jsonify({
            'code': 200,
            'msg': '统计信息获取成功',
            'data': {
                'total_trades': total_trades,
                'success_trades': success_trades,
                'failed_trades': failed_trades
            }
        })
        
    except Exception as e:
        logger.error(f"Get copy trade stats failed: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '统计信息获取失败',
            'error': str(e)
        }), 500

@copy_trade_bp.route('/records', methods=['GET'])
@require_login
@require_module_permission('copy_trade')
def get_copy_trade_records():
    """获取跟单据
    
    参数：
        limit: 限制条数
    
    返回：
        跟单据列表
    """
    try:
        # 获取当前登录用户
        user_id = get_jwt_identity()
        
        # 查找配置
        config = CopyTradeConfig.query.filter_by(user_id=user_id).first()
        if not config:
            return jsonify({
                'code': 404,
                'msg': '未找到跟单配置'
            }), 404
        
        # 获取请求参数
        limit = request.args.get('limit', 50, type=int)
        
        # 查询交易记录
        records = CopyTradeRecord.query.filter_by(task_id=config.task_id)\
            .order_by(CopyTradeRecord.created_at.desc())\
            .limit(limit)\
            .all()
        
        # 转换为字典列表
        record_list = [record.to_dict() for record in records]
        
        logger.info(f"Retrieved {len(record_list)} copy trade records for user {user_id}")
        
        return jsonify({
            'code': 200,
            'msg': '跟单据获取成功',
            'data': {
                'records': record_list,
                'total': len(record_list)
            }
        })
        
    except Exception as e:
        logger.error(f"Get copy trade records failed: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '跟单据获取失败',
            'error': str(e)
        }), 500