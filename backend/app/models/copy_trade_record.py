from app.extensions import db
from datetime import datetime

class CopyTradeRecord(db.Model):
    __tablename__ = 'copy_trade_record'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(100), nullable=False)
    target_user = db.Column(db.String(100), nullable=False)
    target_tx_hash = db.Column(db.String(100), nullable=False)
    tx_hash = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    size = db.Column(db.Float, nullable=False)
    side = db.Column(db.String(10), nullable=False)
    token_id = db.Column(db.String(100), nullable=False)
    event_title = db.Column(db.String(255), nullable=True)  # 事件标题
    event_slug = db.Column(db.String(255), nullable=True)    # 事件标识
    status = db.Column(db.String(20), nullable=False)  # success, failed, pending, live
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'target_user': self.target_user,
            'target_tx_hash': self.target_tx_hash,
            'tx_hash': self.tx_hash,
            'amount': self.amount,
            'price': self.price,
            'size': self.size,
            'side': self.side,
            'token_id': self.token_id,
            'event_title': self.event_title,
            'event_slug': self.event_slug,
            'status': self.status,
            'timestamp': int(self.created_at.timestamp())
        }