# Railway Deployment Guide - Frontend

This guide explains how to deploy the React frontend to Railway.

## Problem Solved

Previously, Railway detected the project as Python (due to root-level `requirements.txt`) and tried to run npm commands without Node.js installed, causing the error:
```
/bin/bash: line 1: npm: command not found
```

This has been fixed with `nixpacks.toml` configuration that forces Node.js detection with pnpm.

## Prerequisites

- Railway account (https://railway.app)
- This repository connected to Railway
- `pnpm-lock.yaml` file present in frontend directory

## Railway Service Configuration

### 1. Create New Service

In your Railway project:
1. Click "New" → "Deploy from GitHub repo"
2. Select this repository
3. Choose "Deploy Now"

### 2. Configure Service Settings

Go to Service Settings and configure:

#### **Root Directory**
```
frontend
```
⚠️ **IMPORTANT**: Set root directory to `frontend/` so Railway only deploys the frontend code.

#### **Build Command** (Optional - nixpacks.toml handles this)
```
pnpm install --frozen-lockfile && pnpm build
```

#### **Start Command** (Optional - nixpacks.toml handles this)
```
pnpm preview --host 0.0.0.0 --port $PORT
```

#### **Watch Paths** (Optional)
```
frontend/**
```
This ensures Railway only rebuilds when frontend files change.

### 3. Environment Variables

If your frontend needs environment variables (API URLs, etc.), add them in:
- Railway Dashboard → Your Service → Variables

Example:
```bash
VITE_API_URL=https://your-backend.railway.app
VITE_GOOGLE_AI_API_KEY=your_key_here
```

⚠️ **Note**: Vite requires env vars to be prefixed with `VITE_` to be exposed to the client.

### 4. Custom Domain (Optional)

1. Go to Service Settings → Networking
2. Click "Generate Domain" for a Railway subdomain
3. Or add your custom domain

## How It Works

### nixpacks.toml Configuration

The `nixpacks.toml` file tells Railway:

```toml
[phases.setup]
nixPkgs = ["nodejs_20", "pnpm"]  # Install Node.js 20 + pnpm

[phases.install]
cmds = ["pnpm install --frozen-lockfile"]  # Install dependencies

[phases.build]
cmds = ["pnpm build"]  # Build Vite production bundle

[start]
cmd = "pnpm preview --host 0.0.0.0 --port $PORT"  # Serve built app
```

### .railwayignore

Excludes Python backend, docs, and unnecessary files to:
- Speed up deployment (less to upload)
- Reduce build image size
- Prevent confusion with Python files

## Production Considerations

### Current Setup: Vite Preview Server

The current configuration uses `vite preview` which is **NOT recommended for production** by Vite docs. It's suitable for:
- Development/staging environments
- Low-traffic applications
- Quick previews

### Recommended: Static File Server

For production, serve the built files with a proper static server:

#### Option 1: Using `serve` (Simple)

1. Install serve:
```bash
cd frontend
pnpm add -D serve
```

2. Update `nixpacks.toml`:
```toml
[start]
cmd = "pnpm dlx serve -s dist -l $PORT"
```

#### Option 2: Using Express (More Control)

1. Create `server.js` in frontend/:
```javascript
import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from dist
app.use(express.static(join(__dirname, 'dist')));

// Handle client-side routing
app.get('*', (req, res) => {
  res.sendFile(join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
```

2. Install express:
```bash
pnpm add express
```

3. Update `nixpacks.toml`:
```toml
[start]
cmd = "node server.js"
```

#### Option 3: Nginx (Best Performance)

For high-traffic production, consider using Railway's static site deployment or a separate Nginx container.

## Troubleshooting

### Build Fails with "pnpm not found"

**Cause**: Railway isn't reading `nixpacks.toml`

**Fix**:
1. Ensure `nixpacks.toml` is in the `frontend/` directory
2. Verify Root Directory is set to `frontend/` in Railway settings
3. Redeploy

### "npm: command not found" Error

**Cause**: Railway still detecting as Python project

**Fix**:
1. Check Root Directory is `frontend/` (not root)
2. Verify `nixpacks.toml` exists in `frontend/`
3. Clear Railway build cache: Settings → Delete Build Cache → Redeploy

### Build Succeeds but Site Doesn't Load

**Cause**: Port configuration issue

**Fix**:
1. Ensure start command uses `--host 0.0.0.0 --port $PORT`
2. Vite preview needs both flags to work on Railway
3. Check Railway logs for port binding errors

### TypeScript Build Errors

**Cause**: Type checking failures during build

**Fix**:
1. Run `pnpm build` locally first to fix type errors
2. Or modify `build` script to skip type checking:
   ```json
   "build": "vite build"  // removes tsc type checking
   ```

### Dependencies Not Installing

**Cause**: `pnpm-lock.yaml` out of sync

**Fix**:
```bash
cd frontend
rm pnpm-lock.yaml
pnpm install
git add pnpm-lock.yaml
git commit -m "Update pnpm lockfile"
```

## Deployment Checklist

- [ ] `nixpacks.toml` exists in `frontend/` directory
- [ ] Railway Root Directory set to `frontend/`
- [ ] `pnpm-lock.yaml` is committed and up to date
- [ ] Environment variables configured (if needed)
- [ ] Build succeeds locally with `pnpm build`
- [ ] Custom domain configured (optional)
- [ ] Consider switching from `vite preview` to proper static server for production

## Monitoring

Check deployment status:
1. Railway Dashboard → Your Service → Deployments
2. View build logs for errors
3. View runtime logs for startup issues

## Cost Estimation

Railway Free Tier:
- $5 credit per month
- Unused services go to sleep after inactivity

Estimated costs for frontend:
- **Idle**: $0/month (sleeps when not used)
- **Active (24/7)**: ~$3-5/month
- **With custom domain**: Same cost

## Support

- Railway Docs: https://docs.railway.app/
- Nixpacks Docs: https://nixpacks.com/docs
- Vite Deployment: https://vitejs.dev/guide/static-deploy.html

## Next Steps

After successful deployment:
1. Test all routes work (client-side routing)
2. Verify API connections (if using backend)
3. Check browser console for errors
4. Test on mobile devices
5. Set up monitoring (Railway provides basic metrics)
6. Consider CDN for static assets (Cloudflare, etc.)
