# Railway Environment Variables Setup

This guide explains how to configure your Railway frontend deployment to connect to your Fly.io backend API.

## Quick Setup

### Step 1: Add Environment Variable in Railway

1. **Go to Railway Dashboard** → https://railway.app
2. **Select your frontend service**
3. **Click "Variables" tab** (in the top navigation)
4. **Click "New Variable"**
5. **Add the following**:
   - **Variable Name**: `VITE_API_URL`
   - **Value**: `https://fx-agent-prod-thrumming-smoke-7736.fly.dev`
6. **Click "Add"**

### Step 2: Redeploy

After adding the environment variable:
- Railway will automatically trigger a new deployment
- OR click "Deploy" → "Redeploy" to force rebuild

**Important**: Environment variables in Vite are **baked into the build at build time**, so you must redeploy for changes to take effect.

---

## Understanding Vite Environment Variables

### How It Works

Vite uses a special prefix `VITE_` for environment variables that should be exposed to the client:

1. **Build Time**: When Railway builds your app, it reads `VITE_API_URL`
2. **Compile**: Vite replaces all instances of `import.meta.env.VITE_API_URL` with the actual value
3. **Bundle**: The value is hardcoded into your JavaScript bundle
4. **Runtime**: The browser uses the hardcoded value (no runtime env vars)

### Why VITE_ Prefix?

- **Security**: Only variables with `VITE_` prefix are exposed to the browser
- **Prevents**: Accidentally exposing secrets (API keys, database URLs, etc.)
- **Required**: By Vite for client-side environment variables

---

## Environment Variable Configuration

### For Railway Deployment

Set in **Railway Dashboard → Variables**:

```bash
VITE_API_URL=https://fx-agent-prod-thrumming-smoke-7736.fly.dev
```

### For Local Development

Create `.env.local` file in `frontend/` directory:

```bash
# frontend/.env.local
VITE_API_URL=http://localhost:8000
```

**Note**: `.env.local` is gitignored automatically by Vite.

### For Production (Other Platforms)

If deploying to other platforms:

**Vercel**:
- Settings → Environment Variables → Add `VITE_API_URL`

**Netlify**:
- Site settings → Build & deploy → Environment → Add `VITE_API_URL`

**Docker**:
```bash
docker build --build-arg VITE_API_URL=https://your-api.com -t frontend .
```

---

## Verification

### Check if Environment Variable is Set

After deployment, you can verify the API URL:

1. **Open Railway deployment URL** in browser
2. **Open browser console** (F12 → Console tab)
3. **Run**:
   ```javascript
   // This will show the compiled API URL
   console.log(import.meta.env.VITE_API_URL)
   ```

**Expected Output**: `https://fx-agent-prod-thrumming-smoke-7736.fly.dev`

### Test API Connection

In the browser console:

```javascript
fetch('https://fx-agent-prod-thrumming-smoke-7736.fly.dev/health')
  .then(r => r.json())
  .then(d => console.log('Backend health:', d))
```

**Expected**: Should return backend health status

---

## Troubleshooting

### Frontend Still Connects to localhost:8000

**Cause**: Environment variable not set or deployment not rebuilt

**Solution**:
1. Verify `VITE_API_URL` is in Railway Variables
2. Click "Deploy" → "Redeploy" to rebuild
3. Check build logs for: "VITE_API_URL=https://..."

### CORS Errors

**Error**: `Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS`

**Cause**: Backend not configured to allow requests from frontend domain

**Solution**: Update backend CORS settings to allow Railway frontend domain

**In your Fly.io backend** (`backend/server.py` or similar):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-railway-frontend.railway.app",  # Add your Railway domain
        "http://localhost:3000",  # Keep for local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy your Fly.io backend:
```bash
fly deploy
```

### Environment Variable Not Showing in Build Logs

**Cause**: Railway not passing variable to build

**Solution**: Ensure variable name is exactly `VITE_API_URL` (case-sensitive)

### API URL Contains Quotes

**Wrong**: `VITE_API_URL="https://..."`
**Correct**: `VITE_API_URL=https://...`

Don't use quotes in Railway variables - Railway handles values as strings automatically.

---

## Advanced: Multiple Environments

If you want different API URLs for staging and production:

### Option 1: Separate Railway Services

1. Create two Railway services from the same repo
2. Set different `VITE_API_URL` for each:
   - **Staging**: `https://fx-agent-staging.fly.dev`
   - **Production**: `https://fx-agent-prod-thrumming-smoke-7736.fly.dev`

### Option 2: Branch-Based Deployment

1. Railway settings → Connect different branches:
   - `main` branch → Production service
   - `staging` branch → Staging service
2. Set different env vars for each service

---

## Environment Variable Reference

### Current Setup

| Variable | Value | Purpose |
|----------|-------|---------|
| `VITE_API_URL` | `https://fx-agent-prod-thrumming-smoke-7736.fly.dev` | Backend API endpoint |
| `PORT` | Auto-set by Railway | Port for frontend server (don't set manually) |

### Optional Variables

You might want to add these in the future:

| Variable | Example | Purpose |
|----------|---------|---------|
| `VITE_API_TIMEOUT` | `30000` | API request timeout (ms) |
| `VITE_ENABLE_ANALYTICS` | `true` | Enable/disable analytics |
| `VITE_SENTRY_DSN` | `https://...` | Error tracking (Sentry) |

---

## Code Changes Made

### 1. `src/App.tsx` (Line 16)

**Before**:
```typescript
const { analyze, state, isAnalyzing, error } = useForexAnalysis({
  apiUrl: 'http://localhost:8000',
})
```

**After**:
```typescript
const { analyze, state, isAnalyzing, error } = useForexAnalysis({
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})
```

### 2. `Dockerfile` (Lines 21-23)

Added build argument support:
```dockerfile
# Accept build argument for API URL
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
```

### 3. `.env.example`

Created example file for documentation.

---

## Summary

**To connect Railway frontend to Fly.io backend**:

1. ✅ Set `VITE_API_URL=https://fx-agent-prod-thrumming-smoke-7736.fly.dev` in Railway Variables
2. ✅ Redeploy on Railway
3. ✅ Update backend CORS to allow Railway domain
4. ✅ Test connection in browser console

**Key Points**:
- Use `VITE_` prefix for client-side env vars
- Redeploy after changing env vars (not runtime changes)
- Update backend CORS settings
- No quotes needed in Railway variable values

---

## Support

- Vite Env Docs: https://vitejs.dev/guide/env-and-mode.html
- Railway Env Docs: https://docs.railway.app/develop/variables
- Fly.io CORS: https://fly.io/docs/

## Next Steps

After setting up the environment variable:

1. ✅ Test API connection from Railway frontend
2. ✅ Update backend CORS (if needed)
3. ✅ Test full analysis workflow
4. ✅ Monitor for CORS or connection errors
5. ✅ Set up custom domain (optional)
