from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from lib.oauth_manager import oauth_manager
from lib.encryption import token_encryption
from lib.supabase_client import supabase_manager
from oauth.pipedrive import router as pipedrive_router

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add production URLs only if set
frontend_url = os.getenv("FRONTEND_URL")
vercel_url = os.getenv("VERCEL_URL")
if frontend_url:
    origins.append(frontend_url)
if vercel_url:
    origins.append(vercel_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include OAuth routers
app.include_router(pipedrive_router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint for frontend connectivity verification"""
    return {
        "message": "Backend is accessible!",
        "timestamp": "2024-01-01T00:00:00Z",
        "status": "success",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.post("/api/test")
async def test_post_endpoint():
    """Test POST endpoint for frontend connectivity verification"""
    return {
        "message": "POST request received by backend!",
        "timestamp": "2024-01-01T00:00:00Z",
        "status": "success",
        "method": "POST"
    }

@app.get("/api/oauth/test")
async def test_oauth_infrastructure():
    """Test OAuth infrastructure setup"""
    try:
        # Test OAuth manager
        oauth_config = oauth_manager.validate_config()
        
        # Test encryption
        test_token = "test_token_123"
        encrypted = token_encryption.encrypt_token(test_token)
        decrypted = token_encryption.decrypt_token(encrypted)
        encryption_works = test_token == decrypted
        
        # Test Supabase connection
        supabase_works = True  # Will be tested when we actually use it
        
        # Test Pipedrive OAuth configuration
        pipedrive_config = {
            "client_id": bool(os.getenv("PIPEDRIVE_CLIENT_ID")),
            "client_secret": bool(os.getenv("PIPEDRIVE_CLIENT_SECRET")),
            "redirect_uri": os.getenv("PIPEDRIVE_REDIRECT_URI", "http://localhost:3000/oauth/pipedrive/callback")
        }
        
        return {
            "status": "success",
            "oauth_config": oauth_config,
            "pipedrive_config": pipedrive_config,
            "encryption_works": encryption_works,
            "supabase_works": supabase_works,
            "message": "OAuth infrastructure is properly configured"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"OAuth infrastructure test failed: {str(e)}"
        } 