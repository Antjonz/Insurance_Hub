"""Sync routes - monitor and manage insurer data synchronization."""
from flask import Blueprint, jsonify
from sqlalchemy import func
from app import db
from app.models import Insurer, SyncLog

sync_bp = Blueprint('sync', __name__)


@sync_bp.route('/sync/status')
def sync_status():
    """Return sync status overview for all insurers.

    Shows connection health, last sync details, and recent error counts.
    """
    insurers = Insurer.query.order_by(Insurer.name).all()
    status_data = []

    for insurer in insurers:
        # Get latest sync log
        latest = SyncLog.query.filter_by(
            insurer_id=insurer.id
        ).order_by(SyncLog.sync_time.desc()).first()

        # Count recent failures (last 24 hours)
        from datetime import datetime, timedelta
        recent_failures = SyncLog.query.filter(
            SyncLog.insurer_id == insurer.id,
            SyncLog.status == 'failed',
            SyncLog.sync_time > datetime.utcnow() - timedelta(hours=24)
        ).count()

        # Determine health status
        if insurer.api_status == 'error' or recent_failures > 2:
            health = 'red'
        elif recent_failures > 0 or insurer.api_status == 'inactive':
            health = 'yellow'
        else:
            health = 'green'

        status_data.append({
            'insurer_id': insurer.id,
            'insurer_name': insurer.name,
            'insurer_code': insurer.code,
            'api_status': insurer.api_status,
            'api_format': insurer.api_format,
            'last_sync': insurer.last_sync.isoformat() if insurer.last_sync else None,
            'last_sync_status': latest.status if latest else None,
            'last_sync_records': latest.records_processed if latest else 0,
            'last_sync_duration_ms': latest.duration_ms if latest else None,
            'last_sync_errors': latest.errors if latest else None,
            'recent_failures': recent_failures,
            'health': health,
        })

    return jsonify(status_data)


@sync_bp.route('/sync/logs')
def sync_logs():
    """Return recent sync logs across all insurers."""
    logs = SyncLog.query.order_by(SyncLog.sync_time.desc()).limit(50).all()
    return jsonify([log.to_dict() for log in logs])
