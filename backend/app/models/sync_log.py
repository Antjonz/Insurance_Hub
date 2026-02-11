"""SyncLog model - tracks data synchronization with insurers."""
from app import db
from datetime import datetime


class SyncLog(db.Model):
    __tablename__ = 'sync_logs'

    id = db.Column(db.Integer, primary_key=True)
    insurer_id = db.Column(db.Integer, db.ForeignKey('insurers.id'), nullable=False)
    sync_time = db.Column(db.DateTime, default=datetime.utcnow)
    sync_type = db.Column(db.String(20), default='full')
    status = db.Column(db.String(20), nullable=False)
    records_processed = db.Column(db.Integer, default=0)
    records_created = db.Column(db.Integer, default=0)
    records_updated = db.Column(db.Integer, default=0)
    records_failed = db.Column(db.Integer, default=0)
    errors = db.Column(db.Text)
    duration_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'insurer_id': self.insurer_id,
            'insurer_name': self.insurer.name if self.insurer else None,
            'sync_time': self.sync_time.isoformat() if self.sync_time else None,
            'sync_type': self.sync_type,
            'status': self.status,
            'records_processed': self.records_processed,
            'records_created': self.records_created,
            'records_updated': self.records_updated,
            'records_failed': self.records_failed,
            'errors': self.errors,
            'duration_ms': self.duration_ms,
        }
