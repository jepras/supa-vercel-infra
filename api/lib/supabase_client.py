import os
from supabase import create_client, Client
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_service_key:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required")

supabase: Client = create_client(supabase_url, supabase_service_key)

class SupabaseManager:
    def __init__(self):
        self.client = supabase
    
    async def get_user_integration(self, user_id: str, provider: str) -> Optional[Dict[str, Any]]:
        """Get user's integration for a specific provider"""
        try:
            result = self.client.table('integrations').select('*').eq('user_id', user_id).eq('provider', provider).single().execute()
            return result.data if result.data else None
        except Exception as e:
            logger.error(f"Error getting integration for user {user_id}, provider {provider}: {str(e)}")
            return None
    
    async def save_integration(self, user_id: str, provider: str, token_data: Dict[str, Any], user_info: Optional[Dict[str, Any]] = None) -> bool:
        """Save or update integration data"""
        try:
            from .oauth_manager import oauth_manager
            
            integration_data = {
                'user_id': user_id,
                'provider': provider,
                'access_token': oauth_manager.encrypt_token(token_data['access_token']),
                'token_expires_at': token_data['expires_at'],
                'scopes': token_data.get('scope', '').split(' '),
                'is_active': True
            }
            
            if token_data.get('refresh_token'):
                integration_data['refresh_token'] = oauth_manager.encrypt_token(token_data['refresh_token'])
            
            if user_info:
                integration_data['provider_user_id'] = user_info.get('id')
                integration_data['provider_user_email'] = user_info.get('email')
            
            # Check if integration already exists
            existing = await self.get_user_integration(user_id, provider)
            
            if existing:
                # Update existing integration
                result = self.client.table('integrations').update(integration_data).eq('id', existing['id']).execute()
            else:
                # Create new integration
                result = self.client.table('integrations').insert(integration_data).execute()
            
            return bool(result.data)
        except Exception as e:
            logger.error(f"Error saving integration for user {user_id}, provider {provider}: {str(e)}")
            return False
    
    async def delete_integration(self, user_id: str, provider: str) -> bool:
        """Delete user's integration for a specific provider"""
        try:
            result = self.client.table('integrations').delete().eq('user_id', user_id).eq('provider', provider).execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Error deleting integration for user {user_id}, provider {provider}: {str(e)}")
            return False
    
    async def log_activity(self, user_id: str, activity_type: str, status: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Log activity for real-time updates"""
        try:
            activity_data = {
                'user_id': user_id,
                'activity_type': activity_type,
                'status': status,
                'message': message,
                'metadata': metadata or {}
            }
            
            result = self.client.table('activity_logs').insert(activity_data).execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Error logging activity for user {user_id}: {str(e)}")
            return False
    
    async def log_opportunity(self, user_id: str, email_hash: str, recipient_email: str, opportunity_detected: bool, 
                            deal_existed: Optional[bool] = None, deal_created: bool = False, 
                            pipedrive_deal_id: Optional[str] = None, ai_confidence: Optional[float] = None,
                            ai_reasoning: Optional[str] = None, error_message: Optional[str] = None) -> bool:
        """Log sales opportunity processing"""
        try:
            opportunity_data = {
                'user_id': user_id,
                'email_hash': email_hash,
                'recipient_email': recipient_email,
                'opportunity_detected': opportunity_detected,
                'deal_existed': deal_existed,
                'deal_created': deal_created,
                'pipedrive_deal_id': pipedrive_deal_id,
                'ai_confidence_score': ai_confidence,
                'ai_reasoning': ai_reasoning,
                'error_message': error_message
            }
            
            result = self.client.table('opportunity_logs').insert(opportunity_data).execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Error logging opportunity for user {user_id}: {str(e)}")
            return False

# Global instance
supabase_manager = SupabaseManager() 