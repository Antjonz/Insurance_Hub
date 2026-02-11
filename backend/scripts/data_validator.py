"""Data Validation Script

Validates imported insurance data quality across the database.
Checks for missing required fields, duplicate entries, data consistency,
and generates a comprehensive validation report with statistics.

Usage:
    python scripts/data_validator.py [--fix] [--report output.json]
"""
import os
import sys
import json
import argparse
import logging
from datetime import datetime
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Insurer, Product, Policy, Claim

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def validate_insurers():
    """Validate insurer records for completeness and consistency."""
    issues = []
    insurers = Insurer.query.all()

    for ins in insurers:
        if not ins.contact_email:
            issues.append({
                'table': 'insurers',
                'id': ins.id,
                'field': 'contact_email',
                'severity': 'warning',
                'message': f'{ins.name}: Missing contact email',
            })
        if not ins.kvk_number:
            issues.append({
                'table': 'insurers',
                'id': ins.id,
                'field': 'kvk_number',
                'severity': 'warning',
                'message': f'{ins.name}: Missing KVK number',
            })
        if ins.api_status == 'error':
            issues.append({
                'table': 'insurers',
                'id': ins.id,
                'field': 'api_status',
                'severity': 'error',
                'message': f'{ins.name}: API connection in error state',
            })

    return issues


def validate_products():
    """Validate product records for data quality."""
    issues = []
    products = Product.query.all()

    # Check for duplicates
    codes = Counter(p.product_code for p in products)
    for code, count in codes.items():
        if count > 1:
            issues.append({
                'table': 'products',
                'field': 'product_code',
                'severity': 'error',
                'message': f'Duplicate product code: {code} ({count} occurrences)',
            })

    for prod in products:
        if float(prod.base_premium) <= 0:
            issues.append({
                'table': 'products',
                'id': prod.id,
                'field': 'base_premium',
                'severity': 'error',
                'message': f'{prod.product_code}: Invalid base premium (€{prod.base_premium})',
            })
        if prod.coverage_amount and float(prod.coverage_amount) < 0:
            issues.append({
                'table': 'products',
                'id': prod.id,
                'field': 'coverage_amount',
                'severity': 'error',
                'message': f'{prod.product_code}: Negative coverage amount',
            })
        if not prod.description:
            issues.append({
                'table': 'products',
                'id': prod.id,
                'field': 'description',
                'severity': 'info',
                'message': f'{prod.product_code}: Missing product description',
            })
        valid_types = ['property', 'life', 'health', 'auto', 'liability', 'travel']
        if prod.product_type not in valid_types:
            issues.append({
                'table': 'products',
                'id': prod.id,
                'field': 'product_type',
                'severity': 'warning',
                'message': f'{prod.product_code}: Unknown product type "{prod.product_type}"',
            })

    return issues


def validate_policies():
    """Validate policy records for completeness and logical consistency."""
    issues = []
    policies = Policy.query.all()

    # Check for duplicate policy numbers
    numbers = Counter(p.policy_number for p in policies)
    for number, count in numbers.items():
        if count > 1:
            issues.append({
                'table': 'policies',
                'field': 'policy_number',
                'severity': 'error',
                'message': f'Duplicate policy number: {number} ({count} occurrences)',
            })

    for pol in policies:
        if not pol.customer_email:
            issues.append({
                'table': 'policies',
                'id': pol.id,
                'field': 'customer_email',
                'severity': 'warning',
                'message': f'{pol.policy_number}: Missing customer email',
            })
        if pol.end_date and pol.start_date and pol.end_date < pol.start_date:
            issues.append({
                'table': 'policies',
                'id': pol.id,
                'field': 'end_date',
                'severity': 'error',
                'message': f'{pol.policy_number}: End date before start date',
            })
        if float(pol.premium_amount) <= 0:
            issues.append({
                'table': 'policies',
                'id': pol.id,
                'field': 'premium_amount',
                'severity': 'error',
                'message': f'{pol.policy_number}: Invalid premium amount (€{pol.premium_amount})',
            })
        # Check postcode format (Dutch: 4 digits + 2 letters)
        if pol.postcode:
            pc = pol.postcode.replace(' ', '')
            if len(pc) != 6 or not pc[:4].isdigit() or not pc[4:].isalpha():
                issues.append({
                    'table': 'policies',
                    'id': pol.id,
                    'field': 'postcode',
                    'severity': 'warning',
                    'message': f'{pol.policy_number}: Invalid Dutch postcode format: {pol.postcode}',
                })

    return issues


def validate_claims():
    """Validate claim records."""
    issues = []
    claims = Claim.query.all()

    for claim in claims:
        if claim.approved_amount and claim.amount:
            if float(claim.approved_amount) > float(claim.amount):
                issues.append({
                    'table': 'claims',
                    'id': claim.id,
                    'field': 'approved_amount',
                    'severity': 'warning',
                    'message': f'{claim.claim_number}: Approved amount (€{claim.approved_amount}) '
                              f'exceeds claimed amount (€{claim.amount})',
                })
        if claim.claim_date and claim.reported_date:
            if claim.reported_date < claim.claim_date:
                issues.append({
                    'table': 'claims',
                    'id': claim.id,
                    'field': 'reported_date',
                    'severity': 'error',
                    'message': f'{claim.claim_number}: Reported date before claim date',
                })

    return issues


def generate_report(all_issues):
    """Generate a summary report from all validation issues."""
    severity_counts = Counter(i['severity'] for i in all_issues)
    table_counts = Counter(i['table'] for i in all_issues)

    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_issues': len(all_issues),
            'by_severity': dict(severity_counts),
            'by_table': dict(table_counts),
        },
        'issues': all_issues,
    }

    return report


def main():
    parser = argparse.ArgumentParser(description='Validate insurance data quality')
    parser.add_argument('--report', '-r', help='Save report to JSON file')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        logger.info('=== InsuranceHub Data Validation ===')

        all_issues = []

        logger.info('Validating insurers...')
        all_issues.extend(validate_insurers())

        logger.info('Validating products...')
        all_issues.extend(validate_products())

        logger.info('Validating policies...')
        all_issues.extend(validate_policies())

        logger.info('Validating claims...')
        all_issues.extend(validate_claims())

        # Generate report
        report = generate_report(all_issues)

        # Print summary
        logger.info(f'\n=== Validation Summary ===')
        logger.info(f'Total issues found: {report["summary"]["total_issues"]}')
        for severity, count in report['summary']['by_severity'].items():
            logger.info(f'  {severity.upper()}: {count}')
        logger.info('')
        for table, count in report['summary']['by_table'].items():
            logger.info(f'  {table}: {count} issues')

        # Print all issues
        for issue in all_issues:
            level = issue['severity'].upper()
            logger.log(
                logging.ERROR if level == 'ERROR' else logging.WARNING if level == 'WARNING' else logging.INFO,
                f'  [{level}] {issue["message"]}'
            )

        # Save report if requested
        if args.report:
            with open(args.report, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f'\nReport saved to {args.report}')


if __name__ == '__main__':
    main()
