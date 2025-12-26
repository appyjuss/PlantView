# PlantView 🌱

AI-powered plant disease detection web application with React frontend and Flask backend.

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)
- Supabase account (https://app.supabase.com)

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/appyjuss/PlantView.git
cd PlantView
```

**Backend:**
```pwsh
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

**Frontend:**
```bash
cd plantViewFrontend
npm install
cd ..
```

### 2. Configure Environment (Supabase)

1. Create a Supabase project at https://app.supabase.com
2. Copy your project credentials (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`)
3. Create `backend/.env` with:
```env
DATABASE_URL=postgresql://[user]:[password]@[host]:5432/[database]
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
JWT_SECRET=your_secret_key_here
```

### 3. Initialize Database

```pwsh
cd backend
python -m flask --app main db upgrade
```

### 4. Run Backend & Frontend

**Terminal 1 - Backend:**
```pwsh
# From backend directory (with venv activated)
python -m flask --app main run
# Runs on http://localhost:5000
```

**Terminal 2 - Frontend:**
```bash
cd plantViewFrontend
npm run dev
# Runs on http://localhost:5173
```

---

## Project Structure

```
PlantView/
├── backend/                      # Flask backend
│   ├── core/                    # Core logic (auth, models, storage, schemas)
│   │   ├── auth.py              # JWT authentication
│   │   ├── models.py            # SQLAlchemy models (User, Detection, Upload)
│   │   ├── storage.py           # Supabase file operations
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   └── utils.py             # Helper utilities
│   ├── routes/                  # API route blueprints
│   │   ├── auth_routes.py       # /api/auth/* endpoints
│   │   ├── detect_routes.py     # /api/detect endpoint (inference)
│   │   └── upload_routes.py     # /api/upload/* endpoints
│   ├── tests/                   # Pytest test suite
│   │   ├── conftest.py          # Test fixtures and mocks
│   │   ├── test_auth_db.py      # Auth & database tests
│   │   ├── test_auth_flow.py    # Full auth flow tests
│   │   ├── test_upload.py       # Upload endpoint tests
│   │   └── test_upload_upsert.py# Upload/upsert logic tests
│   ├── app.py                   # Flask application factory
│   ├── main.py                  # Entry point
│   ├── prediction.py            # ML model inference
│   ├── requirements.txt          # Python dependencies
│   └── run-flask.ps1            # PowerShell run script
├── plantViewFrontend/            # React frontend
│   ├── src/
│   │   ├── pages/               # Page components
│   │   │   ├── Landing.tsx      # Public landing page
│   │   │   ├── Dashboard.tsx    # Main app (protected)
│   │   │   ├── Login.tsx        # Login page
│   │   │   └── SignUp.tsx       # Registration page
│   │   ├── components/          # Reusable components
│   │   │   ├── dashboard/       # Dashboard sub-components
│   │   │   ├── landing/         # Landing page sections
│   │   │   └── ui/              # UI library (button, card)
│   │   ├── context/             # React context
│   │   │   └── AuthContext.tsx  # Auth state management
│   │   ├── lib/                 # Libraries & utilities
│   │   │   ├── api.ts           # Axios client with JWT injection
│   │   │   ├── detections.ts    # Detection helpers
│   │   │   └── utils.ts         # General utilities
│   │   ├── App.tsx              # Main router (BrowserRouter)
│   │   └── main.tsx             # Entry point
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
├── migrations/                   # Alembic database migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│       └── 33615b6b0d60_initial_schema.py
├── models/                       # ML model artifacts
│   ├── resnet50_model.pth       # Fine-tuned ResNet50 weights
│   └── labels_mapping.json      # Disease class labels (38 classes)
├── .env.example                  # Environment template
├── package.json                  # Root-level scripts
└── pytest.ini                   # Pytest configuration
```

---

## API Endpoints

### Authentication Routes (`/api/auth`)
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/refresh` - Refresh expired JWT
- `GET /api/auth/verify` - Verify token validity
- `POST /api/auth/logout` - Logout user

### Detection Routes (`/api/detect`)
- `POST /api/detect` - Send image for disease detection (requires auth)
  - Returns: `{confidence: float, disease_class: string, disease_label: string, timestamp: string}`

### Upload Routes (`/api/upload`)
- `POST /api/upload` - Upload image and get signed URL (requires auth)
- `GET /api/upload/history` - Get user's upload history (requires auth)

### Authentication
All protected endpoints require header:
```
Authorization: Bearer <JWT_TOKEN>
```

---

## Database

**Database Engine:** Supabase (Managed PostgreSQL)

**Initialization:**
```pwsh
python -m flask --app main db upgrade
```

**Tables:**
- `users` - User accounts with hashed passwords
- `uploads` - Image metadata and signed URLs
- `detections` - ML inference results linked to uploads

**Verify Connection:**
Use Supabase dashboard SQL editor or psql CLI to test connection.

---

## Testing

**Run All Tests:**
```bash
pytest backend/tests -v
```

**Run Specific Test File:**
```bash
pytest backend/tests/test_auth_db.py -v
```

**Run with Coverage:**
```bash
pytest backend/tests --cov=backend --cov-report=html
```

**Test Categories:**
- `test_auth_db.py` - User registration, login, token refresh
- `test_auth_flow.py` - Full authentication flow with protected routes
- `test_upload.py` - Image upload to Supabase
- `test_upload_upsert.py` - Upload metadata persistence and updates

**Note:** Tests use mocked Supabase interactions; actual file uploads are not tested against real storage.

---

## Development

### Backend Commands

**Run Development Server:**
```pwsh
cd backend
python -m flask --app main run
# Runs on http://localhost:5000
```

**Run with Auto-reload:**
```pwsh
python -m flask --app main run --reload
```

**Database Migration (if schema changed):**
```pwsh
# Create new migration
python -m flask --app main db migrate -m "your message"

# Apply migration
python -m flask --app main db upgrade
```

### Frontend Commands

**Run Development Server:**
```bash
cd plantViewFrontend
npm run dev
# Runs on http://localhost:5173
```

**Build for Production:**
```bash
npm run build
```

**Preview Production Build:**
```bash
npm run preview
```

---

## Troubleshooting

### Backend Won't Start
```pwsh
# Ensure venv is activated
.\venv\Scripts\Activate.ps1

# Install missing dependencies
pip install -r backend/requirements.txt

# Check for port conflicts (port 5000)
netstat -ano | findstr :5000
```

### Database Connection Error
- Verify `DATABASE_URL` in `backend/.env` is correct
- Check Supabase project is active and running
- Ensure `.env` file has correct credentials from Supabase dashboard

### Frontend Build Error
```bash
cd plantViewFrontend
rm -r node_modules package-lock.json
npm install
npm run dev
```

### Port Already in Use
```pwsh
# Find process using port
netstat -ano | findstr :5000

# Kill process (replace <PID> with actual process ID)
Stop-Process -Id <PID> -Force

# Or use different port
python -m flask --app main run --port 5001
```

---

## Tech Stack

**Backend**
- Flask 3.1.2 - Web framework
- SQLAlchemy - ORM
- Alembic - Database migrations
- PyJWT - JWT token handling
- Bcrypt - Password hashing
- Supabase Client - PostgreSQL & object storage
- Python 3.10+

**Frontend**
- React 18 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- React Router - Navigation (multi-page routing)
- Axios - HTTP client
- Tailwind CSS - Styling
- Node.js 18+

**ML Model**
- ResNet50 (transfer learning) - Disease classification backbone
- 38 plant disease classes

**Infrastructure**
- Supabase - PostgreSQL database + object storage
- Pytest - Testing framework

---

## Project Goals

* Apply AI to agriculture for practical crop health monitoring
* Help farmers and researchers identify plant diseases early
* Demonstrate CNN effectiveness in agricultural image classification

---

## Future Improvements

* Expand model to support more plant species and disease variants
* Add real-time prediction confidence visualization
* Implement batch detection API for bulk image analysis
* Deploy to production with cloud infrastructure
* Mobile app support (React Native)

---

## License

MIT
