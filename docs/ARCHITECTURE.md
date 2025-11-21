# Architecture Diagrams
# Supabase Storage Integration

All image uploads are stored in a Supabase bucket named `uploads`. The bucket is configured for private access. Backend endpoints authenticate with Supabase using environment variables for keys and secrets. Uploaded files are only accessible to authenticated users.

# Environment Variable Management

Sensitive keys (Supabase service key, JWT secret, etc.) are managed via environment variables. Separate `.env` files are used for staging and production environments. The backend loads these variables at startup and never hardcodes secrets.

# CI/CD Pipeline

Automated CI/CD is set up using GitHub Actions. The pipeline runs linting, pytest-based tests, and deploys to staging or production based on branch or tag. Rollbacks and monitoring are included for reliability.

# Automated Testing

All backend features (auth, upload, detection) are covered by pytest-based tests in the `tests/` directory. Tests run automatically in CI/CD before deployment.

## Authentication Flow

### Sign Up Process
```
┌─────────────────┐
│   User enters   │
│ email + password│
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Frontend Form  │
│  /signup page   │
└────────┬────────┘
         │
         ├─→ POST /api/auth/signup
         │
         ↓
┌─────────────────────┐
│  Backend (Flask)    │
│  - Validate input   │
│  - Hash password    │
│  - Store user       │
│  - Create JWT token │
└────────┬────────────┘
         │
         ├─→ Return { token, user }
         │
         ↓
┌──────────────────────┐
│   Frontend           │
│  - Store token in    │
│    localStorage      │
│  - Update user state │
│  - Redirect /dash    │
└──────────────────────┘
```

### Login Process
```
┌─────────────────┐
│   User enters   │
│ email + password│
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Frontend Form  │
│  /login page    │
└────────┬────────┘
         │
         ├─→ POST /api/auth/login
         │
         ↓
┌──────────────────────┐
│  Backend (Flask)     │
│  - Find user by email│
│  - Verify password   │
│  - Create JWT token  │
└────────┬─────────────┘
         │
         ├─→ Return { token, user }
         │
         ↓
┌──────────────────────┐
│   Frontend           │
│  - Store token       │
│  - Update user state │
│  - Redirect /dash    │
└──────────────────────┘
```

### Protected API Call
```
┌──────────────────┐
│  React Component │
│  (Dashboard)     │
└────────┬─────────┘
         │
         ├─→ POST /API/upload
         │   with file + token
         │
         ↓
┌─────────────────────────────┐
│  Request Headers            │
│  Authorization: Bearer <JWT>│
└────────┬────────────────────┘
         │
         ↓
┌──────────────────────────────┐
│  Backend @require_auth check │
│  - Extract token from header │
│  - Verify signature          │
│  - Check expiration          │
└────────┬─────────────────────┘
         │
      Valid?
      /  \
    YES   NO
    /      \
   ↓        ↓
PROCESS   REJECT
REQUEST   (401)
```

## System Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    PlantView System                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────┐  ┌──────────────────────┐  │
│  │   React Frontend         │  │  Flask Backend       │  │
│  │   localhost:5173         │  │  localhost:5000      │  │
│  │                          │  │                      │  │
│  │  ┌────────────────────┐  │  │  ┌────────────────┐  │  │
│  │  │ Login/SignUp Pages │  │  │  │ Auth Endpoints │  │  │
│  │  │ /login             │  │  │  │ /api/auth/*    │  │  │
│  │  │ /signup            │  │  │  │                │  │  │
│  │  └────────────────────┘  │  │  └────────────────┘  │  │
│  │           ↕              │  │         ↕            │  │
│  │  ┌────────────────────┐  │  │  ┌────────────────┐  │  │
│  │  │ AuthContext        │  │  │  │ Token Verify   │  │  │
│  │  │ - user state       │  │  │  │ @require_auth  │  │  │
│  │  │ - auth functions   │  │  │  │                │  │  │
│  │  └────────────────────┘  │  │  └────────────────┘  │  │
│  │           ↕              │  │         ↕            │  │
│  │  ┌────────────────────┐  │  │  ┌────────────────┐  │  │
│  │  │ Dashboard          │  │  │  │ Upload Handler │  │  │
│  │  │ - UploadForm       │◄─┼─┼─┤ /API/upload    │  │  │
│  │  │ - HistoryList      │  │  │  │                │  │  │
│  │  │ - DetectionCard    │  │  │  └────────────────┘  │  │
│  │  └────────────────────┘  │  │         ↕            │  │
│  │                          │  │  ┌────────────────┐  │  │
│  │  ┌────────────────────┐  │  │  │ User Database  │  │  │
│  │  │ localStorage       │  │  │  │ users.json     │  │  │
│  │  │ - authToken        │  │  │  │ (password hash)│  │  │
│  │  │ - user data        │  │  │  └────────────────┘  │  │
│  │  └────────────────────┘  │  │                      │  │
│  └──────────────────────────┘  └──────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              Network Requests (HTTP)                 │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

## Data Flow: File Upload

```
User selects image
        ↓
Frontend validates file
        ↓
Create FormData with file + get token
        ↓
POST /API/upload
  Authorization: Bearer <JWT>
  Content-Type: multipart/form-data
        ↓
Backend @require_auth decorator
        ↓
Verify JWT signature and expiry
        ↓
Is token valid?
    /    \
  YES    NO
  /       \
 ↓         ↓
Verify  Return 401
file    Error
 ↓
Valid file?
  /    \
YES    NO
 /      \
↓       ↓
Save  Return
file  Error
 ↓
Return file path
        ↓
Frontend updates UI
with uploaded file
```

## Token Lifecycle

```
┌─────────────────────────────────────────┐
│      JWT Token Lifecycle                │
├─────────────────────────────────────────┤
│                                         │
│  Created                                │
│  ├─ Payload: { user_id, email }        │
│  ├─ Added: iat (issued at time)        │
│  ├─ Added: exp (expires at time)       │
│  ├─ Signed with SECRET_KEY              │
│  └─ Returned to frontend                │
│     (typically ~400 chars)              │
│                                         │
│  Stored                                 │
│  ├─ Browser localStorage                │
│  ├─ Key: 'authToken'                    │
│  ├─ Persists across page reload        │
│  └─ Survives browser restart            │
│                                         │
│  Usage (24 hours)                       │
│  ├─ Sent in Authorization header        │
│  ├─ Format: Bearer <token>              │
│  ├─ Every API request to protected      │
│  │   endpoints includes it              │
│  └─ Backend validates signature/exp     │
│                                         │
│  Expires                                │
│  ├─ After 24 hours                      │
│  ├─ Backend returns 401 Unauthorized    │
│  ├─ Frontend should redirect to /login  │
│  └─ Token removed from storage          │
│                                         │
└─────────────────────────────────────────┘

         ┌──────────────────┐
         │    Logout        │
         ├──────────────────┤
         │ User clicks out  │
         │       ↓          │
         │ Clear token from │
         │  localStorage    │
         │       ↓          │
         │ Redirect /login  │
         │       ↓          │
         │ Token invalid on │
         │  next request    │
         └──────────────────┘
```

## Security Layers

```
┌─────────────────────────────────────────────────────────┐
│              Security Implementation                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Layer 1: Password Hashing                             │
│  ├─ Input: plain password                              │
│  ├─ Process: PBKDF2 with SHA-256                       │
│  ├─ Output: hash (never the plain password)            │
│  └─ Storage: users.json (hash only)                    │
│                                                         │
│  Layer 2: JWT Signing                                  │
│  ├─ Input: user data                                   │
│  ├─ Process: HMAC with HS256                           │
│  ├─ Secret: SECRET_KEY environment variable           │
│  └─ Output: signed token (verifiable)                  │
│                                                         │
│  Layer 3: Token Expiration                             │
│  ├─ Issued: Now                                        │
│  ├─ Expires: Now + 24 hours                            │
│  ├─ Check: Backend verifies exp claim                  │
│  └─ Reject: If expired                                 │
│                                                         │
│  Layer 4: Authorization Header                         │
│  ├─ Format: "Bearer <token>"                           │
│  ├─ Sent: HTTPS only (production)                      │
│  ├─ Verified: Signature checked                        │
│  └─ Reject: If missing/invalid                         │
│                                                         │
│  Layer 5: Protected Routes                             │
│  ├─ @require_auth decorator                            │
│  ├─ Checks: Token present & valid                      │
│  ├─ Sets: request.user_id & request.user_email         │
│  └─ Reject: 401 if unauthorized                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## File Organization

```
PlantView/
├── backend/
│   ├── main.py                 ← Auth endpoints + logic
│   ├── requirements.txt        ← PyJWT dependency
│   └── users.json              ← User database (auto-created)
│
├── plantViewFrontend/
│   ├── .env.local              ← VITE_API_URL config
│   └── src/
│       ├── lib/
│       │   ├── api.ts          ← NEW: Auth API client
│       │   └── supabase.ts     ← (deprecated, kept for ref)
│       ├── context/
│       │   └── AuthContext.tsx ← UPDATED: Self-hosted auth
│       ├── pages/
│       │   ├── Login.tsx       ← UPDATED: Error handling
│       │   ├── SignUp.tsx      ← UPDATED: Backend integration
│       │   └── Dashboard.tsx   ← Works with new auth
│       └── components/
│           └── dashboard/
│               └── UploadForm.tsx ← UPDATED: Real API calls
│
├── AUTH_SETUP.md               ← Quick start guide
├── SELF_HOSTED_AUTH.md         ← Technical details
├── IMPLEMENTATION_COMPLETE.md  ← Summary
├── start-dev.bat               ← Automated startup
└── README.md                   ← Project overview
```

---

This self-hosted authentication system is now complete and ready for testing!
