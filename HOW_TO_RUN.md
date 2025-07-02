# How to Run - Local Development & Deployment Guide

## Local Development Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+ and pip
- Docker (optional, for backend)
- Git

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd supa-vercel-infra
```

### 2. Frontend Setup (Next.js)
```bash
# Install dependencies
npm install

# Create environment file
cp env.example .env.local
# Edit .env.local with your local values

# Start development server
npm run dev
```
**Frontend runs on**: http://localhost:3000

### 3. Backend Setup (FastAPI)
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp ../env.example .env
# Edit .env with your local values

# Start development server
uvicorn app.main:app --reload --port 8000
```
**Backend runs on**: http://localhost:8000

### 4. Database Setup (Supabase)
```bash
# Install Supabase CLI
npm install -g supabase

# Start local Supabase
supabase start

# Apply migrations
supabase db reset
```
**Local Supabase runs on**: http://localhost:54321

### 5. Verify Setup
- Frontend: http://localhost:3000 (should show your app)
- Backend: http://localhost:8000/health (should return `{"status": "ok"}`)
- Supabase Studio: http://localhost:54323 (database management)

## Environment Variables

### Frontend (.env.local)
```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_local_anon_key

# Backend API
NEXT_PUBLIC_RAILWAY_API_URL=http://localhost:8000
```

### Backend (.env)
```bash
# Supabase
SUPABASE_URL=http://localhost:54321
SUPABASE_SERVICE_ROLE_KEY=your_local_service_role_key

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

### Running Both Services
```bash
# Terminal 1 - Frontend
npm run dev

# Terminal 2 - Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 3 - Database (if needed)
supabase start
```

### Docker Alternative for Backend
```bash
cd backend
docker build -t my-saas-backend .
docker run -p 8000:8000 my-saas-backend
```

## Deployment

### Frontend Deployment (Vercel)

1. **Connect to Vercel**
```bash
npm install -g vercel
vercel login
```

2. **Deploy**
```bash
vercel --prod
```

3. **Environment Variables in Vercel Dashboard**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_production_anon_key
NEXT_PUBLIC_RAILWAY_API_URL=https://your-app.railway.app
```

**Production Frontend URL**: https://your-app.vercel.app

### Backend Deployment (Railway)

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login and Deploy**
```bash
cd backend
railway login
railway init
railway up
```

3. **Environment Variables in Railway Dashboard**
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_production_service_role_key
PIPEDRIVE_CLIENT_ID=your_pipedrive_client_id
PIPEDRIVE_CLIENT_SECRET=your_pipedrive_client_secret
OUTLOOK_CLIENT_ID=your_outlook_client_id
OUTLOOK_CLIENT_SECRET=your_outlook_client_secret
OPENAI_API_KEY=your_openai_api_key
RAILWAY_STATIC_URL=https://your-app.railway.app
```

**Production Backend URL**: https://your-app.railway.app

### Database Deployment (Supabase)

1. **Push migrations to production**
```bash
supabase db push
```

2. **Update production environment variables** with production Supabase URLs

## URL Summary

### Development
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Supabase**: http://localhost:54321
- **Supabase Studio**: http://localhost:54323

### Production
- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-app.railway.app
- **Supabase**: https://your-project.supabase.co

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
```bash
supabase status
supabase start
```

### Useful Commands

```bash
# Reset everything
supabase stop
supabase start
supabase db reset

# View logs
supabase logs

# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

## Development Tips

1. **Hot Reload**: Both frontend and backend support hot reload
2. **Environment Switching**: Use different .env files for different environments
3. **Database**: Use Supabase local for development, production for deployment
4. **Logs**: Check Railway logs for backend issues, Vercel logs for frontend issues
5. **Testing**: Test OAuth flows with local URLs first, then update to production URLs 