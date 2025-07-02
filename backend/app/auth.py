from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import os
from typing import Optional

# Initialize Supabase client
supabase_url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_service_key:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required")

supabase: Client = create_client(supabase_url, supabase_service_key)

security = HTTPBearer()

def verify_supabase_token(token: str) -> Optional[dict]:
    """Verify Supabase JWT token and return user data"""
    try:
        # Verify token with Supabase
        result = supabase.auth.get_user(token)
        
        if result.user:
            return {
                'id': result.user.id,
                'email': result.user.email,
                'aud': result.user.aud,
                'role': result.user.role
            }
        
        return None
    except Exception as e:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current user from JWT token"""
    token = credentials.credentials
    user = verify_supabase_token(token)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_user_from_request(request: Request) -> Optional[dict]:
    """Extract user from request headers (for webhooks)"""
    auth_header = request.headers.get('authorization') or request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    return verify_supabase_token(token) 