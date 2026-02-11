"""Product model - insurance products offered by each insurer."""
from app import db
from datetime import datetime


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    insurer_id = db.Column(db.Integer, db.ForeignKey('insurers.id'), nullable=False)
    product_code = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    product_type = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text)
    base_premium = db.Column(db.Numeric(10, 2), nullable=False)
    coverage_amount = db.Column(db.Numeric(12, 2))
    deductible = db.Column(db.Numeric(10, 2), default=0)
    rules_json = db.Column(db.JSON)
    min_age = db.Column(db.Integer, default=18)
    max_age = db.Column(db.Integer, default=75)
    status = db.Column(db.String(20), default='active')
    effective_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    policies = db.relationship('Policy', backref='product', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'insurer_id': self.insurer_id,
            'insurer_name': self.insurer.name if self.insurer else None,
            'product_code': self.product_code,
            'name': self.name,
            'product_type': self.product_type,
            'description': self.description,
            'base_premium': float(self.base_premium),
            'coverage_amount': float(self.coverage_amount) if self.coverage_amount else None,
            'deductible': float(self.deductible) if self.deductible else 0,
            'rules_json': self.rules_json,
            'min_age': self.min_age,
            'max_age': self.max_age,
            'status': self.status,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'policy_count': self.policies.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
