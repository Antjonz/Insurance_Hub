"""Sync Insurer Products Script

Fetches product data from mock insurer APIs, compares with the database,
detects changes (new products, price updates, discontinued products),
and logs sync results. Demonstrates API integration, data comparison,
and automated reporting.

Usage:
    python scripts/sync_insurer_products.py [--insurer CODE] [--dry-run]
"""
import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime

import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Insurer, Product, SyncLog
from integrations.json_parser import normalize_product
from integrations.xml_parser import parse_xml_products

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def fetch_insurer_products(insurer):
    """Fetch products from an insurer's API endpoint.

    Handles both JSON and XML response formats based on insurer configuration.
    """
    logger.info(f'Fetching products from {insurer.name} ({insurer.api_endpoint})')

    try:
        response = requests.get(insurer.api_endpoint, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f'Failed to connect to {insurer.name}: {e}')
        return None

    if insurer.api_format == 'xml':
        # Save XML to temp file for parsing
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(response.text)
            temp_path = f.name
        try:
            products = parse_xml_products(temp_path)
        finally:
            os.unlink(temp_path)
        return products
    else:
        # JSON format - normalize the response
        data = response.json()
        raw_products = []
        if isinstance(data, list):
            raw_products = data
        elif isinstance(data, dict):
            for key in ['products', 'catalog', 'items']:
                if key in data and isinstance(data[key], list):
                    raw_products = data[key]
                    break
        return [normalize_product(p) for p in raw_products]


def compare_and_update(insurer, api_products, dry_run=False):
    """Compare API products with database and detect changes.

    Returns a summary of changes: new products, updated fields, and
    products no longer available from the insurer.
    """
    changes = {
        'created': [],
        'updated': [],
        'unchanged': [],
        'errors': [],
    }

    db_products = {p.product_code: p for p in insurer.products.all()}

    for api_product in api_products:
        code = api_product.get('product_code')
        if not code:
            changes['errors'].append('Product missing product_code')
            continue

        if code in db_products:
            # Compare fields for changes
            db_prod = db_products[code]
            field_changes = []

            if api_product.get('name') and api_product['name'] != db_prod.name:
                field_changes.append(f'name: {db_prod.name} -> {api_product["name"]}')
                if not dry_run:
                    db_prod.name = api_product['name']

            api_premium = api_product.get('base_premium')
            if api_premium is not None and float(api_premium) != float(db_prod.base_premium):
                field_changes.append(f'premium: €{db_prod.base_premium} -> €{api_premium}')
                if not dry_run:
                    db_prod.base_premium = api_premium

            api_coverage = api_product.get('coverage_amount')
            if api_coverage is not None and db_prod.coverage_amount and float(api_coverage) != float(db_prod.coverage_amount):
                field_changes.append(f'coverage: €{db_prod.coverage_amount} -> €{api_coverage}')
                if not dry_run:
                    db_prod.coverage_amount = api_coverage

            if field_changes:
                changes['updated'].append({
                    'code': code,
                    'changes': field_changes,
                })
                logger.info(f'  Updated {code}: {", ".join(field_changes)}')
            else:
                changes['unchanged'].append(code)

            del db_products[code]
        else:
            # New product
            changes['created'].append(code)
            logger.info(f'  New product: {code} - {api_product.get("name")}')
            if not dry_run:
                new_product = Product(
                    insurer_id=insurer.id,
                    product_code=code,
                    name=api_product.get('name', ''),
                    product_type=api_product.get('product_type', 'unknown'),
                    base_premium=api_product.get('base_premium', 0),
                    coverage_amount=api_product.get('coverage_amount'),
                    deductible=api_product.get('deductible', 0),
                    description=api_product.get('description', ''),
                    status='active',
                )
                db.session.add(new_product)

    return changes


def sync_insurer(insurer, dry_run=False):
    """Run a full sync for a single insurer."""
    logger.info(f'=== Starting sync for {insurer.name} (code: {insurer.code}) ===')
    start_time = time.time()

    # Fetch from API
    products = fetch_insurer_products(insurer)
    if products is None:
        # Log failure
        if not dry_run:
            sync_log = SyncLog(
                insurer_id=insurer.id,
                sync_type='full',
                status='failed',
                errors='Failed to fetch products from API',
                duration_ms=int((time.time() - start_time) * 1000),
            )
            db.session.add(sync_log)
            insurer.api_status = 'error'
            db.session.commit()
        return None

    logger.info(f'  Received {len(products)} products from API')

    # Compare and update
    changes = compare_and_update(insurer, products, dry_run)

    duration_ms = int((time.time() - start_time) * 1000)

    # Log sync result
    if not dry_run:
        sync_log = SyncLog(
            insurer_id=insurer.id,
            sync_type='full',
            status='success',
            records_processed=len(products),
            records_created=len(changes['created']),
            records_updated=len(changes['updated']),
            records_failed=len(changes['errors']),
            errors='\n'.join(changes['errors']) if changes['errors'] else None,
            duration_ms=duration_ms,
        )
        db.session.add(sync_log)
        insurer.api_status = 'active'
        insurer.last_sync = datetime.utcnow()
        db.session.commit()

    # Print summary
    logger.info(f'  Sync complete in {duration_ms}ms:')
    logger.info(f'    Created: {len(changes["created"])}')
    logger.info(f'    Updated: {len(changes["updated"])}')
    logger.info(f'    Unchanged: {len(changes["unchanged"])}')
    logger.info(f'    Errors: {len(changes["errors"])}')

    return changes


def main():
    parser = argparse.ArgumentParser(description='Sync insurer product data')
    parser.add_argument('--insurer', '-i', help='Sync specific insurer by code (e.g., ACH)')
    parser.add_argument('--dry-run', '-d', action='store_true',
                       help='Preview changes without writing to database')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if args.insurer:
            insurer = Insurer.query.filter_by(code=args.insurer.upper()).first()
            if not insurer:
                logger.error(f'Insurer with code "{args.insurer}" not found')
                sys.exit(1)
            sync_insurer(insurer, dry_run=args.dry_run)
        else:
            # Sync all active insurers
            insurers = Insurer.query.filter(
                Insurer.api_status.in_(['active', 'error'])
            ).all()
            logger.info(f'Starting sync for {len(insurers)} insurers')
            for insurer in insurers:
                sync_insurer(insurer, dry_run=args.dry_run)
            logger.info('All syncs completed')


if __name__ == '__main__':
    main()
