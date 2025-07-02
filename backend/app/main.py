from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from .auth import verify_supabase_token, get_current_user
from .oauth import pipedrive, azure
from .agents import email_analyzer, deal_creator, webhook_processor

# Load environment variables
load_dotenv()

app = FastAPI(
    title="SaaS AI Agent Backend",
    description="AI-driven sales opportunity detection backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local frontend
        "https://your-frontend-domain.vercel.app",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-agent-backend"}

# OAuth endpoints
@app.post("/api/oauth/pipedrive/connect")
async def connect_pipedrive(request: Request, user=Depends(get_current_user)):
    """Initiate Pipedrive OAuth flow"""
    return await pipedrive.initiate_oauth(user)

@app.get("/api/oauth/pipedrive/callback")
async def pipedrive_callback(request: Request):
    """Handle Pipedrive OAuth callback"""
    return await pipedrive.handle_callback(request)

@app.post("/api/oauth/azure/connect")
async def connect_azure(request: Request, user=Depends(get_current_user)):
    """Initiate Azure OAuth flow"""
    return await azure.initiate_oauth(user)

@app.get("/api/oauth/azure/callback")
async def azure_callback(request: Request):
    """Handle Azure OAuth callback"""
    return await azure.handle_callback(request)

# AI Agent endpoints
@app.post("/api/agents/analyze-email")
async def analyze_email(request: Request, user=Depends(get_current_user)):
    """Analyze email for sales opportunities"""
    return await email_analyzer.analyze(request, user)

@app.post("/api/agents/create-deal")
async def create_deal(request: Request, user=Depends(get_current_user)):
    """Create deal in Pipedrive"""
    return await deal_creator.create(request, user)

@app.post("/api/webhooks/outlook")
async def outlook_webhook(request: Request):
    """Handle Outlook webhook for new emails"""
    return await webhook_processor.handle_outlook_webhook(request)

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 