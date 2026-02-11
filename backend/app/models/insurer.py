"""Insurer model - represents insurance companies connected to the platform."""
from app import db
from datetime import datetime


class Insurer(db.Model):
    __tablename__ = 'insurers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    api_endpoint = db.Column(db.String(255))
    api_format = db.Column(db.String(10), default='json')
    api_status = db.Column(db.String(20), default='active')
    last_sync = db.Column(db.DateTime)
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    kvk_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = db.relationship('Product', backref='insurer', lazy='dynamic')
    sync_logs = db.relationship('SyncLog', backref='insurer', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'api_endpoint': self.api_endpoint,
            'api_format': self.api_format,
            'api_status': self.api_status,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'address': self.address,
            'kvk_number': self.kvk_number,
            'product_count': self.products.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
