"""Mock insurer API endpoints.

Simulates different insurer APIs returning product data in various formats
(JSON and XML), demonstrating multi-format integration handling.
"""
from flask import Blueprint, jsonify, Response

mock_bp = Blueprint('mock', __name__)


@mock_bp.route('/achmea')
def achmea_api():
    """Achmea mock API - returns JSON product data."""
    return jsonify({
        'insurer': 'Achmea',
        'api_version': '2.1',
        'products': [
            {
                'product_code': 'ACH-WOZ-001',
                'name': 'Woonhuis Verzekering Basis',
                'type': 'property',
                'coverage_amount': 250000,
                'base_premium': 25.50,
                'deductible': 250,
                'status': 'active',
            },
            {
                'product_code': 'ACH-WOZ-002',
                'name': 'Woonhuis Verzekering Plus',
                'type': 'property',
                'coverage_amount': 500000,
                'base_premium': 42.75,
                'deductible': 150,
                'status': 'active',
            },
            {
                'product_code': 'ACH-INB-001',
                'name': 'Inboedelverzekering Standaard',
                'type': 'property',
                'coverage_amount': 75000,
                'base_premium': 15.80,
                'deductible': 100,
                'status': 'active',
            },
            {
                'product_code': 'ACH-AUTO-001',
                'name': 'Autoverzekering WA',
                'type': 'auto',
                'coverage_amount': 2500000,
                'base_premium': 35.00,
                'deductible': 0,
                'status': 'active',
            },
            {
                'product_code': 'ACH-AUTO-002',
                'name': 'Autoverzekering AllRisk',
                'type': 'auto',
                'coverage_amount': 2500000,
                'base_premium': 85.00,
                'deductible': 500,
                'status': 'active',
            },
        ]
    })


@mock_bp.route('/aegon')
def aegon_api():
    """Aegon mock API - returns XML product data."""
    xml_data = '''<?xml version="1.0" encoding="UTF-8"?>
<insurer_response>
    <insurer>Aegon</insurer>
    <api_version>1.5</api_version>
    <products>
        <product>
            <code>AEG-LIFE-001</code>
            <name>Levensverzekering Standaard</name>
            <type>life</type>
            <coverage>100000</coverage>
            <premium>15.75</premium>
            <deductible>0</deductible>
            <status>active</status>
        </product>
        <product>
            <code>AEG-LIFE-002</code>
            <name>Levensverzekering Premium</name>
            <type>life</type>
            <coverage>300000</coverage>
            <premium>45.00</premium>
            <deductible>0</deductible>
            <status>active</status>
        </product>
        <product>
            <code>AEG-HEALTH-001</code>
            <name>Zorgverzekering Basis</name>
            <type>health</type>
            <coverage>0</coverage>
            <premium>128.50</premium>
            <deductible>385</deductible>
            <status>active</status>
        </product>
        <product>
            <code>AEG-REIS-001</code>
            <name>Reisverzekering Wereld</name>
            <type>travel</type>
            <coverage>50000</coverage>
            <premium>6.50</premium>
            <deductible>50</deductible>
            <status>active</status>
        </product>
    </products>
</insurer_response>'''
    return Response(xml_data, mimetype='application/xml')


@mock_bp.route('/allianz')
def allianz_api():
    """Allianz mock API - returns JSON product data."""
    return jsonify({
        'vendor': 'Allianz Nederland',
        'format_version': '3.0',
        'catalog': [
            {
                'sku': 'ALZ-LIAB-001',
                'display_name': 'Aansprakelijkheidsverzekering Particulier',
                'category': 'liability',
                'max_coverage': 1250000,
                'monthly_rate': 4.95,
                'excess': 0,
                'available': True,
            },
            {
                'sku': 'ALZ-PROP-001',
                'display_name': 'Opstalverzekering Comfort',
                'category': 'property',
                'max_coverage': 400000,
                'monthly_rate': 38.90,
                'excess': 200,
                'available': True,
            },
            {
                'sku': 'ALZ-AUTO-001',
                'display_name': 'Motorverzekering WA+',
                'category': 'auto',
                'max_coverage': 2500000,
                'monthly_rate': 55.00,
                'excess': 300,
                'available': True,
            },
        ]
    })


@mock_bp.route('/asr')
def asr_api():
    """ASR mock API - returns JSON product data."""
    return jsonify({
        'provider': 'ASR Nederland',
        'timestamp': '2024-01-15T10:00:00Z',
        'products': [
            {
                'product_id': 'ASR-WOZ-001',
                'title': 'Woonverzekering All-in-One',
                'insurance_type': 'property',
                'sum_insured': 600000,
                'premium_monthly': 52.00,
                'own_risk': 200,
                'active': True,
            },
            {
                'product_id': 'ASR-HEALTH-001',
                'title': 'Zorgverzekering Compleet',
                'insurance_type': 'health',
                'sum_insured': 0,
                'premium_monthly': 165.00,
                'own_risk': 385,
                'active': True,
            },
            {
                'product_id': 'ASR-REIS-001',
                'title': 'Doorlopende Reisverzekering',
                'insurance_type': 'travel',
                'sum_insured': 75000,
                'premium_monthly': 9.75,
                'own_risk': 75,
                'active': True,
            },
            {
                'product_id': 'ASR-LIAB-001',
                'title': 'AVP Gezinspolis',
                'insurance_type': 'liability',
                'sum_insured': 2500000,
                'premium_monthly': 5.50,
                'own_risk': 0,
                'active': True,
            },
        ]
    })


@mock_bp.route('/nn')
def nn_api():
    """NN Group mock API - returns XML (simulating connection issues)."""
    xml_data = '''<?xml version="1.0" encoding="UTF-8"?>
<response status="ok">
    <company>NN Group</company>
    <products>
        <product>
            <code>NNG-LIFE-001</code>
            <name>Overlijdensrisicoverzekering Flex</name>
            <type>life</type>
            <coverage_amount>200000</coverage_amount>
            <monthly_premium>22.00</monthly_premium>
            <deductible>0</deductible>
        </product>
        <product>
            <code>NNG-PENSIOEN-001</code>
            <name>Pensioenplan Individueel</name>
            <type>life</type>
            <coverage_amount>500000</coverage_amount>
            <monthly_premium>150.00</monthly_premium>
            <deductible>0</deductible>
        </product>
    </products>
</response>'''
    return Response(xml_data, mimetype='application/xml')


@mock_bp.route('/nn-direct')
def nn_direct_api():
    """Nationale-Nederlanden mock API - returns JSON."""
    return jsonify({
        'source': 'Nationale-Nederlanden',
        'products': [
            {
                'code': 'NAT-AUTO-001',
                'name': 'Auto Compleet Verzekering',
                'type': 'auto',
                'coverage': 2500000,
                'premium': 72.00,
                'deductible': 250,
            },
            {
                'code': 'NAT-WOZ-001',
                'name': 'Woonpakket Basis',
                'type': 'property',
                'coverage': 300000,
                'premium': 32.00,
                'deductible': 175,
            },
            {
                'code': 'NAT-HEALTH-001',
                'name': 'Zorgverzekering Direct',
                'type': 'health',
                'coverage': 0,
                'premium': 131.00,
                'deductible': 385,
            },
        ]
    })
