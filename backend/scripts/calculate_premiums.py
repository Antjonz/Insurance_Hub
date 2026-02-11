"""Premium Calculation Script

Batch-processes premium calculations for policies using product-specific
calculation rules. Supports different calculation methods per insurer
and can recalculate premiums when rules change.

Usage:
    python scripts/calculate_premiums.py [--product-id ID] [--recalculate-all]
"""
import os
import sys
import json
import argparse
import logging
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Product, Policy

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def calculate_age(date_of_birth):
    """Calculate age from date of birth."""
    if not date_of_birth:
        return None
    today = datetime.now().date()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


def find_bracket_factor(age, age_factors):
    """Find the matching factor for an age within bracket rules.

    Brackets are defined as strings like '18-30', '31-45', '55+'.
    """
    for bracket, factor in age_factors.items():
        bracket_str = str(bracket)
        if '+' in bracket_str:
            min_age = int(bracket_str.replace('+', ''))
            if age >= min_age:
                return factor
        elif '-' in bracket_str:
            parts = bracket_str.split('-')
            low, high = int(parts[0]), int(parts[1])
            if low <= age <= high:
                return factor
        else:
            try:
                if age == int(bracket_str):
                    return factor
            except ValueError:
                pass
    return 1.0


def calculate_premium(product, policy):
    """Calculate premium for a policy based on product rules.

    Applies all applicable factors from the product's rules_json:
    - Age factor (leeftijdsfactor)
    - Region factor (regiofactor)
    - Claim-free years (schadevrije jaren)
    - Smoker surcharge (rokers toeslag)
    - Combined/package discounts
    """
    base_premium = float(product.base_premium)
    rules = product.rules_json or {}
    factors = []
    total_factor = 1.0

    # Age factor
    if 'age_factor' in rules and policy.date_of_birth:
        age = calculate_age(policy.date_of_birth)
        if age:
            factor = find_bracket_factor(age, rules['age_factor'])
            total_factor *= factor
            factors.append(('age', factor))

    # Region factor (derived from postcode if available)
    if 'region_factor' in rules and policy.postcode:
        # Simple Dutch postcode-to-region mapping
        pc = int(policy.postcode[:4]) if policy.postcode[:4].isdigit() else 0
        if pc < 4000:
            region = 'west'
        elif pc < 6000:
            region = 'south'
        elif pc < 8000:
            region = 'east'
        else:
            region = 'north'

        if region in rules['region_factor']:
            factor = rules['region_factor'][region]
            total_factor *= factor
            factors.append(('region', factor))

    # Combined discount
    if 'combined_discount' in rules:
        factor = rules['combined_discount']
        total_factor *= factor
        factors.append(('combined_discount', factor))

    # Student discount
    if 'student_discount' in rules:
        if policy.date_of_birth:
            age = calculate_age(policy.date_of_birth)
            if age and age < 26:
                factor = rules['student_discount']
                total_factor *= factor
                factors.append(('student_discount', factor))

    calculated = round(base_premium * total_factor, 2)

    return {
        'base_premium': base_premium,
        'factors': factors,
        'total_factor': round(total_factor, 4),
        'calculated_premium': calculated,
    }


def batch_calculate(product_id=None, recalculate_all=False):
    """Run batch premium calculation for policies.

    Args:
        product_id: If set, only calculate for this product's policies
        recalculate_all: If True, recalculate even if premium hasn't changed
    """
    query = Policy.query.filter(Policy.status == 'active')
    if product_id:
        query = query.filter(Policy.product_id == product_id)

    policies = query.all()
    logger.info(f'Processing {len(policies)} active policies')

    results = {
        'processed': 0,
        'updated': 0,
        'unchanged': 0,
        'errors': 0,
        'details': [],
    }

    for policy in policies:
        try:
            product = policy.product
            if not product:
                logger.warning(f'Policy {policy.policy_number}: product not found')
                results['errors'] += 1
                continue

            calc = calculate_premium(product, policy)
            current_premium = float(policy.premium_amount)
            new_premium = calc['calculated_premium']

            results['processed'] += 1

            if abs(current_premium - new_premium) > 0.01 or recalculate_all:
                detail = {
                    'policy_number': policy.policy_number,
                    'customer': policy.customer_name,
                    'product': product.product_code,
                    'old_premium': current_premium,
                    'new_premium': new_premium,
                    'difference': round(new_premium - current_premium, 2),
                    'factors': calc['factors'],
                }

                if abs(current_premium - new_premium) > 0.01:
                    logger.info(
                        f'  {policy.policy_number}: €{current_premium:.2f} -> €{new_premium:.2f} '
                        f'({"+" if new_premium > current_premium else ""}'
                        f'{new_premium - current_premium:.2f})'
                    )
                    policy.premium_amount = new_premium
                    results['updated'] += 1
                else:
                    results['unchanged'] += 1

                results['details'].append(detail)
            else:
                results['unchanged'] += 1

        except Exception as e:
            logger.error(f'  Error processing {policy.policy_number}: {e}')
            results['errors'] += 1

    db.session.commit()

    # Print summary
    logger.info(f'\n=== Premium Calculation Summary ===')
    logger.info(f'  Processed:  {results["processed"]}')
    logger.info(f'  Updated:    {results["updated"]}')
    logger.info(f'  Unchanged:  {results["unchanged"]}')
    logger.info(f'  Errors:     {results["errors"]}')

    if results['details']:
        total_diff = sum(d['difference'] for d in results['details'] if 'difference' in d)
        logger.info(f'  Net premium change: €{total_diff:+.2f}')

    return results


def main():
    parser = argparse.ArgumentParser(description='Batch premium calculation')
    parser.add_argument('--product-id', type=int, help='Calculate for specific product only')
    parser.add_argument('--recalculate-all', action='store_true',
                       help='Recalculate all premiums including unchanged ones')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        batch_calculate(
            product_id=args.product_id,
            recalculate_all=args.recalculate_all,
        )


if __name__ == '__main__':
    main()
