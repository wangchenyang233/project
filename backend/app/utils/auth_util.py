from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, verify_jwt_in_request, get_jwt
from functools import wraps
from flask import jsonify, request
from app.models import User  # 假设User模型已定义
from app.extensions import db

# JWT令牌生成函数
def generate_tokens(user_id, is_super_admin=False):
    """生成访问令牌和刷新令牌"""
    additional_claims = {
        'is_super_admin': is_super_admin
    }
    access_token = create_access_token(identity=user_id, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user_id, additional_claims=additional_claims)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

# 获取当前用户信息
def get_current_user():
    """从JWT令牌中获取当前用户信息"""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.get(user_id)

# 登录验证装饰器
def require_login(f):
    """验证用户是否登录的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'code': 401,
                'message': '请先登录',
                'error': str(e)
            }), 401
    return decorated_function

# 超级管理员验证装饰器
def require_super_admin(f):
    """验证用户是否为超级管理员的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if not claims.get('is_super_admin', False):
                return jsonify({
                    'code': 403,
                    'message': '需要超级管理员权限'
                }), 403
            return f(*args, **kwargs)
        except Exception as e:
            if 'Missing' in str(e) or 'Invalid' in str(e):
                return jsonify({
                    'code': 401,
                    'message': '请先登录'
                }), 401
            return jsonify({
                'code': 403,
                'message': '需要超级管理员权限'
            }), 403
    return decorated_function

# 模块权限验证装饰器
def require_module_permission(module):
    """验证用户是否拥有指定模块权限的装饰器
    
    Args:
        module: 模块标识字符串（如 'activity_query', 'activity_monitor', 'copy_trade'）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = User.query.get(user_id)
                
                # 检查是否为超级管理员
                if hasattr(user, 'is_super_admin') and user.is_super_admin:
                    return f(*args, **kwargs)
                
                # 检查是否拥有模块权限
                if not hasattr(user, module) or not getattr(user, module):
                    return jsonify({
                        'code': 403,
                        'message': f'缺少{module}模块的访问权限'
                    }), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                if 'Missing' in str(e) or 'Invalid' in str(e):
                    return jsonify({
                        'code': 401,
                        'message': '请先登录'
                    }), 401
                return jsonify({
                    'code': 403,
                    'message': f'缺少{module}模块的访问权限'
                }), 403
        return decorated_function
    return decorator
