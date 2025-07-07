from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
import os
from typing import Dict, Any
import httpx
from app.lib.oauth_manager import oauth_manager
from app.lib.encryption import token_encryption
from app.lib.supabase_client import supabase_manager
from app.auth import get_current_user

router = APIRouter(prefix="/api/oauth/microsoft", tags=["microsoft-oauth"])

# Microsoft OAuth configuration
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
MICROSOFT_REDIRECT_URI = os.getenv("MICROSOFT_REDIRECT_URI", "http://localhost:3000/oauth/microsoft/callback")

# Microsoft API endpoints
MICROSOFT_AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
MICROSOFT_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
MICROSOFT_API_BASE = "https://graph.microsoft.com/v1.0"

@router.get("/connect")
async def connect_microsoft():
    """Generate Microsoft OAuth authorization URL"""
    try:
        if not MICROSOFT_CLIENT_ID:
            raise HTTPException(status_code=500, detail="Microsoft client ID not configured")
        
        # Generate state parameter for security
        state = oauth_manager.generate_state()
        
        # Build authorization URL with required scopes
        auth_params = {
            "client_id": MICROSOFT_CLIENT_ID,
            "redirect_uri": MICROSOFT_REDIRECT_URI,
            "response_type": "code",
            "state": state,
            "scope": "https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/User.Read"
        }
        
        auth_url = f"{MICROSOFT_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in auth_params.items()])}"
        
        return {
            "auth_url": auth_url,
            "state": state,
            "message": "Microsoft OAuth authorization URL generated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate OAuth URL: {str(e)}")

@router.post("/callback")
async def microsoft_callback(request: Request, current_user: dict = Depends(get_current_user)):
    """Handle Microsoft OAuth callback and token exchange"""
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
        await store_microsoft_tokens(token_data, current_user)
        
        return {
            "status": "success",
            "message": "Microsoft connected successfully",
            "user_id": token_data.get("user_id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

@router.get("/status")
async def microsoft_status(current_user: dict = Depends(get_current_user)):
    """Check Microsoft connection status"""
    try:
        # Get stored tokens
        tokens = await get_microsoft_tokens(current_user)
        
        if not tokens:
            return {
                "connected": False,
                "message": "Microsoft not connected"
            }
        
        # Test API connectivity
        is_valid = await test_microsoft_connection(tokens)
        
        return {
            "connected": is_valid,
            "message": "Microsoft connected and API accessible" if is_valid else "Microsoft connected but API not accessible",
            "user_id": tokens.get("user_id")
        }
    except Exception as e:
        return {
            "connected": False,
            "message": f"Error checking status: {str(e)}"
        }

@router.post("/test")
async def test_microsoft_connection(current_user: dict = Depends(get_current_user)):
    """Test Microsoft Graph API connection with stored tokens"""
    try:
        # Get stored tokens
        tokens = await get_microsoft_tokens(current_user)
        
        if not tokens:
            raise HTTPException(status_code=404, detail="Microsoft not connected")
        
        # Test API call to Microsoft Graph
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MICROSOFT_API_BASE}/me",
                headers={
                    "Authorization": f"Bearer {tokens['access_token']}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "status": "success",
                    "message": "Microsoft Graph API connection successful",
                    "user_info": {
                        "name": user_data.get("displayName"),
                        "email": user_data.get("mail") or user_data.get("userPrincipalName"),
                        "id": user_data.get("id")
                    }
                }
            else:
                raise HTTPException(status_code=response.status_code, detail=f"Microsoft Graph API error: {response.text}")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@router.delete("/disconnect")
async def disconnect_microsoft(current_user: dict = Depends(get_current_user)):
    """Disconnect Microsoft integration"""
    try:
        # Remove stored tokens
        await remove_microsoft_tokens(current_user)
        
        return {
            "status": "success",
            "message": "Microsoft disconnected successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disconnect: {str(e)}")

async def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """Exchange authorization code for access token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            MICROSOFT_TOKEN_URL,
            data={
                "client_id": MICROSOFT_CLIENT_ID,
                "client_secret": MICROSOFT_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": MICROSOFT_REDIRECT_URI
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {response.text}")
        
        return response.json()

async def store_microsoft_tokens(token_data: Dict[str, Any], current_user: dict):
    """Store Microsoft tokens securely in database"""
    try:
        # Encrypt tokens before storing
        encrypted_access_token = token_encryption.encrypt_token(token_data["access_token"])
        encrypted_refresh_token = token_encryption.encrypt_token(token_data.get("refresh_token", ""))
        
        # Get Microsoft user ID from /me endpoint
        microsoft_user_id = await get_microsoft_user_id(token_data["access_token"])
        
        # Store in Supabase
        data = {
            "provider": "microsoft",
            "access_token": encrypted_access_token,
            "refresh_token": encrypted_refresh_token,
            "token_expires_at": token_data.get("expires_at"),
            "user_id": current_user["id"],  # Use authenticated user ID
            "microsoft_user_id": microsoft_user_id,  # Store Microsoft user ID
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

async def get_microsoft_user_id(access_token: str) -> str:
    """Get Microsoft user ID from /me endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MICROSOFT_API_BASE}/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                user_data = response.json()
                microsoft_user_id = user_data.get("id")
                if not microsoft_user_id:
                    raise Exception("Microsoft user ID not found in /me response")
                return microsoft_user_id
            else:
                raise Exception(f"Failed to get Microsoft user info: {response.status_code} - {response.text}")
    except Exception as e:
        raise Exception(f"Failed to get Microsoft user ID: {str(e)}")

async def get_microsoft_tokens(current_user: dict) -> Dict[str, Any]:
    """Retrieve and decrypt Microsoft tokens"""
    try:
        # Get from Supabase
        result = supabase_manager.client.table("integrations").select("*").eq("provider", "microsoft").eq("user_id", current_user["id"]).execute()
        
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

async def test_microsoft_connection(tokens: Dict[str, Any]) -> bool:
    """Test Microsoft Graph API connectivity"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MICROSOFT_API_BASE}/me",
                headers={
                    "Authorization": f"{tokens['token_type']} {tokens['access_token']}"
                }
            )
            
            return response.status_code == 200
    except Exception:
        return False

async def remove_microsoft_tokens(current_user: dict):
    """Remove Microsoft tokens for the current user"""
    try:
        result = supabase_manager.client.table("integrations").delete().eq("provider", "microsoft").eq("user_id", current_user["id"]).execute()
        return result
    except Exception as e:
        raise Exception(f"Failed to remove tokens: {str(e)}") 