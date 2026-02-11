"""Bulk Excel Import Script

Reads Excel files containing product or policy data, validates the format,
performs bulk inserts into the database with error handling and rollback
capability.

Usage:
    python scripts/import_excel_bulk.py --file <path.xlsx> --type [products|policies]
"""
import os
import sys
import argparse
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Insurer, Product, Policy
from integrations.excel_handler import parse_excel_products

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def validate_product_row(row, row_num):
    """Validate a single product row and return a list of errors."""
    errors = []

    if not row.get('product_code'):
        errors.append(f'Row {row_num}: Missing product_code')
    if not row.get('name'):
        errors.append(f'Row {row_num}: Missing product name')
    if not row.get('product_type'):
        errors.append(f'Row {row_num}: Missing product type')

    valid_types = ['property', 'life', 'health', 'auto', 'liability', 'travel']
    if row.get('product_type') and row['product_type'] not in valid_types:
        errors.append(f'Row {row_num}: Invalid product type "{row["product_type"]}" '
                      f'(must be one of: {", ".join(valid_types)})')

    premium = row.get('base_premium', 0)
    try:
        if float(premium) < 0:
            errors.append(f'Row {row_num}: Negative premium value')
    except (ValueError, TypeError):
        errors.append(f'Row {row_num}: Invalid premium value "{premium}"')

    return errors


def validate_policy_row(row, row_num):
    """Validate a single policy row."""
    errors = []

    if not row.get('customer_name'):
        errors.append(f'Row {row_num}: Missing customer name')
    if not row.get('product_code'):
        errors.append(f'Row {row_num}: Missing product code')
    if not row.get('start_date'):
        errors.append(f'Row {row_num}: Missing start date')

    return errors


def import_products(filepath):
    """Import products from an Excel file with validation and rollback."""
    logger.info(f'Importing products from: {filepath}')

    products_data = parse_excel_products(filepath)
    logger.info(f'Found {len(products_data)} product rows')

    # Validation pass
    all_errors = []
    for i, row in enumerate(products_data, 1):
        errors = validate_product_row(row, i)
        all_errors.extend(errors)

    if all_errors:
        logger.warning(f'Found {len(all_errors)} validation errors:')
        for error in all_errors:
            logger.warning(f'  {error}')

        # Check if there are critical errors
        critical = [e for e in all_errors if 'Missing product_code' in e or 'Missing product name' in e]
        if critical:
            logger.error('Critical validation errors found. Aborting import.')
            return {'success': False, 'errors': all_errors}

    # Import pass
    results = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': []}
    savepoint = db.session.begin_nested()

    try:
        for i, row in enumerate(products_data, 1):
            try:
                code = row.get('product_code', '')
                if not code:
                    results['skipped'] += 1
                    continue

                # Find insurer
                insurer_code = row.get('insurer_code', code.split('-')[0] if '-' in code else '')
                insurer = Insurer.query.filter_by(code=insurer_code).first()
                if not insurer:
                    results['errors'].append(f'Row {i}: Unknown insurer code "{insurer_code}"')
                    results['skipped'] += 1
                    continue

                # Check for existing product
                existing = Product.query.filter_by(product_code=code).first()
                if existing:
                    existing.name = row.get('name', existing.name)
                    existing.product_type = row.get('product_type', existing.product_type)
                    existing.base_premium = row.get('base_premium', existing.base_premium)
                    existing.coverage_amount = row.get('coverage_amount', existing.coverage_amount)
                    existing.deductible = row.get('deductible', existing.deductible)
                    results['updated'] += 1
                    logger.info(f'  Updated: {code}')
                else:
                    product = Product(
                        insurer_id=insurer.id,
                        product_code=code,
                        name=row.get('name', ''),
                        product_type=row.get('product_type', 'unknown'),
                        base_premium=row.get('base_premium', 0),
                        coverage_amount=row.get('coverage_amount'),
                        deductible=row.get('deductible', 0),
                        description=row.get('description', ''),
                        status='active',
                    )
                    db.session.add(product)
                    results['created'] += 1
                    logger.info(f'  Created: {code}')

            except Exception as e:
                results['errors'].append(f'Row {i}: {str(e)}')
                logger.error(f'  Row {i} error: {e}')

        db.session.commit()
        logger.info(f'\nImport completed successfully!')

    except Exception as e:
        db.session.rollback()
        logger.error(f'Import failed, rolled back all changes: {e}')
        results['errors'].append(f'Bulk error: {str(e)}')
        return {'success': False, **results}

    # Print summary
    logger.info(f'\n=== Import Summary ===')
    logger.info(f'  Created:  {results["created"]}')
    logger.info(f'  Updated:  {results["updated"]}')
    logger.info(f'  Skipped:  {results["skipped"]}')
    logger.info(f'  Errors:   {len(results["errors"])}')

    return {'success': True, **results}


def main():
    parser = argparse.ArgumentParser(description='Bulk import from Excel')
    parser.add_argument('--file', '-f', required=True, help='Path to Excel file')
    parser.add_argument('--type', '-t', choices=['products', 'policies'],
                       default='products', help='Type of data to import')
    args = parser.parse_args()

    if not os.path.exists(args.file):
        logger.error(f'File not found: {args.file}')
        sys.exit(1)

    app = create_app()
    with app.app_context():
        if args.type == 'products':
            import_products(args.file)
        else:
            logger.info('Policy import not yet implemented')


if __name__ == '__main__':
    main()
