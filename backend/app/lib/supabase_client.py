import os
from supabase import create_client, Client
from typing import Dict, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SupabaseManager:
    def __init__(self):
        self._client = None
        self._initialized = False
    
    def _initialize_client(self):
        """Lazy initialization of Supabase client"""
        if self._initialized:
            return
        
        supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and service role key are required")
        
        self._client: Client = create_client(supabase_url, supabase_key)
        self._initialized = True
    
    @property
    def client(self) -> Client:
        """Get the Supabase client, initializing if needed"""
        if not self._initialized:
            self._initialize_client()
        return self._client
    
    async def save_integration(self, user_id: str, provider: str, token_data: Dict, user_info: Dict) -> bool:
        """Save OAuth integration to database"""
        try:
            # Encrypt sensitive token data
            from app.lib.encryption import token_encryption
            encrypted_tokens = token_encryption.encrypt_dict(token_data)
            
            integration_data = {
                "user_id": user_id,
                "provider": provider,
                "access_token": encrypted_tokens.get("access_token"),
                "refresh_token": encrypted_tokens.get("refresh_token"),
                "token_type": token_data.get("token_type"),
                "expires_in": token_data.get("expires_in"),
                "expires_at": self._calculate_expires_at(token_data.get("expires_in")),
                "provider_user_id": user_info.get("id"),
                "provider_user_email": user_info.get("email"),
                "provider_user_name": user_info.get("name"),
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("integrations").upsert(integration_data).execute()
            
            if result.data:
                logger.info(f"Successfully saved {provider} integration for user {user_id}")
                return True
            else:
                logger.error(f"Failed to save {provider} integration for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving {provider} integration: {str(e)}")
            return False
    
    async def get_integration(self, user_id: str, provider: str) -> Optional[Dict]:
        """Get OAuth integration from database"""
        try:
            result = self.client.table("integrations").select("*").eq("user_id", user_id).eq("provider", provider).eq("is_active", True).execute()
            
            if result.data:
                integration = result.data[0]
                # Decrypt tokens
                from app.lib.encryption import token_encryption
                decrypted_integration = token_encryption.decrypt_dict(integration)
                return decrypted_integration
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting {provider} integration: {str(e)}")
            return None
    
    async def get_user_integrations(self, user_id: str) -> List[Dict]:
        """Get all active integrations for a user"""
        try:
            result = self.client.table("integrations").select("*").eq("user_id", user_id).eq("is_active", True).execute()
            
            integrations = []
            for integration in result.data:
                # Decrypt tokens
                from app.lib.encryption import token_encryption
                decrypted_integration = token_encryption.decrypt_dict(integration)
                integrations.append(decrypted_integration)
            
            return integrations
            
        except Exception as e:
            logger.error(f"Error getting user integrations: {str(e)}")
            return []
    
    async def deactivate_integration(self, user_id: str, provider: str) -> bool:
        """Deactivate an OAuth integration"""
        try:
            result = self.client.table("integrations").update({"is_active": False, "updated_at": datetime.utcnow().isoformat()}).eq("user_id", user_id).eq("provider", provider).execute()
            
            if result.data:
                logger.info(f"Successfully deactivated {provider} integration for user {user_id}")
                return True
            else:
                logger.error(f"Failed to deactivate {provider} integration for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deactivating {provider} integration: {str(e)}")
            return False
    
    async def log_activity(self, user_id: str, activity_type: str, status: str, message: str, metadata: Optional[Dict] = None) -> bool:
        """Log activity to the activity_logs table"""
        try:
            activity_data = {
                "user_id": user_id,
                "activity_type": activity_type,
                "status": status,
                "message": message,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("activity_logs").insert(activity_data).execute()
            
            if result.data:
                logger.info(f"Successfully logged activity: {activity_type} for user {user_id}")
                return True
            else:
                logger.error(f"Failed to log activity: {activity_type} for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")
            return False
    
    def _calculate_expires_at(self, expires_in: Optional[int]) -> Optional[str]:
        """Calculate expiration timestamp"""
        if not expires_in:
            return None
        
        expires_at = datetime.utcnow().timestamp() + expires_in
        return datetime.fromtimestamp(expires_at).isoformat()

# Create global instance
supabase_manager = SupabaseManager() 