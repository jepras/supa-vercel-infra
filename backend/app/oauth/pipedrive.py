from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
import os
from typing import Dict, Any
import httpx
from app.lib.oauth_manager import oauth_manager
from app.lib.encryption import token_encryption
from app.lib.supabase_client import supabase_manager
from app.auth import get_current_user

router = APIRouter(prefix="/api/oauth/pipedrive", tags=["pipedrive-oauth"])

# Pipedrive OAuth configuration
PIPEDRIVE_CLIENT_ID = os.getenv("PIPEDRIVE_CLIENT_ID")
PIPEDRIVE_CLIENT_SECRET = os.getenv("PIPEDRIVE_CLIENT_SECRET")
PIPEDRIVE_REDIRECT_URI = os.getenv("PIPEDRIVE_REDIRECT_URI", "http://localhost:3000/oauth/pipedrive/callback")

# Pipedrive API endpoints
PIPEDRIVE_AUTH_URL = "https://oauth.pipedrive.com/oauth/authorize"
PIPEDRIVE_TOKEN_URL = "https://oauth.pipedrive.com/oauth/token"
PIPEDRIVE_API_BASE = "https://api.pipedrive.com/v1"

@router.get("/connect")
async def connect_pipedrive():
    """Generate Pipedrive OAuth authorization URL"""
    try:
        if not PIPEDRIVE_CLIENT_ID:
            raise HTTPException(status_code=500, detail="Pipedrive client ID not configured")
        
        # Generate state parameter for security
        state = oauth_manager.generate_state()
        
        # Build authorization URL
        auth_params = {
            "client_id": PIPEDRIVE_CLIENT_ID,
            "redirect_uri": PIPEDRIVE_REDIRECT_URI,
            "response_type": "code",
            "state": state
        }
        
        auth_url = f"{PIPEDRIVE_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in auth_params.items()])}"
        
        return {
            "auth_url": auth_url,
            "state": state,
            "message": "Pipedrive OAuth authorization URL generated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate OAuth URL: {str(e)}")

