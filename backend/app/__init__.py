import os
import logging
from flask import Flask
from .extensions import db, celery, cors, jwt
from .config import config

# 设置日志配置
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger('werkzeug').setLevel(logging.WARNING)  # 降低werkzeug的日志级别
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)  # 降低SQLAlchemy的日志级别

# 创建Flask应用

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 绑定扩展
    register_extensions(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 初始化数据库
    with app.app_context():
        db.create_all()
        
    return app

# 注册扩展
def register_extensions(app):
    # 绑定SQLAlchemy
    db.init_app(app)
    
    # 绑定Celery
    celery.conf.update(app.config)
    celery.conf.broker_url = app.config['REDIS_URL']
    celery.conf.result_backend = app.config['REDIS_URL']
    
    # 绑定CORS
    cors.init_app(app, resources={r"/*": {"origins": "*"}})
    
    # 绑定JWT
    jwt.init_app(app)

# 注册蓝图
def register_blueprints(app):
    # 导入蓝图
    from .api import auth_bp, user_manage_bp, activity_bp, monitor_bp, copy_trade_bp
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(user_manage_bp, url_prefix='/api/v1/user-manage')
    app.register_blueprint(activity_bp, url_prefix='/api/v1/activity')
    app.register_blueprint(monitor_bp, url_prefix='/api/v1/monitor')
    app.register_blueprint(copy_trade_bp, url_prefix='/api/v1/copy-trade')
