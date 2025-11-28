# PlantView 🌱

AI-powered plant disease detection web application with React frontend and Flask backend.

---

## Quick Start

### Prerequisites
- Python 3.10+
- Docker Desktop
- Node.js 18+ (for frontend)

### 1. Clone & Setup
```bash
git clone https://github.com/appyjuss/PlantView.git
cd PlantView
python setup.py
```

The setup script will:
- Install Python dependencies
- Create `.env` file
# PlantView 🌱

AI-powered plant disease detection web application with React frontend and Flask backend.

---

## Quick Start (Supabase-backed)

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)

### 1. Clone & install
```bash
git clone https://github.com/appyjuss/PlantView.git
cd PlantView
python -m pip install -r backend/requirements.txt
```

### 2. Configure environment (Supabase)
1. Create a Supabase project at https://app.supabase.com and copy the `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY`.
2. Copy `.env.example` to `backend/.env` and fill in the values (do not commit `.env`).

### 3. Initialize DB & run backend
```pwsh
# Activate your Python venv, then:
python -m flask --app backend.main db migrate -m "initial schema"
python -m flask --app backend.main db upgrade
python -m flask --app backend.main run
```

Backend runs on `http://localhost:5000`

### 4. Start Frontend
```bash
cd plantViewFrontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

---

## Project Structure

```
PlantView/
├── backend/                 # Flask backend
│   ├── core/               # Core logic (auth, models, storage)
│   ├── routes/             # API routes
│   ├── tests/              # Test suite
│   ├── app.py              # Flask app factory
│   └── main.py             # Entry point
├── plantViewFrontend/      # React frontend
│   ├── src/
│   │   ├── pages/          # Page components
│   │   ├── components/     # Reusable components
│   │   ├── context/        # React context (auth)
│   │   └── lib/            # API client, utilities
│   └── vite.config.ts
├── migrations/             # Alembic migrations
├── .env.example            # Environment template
```

---

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/verify` - Verify token
- `POST /api/auth/logout` - Logout

### Protected Routes
All endpoints require `Authorization: Bearer <token>` header (unless you use cookies after server-side changes).

---

## Database

This project uses Supabase (hosted Postgres) as the primary database. After creating a Supabase project, copy your project's connection string into `backend/.env` as `DATABASE_URL`.

### Verify tables
Use the Supabase SQL editor to run:
```sql
SELECT tablename
FROM pg_catalog.pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```

---

## Testing

### Run All Tests
```bash
pytest backend/tests -v
```

### Run Specific Test File
```bash
pytest backend/tests/test_auth_db.py -v
```

### Run with Coverage
```bash
pytest backend/tests --cov=backend --cov-report=html
```

---

## Development

### Backend Commands
```bash
# Run development server
python -m flask --app backend.main run
```

npm run dev

# Build for production
npm run build
```

### Docker Commands
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart postgres
```

---

## Troubleshooting

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Redis Connection Error
```bash
# Check if Redis is running
docker ps | grep redis

# Test Redis connection
docker exec -it plantview-redis redis-cli ping
```

### Port Already in Use
```bash
# Find process using port (Windows)
netstat -ano | findstr :5000

# Kill process (Windows PowerShell)
Stop-Process -Id <PID> -Force

# Or change port in .env
PORT=5001
```

### Migration Issues
```bash
# Reset database
flask --app backend.main init-db

# If that fails, restart from scratch
docker-compose down -v
docker-compose up -d
flask --app backend.main init-db
```

---

## Tech Stack

**Backend**
- Flask 3.1.2
- SQLAlchemy (ORM)
- PostgreSQL 16
- Redis (rate limiting)
- JWT authentication
- Bcrypt (password hashing)

**Frontend**
- React 18
- TypeScript
- Vite
- React Router
- Axios

**DevOps**
- Docker & Docker Compose
- Pytest (testing)
- Flask-Migrate (migrations)

---

## Project Goals

* Showcase how AI can be applied in agriculture
* Help farmers and researchers monitor crop health
* Explore the potential of CNNs in image classification

---

## Future Improvements

* Expand dataset for more plant species and diseases
* Add visualization for prediction confidence levels
* Implement ML model inference endpoints
* Deploy to production with Supabase/Railway

---

## Documentation

For detailed documentation, see:
- [`GETTING_STARTED.md`](GETTING_STARTED.md) - Quick start guide
- [`docs/DATABASE_MIGRATION.md`](docs/DATABASE_MIGRATION.md) - Database setup guide
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - System architecture
- [`docs/AUTH_SETUP.md`](docs/AUTH_SETUP.md) - Authentication details

---

## License

MIT
