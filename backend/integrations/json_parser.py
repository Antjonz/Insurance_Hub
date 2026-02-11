"""JSON parser for insurance product data.

Handles parsing and validation of JSON product files from various insurers.
Each insurer may use slightly different JSON structures, so this module
normalizes them into a standard format for database import.
"""
import json
from jsonschema import validate, ValidationError

# Standard schema that imported JSON products should conform to
PRODUCT_SCHEMA = {
    "type": "object",
    "required": ["product_code", "name", "product_type", "base_premium"],
    "properties": {
        "product_code": {"type": "string", "pattern": "^[A-Z]{2,4}-[A-Z]+-\\d{3}$"},
        "name": {"type": "string", "minLength": 3},
        "product_type": {
            "type": "string",
            "enum": ["property", "life", "health", "auto", "liability", "travel"]
        },
        "base_premium": {"type": "number", "minimum": 0},
        "coverage_amount": {"type": "number", "minimum": 0},
        "deductible": {"type": "number", "minimum": 0},
        "description": {"type": "string"},
        "insurer_code": {"type": "string"},
    }
}

# Field mapping for different insurer JSON formats
FIELD_MAPPINGS = {
    'default': {
        'product_code': ['product_code', 'code', 'sku', 'product_id'],
        'name': ['name', 'display_name', 'title', 'product_name'],
        'product_type': ['product_type', 'type', 'category', 'insurance_type'],
        'base_premium': ['base_premium', 'premium', 'monthly_rate', 'premium_monthly'],
        'coverage_amount': ['coverage_amount', 'coverage', 'max_coverage', 'sum_insured'],
        'deductible': ['deductible', 'excess', 'own_risk', 'eigen_risico'],
        'description': ['description', 'desc', 'details'],
    }
}


def normalize_product(raw: dict) -> dict:
    """Normalize a product dict from any insurer format to our standard format.

    Handles different field names used by different insurers by trying
    multiple possible field names for each standard field.
    """
    mapping = FIELD_MAPPINGS['default']
    normalized = {}

    for standard_field, possible_names in mapping.items():
        for name in possible_names:
            if name in raw:
                normalized[standard_field] = raw[name]
                break

    # Extract insurer code from product_code if not provided
    if 'product_code' in normalized and 'insurer_code' not in normalized:
        code = normalized['product_code']
        if '-' in code:
            normalized['insurer_code'] = code.split('-')[0]

    return normalized


def parse_json_products(filepath: str) -> list:
    """Parse a JSON file containing insurance product data.

    Supports both flat arrays and nested structures (products under
    different key names like 'products', 'catalog', 'items').

    Args:
        filepath: Path to the JSON file

    Returns:
        List of normalized product dictionaries

    Raises:
        ValueError: If the file cannot be parsed or contains no products
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle different JSON structures
    products_raw = []

    if isinstance(data, list):
        # Direct array of products
        products_raw = data
    elif isinstance(data, dict):
        # Look for products under common key names
        for key in ['products', 'catalog', 'items', 'data']:
            if key in data and isinstance(data[key], list):
                products_raw = data[key]
                break

        # If still empty, try the dict itself as a single product
        if not products_raw and 'product_code' in data or 'code' in data:
            products_raw = [data]

    if not products_raw:
        raise ValueError('No products found in JSON file')

    # Normalize each product
    products = []
    for raw in products_raw:
        normalized = normalize_product(raw)
        if normalized.get('product_code') and normalized.get('name'):
            products.append(normalized)

    return products


def validate_product(product: dict) -> list:
    """Validate a normalized product dict against the schema.

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    try:
        validate(instance=product, schema=PRODUCT_SCHEMA)
    except ValidationError as e:
        errors.append(str(e.message))
    return errors
