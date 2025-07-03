# How to Run - Local Development & Deployment

## Local Development Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+ and pip
- Docker (optional, for backend)
- Git

### 1. Start Frontend (Next.js)
```bash
# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```
**Frontend runs on**: http://localhost:3000

### 2. Start Backend (FastAPI)
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (if not already done)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload --port 8000
```
**Backend runs on**: http://localhost:8000

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
NEXT_PUBLIC_RAILWAY_API_URL=http://localhost:8000
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

# Terminal 2 - Backend
cd backend
uvicorn app.main:app --reload --port 8000
```

### Docker Alternative for Backend
```bash
cd backend
docker build -t my-saas-backend .
docker run -p 8000:8000 my-saas-backend
```

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

# Test with Docker
docker build -t my-saas-backend .
docker run -p 8000:8000 my-saas-backend

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