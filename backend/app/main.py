from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

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