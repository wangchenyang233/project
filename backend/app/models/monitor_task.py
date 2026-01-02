from app.extensions import db
from datetime import datetime

class MonitorTask(db.Model):
    __tablename__ = 'monitor_task'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(100), unique=True, nullable=False)
    target_user = db.Column(db.String(100), nullable=False)
    poll_seconds = db.Column(db.Integer, default=5)
    status = db.Column(db.String(20), default='running')  # running, stopped, finished, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'target_user': self.target_user,
            'poll_seconds': self.poll_seconds,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }