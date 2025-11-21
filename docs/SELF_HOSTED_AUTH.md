# Self-Hosted Secure Authentication Setup

## Overview

This system uses **JWT tokens** and **password hashing** for secure authentication without third-party dependencies. All user credentials are stored locally with bcrypt-equivalent hashing.

### Architecture

```
Frontend (React)          Backend (Flask)
─────────────────        ──────────────
Login/SignUp              /api/auth/signup
     ↓                           ↑
Submit credentials → POST        │ Validate & hash password
     ↓                           ↓ Store user
Receive JWT token ← Return token + user info
     ↓
Store in localStorage
(authToken)
     ↓
Attach to API requests
(Authorization: Bearer <token>)
```

## Setup Instructions

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```

2. **Set environment variable (optional but recommended):**
   ```bash
   # On Windows PowerShell:
   $env:SECRET_KEY = "your-secret-key-change-in-production"
   
   # On Windows CMD:
   set SECRET_KEY=your-secret-key-change-in-production
   ```
   
   If not set, defaults to `'your-secret-key-change-in-production'`. **Change this in production!**

3. **Start the Flask server:**
   ```bash
   python main.py
   ```
   
   The server will run on `http://localhost:5000`

### Frontend Setup

1. **Ensure `.env.local` is configured:**
   ```
   VITE_API_URL=http://localhost:5000
   ```

2. **Start the dev server:**
   ```bash
   cd plantViewFrontend
   npm run dev
   ```

3. **Test the flow:**
   - Navigate to `http://localhost:5173/signup`
   - Create an account with email and password
   - You'll be redirected to `/dashboard`
   - Token is stored in browser's `localStorage` as `authToken`

## Security Features

### Password Storage
- Passwords are hashed using **werkzeug.security.generate_password_hash**
- Uses PBKDF2 with SHA-256 by default (configurable)
- Original passwords are **never stored**

### Token Generation
- Uses **JWT (JSON Web Tokens)** with HS256 algorithm
- Tokens expire after **24 hours** (configurable in `JWT_EXPIRATION_HOURS`)
- Signed with a secret key

### API Protection
- Protected endpoints require `Authorization: Bearer <token>` header
- Tokens are verified before accessing protected routes
- Expired tokens are rejected with 401 response

### User Database
- Stores users in `users.json` (file-based for simplicity)
- Can be replaced with a real database (PostgreSQL, SQLite, etc.)
- Passwords are hashed immediately upon registration

## API Endpoints

### POST `/api/auth/signup`
Register a new user
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```
Response (201):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "1",
    "email": "user@example.com"
  }
}
```

### POST `/api/auth/login`
Authenticate user
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```
Response (200):
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "1",
    "email": "user@example.com"
  }
}
```

### GET `/api/auth/verify`
Verify current token (requires auth)
```
Header: Authorization: Bearer <token>
```
Response (200):
```json
{
  "user": {
    "id": "1",
    "email": "user@example.com"
  }
}
```

### POST `/API/upload`
Upload image file (requires auth)
```
Header: Authorization: Bearer <token>
Body: multipart/form-data with 'file' field
```

## Frontend Implementation

### API Utilities (`src/lib/api.ts`)
- `signup(email, password)` - Register new user
- `login(email, password)` - Authenticate user
- `verifyToken()` - Check if token is valid
- `apiCall(endpoint, options)` - Generic authenticated API calls
- `getToken()` - Get stored JWT token
- `setToken(token)` - Store JWT token
- `clearToken()` - Remove JWT token

### Auth Context (`src/context/AuthContext.tsx`)
```typescript
const { user, loading, login, signup, logout } = useAuth();
```

## Security Best Practices

### For Production

1. **Change SECRET_KEY:**
   - Generate a strong random key: `python -c "import secrets; print(secrets.token_hex(32))"`
   - Set via environment variable

2. **Use HTTPS:**
   - Never send tokens over unencrypted HTTP in production
   - Use proper SSL/TLS certificates

3. **Use a Real Database:**
   - Replace `users.json` with PostgreSQL or SQLite
   - Implement proper backup and recovery

4. **Add Rate Limiting:**
   - Prevent brute force attacks on login
   - Use Flask-Limiter or similar

5. **Secure Token Storage:**
   - Set `secure` flag on cookies if using them
   - Use `httpOnly` flag to prevent XSS attacks
   - Current implementation uses localStorage (acceptable for SPAs)

6. **Add CORS Protection:**
   - Restrict to specific origins instead of `*`
   - Example: `origins=['https://yourdomain.com']`

## Troubleshooting

**"Missing authorization token" error**
- Check that token is being stored in localStorage
- Verify login was successful
- Check browser DevTools → Application → Local Storage

**"Invalid or expired token" error**
- Token expires after 24 hours
- User must log in again
- Check if system clock is synchronized

**"User already exists" error**
- Email is already registered
- Try signing in instead
- Reset by deleting `users.json` in backend folder (loses all users)

**"Invalid email or password" error**
- Check email/password spelling
- Ensure account exists (register first if needed)
- Passwords are case-sensitive

**Backend not responding**
- Ensure Flask is running on port 5000
- Check that `VITE_API_URL` matches backend URL
- Restart Flask after changing environment variables

## File Locations

- **Backend auth code:** `backend/main.py` (lines ~10-100)
- **User database:** `backend/users.json` (created automatically)
- **Frontend auth context:** `src/context/AuthContext.tsx`
- **Frontend API utilities:** `src/lib/api.ts`
- **Environment config:** `plantViewFrontend/.env.local`
- **Login page:** `src/pages/Login.tsx`
- **Signup page:** `src/pages/SignUp.tsx`

## Next Steps

1. Test signup/login flow locally
2. Verify tokens are working in network tab
3. Implement additional endpoints (detection history, etc.)
4. Consider moving to a real database (SQLite or PostgreSQL)
5. Add rate limiting and additional security measures
6. Set up production deployment with proper SECRET_KEY
