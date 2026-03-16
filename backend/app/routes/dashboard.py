"""Dashboard routes - KPIs and overview data for the main dashboard."""
from flask import Blueprint, jsonify
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from app import db
from app.models import Insurer, Product, Policy, Claim, SyncLog

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard/stats')
def get_dashboard_stats():
    """Return KPI data and overview statistics for the dashboard."""

    # Core KPIs for the dashboard
    total_policies = Policy.query.filter(Policy.status == 'active').count()
    active_claims = Claim.query.filter(
        Claim.status.in_(['submitted', 'under_review'])
    ).count()
    monthly_premium = db.session.query(
        func.sum(Policy.premium_amount)
    ).filter(Policy.status == 'active').scalar() or 0
    connected_insurers = Insurer.query.filter(
        Insurer.api_status == 'active'
    ).count()
    total_insurers = Insurer.query.count()

    # Policies by insurer (for pie chart)
    policies_by_insurer = db.session.query(
        Insurer.name,
        func.count(Policy.id).label('count')
    ).join(Product, Product.insurer_id == Insurer.id)\
     .join(Policy, Policy.product_id == Product.id)\
     .filter(Policy.status == 'active')\
     .group_by(Insurer.name)\
     .all()

    # Premium trends over 12 months (for line chart)
    # Generate monthly data points
    premium_trends = []
    for i in range(11, -1, -1):
        month_date = datetime.now() - timedelta(days=30 * i)
        month_label = month_date.strftime('%b %Y')
        # Simulate trending data based on active policies
        base = float(monthly_premium) * (0.85 + (11 - i) * 0.015)
        premium_trends.append({
            'month': month_label,
            'premium': round(base, 2)
        })

    # Policies by product type
    # Note: This assumes Product has a 'product_type' field. Adjust as needed.
    policies_by_type = db.session.query(
        Product.product_type,
        func.count(Policy.id).label('count')
    ).join(Policy, Policy.product_id == Product.id)\
     .filter(Policy.status == 'active')\
     .group_by(Product.product_type)\
     .all()

    # Claims by status
    # Note: This assumes Claim has a 'status' field. Adjust as needed.
    claims_by_status = db.session.query(
        Claim.status,
        func.count(Claim.id).label('count')
    ).group_by(Claim.status).all()

    # Recent activity (last 10 events from claims and sync logs)
    recent_claims = Claim.query.order_by(Claim.created_at.desc()).limit(5).all()
    recent_syncs = SyncLog.query.order_by(SyncLog.sync_time.desc()).limit(5).all()

    activities = []
    for claim in recent_claims:
        activities.append({
            'type': 'claim',
            'message': f'Claim {claim.claim_number} - {claim.status}',
            'detail': claim.description[:80] + '...' if len(claim.description) > 80 else claim.description,
            'timestamp': claim.created_at.isoformat() if claim.created_at else None,
            'status': claim.status,
        })
    for sync in recent_syncs:
        activities.append({
            'type': 'sync',
            'message': f'Sync {sync.insurer.name if sync.insurer else "Unknown"} - {sync.status}',
            'detail': f'{sync.records_processed} records processed',
            'timestamp': sync.sync_time.isoformat() if sync.sync_time else None,
            'status': sync.status,
        })

    # Sort by timestamp descending and take top 10
    activities.sort(key=lambda x: x['timestamp'] or '', reverse=True)
    activities = activities[:10]

    return jsonify({
        'kpis': {
            'total_policies': total_policies,
            'active_claims': active_claims,
            'monthly_premium': float(monthly_premium),
            'connected_insurers': connected_insurers,
            'total_insurers': total_insurers,
        },
        'policies_by_insurer': [
            {'name': name, 'value': count}
            for name, count in policies_by_insurer
        ],
        'premium_trends': premium_trends,
        'policies_by_type': [
            {'type': ptype, 'count': count}
            for ptype, count in policies_by_type
        ],
        'claims_by_status': [
            {'status': status, 'count': count}
            for status, count in claims_by_status
        ],
        'recent_activity': activities,
    })
