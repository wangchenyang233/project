from flask import request, jsonify
from . import activity_bp
from app.utils.auth_util import require_login, require_module_permission
from app.utils.request_util import fetch_latest_trades
from app.utils.dedup_util import get_unique_key, deduplicate_data
from app.models import ActivityRecord
from app.extensions import db
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)

# 默认输出字段
DEFAULT_OUTPUT_FIELDS = ['timestamp', 'asset', 'side', 'size', 'price', 'transaction_hash']

@activity_bp.route('/query', methods=['GET'])
@require_login
@require_module_permission('activity_query')
def query_activity():
    """查询用户活动记录
    
    参数：
        user/user_address: 目标用户钱包地址
        limit: 查询数量（1-500）
        offset: 偏移量（可选）
        fields: 输出字段列表（可选）
        side: 交易方向（可选）
        condition_id: 条件ID（可选）
    
    返回：
        查询结果列表和记录总数
    """
    try:
        # 获取请求参数
        target_user = request.args.get('user') or request.args.get('user_address')
        limit = request.args.get('limit', type=int, default=50)
        offset = request.args.get('offset', type=int, default=0)
        fields = request.args.getlist('fields')  # 支持多个fields参数
        side = request.args.get('side')
        condition_id = request.args.get('condition_id')
        type = request.args.get('type', default='TRADE')  # 活动类型（默认为TRADE）
        
        # 参数验证
        if not target_user:
            return jsonify({
                'code': 400,
                'msg': 'user或user_address参数不能为空'
            }), 400
            
        if limit <= 0 or limit > 500:
            return jsonify({
                'code': 400,
                'msg': 'limit参数必须在1-500之间'
            }), 400
        
        if offset < 0:
            return jsonify({
                'code': 400,
                'msg': 'offset参数不能小于0'
            }), 400
        
        # 构建API请求参数
        params = {
            'user': target_user,
            'limit': limit
        }
        
        if offset > 0:
            params['offset'] = offset
            
        if side:
            params['side'] = side
            
        if condition_id:
            params['conditionId'] = condition_id
            
        if type:
            params['type'] = type
        
        # 调用Polymarket API获取最新交易数据
        logger.info(f"Fetching latest trades for user {target_user}, limit {limit}, offset {offset}, type {type or 'TRADE'}")
        trades_data = fetch_latest_trades(params)
        logger.info(f"API returned {len(trades_data)} records")
        if trades_data:
            logger.debug(f"First trade sample: {trades_data[0]}")
        
        # 数据去重
        unique_trades = deduplicate_data(trades_data)
        logger.info(f"Deduplicated data: {len(unique_trades)} unique records from {len(trades_data)} total")
        if unique_trades:
            logger.debug(f"First unique trade sample: {unique_trades[0]}")
        
        # 添加调试日志：检查去重后的数据是否包含预期字段
        if unique_trades:
            logger.debug(f"All fields in first unique trade: {list(unique_trades[0].keys())}")
        
        # 字段映射配置（后端字段 -> 前端字段）
        FIELD_MAPPING = {
            'transactionHash': 'transaction_hash',
            'size': 'size',
            'usdcSize': 'size',
            'tokenId': 'asset',
            'asset': 'asset'
        }
        
        logger.info(f"Field mapping: {FIELD_MAPPING}")
        logger.info(f"Request parameters: {dict(request.args)}")
        
        # 确定最终输出字段
        output_fields = fields if fields else DEFAULT_OUTPUT_FIELDS
        
        # 先处理数据持久化
        new_records_count = 0
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
                target_user=target_user,
                transaction_hash=trade.get('transactionHash'),
                timestamp=trade.get('timestamp'),
                asset=trade.get('tokenId') or trade.get('asset'),
                side=trade.get('side'),
                size=trade.get('size') or trade.get('usdcSize'),
                price=trade.get('price'),
                unique_key=unique_key
            )
            
            # 添加到数据库
            db.session.add(record)
            new_records_count += 1
        
        # 提交数据库事务
        if new_records_count > 0:
            db.session.commit()
            logger.info(f"Successfully saved {new_records_count} new activity records")
        else:
            logger.info("No new records to save")
        
        # 然后构建返回给前端的结果
        results = []
        logger.info(f"Processing {len(unique_trades)} unique trades for response")
        
        for i, trade in enumerate(unique_trades):
            logger.debug(f"Processing trade {i+1}: {trade}")
            
            # 构建结果项，进行字段映射
            result_item = {}
            for backend_field in trade.keys():
                # 应用字段映射
                front_field = FIELD_MAPPING.get(backend_field, backend_field)
                result_item[front_field] = trade.get(backend_field)
                logger.debug(f"Mapped field: {backend_field} -> {front_field}: {trade.get(backend_field)}")
            
            # 添加用户地址字段
            result_item['user_address'] = target_user
            logger.debug(f"Added user_address: {target_user}")
            
            # 如果指定了输出字段，则进行筛选
            if fields:
                filtered_result = {}
                logger.debug(f"Filtering fields: {fields}")
                for field in fields:
                    if field in result_item:
                        filtered_result[field] = result_item[field]
                        logger.debug(f"Including field: {field} = {result_item[field]}")
                    # 特殊处理block_number（当前API不返回，设置为None）
                    elif field == 'block_number':
                        filtered_result[field] = None
                        logger.debug(f"Including field: block_number = None (API doesn't return this)")
                results.append(filtered_result)
                logger.debug(f"Filtered result: {filtered_result}")
            else:
                results.append(result_item)
                logger.debug(f"Full result item: {result_item}")
        
        logger.info(f"Final results count: {len(results)}")
        if results:
            logger.debug(f"First result item: {results[0]}")
        
        # 返回结果（调整结构以匹配前端期望）
        return jsonify({
            'code': 200,
            'msg': '查询成功',
            'data': results,  # 直接返回结果数组，与前端期望一致
            'total': len(results)  # 添加total字段用于分页
        })
        
    except Exception as e:
        logger.error(f"Activity query failed: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': '查询失败',
            'error': str(e)
        }), 500