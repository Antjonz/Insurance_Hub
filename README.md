# InsuranceHub

A full-stack multi-insurer integration platform that aggregates and manages insurance products from multiple Dutch insurers with different data formats (JSON/XML/Excel), provides real-time premium calculation, and interactive analytics.

## Project Context

This project was built as a technical portfolio piece for an Application Administrator role at a Dutch insurance intermediary. It demonstrates the ability to work with the complex technical landscape of insurance platforms that manage products from 40+ insurers.

### Skills Demonstrated

| Skill | Where It's Used |
|-------|----------------|
| **SQL Database Design** | PostgreSQL schema with 5 normalized tables, complex views, seed data |
| **Complex SQL Queries** | Monthly premium reports, claims analysis, product comparisons, sync monitoring |
| **Python Scripting** | 5 automation scripts for sync, calculation, validation, reporting, import |
| **REST API Development** | Flask API with 15+ endpoints, pagination, filtering, file upload |
| **JSON/XML Parsing** | Multi-format parsers that normalize different insurer data structures |
| **Excel/VBA** | openpyxl reports with charts, formatting, currency; VBA validation macro |
| **React Frontend** | 7-page SPA with charts, forms, data tables, drag-and-drop upload |
| **Docker** | docker-compose with PostgreSQL, Flask backend, React frontend |
| **Data Integration** | Mock insurer APIs returning different formats, sync monitoring |

## Tech Stack

- **Frontend**: React 18, Tailwind CSS, Recharts, React Router, Axios
- **Backend**: Python 3.11, Flask, SQLAlchemy, openpyxl, lxml
- **Database**: PostgreSQL 15
- **Infrastructure**: Docker, docker-compose

## Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/yourusername/Insurance_Hub.git
cd Insurance_Hub

# Start all services
docker-compose up --build

# The application will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000/api
# Database: localhost:5432
```

The database is automatically initialized with the schema and seed data (6 insurers, 21 products, 21 policies, 12 claims).

## Manual Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Database Setup
```bash
# Create database
createdb insurancehub

# Run schema and seed data
psql -d insurancehub -f database/schema.sql
psql -d insurancehub -f database/seed_data.sql
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run the server
python run.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Project Structure

```
Insurance_Hub/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── insurer.py       # Insurer model
│   │   │   ├── product.py       # Product model
│   │   │   ├── policy.py        # Policy model
│   │   │   ├── claim.py         # Claim model
│   │   │   └── sync_log.py      # Sync log model
│   │   └── routes/
│   │       ├── dashboard.py     # KPI and overview endpoints
│   │       ├── insurers.py      # Insurer management
│   │       ├── products.py      # Product catalog & import
│   │       ├── policies.py      # Policy CRUD & premium calc
│   │       ├── reports.py       # Report generation & Excel export
│   │       ├── sync.py          # Sync monitoring
│   │       └── mock_apis.py     # Simulated insurer APIs
│   ├── integrations/
│   │   ├── json_parser.py       # JSON product import
│   │   ├── xml_parser.py        # XML product import
│   │   └── excel_handler.py     # Excel import/export
│   ├── scripts/
│   │   ├── sync_insurer_products.py  # API sync automation
│   │   ├── calculate_premiums.py     # Batch premium calc
│   │   ├── data_validator.py         # Data quality checks
│   │   ├── generate_reports.py       # Excel report generation
│   │   └── import_excel_bulk.py      # Bulk Excel import
│   └── tests/
│       └── test_parsers.py      # Unit tests for parsers
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Dashboard/       # KPI cards, charts, activity feed
│       │   ├── Insurers/        # Insurer list, sync monitor
│       │   ├── Products/        # Product catalog, import wizard
│       │   ├── Policies/        # Policy list, multi-step form
│       │   ├── Reports/         # Report builder with export
│       │   └── Common/          # DataTable, StatusBadge, Spinner
│       └── services/
│           └── api.js           # Centralized API client
├── database/
│   ├── schema.sql               # Full database schema with views
│   └── seed_data.sql            # Realistic sample data
├── sample-data/
│   └── insurers/                # Sample JSON/XML import files
├── docker-compose.yml
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/dashboard/stats` | Dashboard KPIs and chart data |
| GET | `/api/insurers` | List all insurers with sync status |
| POST | `/api/insurers/:id/sync` | Trigger manual sync |
| GET | `/api/products` | List products (filterable, paginated) |
| POST | `/api/products/import` | Import from JSON/XML/Excel file |
| GET | `/api/products/types` | Available product types |
| GET | `/api/policies` | List policies (filterable, paginated) |
| POST | `/api/policies` | Create new policy |
| POST | `/api/policies/calculate` | Calculate premium with rules |
| GET | `/api/reports/premiums` | Premium summary report |
| GET | `/api/reports/claims` | Claims analysis report |
| GET | `/api/reports/products` | Product performance report |
| POST | `/api/reports/export` | Export report to Excel |
| GET | `/api/sync/status` | All insurers sync health |
| GET | `/api/sync/logs` | Recent sync log entries |

