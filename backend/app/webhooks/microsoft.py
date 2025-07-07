from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import httpx
from app.lib.supabase_client import supabase_manager
from app.lib.oauth_manager import oauth_manager
from app.lib.webhook_validation import webhook_validator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks/microsoft", tags=["microsoft-webhooks"])

# Microsoft Graph API configuration
MICROSOFT_GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
WEBHOOK_VERIFICATION_TOKEN = os.getenv("MICROSOFT_WEBHOOK_VERIFICATION_TOKEN", "default_token")

class MicrosoftWebhookManager:
    """Manages Microsoft Graph webhook subscriptions and email processing"""
    
    def __init__(self):
        self.graph_base_url = MICROSOFT_GRAPH_BASE_URL
    
    async def get_access_token(self, user_id: str) -> Optional[str]:
        """Get Microsoft access token for a user"""
        try:
            # Get user's Microsoft integration
            result = supabase_manager.supabase.table("integrations").select("*").eq("user_id", user_id).eq("provider", "microsoft").eq("is_active", True).execute()
            
            if not result.data:
                logger.error(f"No active Microsoft integration found for user {user_id}")
                return None
            
            integration = result.data[0]
            encrypted_token = integration.get("access_token")
            
            if not encrypted_token:
                logger.error(f"No access token found for user {user_id}")
                return None
            
            # Decrypt the token
            from app.lib.encryption import token_encryption
            access_token = token_encryption.decrypt_token(encrypted_token)
            return access_token
            
        except Exception as e:
            logger.error(f"Error getting access token for user {user_id}: {str(e)}")
            return None
    
    async def create_webhook_subscription(self, user_id: str, notification_url: str) -> Dict[str, Any]:
        """Create a Microsoft Graph webhook subscription for email notifications"""
        try:
            access_token = await self.get_access_token(user_id)
            if not access_token:
                raise HTTPException(status_code=401, detail="No valid Microsoft access token found")
            
            # Calculate expiration date (3 days from now, max allowed by Microsoft)
            expiration_date = datetime.utcnow() + timedelta(days=3)
            
            subscription_data = {
                "changeType": "created",
                "notificationUrl": notification_url,
                "resource": "/me/messages",
                "expirationDateTime": expiration_date.isoformat() + "Z",
                "clientState": f"user_{user_id}"  # Include user ID for webhook processing
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.graph_base_url}/subscriptions",
                    json=subscription_data,
                    headers=headers
                )
                
                if response.status_code != 201:
                    logger.error(f"Failed to create webhook subscription: {response.text}")
                    raise HTTPException(status_code=response.status_code, detail="Failed to create webhook subscription")
                
                subscription = response.json()
                
                # Store subscription in database
                db_subscription = {
                    "user_id": user_id,
                    "subscription_id": subscription["id"],
                    "resource": subscription["resource"],
                    "change_type": subscription["changeType"],
                    "notification_url": subscription["notificationUrl"],
                    "expiration_date": subscription["expirationDateTime"],
                    "is_active": True
                }
                
                result = supabase_manager.supabase.table("webhook_subscriptions").insert(db_subscription).execute()
                
                logger.info(f"Created webhook subscription {subscription['id']} for user {user_id}")
                return subscription
                
        except Exception as e:
            logger.error(f"Error creating webhook subscription for user {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create webhook subscription: {str(e)}")
    
    async def list_webhook_subscriptions(self, user_id: str) -> list:
        """List webhook subscriptions for a user"""
        try:
            result = supabase_manager.supabase.table("webhook_subscriptions").select("*").eq("user_id", user_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error listing webhook subscriptions for user {user_id}: {str(e)}")
            return []
    
    async def delete_webhook_subscription(self, user_id: str, subscription_id: str) -> bool:
        """Delete a webhook subscription"""
        try:
            access_token = await self.get_access_token(user_id)
            if not access_token:
                raise HTTPException(status_code=401, detail="No valid Microsoft access token found")
            
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.graph_base_url}/subscriptions/{subscription_id}",
                    headers=headers
                )
                
                if response.status_code == 204:
                    # Delete from database
                    supabase_manager.supabase.table("webhook_subscriptions").delete().eq("subscription_id", subscription_id).execute()
                    logger.info(f"Deleted webhook subscription {subscription_id} for user {user_id}")
                    return True
                else:
                    logger.error(f"Failed to delete webhook subscription: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting webhook subscription {subscription_id} for user {user_id}: {str(e)}")
            return False
    
    async def process_email_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email webhook from Microsoft Graph"""
        try:
            # Extract email data from webhook
            value = webhook_data.get("value", [])
            if not value:
                logger.warning("No email data in webhook payload")
                return {"status": "no_data"}
            
            processed_emails = []
            
            for email_data in value:
                try:
                    # Extract email metadata
                    email_id = email_data.get("id")
                    subject = email_data.get("subject", "")
                    sender = email_data.get("from", {}).get("emailAddress", {}).get("address", "")
                    recipient = email_data.get("toRecipients", [{}])[0].get("emailAddress", {}).get("address", "")
                    sent_at = email_data.get("sentDateTime")
                    
                    # Extract user ID from clientState
                    client_state = webhook_data.get("clientState", "")
                    user_id = client_state.replace("user_", "") if client_state.startswith("user_") else None
                    
                    if not user_id or not email_id:
                        logger.warning(f"Missing user_id or email_id: user_id={user_id}, email_id={email_id}")
                        continue
                    
                    # Store email metadata in database
                    email_record = {
                        "user_id": user_id,
                        "microsoft_email_id": email_id,
                        "subject": subject,
                        "sender_email": sender,
                        "recipient_email": recipient,
                        "sent_at": sent_at,
                        "webhook_received_at": datetime.utcnow().isoformat(),
                        "processing_status": "pending",
                        "content_retrieved": False,
                        "ai_analyzed": False,
                        "opportunity_detected": None
                    }
                    
                    result = supabase_manager.supabase.table("emails").insert(email_record).execute()
                    
                    if result.data:
                        processed_emails.append({
                            "email_id": email_id,
                            "subject": subject,
                            "status": "stored"
                        })
                        logger.info(f"Stored email {email_id} for user {user_id}")
                    else:
                        logger.error(f"Failed to store email {email_id} for user {user_id}")
                        
                except Exception as e:
                    logger.error(f"Error processing email in webhook: {str(e)}")
                    continue
            
            return {
                "status": "success",
                "processed_count": len(processed_emails),
                "emails": processed_emails
            }
            
        except Exception as e:
            logger.error(f"Error processing email webhook: {str(e)}")
            return {"status": "error", "message": str(e)}

# Initialize webhook manager
webhook_manager = MicrosoftWebhookManager()

@router.post("/email")
async def handle_email_webhook(request: Request):
    """Handle Microsoft Graph email webhook notifications"""
    try:
        # Get webhook payload
        body = await request.body()
        webhook_data = await request.json()
        logger.info(f"Received Microsoft email webhook: {json.dumps(webhook_data, indent=2)}")
        
        # Validate webhook signature (optional for development, required for production)
        if os.getenv("ENVIRONMENT") == "production":
            if not webhook_validator.validate_webhook_signature(request, body):
                logger.warning("Webhook signature validation failed")
                return JSONResponse(
                    status_code=401,
                    content={"status": "unauthorized", "message": "Invalid webhook signature"}
                )
        
        # Validate webhook payload structure
        if not webhook_validator.validate_webhook_payload(webhook_data):
            logger.warning("Webhook payload validation failed")
            return JSONResponse(
                status_code=400,
                content={"status": "bad_request", "message": "Invalid webhook payload"}
            )
        
        # Extract and validate user ID
        client_state = webhook_data.get("clientState", "")
        user_id = webhook_validator.extract_user_id_from_client_state(client_state)
        
        if not user_id:
            logger.warning("Could not extract user ID from client state")
            return JSONResponse(
                status_code=400,
                content={"status": "bad_request", "message": "Invalid client state"}
            )
        
        # Validate subscription exists
        subscription_id = webhook_data.get("subscriptionId")
        if not webhook_validator.validate_subscription_exists(subscription_id, user_id):
            logger.warning(f"Subscription {subscription_id} not found for user {user_id}")
            return JSONResponse(
                status_code=404,
                content={"status": "not_found", "message": "Subscription not found"}
            )
        
        # Process the webhook
        result = await webhook_manager.process_email_webhook(webhook_data)
        
        # Return 202 Accepted (Microsoft expects this)
        return JSONResponse(
            status_code=202,
            content={"status": "accepted", "processed": result}
        )
        
    except Exception as e:
        logger.error(f"Error handling email webhook: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@router.post("/subscribe")
async def create_subscription(user_id: str, notification_url: str):
    """Create a new webhook subscription for email notifications"""
    try:
        subscription = await webhook_manager.create_webhook_subscription(user_id, notification_url)
        return {
            "status": "success",
            "subscription": subscription
        }
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscriptions/{user_id}")
async def list_subscriptions(user_id: str):
    """List webhook subscriptions for a user"""
    try:
        subscriptions = await webhook_manager.list_webhook_subscriptions(user_id)
        return {
            "status": "success",
            "subscriptions": subscriptions
        }
    except Exception as e:
        logger.error(f"Error listing subscriptions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/subscriptions/{user_id}/{subscription_id}")
async def delete_subscription(user_id: str, subscription_id: str):
    """Delete a webhook subscription"""
    try:
        success = await webhook_manager.delete_webhook_subscription(user_id, subscription_id)
        if success:
            return {"status": "success", "message": "Subscription deleted"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete subscription")
    except Exception as e:
        logger.error(f"Error deleting subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_webhook_endpoint():
    """Test endpoint to verify webhook infrastructure"""
    return {
        "status": "success",
        "message": "Microsoft webhook infrastructure is working",
        "endpoints": {
            "email_webhook": "/api/webhooks/microsoft/email",
            "create_subscription": "/api/webhooks/microsoft/subscribe",
            "list_subscriptions": "/api/webhooks/microsoft/subscriptions/{user_id}",
            "delete_subscription": "/api/webhooks/microsoft/subscriptions/{user_id}/{subscription_id}"
        }
    } 