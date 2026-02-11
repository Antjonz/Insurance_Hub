# InsuranceHub API Documentation

Base URL: `http://localhost:5000/api`

## Health Check

### GET /api/health
Returns API status.

**Response:**
```json
{
  "status": "healthy",
  "service": "InsuranceHub API"
}
```

---

## Dashboard

### GET /api/dashboard/stats
Returns all dashboard KPIs, chart data, and recent activity.

**Response:**
```json
{
  "kpis": {
    "total_policies": 19,
    "active_claims": 4,
    "monthly_premium": 1083.47,
    "connected_insurers": 5,
    "total_insurers": 6
  },
  "policies_by_insurer": [
    { "name": "Achmea", "value": 5 }
  ],
  "premium_trends": [
    { "month": "Mar 2024", "premium": 950.00 }
  ],
  "policies_by_type": [
    { "type": "property", "count": 7 }
  ],
  "claims_by_status": [
    { "status": "paid", "count": 6 }
  ],
  "recent_activity": [
    {
      "type": "claim",
      "message": "Claim CLM-2024-00001 - paid",
      "detail": "Dakschade door storm...",
      "timestamp": "2024-03-11T00:00:00",
      "status": "paid"
    }
  ]
}
```

---

## Insurers

### GET /api/insurers
List all connected insurers with sync status.

**Response:** Array of insurer objects with `last_sync_status`, `product_count`.

### GET /api/insurers/:id
Get detailed insurer info including recent sync logs.

### POST /api/insurers/:id/sync
Trigger a manual data sync for a specific insurer.

**Response:**
```json
{
  "message": "Sync completed for Achmea",
  "sync_log": {
    "status": "success",
    "records_processed": 5,
    "duration_ms": 1250
  }
}
```

---

## Products

### GET /api/products
List products with filtering, sorting, and pagination.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string | Filter by product type (property, life, health, auto, liability, travel) |
| `insurer_id` | integer | Filter by insurer |
| `status` | string | Filter by status (active, discontinued) |
| `search` | string | Search by name or product code |
| `sort` | string | Sort field (name, base_premium, product_type) |
| `order` | string | Sort direction (asc, desc) |
| `page` | integer | Page number (default: 1) |
| `per_page` | integer | Items per page (default: 20, max: 100) |

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "product_code": "ACH-WOZ-001",
      "name": "Woonhuis Verzekering Basis",
      "product_type": "property",
      "base_premium": 25.50,
      "coverage_amount": 250000,
      "deductible": 250,
      "insurer_name": "Achmea",
      "policy_count": 2,
      "status": "active"
    }
  ],
  "total": 21,
  "page": 1,
  "per_page": 20,
  "pages": 2
}
```

### GET /api/products/:id
Get detailed product information including calculation rules.

### GET /api/products/types
Returns array of available product types: `["property", "life", "health", "auto", "liability", "travel"]`

### POST /api/products/import
Import products from a file upload.

**Request:** `multipart/form-data` with `file` field.
Accepted formats: `.json`, `.xml`, `.xlsx`

**Response:**
```json
{
  "message": "Import completed",
  "results": {
    "created": 3,
    "updated": 1,
    "errors": [
      { "row": 5, "error": "Missing required fields: product_code" }
    ]
  }
}
```

---

## Policies

### GET /api/policies
List policies with filtering and pagination. Same query parameters as products.

### GET /api/policies/:id
Get policy details including associated claims.

### POST /api/policies
Create a new policy.

**Request Body:**
```json
{
  "product_id": 1,
  "customer_name": "Jan de Vries",
  "customer_email": "j.devries@email.nl",
  "customer_phone": "06-12345678",
  "date_of_birth": "1985-03-15",
  "address": "Keizersgracht 123",
  "postcode": "1015 CJ",
  "start_date": "2024-01-15",
  "end_date": "2025-01-15",
  "premium_amount": 28.05,
  "payment_freq": "monthly"
}
```

**Required fields:** `product_id`, `customer_name`, `start_date`

**Response (201):**
```json
{
  "message": "Policy created successfully",
  "policy": {
    "id": 22,
    "policy_number": "POL-2024-00020",
    "customer_name": "Jan de Vries",
    "premium_amount": 28.05,
    "status": "active"
  }
}
```

### POST /api/policies/calculate
Calculate premium based on product rules and customer data.

**Request Body:**
```json
{
  "product_id": 4,
  "date_of_birth": "1992-11-08",
  "postcode": "1012 LN",
  "claim_free_years": 5,
  "smoker": false
}
```

**Response:**
```json
{
  "product": {
    "id": 4,
    "name": "Autoverzekering WA",
    "product_code": "ACH-AUTO-001"
  },
  "base_premium": 35.00,
  "factors": [
    { "name": "Leeftijdsfactor (25-34)", "factor": 1.2 },
    { "name": "Schadevrije jaren (4-7)", "factor": 1.0 }
  ],
  "total_factor": 1.2,
  "calculated_premium": 42.00,
  "coverage_amount": 2500000,
  "deductible": 0
}
```

---

## Reports

### GET /api/reports/premiums
Premium summary grouped by insurer and product type.

**Query Parameters:** `start_date`, `end_date` (optional date filters)

### GET /api/reports/claims
Claims analysis with totals by insurer, status, and category.

### GET /api/reports/products
Product performance comparison with sales and revenue data.

### POST /api/reports/export
Export a report to formatted Excel (.xlsx) file.

**Request Body:**
```json
{
  "report_type": "premiums"
}
```

**Response:** Binary Excel file download.

---

## Sync

### GET /api/sync/status
Returns health status overview for all insurers.

**Response:**
```json
[
  {
    "insurer_id": 1,
    "insurer_name": "Achmea",
    "api_status": "active",
    "health": "green",
    "last_sync": "2024-06-15T10:00:00",
    "last_sync_status": "success",
    "last_sync_records": 5,
    "last_sync_duration_ms": 1250,
    "recent_failures": 0
  }
]
```

Health values: `green` (healthy), `yellow` (warning), `red` (error)

### GET /api/sync/logs
Returns the 50 most recent sync log entries across all insurers.

---

## Mock Insurer APIs

These endpoints simulate real insurer APIs for demonstration:

| Endpoint | Format | Insurer |
|----------|--------|---------|
| `/mock/achmea` | JSON | Achmea |
| `/mock/aegon` | XML | Aegon |
| `/mock/allianz` | JSON | Allianz (different field names) |
| `/mock/asr` | JSON | ASR (different field names) |
| `/mock/nn` | XML | NN Group |
| `/mock/nn-direct` | JSON | Nationale-Nederlanden |

---

## Error Responses

All errors follow this format:
```json
{
  "error": "Description of the error"
}
```

Common HTTP status codes:
- `400` - Bad request (missing fields, validation error)
- `404` - Resource not found
- `500` - Internal server error