@router.post("/callback")
async def pipedrive_callback(request: Request, current_user: dict = Depends(get_current_user)):
    """Handle Pipedrive OAuth callback and token exchange"""
    try:
        # Get data from request body (for POST requests from frontend)
        body = await request.json()
        code = body.get("code")
        state = body.get("state")
        
        # Fallback to query parameters (for direct OAuth redirects)
        if not code:
            params = dict(request.query_params)
            code = params.get("code")
            state = params.get("state")
            error = params.get("error")
            
            if error:
                raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
        
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code not provided")
        
        # Exchange code for access token
        token_data = await exchange_code_for_token(code)
        
        # Store tokens securely
        await store_pipedrive_tokens(token_data, current_user)
        
        return {
            "status": "success",
            "message": "Pipedrive connected successfully",
            "user_id": token_data.get("user_id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

@router.get("/status")
async def pipedrive_status(current_user: dict = Depends(get_current_user)):
    """Check Pipedrive connection status"""
    try:
        # Get stored tokens
        tokens = await get_pipedrive_tokens(current_user)
        
        if not tokens:
            return {
                "connected": False,
                "message": "Pipedrive not connected"
            }
        
        # Test API connectivity
        is_valid = await test_pipedrive_connection(tokens)
        
        return {
            "connected": is_valid,
            "message": "Pipedrive connected and API accessible" if is_valid else "Pipedrive connected but API not accessible",
            "user_id": tokens.get("user_id")
        }
    except Exception as e:
        return {
            "connected": False,
            "message": f"Error checking status: {str(e)}"
        }

@router.post("/test")
async def test_pipedrive_connection(current_user: dict = Depends(get_current_user)):
    """Test Pipedrive API connection with stored tokens"""
    try:
        # Get stored tokens
        tokens = await get_pipedrive_tokens(current_user)
        
        if not tokens:
            raise HTTPException(status_code=404, detail="Pipedrive not connected")
        
        # Test API call to Pipedrive
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PIPEDRIVE_API_BASE}/users/me",
                headers={
                    "Authorization": f"Bearer {tokens['access_token']}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "status": "success",
                    "message": "Pipedrive API connection successful",
                    "user_info": {
                        "name": user_data.get("data", {}).get("name"),
                        "email": user_data.get("data", {}).get("email"),
                        "company": user_data.get("data", {}).get("company_name")
                    }
                }
            else:
                raise HTTPException(status_code=response.status_code, detail=f"Pipedrive API error: {response.text}")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@router.delete("/disconnect")
async def disconnect_pipedrive(current_user: dict = Depends(get_current_user)):
    """Disconnect Pipedrive integration"""
    try:
        # Remove stored tokens
        await remove_pipedrive_tokens(current_user)
        
        return {
            "status": "success",
            "message": "Pipedrive disconnected successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disconnect: {str(e)}")

async def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """Exchange authorization code for access token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            PIPEDRIVE_TOKEN_URL,
            data={
                "client_id": PIPEDRIVE_CLIENT_ID,
                "client_secret": PIPEDRIVE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": PIPEDRIVE_REDIRECT_URI
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {response.text}")
        
        return response.json()

async def store_pipedrive_tokens(token_data: Dict[str, Any], current_user: dict):
    """Store Pipedrive tokens securely in database"""
    try:
        # Encrypt tokens before storing
        encrypted_access_token = token_encryption.encrypt_token(token_data["access_token"])
        encrypted_refresh_token = token_encryption.encrypt_token(token_data.get("refresh_token", ""))
        
        # Store in Supabase
        data = {
            "provider": "pipedrive",
            "access_token": encrypted_access_token,
            "refresh_token": encrypted_refresh_token,
            "token_expires_at": token_data.get("expires_at"),
            "user_id": current_user["id"],  # Use authenticated user ID
            "scopes": [token_data.get("scope", "")] if token_data.get("scope") else [],
            "metadata": {
                "token_type": token_data.get("token_type", "Bearer")
            }
        }
        
        # Insert or update integration record
        result = supabase_manager.client.table("integrations").upsert(
            data,
            on_conflict="user_id,provider"
        ).execute()
        
        return result
    except Exception as e:
        raise Exception(f"Failed to store tokens: {str(e)}")

async def get_pipedrive_tokens(current_user: dict) -> Dict[str, Any]:
    """Retrieve and decrypt Pipedrive tokens"""
    try:
        # Get from Supabase
        result = supabase_manager.client.table("integrations").select("*").eq("provider", "pipedrive").eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            return None
        
        integration = result.data[0]
        
        # Decrypt tokens
        access_token = token_encryption.decrypt_token(integration["access_token"])
        refresh_token = token_encryption.decrypt_token(integration["refresh_token"]) if integration["refresh_token"] else None
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": integration["token_expires_at"],
            "user_id": integration["user_id"],
            "scope": integration["scopes"][0] if integration["scopes"] else "",
            "token_type": integration["metadata"].get("token_type", "Bearer")
        }
    except Exception as e:
        raise Exception(f"Failed to retrieve tokens: {str(e)}")

async def test_pipedrive_connection(tokens: Dict[str, Any]) -> bool:
    """Test Pipedrive API connectivity"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PIPEDRIVE_API_BASE}/users/me",
                headers={
                    "Authorization": f"{tokens['token_type']} {tokens['access_token']}"
                }
            )
            
            return response.status_code == 200
    except Exception:
        return False

async def remove_pipedrive_tokens(current_user: dict):
    """Remove Pipedrive tokens for the current user"""
    try:
        result = supabase_manager.client.table("integrations").delete().eq("provider", "pipedrive").eq("user_id", current_user["id"]).execute()
        return result
    except Exception as e:
        raise Exception(f"Failed to remove tokens: {str(e)}") 