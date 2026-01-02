from app.extensions import db
from datetime import datetime

class CopyTradeConfig(db.Model):
    __tablename__ = 'copy_trade_config'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_user = db.Column(db.String(100), nullable=False)
    my_proxy_wallet = db.Column(db.String(100), nullable=False)
    pk_encrypted = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='stopped')  # stopped, running, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('copy_trade_configs', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_user': self.target_user,
            'my_proxy_wallet': self.my_proxy_wallet,
            'task_id': self.task_id,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }