from flask import Blueprint

# 创建蓝图
auth_bp = Blueprint('auth', __name__)
user_manage_bp = Blueprint('user_manage', __name__)
activity_bp = Blueprint('activity', __name__)
monitor_bp = Blueprint('monitor', __name__)
copy_trade_bp = Blueprint('copy_trade', __name__)

# 导入路由
from . import auth
from . import user_manage
from . import activity
from . import monitor
from . import copy_trade
