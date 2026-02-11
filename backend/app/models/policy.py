"""Policy model - customer insurance policies (polissen)."""
from app import db
from datetime import datetime


class Policy(db.Model):
    __tablename__ = 'policies'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    policy_number = db.Column(db.String(30), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    customer_bsn = db.Column(db.String(9))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.Text)
    postcode = db.Column(db.String(7))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    premium_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_freq = db.Column(db.String(20), default='monthly')
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    claims = db.relationship('Claim', backref='policy', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'insurer_name': self.product.insurer.name if self.product and self.product.insurer else None,
            'policy_number': self.policy_number,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'address': self.address,
            'postcode': self.postcode,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'premium_amount': float(self.premium_amount),
            'payment_freq': self.payment_freq,
            'status': self.status,
            'notes': self.notes,
            'claims_count': self.claims.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
