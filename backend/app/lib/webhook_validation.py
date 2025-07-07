import hmac
import hashlib
import base64
import os
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

class WebhookValidator:
    """Validates Microsoft Graph webhook requests for security"""
    
    def __init__(self):
        self.verification_token = os.getenv("MICROSOFT_WEBHOOK_VERIFICATION_TOKEN", "default_token")
    
    def validate_webhook_signature(self, request: Request, body: bytes) -> bool:
        """Validate webhook signature from Microsoft Graph"""
        try:
            # Get the signature from headers
            signature = request.headers.get("x-ms-signature")
            if not signature:
                logger.warning("No signature found in webhook request")
                return False
            
            # Microsoft Graph uses HMAC-SHA256 for signature validation
            # The signature is base64 encoded
            expected_signature = base64.b64encode(
                hmac.new(
                    self.verification_token.encode('utf-8'),
                    body,
                    hashlib.sha256
                ).digest()
            ).decode('utf-8')
            
            # Compare signatures
            if hmac.compare_digest(signature, expected_signature):
                logger.info("Webhook signature validated successfully")
                return True
            else:
                logger.warning("Webhook signature validation failed")
                return False
                
        except Exception as e:
            logger.error(f"Error validating webhook signature: {str(e)}")
            return False
    
    def validate_webhook_payload(self, webhook_data: Dict[str, Any]) -> bool:
        """Validate webhook payload structure"""
        try:
            # Check for required fields at root level
            if "value" not in webhook_data:
                logger.warning("Missing required field in webhook payload: value")
                return False
            
            # Validate value is a list
            value_list = webhook_data.get("value")
            if not isinstance(value_list, list) or len(value_list) == 0:
                logger.warning("Webhook value field is not a list or is empty")
                return False
            
            # Get the first item in the value array
            first_item = value_list[0]
            
            # Check for required fields in the first item
            required_fields = ["subscriptionId", "clientState"]
            for field in required_fields:
                if field not in first_item:
                    logger.warning(f"Missing required field in webhook value item: {field}")
                    return False
            
            # Validate subscription ID
            subscription_id = first_item.get("subscriptionId")
            if not subscription_id or not isinstance(subscription_id, str):
                logger.warning("Invalid subscription ID in webhook payload")
                return False
            
            logger.info("Webhook payload validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Error validating webhook payload: {str(e)}")
            return False
    
    def extract_user_id_from_client_state(self, client_state: str) -> Optional[str]:
        """Extract user ID from client state"""
        try:
            if client_state.startswith("user_"):
                return client_state.replace("user_", "")
            return None
        except Exception as e:
            logger.error(f"Error extracting user ID from client state: {str(e)}")
            return None
    
    def validate_subscription_exists(self, subscription_id: str, user_id: str) -> bool:
        """Validate that the subscription exists in our database"""
        try:
            from app.lib.supabase_client import supabase_manager
            
            result = supabase_manager.client.table("webhook_subscriptions").select("*").eq("subscription_id", subscription_id).eq("user_id", user_id).eq("is_active", True).execute()
            
            if result.data:
                logger.info(f"Subscription {subscription_id} validated for user {user_id}")
                return True
            else:
                logger.warning(f"Subscription {subscription_id} not found or inactive for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error validating subscription existence: {str(e)}")
            return False

# Initialize webhook validator
webhook_validator = WebhookValidator() 