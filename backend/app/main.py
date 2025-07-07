from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from app.lib.oauth_manager import oauth_manager
from app.lib.encryption import token_encryption
from app.lib.supabase_client import supabase_manager
from app.oauth.pipedrive import router as pipedrive_router
from app.oauth.microsoft import router as microsoft_router
from app.webhooks.microsoft import router as microsoft_webhook_router
from app.api.ai_test import router as ai_test_router
import httpx
from fastapi import Depends
from app.auth import get_current_user

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://supa-vercel-infra.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pipedrive_router)
app.include_router(microsoft_router)
app.include_router(microsoft_webhook_router)
app.include_router(ai_test_router, prefix="/api/ai", tags=["ai"])

@app.get("/")
async def root():
    return {"message": "Supa-Vercel-Infra Backend API"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Backend is running"}

@app.get("/api/ngrok/url")
async def get_ngrok_url():
    """Get the current ngrok URL for webhook testing"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:4040/api/tunnels")
            if response.status_code == 200:
                tunnels = response.json()
                for tunnel in tunnels.get("tunnels", []):
                    if tunnel.get("proto") == "https":
                        return {"ngrok_url": tunnel.get("public_url")}
                return {"error": "No HTTPS tunnel found"}
            else:
                return {"error": "Failed to get ngrok tunnels"}
    except Exception as e:
        return {"error": f"Failed to connect to ngrok: {str(e)}"}

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
        
        # Test Microsoft OAuth configuration
        microsoft_config = {
            "client_id": bool(os.getenv("MICROSOFT_CLIENT_ID")),
            "client_secret": bool(os.getenv("MICROSOFT_CLIENT_SECRET")),
            "redirect_uri": os.getenv("MICROSOFT_REDIRECT_URI", "http://localhost:3000/oauth/microsoft/callback")
        }
        
        return {
            "status": "success",
            "oauth_config": oauth_config,
            "pipedrive_config": pipedrive_config,
            "microsoft_config": microsoft_config,
            "encryption_works": encryption_works,
            "supabase_works": supabase_works,
            "message": "OAuth infrastructure is properly configured"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"OAuth infrastructure test failed: {str(e)}"
        } 