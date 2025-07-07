import os
import openai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Configure OpenRouter client
client = openai.OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

class TestRequest(BaseModel):
    message: str
    model: Optional[str] = "openai/gpt-3.5-turbo"

class TestResponse(BaseModel):
    success: bool
    response: str
    model_used: str
    error: Optional[str] = None

@router.post("/test", response_model=TestResponse)
async def test_openrouter(request: TestRequest):
    """Test OpenRouter connectivity with a simple message."""
    
    if not os.getenv("OPENROUTER_API_KEY"):
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    
    try:
        response = client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.message}],
            max_tokens=100,
            temperature=0.1
        )
        
        return TestResponse(
            success=True,
            response=response.choices[0].message.content,
            model_used=request.model
        )
        
    except Exception as e:
        return TestResponse(
            success=False,
            response="",
            model_used=request.model,
            error=str(e)
        )

@router.get("/health")
async def ai_health_check():
    """Health check for AI service."""
    return {
        "status": "healthy",
        "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY")),
        "default_model": os.getenv("AI_MODEL", "openai/gpt-4-1106-preview")
    } 