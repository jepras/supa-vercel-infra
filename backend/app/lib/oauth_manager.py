import os
import secrets
import requests
from typing import Dict, Optional
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)

class OAuthManager:
    def __init__(self):
        self.pipedrive_config = {
            "auth_url": "https://oauth.pipedrive.com/oauth/authorize",
            "token_url": "https://oauth.pipedrive.com/oauth/token",
            "api_base": "https://api.pipedrive.com/v1",
            "scopes": ["deals:read", "deals:write", "persons:read", "persons:write"],
            "client_id": os.getenv("PIPEDRIVE_CLIENT_ID"),
            "client_secret": os.getenv("PIPEDRIVE_CLIENT_SECRET"),
            "redirect_uri": f"{os.getenv('RAILWAY_STATIC_URL', 'http://localhost:8000')}/oauth/pipedrive/callback"
        }
        
        self.azure_config = {
            "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "api_base": "https://graph.microsoft.com/v1.0",
            "scopes": [
                "https://graph.microsoft.com/Mail.Read",
                "https://graph.microsoft.com/Mail.ReadWrite",
                "https://graph.microsoft.com/User.Read"
            ],
            "client_id": os.getenv("MICROSOFT_CLIENT_ID"),
            "client_secret": os.getenv("MICROSOFT_CLIENT_SECRET"),
            "redirect_uri": f"{os.getenv('RAILWAY_STATIC_URL', 'http://localhost:8000')}/oauth/azure/callback"
        }
    
    def generate_auth_url(self, provider: str, state: str) -> str:
        """Generate OAuth authorization URL for the specified provider"""
        if provider == "pipedrive":
            config = self.pipedrive_config
        elif provider == "azure":
            config = self.azure_config
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        params = {
            "client_id": config["client_id"],
            "redirect_uri": config["redirect_uri"],
            "response_type": "code",
            "state": state,
            "scope": " ".join(config["scopes"])
        }
        
        auth_url = f"{config['auth_url']}?{urlencode(params)}"
        logger.info(f"Generated OAuth URL for {provider}: {auth_url}")
        return auth_url
    
    async def exchange_code_for_token(self, provider: str, code: str) -> Dict:
        """Exchange authorization code for access token"""
        if provider == "pipedrive":
            config = self.pipedrive_config
        elif provider == "azure":
            config = self.azure_config
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": config["redirect_uri"]
        }
        
        try:
            response = requests.post(config["token_url"], data=data)
            response.raise_for_status()
            token_data = response.json()
            
            logger.info(f"Successfully exchanged code for token for {provider}")
            return token_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error exchanging code for token for {provider}: {str(e)}")
            raise Exception(f"Failed to exchange code for token: {str(e)}")
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate OAuth configuration"""
        validation = {
            "pipedrive": {
                "client_id": bool(self.pipedrive_config["client_id"]),
                "client_secret": bool(self.pipedrive_config["client_secret"]),
                "redirect_uri": bool(self.pipedrive_config["redirect_uri"])
            },
            "azure": {
                "client_id": bool(self.azure_config["client_id"]),
                "client_secret": bool(self.azure_config["client_secret"]),
                "redirect_uri": bool(self.azure_config["redirect_uri"])
            }
        }
        
        return validation

# Create global instance
oauth_manager = OAuthManager() 