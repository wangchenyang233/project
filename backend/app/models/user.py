from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, default=1)  # 1: 启用, 0: 禁用
    is_super_admin = db.Column(db.Boolean, default=False)
    
    # 模块权限配置
    activity_query = db.Column(db.Boolean, default=False)  # 活动查询权限
    activity_monitor = db.Column(db.Boolean, default=False)  # 活动监控权限
    copy_trade = db.Column(db.Boolean, default=False)  # 跟单交易权限
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_permissions=True):
        """将用户对象转换为字典"""
        user_dict = {
            'id': self.id,
            'username': self.username,
            'status': self.status,
            'is_super_admin': self.is_super_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if include_permissions and not self.is_super_admin:
            user_dict.update({
                'activity_query': self.activity_query,
                'activity_monitor': self.activity_monitor,
                'copy_trade': self.copy_trade
            })
        
        return user_dict
