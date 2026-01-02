from flask import request, jsonify
from . import auth_bp
from app.models import User
from app.utils.auth_util import require_login, generate_tokens, get_current_user
from app.utils.encrypt_util import verify_pwd
from app.extensions import db
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
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
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({
                'code': 401,
                'msg': '用户名或密码错误',
                'data': None
            }), 401
        
        # 验证用户状态
        if user.status != 1:
            return jsonify({
                'code': 403,
                'msg': '用户账号已被禁用',
                'data': None
            }), 403
        
        # 验证密码
        if not verify_pwd(user.password, password):
            return jsonify({
                'code': 401,
                'msg': '用户名或密码错误',
                'data': None
            }), 401
        
        # 生成JWT令牌
        tokens = generate_tokens(user.id, user.is_super_admin)
        
        # 返回响应
        return jsonify({
            'code': 200,
            'msg': '登录成功',
            'data': {
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token'],
                'user_info': {
                    'id': user.id,
                    'username': user.username,
                    'is_super_admin': user.is_super_admin
                }
            }
        }), 200
    
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '登录失败，请稍后重试',
            'data': None
        }), 500


@auth_bp.route('/current-user', methods=['GET'])
@require_login
def get_current_user_info():
    """获取当前用户完整信息"""
    try:
        # 获取当前用户
        user = get_current_user()
        if not user:
            return jsonify({
                'code': 401,
                'msg': '用户未登录或登录已过期',
                'data': None
            }), 401
        
        # 构建用户信息响应
        user_info = user.to_dict()
        
        return jsonify({
            'code': 200,
            'msg': '获取用户信息成功',
            'data': user_info
        }), 200
    
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '获取用户信息失败，请稍后重试',
            'data': None
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@require_login
def logout():
    """用户退出登录"""
    try:
        # 在Flask-JWT-Extended中，默认情况下，令牌在有效期内是有效的
        # 如果需要实现令牌黑名单功能，可以使用redis或其他存储来保存已失效的令牌
        # 这里仅返回成功响应
        
        return jsonify({
            'code': 200,
            'msg': '退出登录成功',
            'data': None
        }), 200
    
    except Exception as e:
        logger.error(f"退出登录失败: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '退出登录失败，请稍后重试',
            'data': None
        }), 500
