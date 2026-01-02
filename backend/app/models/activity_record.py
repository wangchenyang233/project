from app.extensions import db
from datetime import datetime

class ActivityRecord(db.Model):
    __tablename__ = 'activity_record'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(100))
    target_user = db.Column(db.String(100), nullable=False)
    transaction_hash = db.Column(db.String(100))
    timestamp = db.Column(db.Integer, nullable=False)
    asset = db.Column(db.String(200))
    side = db.Column(db.String(10))
    size = db.Column(db.Float)
    price = db.Column(db.Float)
    unique_key = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'target_user': self.target_user,
            'transaction_hash': self.transaction_hash,
            'timestamp': self.timestamp,
            'asset': self.asset,
            'side': self.side,
            'size': self.size,
            'price': self.price,
            'unique_key': self.unique_key,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }