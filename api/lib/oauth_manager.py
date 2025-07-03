import os
import json
import base64
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class OAuthManager:
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # OAuth configurations
        self.pipedrive_config = {
            "auth_url": "https://oauth.pipedrive.com/oauth/authorize",
            "token_url": "https://oauth.pipedrive.com/oauth/token",
            "api_base": "https://api.pipedrive.com/v1",
            "scopes": ["deals:read", "deals:write", "persons:read", "persons:write"],
            "redirect_uri": f"{os.environ.get('VERCEL_URL', 'http://localhost:3000')}/api/oauth/pipedrive/callback"
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
            "redirect_uri": f"{os.environ.get('VERCEL_URL', 'http://localhost:3000')}/api/oauth/azure/callback"
        }
    
    def _get_encryption_key(self) -> bytes:
        """Generate or retrieve encryption key for token storage"""
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        if not encryption_key:
            raise ValueError("ENCRYPTION_KEY environment variable is required")
        
        # Convert to bytes if it's a string
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
        
        # Ensure it's 32 bytes for Fernet
        if len(encryption_key) != 32:
            # Derive a 32-byte key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'supa_vercel_infra_salt',
                iterations=100000,
            )
            encryption_key = kdf.derive(encryption_key)
        
        return base64.urlsafe_b64encode(encryption_key)
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt a token for secure storage"""
        return self.cipher_suite.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a token for use"""
        return self.cipher_suite.decrypt(encrypted_token.encode()).decode()
    
    def generate_auth_url(self, provider: str, state: str) -> str:
        """Generate OAuth authorization URL"""
        if provider == 'pipedrive':
            config = self.pipedrive_config
            client_id = os.environ.get('PIPEDRIVE_CLIENT_ID')
        elif provider == 'azure':
            config = self.azure_config
            client_id = os.environ.get('MICROSOFT_CLIENT_ID')
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        if not client_id:
            raise ValueError(f"{provider.upper()}_CLIENT_ID environment variable is required")
        
        params = {
            'client_id': client_id,
            'redirect_uri': config['redirect_uri'],
            'scope': ' '.join(config['scopes']),
            'response_type': 'code',
            'state': state
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{config['auth_url']}?{query_string}"
    
    async def exchange_code_for_token(self, provider: str, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        if provider == 'pipedrive':
            config = self.pipedrive_config
            client_id = os.environ.get('PIPEDRIVE_CLIENT_ID')
            client_secret = os.environ.get('PIPEDRIVE_CLIENT_SECRET')
        elif provider == 'azure':
            config = self.azure_config
            client_id = os.environ.get('MICROSOFT_CLIENT_ID')
            client_secret = os.environ.get('MICROSOFT_CLIENT_SECRET')
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        if not client_id or not client_secret:
            raise ValueError(f"{provider.upper()}_CLIENT_ID and {provider.upper()}_CLIENT_SECRET environment variables are required")
        
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': config['redirect_uri']
        }
        
        try:
            response = requests.post(config['token_url'], data=data)
            response.raise_for_status()
            token_data = response.json()
            
            # Calculate token expiry
            expires_in = token_data.get('expires_in', 3600)
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            return {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'expires_at': expires_at.isoformat(),
                'token_type': token_data.get('token_type', 'Bearer'),
                'scope': token_data.get('scope', '')
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Token exchange failed for {provider}: {str(e)}")
            raise Exception(f"Failed to exchange code for token: {str(e)}")
    
    async def refresh_token(self, provider: str, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token"""
        if provider == 'pipedrive':
            config = self.pipedrive_config
            client_id = os.environ.get('PIPEDRIVE_CLIENT_ID')
            client_secret = os.environ.get('PIPEDRIVE_CLIENT_SECRET')
        elif provider == 'azure':
            config = self.azure_config
            client_id = os.environ.get('MICROSOFT_CLIENT_ID')
            client_secret = os.environ.get('MICROSOFT_CLIENT_SECRET')
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(config['token_url'], data=data)
            response.raise_for_status()
            token_data = response.json()
            
            expires_in = token_data.get('expires_in', 3600)
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            return {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', refresh_token),
                'expires_at': expires_at.isoformat(),
                'token_type': token_data.get('token_type', 'Bearer')
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Token refresh failed for {provider}: {str(e)}")
            raise Exception(f"Failed to refresh token: {str(e)}")
    
    def is_token_expired(self, expires_at: str) -> bool:
        """Check if a token is expired"""
        try:
            expiry_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            return datetime.utcnow() >= expiry_time
        except (ValueError, TypeError):
            return True
    
    async def get_valid_token(self, user_id: str, provider: str) -> Optional[str]:
        """Get a valid access token, refreshing if necessary"""
        from api.lib.supabase_client import supabase
        
        # Get integration record
        result = supabase.table('integrations').select('*').eq('user_id', user_id).eq('provider', provider).single().execute()
        
        if not result.data:
            return None
        
        integration = result.data
        access_token = self.decrypt_token(integration['access_token'])
        
        # Check if token is expired
        if self.is_token_expired(integration['token_expires_at']):
            if integration['refresh_token']:
                try:
                    refresh_token = self.decrypt_token(integration['refresh_token'])
                    new_tokens = await self.refresh_token(provider, refresh_token)
                    
                    # Update database with new tokens
                    update_data = {
                        'access_token': self.encrypt_token(new_tokens['access_token']),
                        'token_expires_at': new_tokens['expires_at'],
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    
                    if new_tokens.get('refresh_token'):
                        update_data['refresh_token'] = self.encrypt_token(new_tokens['refresh_token'])
                    
                    supabase.table('integrations').update(update_data).eq('id', integration['id']).execute()
                    
                    return new_tokens['access_token']
                except Exception as e:
                    logger.error(f"Failed to refresh token for user {user_id}, provider {provider}: {str(e)}")
                    return None
            else:
                return None
        
        return access_token

# Global instance
oauth_manager = OAuthManager() 