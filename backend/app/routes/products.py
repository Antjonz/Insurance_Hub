"""Product routes - manage insurance products and imports."""
import os
import json
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Product, Insurer

products_bp = Blueprint('products', __name__)

ALLOWED_EXTENSIONS = {'json', 'xml', 'xlsx', 'xls'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@products_bp.route('/products')
def list_products():
    """List products with optional filters for type, insurer, and status."""
    query = Product.query

    # Apply filters
    product_type = request.args.get('type')
    if product_type:
        query = query.filter(Product.product_type == product_type)

    insurer_id = request.args.get('insurer_id')
    if insurer_id:
        query = query.filter(Product.insurer_id == int(insurer_id))

    status = request.args.get('status')
    if status:
        query = query.filter(Product.status == status)

    search = request.args.get('search')
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.product_code.ilike(f'%{search}%')
            )
        )

    # Sorting
    sort_by = request.args.get('sort', 'name')
    sort_order = request.args.get('order', 'asc')
    sort_column = getattr(Product, sort_by, Product.name)
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)  # Cap at 100 items per page

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
    })


@products_bp.route('/products/<int:product_id>')
def get_product(product_id):
    """Get detailed product information including calculation rules."""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())


@products_bp.route('/products/types')
def get_product_types():
    """Return available product types for filter dropdowns."""
    types = db.session.query(Product.product_type).distinct().all()
    return jsonify([t[0] for t in types])


@products_bp.route('/products/import', methods=['POST'])
def import_products():
    """Import products from uploaded file (JSON, XML, or Excel).

    Demonstrates file upload handling, format detection, and data transformation.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file. Allowed types: JSON, XML, XLSX'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    ext = filename.rsplit('.', 1)[1].lower()
    results = {'created': 0, 'updated': 0, 'errors': []}

    try:
        if ext == 'json':
            from integrations.json_parser import parse_json_products
            products_data = parse_json_products(filepath)
        elif ext == 'xml':
            from integrations.xml_parser import parse_xml_products
            products_data = parse_xml_products(filepath)
        elif ext in ('xlsx', 'xls'):
            from integrations.excel_handler import parse_excel_products
            products_data = parse_excel_products(filepath)
        else:
            return jsonify({'error': f'Unsupported format: {ext}'}), 400

        # Process each product
        for i, pdata in enumerate(products_data):
            try:
                # Validate required fields
                required = ['product_code', 'name', 'product_type', 'base_premium']
                missing = [f for f in required if f not in pdata or not pdata[f]]
                if missing:
                    results['errors'].append({
                        'row': i + 1,
                        'error': f'Missing required fields: {", ".join(missing)}'
                    })
                    continue

                # Check if product already exists
                existing = Product.query.filter_by(
                    product_code=pdata['product_code']
                ).first()

                if existing:
                    # Update existing product
                    existing.name = pdata['name']
                    existing.product_type = pdata['product_type']
                    existing.base_premium = pdata['base_premium']
                    existing.coverage_amount = pdata.get('coverage_amount')
                    existing.deductible = pdata.get('deductible', 0)
                    existing.description = pdata.get('description', '')
                    results['updated'] += 1
                else:
                    # Determine insurer from product code prefix
                    insurer_code = pdata.get('insurer_code', pdata['product_code'].split('-')[0])
                    insurer = Insurer.query.filter_by(code=insurer_code).first()
                    if not insurer:
                        results['errors'].append({
                            'row': i + 1,
                            'error': f'Unknown insurer code: {insurer_code}'
                        })
                        continue

                    product = Product(
                        insurer_id=insurer.id,
                        product_code=pdata['product_code'],
                        name=pdata['name'],
                        product_type=pdata['product_type'],
                        base_premium=pdata['base_premium'],
                        coverage_amount=pdata.get('coverage_amount'),
                        deductible=pdata.get('deductible', 0),
                        description=pdata.get('description', ''),
                        rules_json=pdata.get('rules_json'),
                        status='active',
                    )
                    db.session.add(product)
                    results['created'] += 1

            except Exception as e:
                results['errors'].append({
                    'row': i + 1,
                    'error': str(e)
                })

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to parse file: {str(e)}'}), 400
    finally:
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)

    return jsonify({
        'message': 'Import completed',
        'results': results,
    })
