# Supabase Authentication Setup Guide

## Implementation Complete ✅

The following files have been created and updated for Supabase authentication:

### Created Files:
- `src/lib/supabase.ts` - Supabase client configuration
- `.env.local` - Environment variables template

### Updated Files:
- `src/context/AuthContext.tsx` - Replaced mock auth with Supabase session management
- `src/pages/Login.tsx` - Added error handling and loading states
- `src/pages/SignUp.tsx` - Added email-only signup (removed name field) with error handling
- `src/pages/Dashboard.tsx` - Updated to use email instead of name

## Next Steps: Configure Supabase

### 1. Create a Supabase Project
1. Go to [supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Fill in project details and database password
4. Wait for the project to initialize (2-3 minutes)

### 2. Get Your Credentials
1. In your Supabase project dashboard, click "Settings" → "API"
2. Copy the following values:
   - **Project URL** (under "API")
   - **Anon Key** (public key under "Project API keys")

### 3. Configure Environment Variables
Edit `plantViewFrontend/.env.local` and replace:
```
VITE_SUPABASE_URL=your_project_url_here
VITE_SUPABASE_ANON_KEY=your_anon_key_here
```

Example:
```
VITE_SUPABASE_URL=https://abcdefgh.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Enable Email/Password Auth in Supabase
1. In Supabase dashboard, go to "Authentication" → "Providers"
2. Ensure "Email" provider is enabled
3. Go to "Email Templates" and customize if needed
4. Go to "Policies" and ensure email/password auth is enabled

### 5. Test Authentication
1. Start your dev server: `npm run dev` (in `plantViewFrontend/`)
2. Navigate to `http://localhost:5173/signup`
3. Create a test account with email and password
4. You should be redirected to the dashboard
5. Try signing out and logging back in

## Features Implemented

### Authentication Flow
- **Sign Up**: Creates new Supabase auth user
- **Sign In**: Authenticates with email/password
- **Session Management**: Automatically restores session on page load
- **Sign Out**: Clears session

### Error Handling
- Invalid credentials feedback
- User already exists errors
- Network error messages
- Loading states during auth operations

### Protected Routes
- Dashboard accessible only when authenticated
- Automatic redirect to login for unauthenticated users
- Preserve intended destination after login

## Architecture Changes

### Before (Mock Auth):
```
localStorage ↔ AuthContext ↔ Login/SignUp/Dashboard
```

### After (Supabase):
```
Supabase Auth API ↔ AuthContext ↔ Login/SignUp/Dashboard
                                ↓
                          localStorage (session)
```

## Integration with Dashboard

The dashboard now:
1. Displays authenticated user's email
2. Requires valid Supabase session to access
3. Properly handles logout via Supabase

## Next: Backend Integration

Once authentication is working, proceed to:
1. Remove `src/lib/mockDetections.ts`
2. Scaffold Flask API endpoints for detection history
3. Wire dashboard components to real API endpoints

## Troubleshooting

**Missing environment variables?**
- Check `.env.local` exists in `plantViewFrontend/` folder
- Restart dev server after changing `.env.local`

**Still seeing login page after signup?**
- Check browser console for errors
- Verify Supabase URL and Anon Key are correct
- Check that Email auth provider is enabled in Supabase

**Errors about missing types?**
- Run `npm install @supabase/supabase-js` if not already installed
- Restart TypeScript server in VS Code

**Session not persisting?**
- Supabase automatically saves session in localStorage
- Check that localStorage is not disabled in browser
- Verify browser DevTools → Application → Local Storage
