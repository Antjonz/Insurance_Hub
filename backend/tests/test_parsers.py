"""Unit tests for data format parsers.

Tests the JSON, XML, and Excel parsing modules that handle
product data import from different insurer formats.
"""
import os
import json
import tempfile
import pytest

# Add parent directory for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.json_parser import parse_json_products, normalize_product, validate_product
from integrations.xml_parser import parse_xml_products


class TestJsonParser:
    """Tests for JSON product parser."""

    def test_parse_flat_array(self):
        """Should parse a flat array of products."""
        data = [
            {"product_code": "TEST-001", "name": "Test Product", "type": "auto", "premium": 25.0}
        ]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            products = parse_json_products(path)
            assert len(products) == 1
            assert products[0]['product_code'] == 'TEST-001'
            assert products[0]['name'] == 'Test Product'
        finally:
            os.unlink(path)

    def test_parse_nested_products(self):
        """Should parse products nested under a 'products' key."""
        data = {
            "insurer": "Test",
            "products": [
                {"code": "TST-001", "name": "Product A", "type": "life", "premium": 10.0},
                {"code": "TST-002", "name": "Product B", "type": "health", "premium": 20.0},
            ]
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            products = parse_json_products(path)
            assert len(products) == 2
            assert products[0]['product_code'] == 'TST-001'
            assert products[1]['product_code'] == 'TST-002'
        finally:
            os.unlink(path)

    def test_parse_catalog_key(self):
        """Should find products under 'catalog' key (Allianz format)."""
        data = {
            "vendor": "Allianz",
            "catalog": [
                {"sku": "ALZ-001", "display_name": "Product C", "category": "property", "monthly_rate": 30.0}
            ]
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            products = parse_json_products(path)
            assert len(products) == 1
            assert products[0]['product_code'] == 'ALZ-001'
            assert products[0]['name'] == 'Product C'
            assert products[0]['base_premium'] == 30.0
        finally:
            os.unlink(path)

    def test_normalize_product_field_mapping(self):
        """Should map various field names to standard fields."""
        raw = {
            "sku": "TEST-001",
            "display_name": "Test",
            "category": "auto",
            "monthly_rate": 50.0,
            "max_coverage": 100000,
            "excess": 250,
        }
        result = normalize_product(raw)
        assert result['product_code'] == 'TEST-001'
        assert result['name'] == 'Test'
        assert result['product_type'] == 'auto'
        assert result['base_premium'] == 50.0
        assert result['coverage_amount'] == 100000
        assert result['deductible'] == 250

    def test_validate_valid_product(self):
        """Valid product should pass validation."""
        product = {
            "product_code": "ACH-WOZ-001",
            "name": "Test Product",
            "product_type": "property",
            "base_premium": 25.0,
        }
        errors = validate_product(product)
        assert len(errors) == 0

    def test_validate_missing_fields(self):
        """Product missing required fields should fail validation."""
        product = {"product_code": "TEST-001"}
        errors = validate_product(product)
        assert len(errors) > 0

    def test_empty_file_raises_error(self):
        """Empty JSON file should raise ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            path = f.name
        try:
            with pytest.raises(ValueError):
                parse_json_products(path)
        finally:
            os.unlink(path)


class TestXmlParser:
    """Tests for XML product parser."""

    def test_parse_standard_xml(self):
        """Should parse standard insurance product XML."""
        xml = '''<?xml version="1.0"?>
        <products>
            <product>
                <code>XML-001</code>
                <name>XML Product</name>
                <type>life</type>
                <coverage>100000</coverage>
                <premium>15.75</premium>
            </product>
        </products>'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml)
            path = f.name
        try:
            products = parse_xml_products(path)
            assert len(products) == 1
            assert products[0]['product_code'] == 'XML-001'
            assert products[0]['name'] == 'XML Product'
            assert products[0]['base_premium'] == 15.75
            assert products[0]['coverage_amount'] == 100000
        finally:
            os.unlink(path)

    def test_parse_nested_xml(self):
        """Should parse XML with products under a wrapper element."""
        xml = '''<?xml version="1.0"?>
        <insurer_response>
            <insurer>Test</insurer>
            <products>
                <product>
                    <code>NES-001</code>
                    <name>Nested Product</name>
                    <type>health</type>
                    <premium>50.00</premium>
                </product>
            </products>
        </insurer_response>'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml)
            path = f.name
        try:
            products = parse_xml_products(path)
            assert len(products) == 1
            assert products[0]['product_code'] == 'NES-001'
        finally:
            os.unlink(path)

    def test_parse_multiple_products(self):
        """Should parse multiple products from XML."""
        xml = '''<?xml version="1.0"?>
        <products>
            <product><code>M-001</code><name>P1</name><type>auto</type><premium>10</premium></product>
            <product><code>M-002</code><name>P2</name><type>life</type><premium>20</premium></product>
            <product><code>M-003</code><name>P3</name><type>health</type><premium>30</premium></product>
        </products>'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml)
            path = f.name
        try:
            products = parse_xml_products(path)
            assert len(products) == 3
        finally:
            os.unlink(path)

    def test_invalid_xml_raises_error(self):
        """Invalid XML should raise ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('not valid xml <><>')
            path = f.name
        try:
            with pytest.raises(ValueError):
                parse_xml_products(path)
        finally:
            os.unlink(path)

    def test_insurer_code_extraction(self):
        """Should extract insurer code from product code."""
        xml = '''<?xml version="1.0"?>
        <products>
            <product>
                <code>ACH-WOZ-001</code>
                <name>Test</name>
                <type>property</type>
                <premium>25</premium>
            </product>
        </products>'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml)
            path = f.name
        try:
            products = parse_xml_products(path)
            assert products[0].get('insurer_code') == 'ACH'
        finally:
            os.unlink(path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
