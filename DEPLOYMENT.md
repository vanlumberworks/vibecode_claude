# Fly.io Deployment Guide

## Quick Start

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Deploy**
   ```bash
   fly launch
   fly deploy
   ```

## Files Created

- `Dockerfile` - Python 3.12 with FastAPI
- `fly.toml` - Fly.io configuration

## Environment Variables

Set secrets on Fly.io:
```bash
fly secrets set GOOGLE_AI_API_KEY=your_key_here
fly secrets set METAL_PRICE_API_KEY=your_key_here  # optional
fly secrets set FOREX_RATE_API_KEY=your_key_here  # optional
```

## Access Your App

After deployment:
- API: `https://your-app-name.fly.dev`
- Health: `https://your-app-name.fly.dev/health`
- Docs: `https://your-app-name.fly.dev/docs`

## Frontend Deployment

Deploy frontend to Railway/Vercel and update API URL in frontend code.