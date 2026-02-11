"""Insurer routes - manage insurance company connections."""
from flask import Blueprint, jsonify, request
from app import db
from app.models import Insurer, SyncLog

insurers_bp = Blueprint('insurers', __name__)


@insurers_bp.route('/insurers')
def list_insurers():
    """List all connected insurers with their status."""
    insurers = Insurer.query.order_by(Insurer.name).all()

    result = []
    for insurer in insurers:
        data = insurer.to_dict()
        # Add latest sync info
        latest_sync = SyncLog.query.filter_by(
            insurer_id=insurer.id
        ).order_by(SyncLog.sync_time.desc()).first()
        if latest_sync:
            data['last_sync_status'] = latest_sync.status
            data['last_sync_records'] = latest_sync.records_processed
            data['last_sync_duration_ms'] = latest_sync.duration_ms
        result.append(data)

    return jsonify(result)


@insurers_bp.route('/insurers/<int:insurer_id>')
def get_insurer(insurer_id):
    """Get details for a specific insurer."""
    insurer = Insurer.query.get_or_404(insurer_id)

    data = insurer.to_dict()
    # Include recent sync logs
    recent_syncs = SyncLog.query.filter_by(
        insurer_id=insurer_id
    ).order_by(SyncLog.sync_time.desc()).limit(10).all()
    data['recent_syncs'] = [s.to_dict() for s in recent_syncs]

    return jsonify(data)


@insurers_bp.route('/insurers/<int:insurer_id>/sync', methods=['POST'])
def trigger_sync(insurer_id):
    """Trigger a manual sync for a specific insurer.

    In production, this would call the insurer's API.
    Here we simulate the sync process with mock data.
    """
    import time
    import random

    insurer = Insurer.query.get_or_404(insurer_id)

    start_time = time.time()

    # Simulate sync processing
    product_count = insurer.products.count()
    records_updated = random.randint(0, min(2, product_count))
    has_error = random.random() < 0.1  # 10% chance of error

    duration_ms = int((time.time() - start_time) * 1000) + random.randint(500, 3000)

    if has_error:
        sync_log = SyncLog(
            insurer_id=insurer_id,
            sync_type='manual',
            status='failed',
            records_processed=0,
            records_failed=product_count,
            errors=f'Connection timeout: {insurer.api_endpoint} niet bereikbaar',
            duration_ms=duration_ms,
        )
        insurer.api_status = 'error'
    else:
        sync_log = SyncLog(
            insurer_id=insurer_id,
            sync_type='manual',
            status='success',
            records_processed=product_count,
            records_updated=records_updated,
            duration_ms=duration_ms,
        )
        insurer.api_status = 'active'
        insurer.last_sync = sync_log.sync_time

    db.session.add(sync_log)
    db.session.commit()

    return jsonify({
        'message': f'Sync {"completed" if not has_error else "failed"} for {insurer.name}',
        'sync_log': sync_log.to_dict(),
    }), 200 if not has_error else 500
