# How to Run - Local Development & Deployment

## Local Development Setup


While developing
Frontend: npm run dev
Backend: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Before deploying
Frontend
open new terminal
rm -rf .next
npm install
npm run build
npm start

Backend
cd backend
docker build -t test-backend .
docker run --env-file ../.env -p 8000:8000 test-backend

When deploying
Frontend
# Deploy to production
npx vercel --prod
# Or deploy to preview
npx vercel

Backend
Git commit & push (check branch on Railway is set correct)

Frontend URL: https://supa-vercel-infra.vercel.app/dashboard
Backend URL: https://supa-vercel-infra-production.up.railway.app


### 1. Start Frontend (Next.js)
```bash
# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```
**Frontend runs on**: http://localhost:3000

### 2. Start Backend (FastAPI)

#### Development with Uvicorn (Recommended for Development)
```bash
# Navigate to backend directory
cd backend

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start backend with uvicorn for development (hot reload)
# Note: Use app.main:app when running from backend/ directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
**Backend runs on**: http://localhost:8000

#### Production-like Testing with Docker
```bash
# Navigate to backend directory
cd backend

# Build the Docker image (if not already built)
docker build -t test-backend .

# Start backend using Docker and your .env file from the root directory
# (This ensures production-like environment and uses all required env variables)
docker run --env-file ../.env -p 8000:8000 test-backend
```

> **Note:** Use uvicorn for development (faster iteration, hot reload). Use Docker when you want to test production-like environment. Always use `--env-file ../.env` with Docker (since you're in the backend directory but .env is in the root).

### Import and Command Differences

**Local Development (from backend/ directory):**
- Use `python -m uvicorn app.main:app` (because you're in backend/ and need to reference the app module)
- Imports work as `from app.lib.oauth_manager import oauth_manager`

**Docker/Production (from /app directory):**
- Use `python -m uvicorn main:app` (because the app/ directory is copied to the root)
- Same imports work: `from app.lib.oauth_manager import oauth_manager`

### 3. Verify Services
- Frontend: http://localhost:3000 (should show your app)
- Backend: http://localhost:8000/health (should return `{"status": "ok"}`)
- Database: Uses production Supabase (for quick iterations)

## Environment Variables

### Frontend (.env.local)
```bash
# Supabase (Production - for quick development iterations)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_production_anon_key

# Backend API
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Backend (.env)
```bash
# Supabase (Production - for quick development iterations)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_production_service_role_key

# OAuth Providers (for testing)
PIPEDRIVE_CLIENT_ID=your_pipedrive_client_id
PIPEDRIVE_CLIENT_SECRET=your_pipedrive_client_secret
OUTLOOK_CLIENT_ID=your_outlook_client_id
OUTLOOK_CLIENT_SECRET=your_outlook_client_secret

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Backend URL
RAILWAY_STATIC_URL=http://localhost:8000
```

## Development Workflow

### Running Services
```bash
# Terminal 1 - Frontend
npm run dev

# Terminal 2 - Backend (Development)
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Backend (Production-like testing)
cd backend
docker run --env-file ../.env -p 8000:8000 test-backend
```

### Development Workflow Summary
1. **Start with uvicorn** for fast development iteration
2. **Test with Docker** when code is working to verify production-like environment
3. **Deploy to Railway** when everything works locally

## Testing Before Deployment

### 1. Test Frontend
```bash
# Build frontend locally
npm run build

# Test production build
npm start
```

### 2. Test Backend
```bash
cd backend

# Test with uvicorn (development)
uvicorn main:app --reload --port 8000

# Test with Docker (production-like)
docker build -t my-saas-backend .
docker run --env-file ../.env -p 8000:8000 my-saas-backend

# Test health endpoint
curl http://localhost:8000/health
```

### 3. Test Database
```bash
# Check production database connection
# (Database is already live in production)
```

### 4. Test Integration
- Verify frontend can connect to backend API
- Test OAuth flows with local URLs
- Verify database operations work with production DB

## Deployment

### Frontend Deployment (Vercel)
```bash
# Deploy to production
npx vercel --prod

# Or deploy to preview
npx vercel
```

**Production Frontend URL**: jepras-supa-vercel-infra.vercel.app

#### Manual Deployment (if automatic deployment fails)
If automatic deployments are failing, use the force flag to bypass cache issues:
```bash
# Force deployment (bypasses cache and deployment issues)
npx vercel --prod --force
```

This is useful when:
- Automatic deployments are stuck
- Cache issues are preventing deployment
- Environment variable changes aren't being picked up
- Build errors persist despite code fixes

### Backend Deployment (Railway)
```bash
cd backend

# Deploy to Railway
railway up
```

**Production Backend URL**: supa-vercel-infra-production.up.railway.app

### Database Deployment (Supabase)
```bash
# Push migrations to production
supabase db push
```

## URL Summary

### Development
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Database**: https://your-project.supabase.co (Production)

### Production
- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-app.railway.app
- **Database**: https://your-project.supabase.co

## Troubleshooting

### Common Issues

1. **Port conflicts**
```bash
# Check what's using port 3000
lsof -i :3000
# Check what's using port 8000
lsof -i :8000
```

2. **Backend not starting**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

3. **Frontend can't connect to backend**
- Check CORS settings in backend
- Verify environment variables
- Check if backend is running on correct port

4. **Database connection issues**
- Verify Supabase environment variables are correct
- Check if production database is accessible

### Useful Commands

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# View Supabase logs (if needed)
supabase logs
```

## Development Tips

1. **Hot Reload**: Both frontend and backend support hot reload
2. **Production Database**: Using production DB for quick iterations
3. **Environment Variables**: Keep production DB URLs for development
4. **Logs**: Check Railway logs for backend issues, Vercel logs for frontend issues
5. **Testing**: Test OAuth flows with local URLs first, then update to production URLs 