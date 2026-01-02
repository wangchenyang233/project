from flask import request, jsonify
from . import user_manage_bp
from app.models import User
from app.utils.auth_util import require_super_admin
from app.utils.encrypt_util import encrypt_pwd
from app.extensions import db
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)


@user_manage_bp.route('/list', methods=['GET'])
@require_super_admin
def get_user_list():
    """获取用户列表接口"""
    try:
        # 获取请求参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        username = request.args.get('username', '')
        
        # 构建查询
        query = User.query.filter_by(is_super_admin=False)
        
        # 模糊查询用户名
        if username:
            query = query.filter(User.username.like(f'%{username}%'))
        
        # 分页查询
        pagination = query.order_by(User.id.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # 构建响应数据
        user_list = []
        for user in pagination.items:
            user_dict = user.to_dict()
            user_list.append(user_dict)
        
        return jsonify({
            'code': 200,
            'msg': '获取用户列表成功',
            'data': {
                'users': user_list,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
        }), 200
    
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '获取用户列表失败，请稍后重试',
            'data': None
        }), 500


@user_manage_bp.route('/add', methods=['POST'])
@require_super_admin
def add_user():
    """添加用户接口"""
    try:
        # 获取请求参数
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # 验证参数完整性
        if not username or not password:
            return jsonify({
                'code': 400,
                'msg': '用户名和密码不能为空',
                'data': None
            }), 400
        
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({
                'code': 400,
                'msg': '用户名已存在',
                'data': None
            }), 400
        
        # 创建新用户（普通用户，权限默认为空）
        new_user = User(
            username=username,
            password=encrypt_pwd(password),
            is_super_admin=False,
            activity_query=False,
            activity_monitor=False,
            copy_trade=False
        )
        
        # 保存到数据库
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '添加用户成功',
            'data': {
                'user_id': new_user.id,
                'username': new_user.username
            }
        }), 200
    
    except Exception as e:
        logger.error(f"添加用户失败: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': '添加用户失败，请稍后重试',
            'data': None
        }), 500


@user_manage_bp.route('/edit', methods=['PUT'])
@require_super_admin
def edit_user():
    """编辑用户接口"""
    try:
        # 获取请求参数
        data = request.get_json()
        user_id = data.get('user_id')
        username = data.get('username')
        password = data.get('password')
        status = data.get('status')
        
        # 验证参数完整性
        if not user_id or not username or status is None:
            return jsonify({
                'code': 400,
                'msg': '用户ID、用户名和状态不能为空',
                'data': None
            }), 400
        
        # 查找用户
        user = User.query.filter_by(id=user_id, is_super_admin=False).first()
        if not user:
            return jsonify({
                'code': 404,
                'msg': '用户不存在',
                'data': None
            }), 404
        
        # 检查用户名是否已存在（排除当前用户）
        existing_user = User.query.filter(
            User.username == username,
            User.id != user_id
        ).first()
        if existing_user:
            return jsonify({
                'code': 400,
                'msg': '用户名已存在',
                'data': None
            }), 400
        
        # 更新用户信息
        user.username = username
        user.status = status
        
        # 如果提供了密码，则更新密码
        if password:
            user.password = encrypt_pwd(password)
        
        # 保存到数据库
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '编辑用户成功',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'status': user.status
            }
        }), 200
    
    except Exception as e:
        logger.error(f"编辑用户失败: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': '编辑用户失败，请稍后重试',
            'data': None
        }), 500


@user_manage_bp.route('/delete', methods=['DELETE'])
@require_super_admin
def delete_user():
    """删除用户接口"""
    try:
        # 获取请求参数
        user_id = request.args.get('user_id')
        
        # 验证参数完整性
        if not user_id:
            return jsonify({
                'code': 400,
                'msg': '用户ID不能为空',
                'data': None
            }), 400
        
        # 查找用户
        user = User.query.filter_by(id=user_id, is_super_admin=False).first()
        if not user:
            return jsonify({
                'code': 404,
                'msg': '用户不存在',
                'data': None
            }), 404
        
        # 删除用户（级联删除权限配置）
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '删除用户成功',
            'data': {
                'user_id': user_id
            }
        }), 200
    
    except Exception as e:
        logger.error(f"删除用户失败: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': '删除用户失败，请稍后重试',
            'data': None
        }), 500


@user_manage_bp.route('/set-permission', methods=['PUT'])
@require_super_admin
def set_user_permission():
    """设置用户权限接口"""
    try:
        # 获取请求参数
        data = request.get_json()
        user_id = data.get('user_id')
        activity_query = data.get('activity_query', False)
        activity_monitor = data.get('activity_monitor', False)
        copy_trade = data.get('copy_trade', False)
        
        # 验证参数完整性
        if not user_id:
            return jsonify({
                'code': 400,
                'msg': '用户ID不能为空',
                'data': None
            }), 400
        
        # 查找用户
        user = User.query.filter_by(id=user_id, is_super_admin=False).first()
        if not user:
            return jsonify({
                'code': 404,
                'msg': '用户不存在',
                'data': None
            }), 404
        
        # 更新用户权限
        user.activity_query = activity_query
        user.activity_monitor = activity_monitor
        user.copy_trade = copy_trade
        
        # 保存到数据库
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '设置用户权限成功',
            'data': {
                'user_id': user.id,
                'activity_query': user.activity_query,
                'activity_monitor': user.activity_monitor,
                'copy_trade': user.copy_trade
            }
        }), 200
    
    except Exception as e:
        logger.error(f"设置用户权限失败: {str(e)}")
        db.session.rollback()
        return jsonify({
            'code': 500,
            'msg': '设置用户权限失败，请稍后重试',
            'data': None
        }), 500
