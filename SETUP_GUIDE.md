# InsuranceHub Setup Guide

Step-by-step instructions for setting up InsuranceHub locally or with Docker.

## Option 1: Docker (Recommended)

### Prerequisites
- Docker Desktop installed and running
- Git

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Insurance_Hub.git
   cd Insurance_Hub
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```
   This will:
   - Start PostgreSQL and automatically run schema + seed data
   - Build and start the Flask backend
   - Build and start the React frontend

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/api
   - API Health: http://localhost:5000/api/health

4. **Stop services**
   ```bash
   docker-compose down
   ```
   To also remove the database volume: `docker-compose down -v`

---

## Option 2: Manual Setup

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 15 or higher
- Git

### Step 1: Clone & Configure

```bash
git clone https://github.com/yourusername/Insurance_Hub.git
cd Insurance_Hub
```

### Step 2: Database Setup

```bash
# Create the database
createdb insurancehub

# Or via psql:
psql -c "CREATE DATABASE insurancehub;"

# Create a user (optional, or use your default postgres user)
psql -c "CREATE USER insurancehub WITH PASSWORD 'insurancehub';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE insurancehub TO insurancehub;"

# Run the schema
psql -d insurancehub -f database/schema.sql

# Load seed data
psql -d insurancehub -f database/seed_data.sql
```

### Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials:
# DATABASE_URL=postgresql://insurancehub:insurancehub@localhost:5432/insurancehub

# Start the backend
python run.py
```

The API will be available at http://localhost:5000

### Step 4: Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will open at http://localhost:3000

---

## Environment Variables

### Backend (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://insurancehub:insurancehub@localhost:5432/insurancehub` | PostgreSQL connection string |
| `FLASK_APP` | `app` | Flask application module |
| `FLASK_ENV` | `development` | Environment (development/production) |
| `FLASK_DEBUG` | `1` | Enable debug mode |
| `SECRET_KEY` | `dev-secret-key` | Flask secret key |
| `UPLOAD_FOLDER` | `uploads` | Directory for uploaded files |
| `MAX_CONTENT_LENGTH` | `16777216` | Max upload size (16MB) |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://localhost:5000/api` | Backend API base URL |

---

## Verifying the Setup

1. **Check API health:**
   ```bash
   curl http://localhost:5000/api/health
   ```
   Expected: `{"service":"InsuranceHub API","status":"healthy"}`

2. **Check insurers loaded:**
   ```bash
   curl http://localhost:5000/api/insurers
   ```
   Expected: JSON array with 6 insurers

3. **Check dashboard:**
   Open http://localhost:3000 - you should see the dashboard with KPI cards and charts

4. **Run tests:**
   ```bash
   cd backend
   python -m pytest tests/ -v
   ```

---

## Troubleshooting

### Database connection refused
- Ensure PostgreSQL is running: `pg_isready`
- Check your `DATABASE_URL` in `.env`
- For Docker: wait for the health check to pass before the backend starts

### Frontend can't connect to API
- Ensure the backend is running on port 5000
- Check `REACT_APP_API_URL` is set correctly
- Check browser console for CORS errors

### Import fails with "No module named 'integrations'"
- Ensure you're running from the `backend/` directory
- The scripts add the parent directory to `sys.path` automatically

### Docker build fails
- Ensure Docker Desktop is running
- Try `docker-compose down -v` then `docker-compose up --build`
- Check that ports 3000, 5000, and 5432 are not in use

### "relation does not exist" errors
- The schema hasn't been loaded. Run:
  ```bash
  psql -d insurancehub -f database/schema.sql
  psql -d insurancehub -f database/seed_data.sql
  ```

### Windows-specific issues
- Use `venv\Scripts\activate` instead of `source venv/bin/activate`
- For PostgreSQL, ensure it's added to your PATH
- Use PowerShell or Git Bash for the best experience
