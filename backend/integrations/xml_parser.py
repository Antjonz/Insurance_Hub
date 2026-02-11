"""XML parser for insurance product data.

Handles parsing and validation of XML product files from insurers
that use XML-based APIs (e.g., Aegon, NN Group). Transforms XML
into the standardized product format used by InsuranceHub.
"""
from lxml import etree


# XSD schema for validating insurance product XML
PRODUCT_XSD = '''<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="products">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="product" maxOccurs="unbounded">
                    <xs:complexType>
                        <xs:all>
                            <xs:element name="code" type="xs:string"/>
                            <xs:element name="name" type="xs:string"/>
                            <xs:element name="type" type="xs:string"/>
                            <xs:element name="coverage" type="xs:decimal" minOccurs="0"/>
                            <xs:element name="premium" type="xs:decimal"/>
                            <xs:element name="deductible" type="xs:decimal" minOccurs="0"/>
                            <xs:element name="status" type="xs:string" minOccurs="0"/>
                            <xs:element name="description" type="xs:string" minOccurs="0"/>
                        </xs:all>
                    </xs:complexType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''

# Mapping of XML element names used by different insurers
ELEMENT_MAPPINGS = {
    'product_code': ['code', 'product_code', 'product_id', 'sku'],
    'name': ['name', 'title', 'display_name', 'product_name'],
    'product_type': ['type', 'category', 'insurance_type', 'product_type'],
    'base_premium': ['premium', 'monthly_premium', 'base_premium', 'premium_monthly', 'monthly_rate'],
    'coverage_amount': ['coverage', 'coverage_amount', 'max_coverage', 'sum_insured'],
    'deductible': ['deductible', 'excess', 'own_risk', 'eigen_risico'],
    'description': ['description', 'desc', 'details'],
}


def find_element_text(product_elem, possible_names: list) -> str | None:
    """Find the text content of an element by trying multiple tag names."""
    for name in possible_names:
        elem = product_elem.find(name)
        if elem is not None and elem.text:
            return elem.text.strip()
    return None


def parse_xml_products(filepath: str) -> list:
    """Parse an XML file containing insurance product data.

    Supports various XML structures used by different insurers:
    - Products directly under root
    - Products nested under a <products> element
    - Products under insurer-specific wrapper elements

    Args:
        filepath: Path to the XML file

    Returns:
        List of normalized product dictionaries

    Raises:
        ValueError: If the file cannot be parsed or contains no products
    """
    try:
        tree = etree.parse(filepath)
    except etree.XMLSyntaxError as e:
        raise ValueError(f'Invalid XML: {e}')

    root = tree.getroot()

    # Find product elements - try different structures
    product_elements = []

    # Try: root/products/product
    products_container = root.find('products')
    if products_container is not None:
        product_elements = products_container.findall('product')

    # Try: root/product (direct children)
    if not product_elements:
        product_elements = root.findall('product')

    # Try: any 'product' element anywhere in the tree
    if not product_elements:
        product_elements = root.findall('.//product')

    if not product_elements:
        raise ValueError('No <product> elements found in XML file')

    products = []
    for elem in product_elements:
        product = {}

        for standard_field, possible_names in ELEMENT_MAPPINGS.items():
            value = find_element_text(elem, possible_names)
            if value is not None:
                # Convert numeric fields
                if standard_field in ('base_premium', 'coverage_amount', 'deductible'):
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                product[standard_field] = value

        # Extract insurer code from product_code
        if 'product_code' in product:
            code = product['product_code']
            if '-' in code:
                product['insurer_code'] = code.split('-')[0]

        if product.get('product_code') and product.get('name'):
            products.append(product)

    return products


def validate_xml_against_xsd(filepath: str) -> list:
    """Validate an XML file against the product XSD schema.

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    try:
        schema_doc = etree.fromstring(PRODUCT_XSD.encode())
        schema = etree.XMLSchema(schema_doc)
        doc = etree.parse(filepath)
        schema.validate(doc)
        for error in schema.error_log:
            errors.append(str(error))
    except Exception as e:
        errors.append(str(e))
    return errors
