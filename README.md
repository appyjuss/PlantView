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
- Start PostgreSQL and Redis containers
- Initialize database
- Run tests

### 2. Start Backend
```bash
python -m backend.main
```
Backend runs on `http://localhost:5000`

### 3. Start Frontend
```bash
cd plantViewFrontend
npm install
npm run dev
```
Frontend runs on `http://localhost:5173`

---

## Manual Setup (If Automated Setup Fails)

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and update values:
```bash
cp .env.example .env
```

### 3. Start Services
```bash
docker-compose up -d
```

### 4. Initialize Database
```bash
flask --app backend.main init-db
```

### 5. Create Admin User (Optional)
```bash
flask --app backend.main create-admin
```

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
├── docker-compose.yml      # Docker services
├── setup.py                # Automated setup script
└── .env.example            # Environment template
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
All endpoints require `Authorization: Bearer <token>` header.

---

## Database

### Connection Info
- **Host**: localhost
- **Port**: 5432
- **User**: postgres
- **Password**: password
- **Database**: plantview_db

### Useful Commands
```bash
# Connect to database
docker exec -it plantview-postgres psql -U postgres -d plantview_db

# View tables
\dt

# View users
SELECT * FROM users;
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
python -m backend.main

# Initialize database
flask --app backend.main init-db

# Create admin user
flask --app backend.main create-admin

# List all users
flask --app backend.main list-users
```

### Frontend Commands
```bash
cd plantViewFrontend

# Install dependencies
npm install

# Start dev server
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