## Key Features

### Dashboard
- 4 KPI cards (policies, claims, premium, insurers)
- Pie chart: policies by insurer
- Line chart: premium trends over 12 months
- Bar chart: policies by product type
- Real-time activity feed

### Product Import Wizard
- Drag-and-drop file upload
- Auto-detection of JSON, XML, and Excel formats
- Field normalization across different insurer formats
- Validation results display
- Progress indicator

### Premium Calculator
- Rule-based calculation engine using product-specific JSON rules
- Factors: age (leeftijdsfactor), region (regiofactor), claim-free years (schadevrije jaren), smoker surcharge
- Real-time calculation preview in policy form

### Insurer Sync Monitor
- Connection health indicators (green/yellow/red)
- Last sync timestamp and duration
- Manual sync trigger
- Error tracking (24-hour window)

### Report Builder
- Three report types: Premium, Claims, Products
- Date range filtering
- Preview in sortable data table
- Export to formatted Excel with styling

## Automation Scripts

Run from `backend/` directory:

```bash
# Sync products from all insurer APIs
python scripts/sync_insurer_products.py

# Sync specific insurer
python scripts/sync_insurer_products.py --insurer ACH

# Batch premium recalculation
python scripts/calculate_premiums.py --recalculate-all

# Data quality validation
python scripts/data_validator.py --report validation.json

# Generate Excel reports
python scripts/generate_reports.py --type all --email

# Bulk import from Excel
python scripts/import_excel_bulk.py --file ../sample-data/products.xlsx
```

## Database Design

The schema follows normalized design with these core tables:

- **insurers** - Insurance companies with API connection details
- **products** - Insurance products with JSONB calculation rules
- **policies** - Customer policies (polissen)
- **claims** - Insurance claims (schademeldingen)
- **sync_logs** - API synchronization audit trail

4 SQL views provide pre-built analytics:
- `v_monthly_premiums` - Revenue by insurer per month
- `v_claims_analysis` - Claims approval rates
- `v_product_comparison` - Cross-insurer product comparison
- `v_sync_status` - Real-time sync health dashboard

## Sample Data

The seed data includes realistic Dutch insurance data:
- **6 insurers**: Achmea, Aegon, Allianz, ASR, NN Group, Nationale-Nederlanden
- **21 products** across 6 types: property, life, health, auto, liability, travel
- **21 policies** with fictional Dutch customer data
- **12 claims** in various statuses with Dutch descriptions
- **10 sync logs** showing success, failure, and partial sync scenarios

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

## Future Improvements

- User authentication and role-based access control
- WebSocket-based real-time sync updates
- PDF report generation
- Advanced search with Elasticsearch
- CI/CD pipeline configuration
- Performance monitoring dashboard
- Automated test suite expansion

## License

MIT License - See [LICENSE](LICENSE) for details.
