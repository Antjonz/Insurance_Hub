"""Policy routes - manage customer insurance policies."""
from flask import Blueprint, jsonify, request
from datetime import datetime, date
from app import db
from app.models import Policy, Product

policies_bp = Blueprint('policies', __name__)


@policies_bp.route('/policies')
def list_policies():
    """List policies with pagination and filters."""
    query = Policy.query

    # Filters
    status = request.args.get('status')
    if status:
        query = query.filter(Policy.status == status)

    search = request.args.get('search')
    if search:
        query = query.filter(
            db.or_(
                Policy.customer_name.ilike(f'%{search}%'),
                Policy.policy_number.ilike(f'%{search}%')
            )
        )

    product_id = request.args.get('product_id')
    if product_id:
        query = query.filter(Policy.product_id == int(product_id))

    # Sorting
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')
    sort_column = getattr(Policy, sort_by, Policy.created_at)
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
    })


@policies_bp.route('/policies/<int:policy_id>')
def get_policy(policy_id):
    """Get detailed policy information including claims."""
    policy = Policy.query.get_or_404(policy_id)
    data = policy.to_dict()
    data['claims'] = [c.to_dict() for c in policy.claims.all()]
    return jsonify(data)


@policies_bp.route('/policies', methods=['POST'])
def create_policy():
    """Create a new insurance policy.

    Validates the request data, calculates the final premium based on
    product rules, and generates a unique policy number.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Validate required fields
    required = ['product_id', 'customer_name', 'start_date']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    # Verify product exists
    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Generate policy number
    year = datetime.now().year
    last_policy = Policy.query.filter(
        Policy.policy_number.like(f'POL-{year}-%')
    ).order_by(Policy.policy_number.desc()).first()

    if last_policy:
        last_num = int(last_policy.policy_number.split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    policy_number = f'POL-{year}-{new_num:05d}'

    # Calculate premium (use provided or base)
    premium = data.get('premium_amount', float(product.base_premium))

    try:
        policy = Policy(
            product_id=data['product_id'],
            policy_number=policy_number,
            customer_name=data['customer_name'],
            customer_email=data.get('customer_email'),
            customer_phone=data.get('customer_phone'),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            address=data.get('address'),
            postcode=data.get('postcode'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            premium_amount=premium,
            payment_freq=data.get('payment_freq', 'monthly'),
            status='active',
            notes=data.get('notes'),
        )
        db.session.add(policy)
        db.session.commit()

        return jsonify({
            'message': 'Policy created successfully',
            'policy': policy.to_dict(),
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@policies_bp.route('/policies/calculate', methods=['POST'])
def calculate_premium():
    """Calculate premium based on product rules and customer data.

    Applies insurer-specific calculation rules stored in product.rules_json.
    Factors include age, region, claim-free years, and product-specific modifiers.
    """
    data = request.get_json()
    if not data or 'product_id' not in data:
        return jsonify({'error': 'product_id is required'}), 400

    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    base_premium = float(product.base_premium)
    factors = []
    total_factor = 1.0
    rules = product.rules_json or {}

    # Age factor
    if data.get('date_of_birth') and 'age_factor' in rules:
        birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
        age = (datetime.now() - birth).days // 365
        age_factors = rules['age_factor']

        # Find matching age bracket
        for bracket, factor in age_factors.items():
            if '-' in str(bracket):
                parts = bracket.replace('+', '-999').split('-')
                low, high = int(parts[0]), int(parts[1])
                if low <= age <= high:
                    total_factor *= factor
                    factors.append({
                        'name': f'Leeftijdsfactor ({bracket})',
                        'factor': factor
                    })
                    break

    # Region factor
    if data.get('region') and 'region_factor' in rules:
        region = data['region'].lower()
        if region in rules['region_factor']:
            factor = rules['region_factor'][region]
            total_factor *= factor
            factors.append({
                'name': f'Regiofactor ({region})',
                'factor': factor
            })

    # Claim-free years (schadevrije jaren)
    if data.get('claim_free_years') is not None and 'claim_free_years' in rules:
        cfy = data['claim_free_years']
        cfy_rules = rules['claim_free_years']
        for bracket, factor in cfy_rules.items():
            if '-' in str(bracket):
                parts = bracket.replace('+', '-999').split('-')
                low, high = int(parts[0]), int(parts[1])
                if low <= cfy <= high:
                    total_factor *= factor
                    factors.append({
                        'name': f'Schadevrije jaren ({bracket})',
                        'factor': factor
                    })
                    break
            elif str(bracket) == str(cfy):
                total_factor *= factor
                factors.append({
                    'name': f'Schadevrije jaren ({bracket})',
                    'factor': factor
                })
                break

    # Smoker surcharge
    if data.get('smoker') and 'smoker_surcharge' in rules:
        factor = rules['smoker_surcharge']
        total_factor *= factor
        factors.append({
            'name': 'Rokers toeslag',
            'factor': factor
        })

    calculated_premium = round(base_premium * total_factor, 2)

    return jsonify({
        'product': {
            'id': product.id,
            'name': product.name,
            'product_code': product.product_code,
        },
        'base_premium': base_premium,
        'factors': factors,
        'total_factor': round(total_factor, 4),
        'calculated_premium': calculated_premium,
        'coverage_amount': float(product.coverage_amount) if product.coverage_amount else None,
        'deductible': float(product.deductible) if product.deductible else 0,
    })
