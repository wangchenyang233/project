import os
from app import create_app

# 创建Flask应用实例
app = create_app(config_name=os.getenv('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    # 获取端口配置
    port = int(os.getenv('PORT', 5000))
    # 获取主机配置
    host = os.getenv('HOST', '0.0.0.0')
    # 获取调试模式配置
    debug = app.config['DEBUG']
    
    # 启动应用
    print(f"Starting Flask application on {host}:{port} in {os.getenv('FLASK_CONFIG', 'development')} mode")
    app.run(host=host, port=port, debug=debug)
