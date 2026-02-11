"""Claim model - insurance claims (schademeldingen)."""
from app import db
from datetime import datetime


class Claim(db.Model):
    __tablename__ = 'claims'

    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('policies.id'), nullable=False)
    claim_number = db.Column(db.String(30), unique=True, nullable=False)
    claim_date = db.Column(db.Date, nullable=False)
    reported_date = db.Column(db.Date, default=datetime.utcnow)
    amount = db.Column(db.Numeric(10, 2))
    approved_amount = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(20), default='submitted')
    category = db.Column(db.String(50))
    description = db.Column(db.Text, nullable=False)
    assessor_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'policy_id': self.policy_id,
            'policy_number': self.policy.policy_number if self.policy else None,
            'customer_name': self.policy.customer_name if self.policy else None,
            'insurer_name': (self.policy.product.insurer.name
                           if self.policy and self.policy.product and self.policy.product.insurer
                           else None),
            'claim_number': self.claim_number,
            'claim_date': self.claim_date.isoformat() if self.claim_date else None,
            'reported_date': self.reported_date.isoformat() if self.reported_date else None,
            'amount': float(self.amount) if self.amount else None,
            'approved_amount': float(self.approved_amount) if self.approved_amount else None,
            'status': self.status,
            'category': self.category,
            'description': self.description,
            'assessor_notes': self.assessor_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
