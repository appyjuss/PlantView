# PlantView - Self-Hosted Authentication System

## 🔐 Security Overview

This implementation provides **production-ready authentication** without third-party dependencies:

- ✅ **JWT Tokens** - Secure token-based authentication
- ✅ **Password Hashing** - Industry-standard PBKDF2 hashing
- ✅ **Expiring Tokens** - Tokens expire after 24 hours
- ✅ **Protected Routes** - API endpoints require valid tokens
- ✅ **No Third-Party** - All auth handled by your own backend

## 🚀 Quick Start

### Option 1: Automated (Windows)
```bash
cd c:\Users\zenit\Documents\PlantView
start-dev.bat
```

This will:
1. Start Flask backend on `http://localhost:5000`
2. Start React dev server on `http://localhost:5173`
3. Open browser to frontend

### Option 2: Manual

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd plantViewFrontend
npm run dev
```

Then open `http://localhost:5173` in browser.

## 📝 Test Account

After starting the app:
1. Go to **Sign Up** page
2. Register with any email and password (min 6 chars)
3. You'll be redirected to **Dashboard**

## 🔑 How It Works

### Registration
```
User enters email + password
        ↓
Frontend sends to /api/auth/signup
        ↓
Backend hashes password & stores user
        ↓
Backend generates JWT token
        ↓
Token returned to frontend
        ↓
Token stored in localStorage
```

### Login
```
User enters credentials
        ↓
Frontend sends to /api/auth/login
        ↓
Backend verifies password hash
        ↓
Backend generates JWT token
        ↓
Token stored in browser
```

### Protected API Calls
```
Frontend requests /API/upload with Authorization header
        ↓
Backend verifies JWT signature
        ↓
If valid → process request
If invalid → return 401 error
```

## 📁 File Structure

### Backend Changes
```
backend/
├── main.py                    ← Auth endpoints added
├── requirements.txt           ← PyJWT added
└── users.json                ← Created on first signup
```

### Frontend Changes
```
plantViewFrontend/src/
├── .env.local                ← API_URL config
├── lib/
│   ├── api.ts               ← NEW: API client with auth
│   └── supabase.ts          ← (removed from use)
├── context/
│   └── AuthContext.tsx      ← Updated for self-hosted auth
├── pages/
│   ├── Login.tsx            ← Updated with error handling
│   └── SignUp.tsx           ← Updated for backend
└── components/dashboard/
    └── UploadForm.tsx       ← Updated to use real API
```

## 🔌 API Endpoints

### Sign Up
```
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response (201):
```
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "1",
    "email": "user@example.com"
  }
}
```

### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response (200):
```
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "1",
    "email": "user@example.com"
  }
}
```

### Verify Token
```
GET /api/auth/verify
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response (200):
```
{
  "user": {
    "id": "1",
    "email": "user@example.com"
  }
}
```

### Upload File (requires auth)
```
POST /API/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image file>

Response: 302 Redirect to /uploads/<filename>
```

## 🔒 Security Features

| Feature | Details |
|---------|---------|
| **Passwords** | Hashed with PBKDF2 (werkzeug.security) |
| **Tokens** | JWT with HS256 signature |
| **Expiration** | 24 hours |
| **Storage** | localStorage (frontend), users.json (backend) |
| **API Protection** | Bearer token in Authorization header |
| **Email Validation** | Required, normalized to lowercase |
| **Password Strength** | Minimum 6 characters |

## 🛠️ Configuration

### Change Secret Key (Recommended for Production)

**Windows PowerShell:**
```powershell
$env:SECRET_KEY = "your-new-secret-key-here"
python main.py
```

**Windows CMD:**
```cmd
set SECRET_KEY=your-new-secret-key-here
python main.py
```

**Generate Strong Key:**
```python
import secrets
print(secrets.token_hex(32))
```

### Change Token Expiration

Edit `backend/main.py`:
```python
JWT_EXPIRATION_HOURS = 24  # Change this
```

### Change Backend URL

Edit `plantViewFrontend/.env.local`:
```
VITE_API_URL=http://your-backend-url:5000
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Missing authorization token" | Check browser DevTools → Storage → Local Storage → authToken |
| "Invalid or expired token" | Log out and log back in. Tokens expire after 24 hours. |
| "User already exists" | Use a different email or check if account exists |
| "Invalid email or password" | Verify email/password are correct (case-sensitive) |
| Backend not responding | Ensure Flask is running on port 5000 |
| CORS errors | Ensure `VITE_API_URL` in .env.local matches backend |

## 📚 Frontend Usage

### In Components

```typescript
import { useAuth } from '../context/AuthContext';

export default function MyComponent() {
  const { user, loading, logout } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>Not logged in</div>;

  return (
    <div>
      Welcome {user.email}!
      <button onClick={logout}>Sign out</button>
    </div>
  );
}
```

### API Calls

```typescript
import { apiCall, getToken } from '../lib/api';

// Authenticated request
const response = await apiCall('/api/some-endpoint', {
  method: 'GET',
  requiresAuth: true
});

// Manual token access
const token = getToken();
```

## 🚀 Next Steps

1. ✅ Test sign up and login flow
2. ✅ Verify tokens in Network tab (DevTools)
3. ⬜ Replace `users.json` with SQLite/PostgreSQL
4. ⬜ Add rate limiting on auth endpoints
5. ⬜ Implement password reset functionality
6. ⬜ Add email verification
7. ⬜ Set up production deployment

## 📖 Documentation

See **SELF_HOSTED_AUTH.md** for detailed technical documentation.

## 🔄 Migration from Supabase

If you previously had Supabase set up:
1. Old Supabase files can be deleted:
   - ~~`src/lib/supabase.ts`~~ (now using `src/lib/api.ts`)
2. All authentication is now self-hosted
3. No changes needed to frontend - it uses the same `AuthContext` interface

## ⚖️ License

This authentication system is part of the PlantView project.
