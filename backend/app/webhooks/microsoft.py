from fastapi import APIRouter, HTTPException, Request, Depends, Response
from fastapi.responses import JSONResponse
import os
import json
import logging
from datetime import datetime, timedelta, timezone
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
WEBHOOK_VERIFICATION_TOKEN = os.getenv(
    "MICROSOFT_WEBHOOK_VERIFICATION_TOKEN", "default_token"
)


class MicrosoftWebhookManager:
    """Manages Microsoft Graph webhook subscriptions and email processing"""

    def __init__(self):
        self.graph_base_url = MICROSOFT_GRAPH_BASE_URL

    async def get_access_token(self, user_id: str) -> Optional[str]:
        """Get Microsoft access token for a user using the Microsoft manager"""
        try:
            logger.info(f"=== get_access_token called for user_id: {user_id} ===")

            # Use the Microsoft manager for token handling with automatic refresh
            from app.agents.microsoft_manager import MicrosoftManager

            microsoft_manager = MicrosoftManager(user_id)

            # The manager will handle token loading, decryption, and refresh automatically
            if microsoft_manager.tokens and microsoft_manager.tokens.get(
                "access_token"
            ):
                logger.info(
                    "=== Successfully retrieved access token from Microsoft manager ==="
                )
                return microsoft_manager.tokens["access_token"]
            else:
                logger.error("=== No access token available from Microsoft manager ===")
                return None

        except Exception as e:
            logger.error(
                f"=== Error getting access token for user {user_id}: {str(e)} ==="
            )
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    async def create_webhook_subscription(
        self, user_id: str, notification_url: str
    ) -> Dict[str, Any]:
        """Create a Microsoft Graph webhook subscription for email notifications"""
        try:
            logger.info(
                f"=== create_webhook_subscription called with user_id: {user_id}, notification_url: {notification_url} ==="
            )

            logger.info("=== Getting access token ===")
            access_token = await self.get_access_token(user_id)
            logger.info(f"Access token retrieved: {'Yes' if access_token else 'No'}")

            if not access_token:
                logger.error("No access token found for user")
                raise HTTPException(
                    status_code=401, detail="No valid Microsoft access token found"
                )

            # Calculate expiration date (3 days from now, max allowed by Microsoft)
            expiration_date = datetime.now(timezone.utc) + timedelta(days=3)

            # Format for Microsoft Graph API (must be in UTC without timezone offset)
            expiration_iso = expiration_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

            subscription_data = {
                "changeType": "created",
                "notificationUrl": notification_url,
                "resource": "/me/mailFolders('sentitems')/messages",  # Only sent emails
                "expirationDateTime": expiration_iso,
                "clientState": f"user_{user_id}",  # Include user ID for webhook processing
            }

            logger.info(f"=== Subscription data prepared: {subscription_data} ===")

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            logger.info(f"=== Making Microsoft Graph API call ===")
            logger.info(f"URL: {self.graph_base_url}/subscriptions")
            logger.info(
                f"Headers: {{'Authorization': 'Bearer {access_token[:20]}...', 'Content-Type': 'application/json'}}"
            )

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.graph_base_url}/subscriptions",
                    json=subscription_data,
                    headers=headers,
                )

                logger.info(f"=== Microsoft Graph API response ===")
                logger.info(f"Status code: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")
                logger.info(f"Response text: {response.text}")

                if response.status_code != 201:
                    logger.error(
                        f"Failed to create webhook subscription: {response.text}"
                    )
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to create webhook subscription",
                    )

                subscription = response.json()
                logger.info(f"=== Subscription created: {subscription} ===")

                # Store subscription in database
                db_subscription = {
                    "user_id": user_id,
                    "subscription_id": subscription["id"],
                    "provider": "microsoft",  # Add provider field
                    "resource": subscription["resource"],
                    "change_type": subscription["changeType"],
                    "notification_url": subscription["notificationUrl"],
                    "expiration_date": subscription["expirationDateTime"],
                    "is_active": True,
                }

                result = (
                    supabase_manager.client.table("webhook_subscriptions")
                    .insert(db_subscription)
                    .execute()
                )

                logger.info(
                    f"Created webhook subscription {subscription['id']} for user {user_id}"
                )
                return subscription

        except Exception as e:
            logger.error(
                f"Error creating webhook subscription for user {user_id}: {str(e)}"
            )
            if "No valid Microsoft access token found" in str(e):
                raise HTTPException(
                    status_code=401,
                    detail="Please connect your Microsoft account first before creating webhook subscriptions",
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create webhook subscription: {str(e)}",
                )

    async def list_webhook_subscriptions(self, user_id: str) -> list:
        """List webhook subscriptions for a user"""
        try:
            result = (
                supabase_manager.client.table("webhook_subscriptions")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(
                f"Error listing webhook subscriptions for user {user_id}: {str(e)}"
            )
            return []

    async def delete_webhook_subscription(
        self, user_id: str, subscription_id: str
    ) -> bool:
        """Delete a webhook subscription"""
        try:
            # Delete from Microsoft Graph
            access_token = await self.get_access_token(user_id)
            if not access_token:
                logger.error(f"No access token found for user {user_id}")
                return False

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.graph_base_url}/subscriptions/{subscription_id}",
                    headers=headers,
                )

                if response.status_code == 204:
                    logger.info(
                        f"Deleted subscription {subscription_id} from Microsoft Graph"
                    )
                else:
                    logger.warning(
                        f"Failed to delete subscription from Microsoft Graph: {response.status_code}"
                    )

            # Delete from database
            result = (
                supabase_manager.client.table("webhook_subscriptions")
                .delete()
                .eq("subscription_id", subscription_id)
                .eq("user_id", user_id)
                .execute()
            )

            if result.data:
                logger.info(f"Deleted subscription {subscription_id} from database")
                return True
            else:
                logger.warning(f"Subscription {subscription_id} not found in database")
                return False

        except Exception as e:
            logger.error(f"Error deleting webhook subscription: {str(e)}")
            return False

    async def email_exists_in_database(
        self, user_id: str, microsoft_email_id: str
    ) -> bool:
        """Check if an email already exists in the database"""
        try:
            result = (
                supabase_manager.client.table("emails")
                .select("id")
                .eq("user_id", user_id)
                .eq("microsoft_email_id", microsoft_email_id)
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error checking if email exists: {str(e)}")
            return False

    async def verify_microsoft_user_mapping(
        self, supabase_user_id: str, microsoft_user_id: str
    ) -> bool:
        """Verify that the Microsoft user ID matches the stored mapping for the Supabase user"""
        try:
            result = (
                supabase_manager.client.table("integrations")
                .select("microsoft_user_id")
                .eq("user_id", supabase_user_id)
                .eq("provider", "microsoft")
                .eq("is_active", True)
                .execute()
            )

            if not result.data:
                logger.error(
                    f"No Microsoft integration found for Supabase user {supabase_user_id}"
                )
                return False

            stored_microsoft_user_id = result.data[0].get("microsoft_user_id")
            if not stored_microsoft_user_id:
                logger.error(
                    f"No Microsoft user ID stored for Supabase user {supabase_user_id}"
                )
                return False

            if stored_microsoft_user_id != microsoft_user_id:
                logger.error(
                    f"Microsoft user ID mismatch: stored={stored_microsoft_user_id}, received={microsoft_user_id}"
                )
                return False

            logger.info(
                f"Microsoft user ID mapping verified: {supabase_user_id} -> {microsoft_user_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error verifying Microsoft user mapping: {str(e)}")
            return False

    async def fetch_email_content(
        self, supabase_user_id: str, message_id: str, microsoft_user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch full email content from Microsoft Graph"""
        try:
            access_token = await self.get_access_token(supabase_user_id)
            if not access_token:
                logger.error(f"No access token found for user {supabase_user_id}")
                return None

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            # Fetch email content from Microsoft Graph using Microsoft user ID
            url = (
                f"{self.graph_base_url}/users/{microsoft_user_id}/messages/{message_id}"
            )
            logger.info(f"Fetching email content from: {url}")

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    email_data = response.json()
                    logger.info(
                        f"Successfully fetched email content for message {message_id}"
                    )
                    return email_data
                else:
                    logger.error(
                        f"Failed to fetch email content: {response.status_code} - {response.text}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Error fetching email content: {str(e)}")
            return None

    async def process_email_webhook(
        self, webhook_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process email webhook from Microsoft Graph"""
        try:
            # Extract notifications from webhook
            value = webhook_data.get("value", [])
            if not value:
                logger.warning("No notification data in webhook payload")
                return {"status": "no_data"}

            processed_emails = []
            skipped_duplicates = []
            ai_processed_emails = []

            for notification in value:
                resource = notification.get("resource", "")
                subscription_id = notification.get("subscriptionId", "")
                client_state = notification.get("clientState", "")

                # Parse resource: "Users/{microsoft_user_id}/Messages/{message_id}"
                microsoft_user_id = None
                message_id = None
                parts = resource.split("/")
                if (
                    len(parts) >= 4
                    and parts[0].lower() == "users"
                    and parts[2].lower() == "messages"
                ):
                    microsoft_user_id = parts[1]
                    message_id = parts[3]

                # Extract Supabase user ID from clientState
                supabase_user_id = None
                if client_state.startswith("user_"):
                    supabase_user_id = client_state.replace("user_", "")

                logger.info(
                    f"Processing notification: microsoft_user_id={microsoft_user_id}, supabase_user_id={supabase_user_id}, message_id={message_id}"
                )

                if not microsoft_user_id or not message_id or not supabase_user_id:
                    logger.warning(
                        f"Invalid resource format or client state: resource={resource}, client_state={client_state}"
                    )
                    continue

                # Check if email already exists in database (use Supabase user ID)
                if await self.email_exists_in_database(supabase_user_id, message_id):
                    logger.info(
                        f"Email {message_id} already exists in database, skipping"
                    )
                    skipped_duplicates.append(
                        {"message_id": message_id, "reason": "already_exists"}
                    )
                    continue

                # Verify Microsoft user mapping
                if not await self.verify_microsoft_user_mapping(
                    supabase_user_id, microsoft_user_id
                ):
                    logger.error(
                        f"Microsoft user ID mapping verification failed for {message_id}"
                    )
                    continue

                # Fetch full email content from Microsoft Graph (use Microsoft user ID)
                email_content = await self.fetch_email_content(
                    supabase_user_id, message_id, microsoft_user_id
                )
                if not email_content:
                    logger.error(f"Failed to fetch email content for {message_id}")
                    continue

                # Extract email metadata
                subject = email_content.get("subject", "")
                sender_email = (
                    email_content.get("from", {})
                    .get("emailAddress", {})
                    .get("address", "")
                )
                recipient_emails = [
                    r.get("emailAddress", {}).get("address", "")
                    for r in email_content.get("toRecipients", [])
                ]
                sent_at = email_content.get("sentDateTime")
                received_at = email_content.get("receivedDateTime")
                body_content = email_content.get("body", {}).get("content", "")
                body_content_type = email_content.get("body", {}).get("contentType", "")

                # Store email metadata in database (use Supabase user ID)
                email_record = {
                    "user_id": supabase_user_id,
                    "microsoft_email_id": message_id,
                    "subject": subject,
                    "sender_email": sender_email,
                    "recipient_emails": recipient_emails,
                    "sent_at": sent_at,
                    "received_at": received_at,
                    "body_content": body_content,
                    "body_content_type": body_content_type,
                    "webhook_received_at": datetime.now(timezone.utc).isoformat(),
                    "processing_status": "stored",
                    "content_retrieved": True,
                    "ai_analyzed": False,
                    "opportunity_detected": None,
                }

                try:
                    result = (
                        supabase_manager.client.table("emails")
                        .insert(email_record)
                        .execute()
                    )

                    if result.data:
                        processed_emails.append(
                            {
                                "message_id": message_id,
                                "subject": subject,
                                "status": "stored",
                            }
                        )
                        logger.info(
                            f"Successfully stored email {message_id} for user {supabase_user_id}"
                        )

                        # Step 2: Trigger AI Agent Flow
                        try:
                            # Prepare email data for AI analysis
                            ai_email_data = {
                                "id": message_id,
                                "subject": subject,
                                "to": (
                                    recipient_emails[0] if recipient_emails else ""
                                ),  # Primary recipient
                                "from": sender_email,
                                "content": body_content,  # Use 'content' for AI analyzer compatibility
                                "sent_at": sent_at,
                                "user_id": supabase_user_id,
                            }

                            # Import and use AgentOrchestrator
                            from app.agents.orchestrator import AgentOrchestrator

                            logger.info(f"Starting AI analysis for email {message_id}")

                            # Create orchestrator and process email
                            orchestrator = AgentOrchestrator(supabase_user_id)
                            ai_result = await orchestrator.process_email(ai_email_data)

                            # Update email record with AI analysis results
                            update_data = {
                                "processing_status": "completed",
                                "ai_analyzed": True,
                                "opportunity_detected": ai_result.get(
                                    "ai_result", {}
                                ).get("is_sales_opportunity", False),
                                "updated_at": datetime.now(timezone.utc).isoformat(),
                            }

                            # Update the email record in database
                            supabase_manager.client.table("emails").update(
                                update_data
                            ).eq("microsoft_email_id", message_id).execute()

                            ai_processed_emails.append(
                                {
                                    "message_id": message_id,
                                    "subject": subject,
                                    "ai_result": ai_result,
                                    "status": "ai_processed",
                                }
                            )

                            logger.info(
                                f"AI analysis completed for email {message_id}: {ai_result.get('outcome', 'Unknown')}"
                            )

                        except Exception as ai_error:
                            logger.error(
                                f"AI analysis failed for email {message_id}: {str(ai_error)}"
                            )

                            # Update email record to mark AI analysis as failed
                            update_data = {
                                "processing_status": "ai_failed",
                                "ai_analyzed": False,
                                "updated_at": datetime.now(timezone.utc).isoformat(),
                            }

                            supabase_manager.client.table("emails").update(
                                update_data
                            ).eq("microsoft_email_id", message_id).execute()

                            ai_processed_emails.append(
                                {
                                    "message_id": message_id,
                                    "subject": subject,
                                    "ai_error": str(ai_error),
                                    "status": "ai_failed",
                                }
                            )
                    else:
                        logger.error(f"Failed to store email {message_id} in database")

                except Exception as db_error:
                    logger.error(
                        f"Database error storing email {message_id}: {str(db_error)}"
                    )
                    continue

            return {
                "status": "success",
                "processed_count": len(processed_emails),
                "skipped_count": len(skipped_duplicates),
                "ai_processed_count": len(ai_processed_emails),
                "processed_emails": processed_emails,
                "skipped_duplicates": skipped_duplicates,
                "ai_processed_emails": ai_processed_emails,
            }

        except Exception as e:
            logger.error(f"Error processing email webhook: {str(e)}")
            return {"status": "error", "message": str(e)}


# Initialize webhook manager
webhook_manager = MicrosoftWebhookManager()


@router.get("/email")
async def validate_webhook(request: Request):
    """Handle Microsoft Graph webhook validation requests"""
    validation_token = request.query_params.get("validationToken")
    if validation_token:
        return Response(content=validation_token, media_type="text/plain")
    return JSONResponse(
        status_code=400,
        content={"status": "bad_request", "message": "Missing validation token"},
    )


@router.post("/email")
async def handle_email_webhook(request: Request):
    """Handle Microsoft Graph email webhook notifications"""
    try:
        # Check if this is a validation request (Microsoft sometimes sends POST for validation)
        validation_token = request.query_params.get("validationToken")
        if validation_token:
            logger.info(f"Received validation request with token: {validation_token}")
            return Response(content=validation_token, media_type="text/plain")

        # Get webhook payload
        body = await request.body()

        # Check if body is empty (some validation requests have empty bodies)
        if not body:
            logger.warning("Received empty webhook body")
            return Response(content="OK", media_type="text/plain")

        try:
            webhook_data = await request.json()
            logger.info(
                f"Received Microsoft email webhook: {json.dumps(webhook_data, indent=2)}"
            )
        except Exception as json_error:
            logger.warning(f"Failed to parse webhook as JSON: {str(json_error)}")
            # Return 200 OK for non-JSON requests (validation requests)
            return Response(content="OK", media_type="text/plain")

        # Validate webhook signature (optional for development, required for production)
        if os.getenv("ENVIRONMENT") == "production":
            if not webhook_validator.validate_webhook_signature(request, body):
                logger.warning("Webhook signature validation failed")
                return JSONResponse(
                    status_code=401,
                    content={
                        "status": "unauthorized",
                        "message": "Invalid webhook signature",
                    },
                )

        # Validate webhook payload structure
        if not webhook_validator.validate_webhook_payload(webhook_data):
            logger.warning("Webhook payload validation failed")
            return JSONResponse(
                status_code=400,
                content={"status": "bad_request", "message": "Invalid webhook payload"},
            )

        # Extract and validate user ID
        client_state = webhook_data.get("value", [{}])[0].get("clientState", "")
        user_id = webhook_validator.extract_user_id_from_client_state(client_state)

        if not user_id:
            logger.warning("Could not extract user ID from client state")
            return JSONResponse(
                status_code=400,
                content={"status": "bad_request", "message": "Invalid client state"},
            )

        # Validate subscription exists
        subscription_id = webhook_data.get("value", [{}])[0].get("subscriptionId")
        if not webhook_validator.validate_subscription_exists(subscription_id, user_id):
            logger.warning(
                f"Subscription {subscription_id} not found for user {user_id}"
            )
            return JSONResponse(
                status_code=404,
                content={"status": "not_found", "message": "Subscription not found"},
            )

        # Process the webhook
        result = await webhook_manager.process_email_webhook(webhook_data)

        # Return 202 Accepted (Microsoft expects this)
        return JSONResponse(
            status_code=202, content={"status": "accepted", "processed": result}
        )

    except Exception as e:
        logger.error(f"Error handling email webhook: {str(e)}")
        # Return 200 OK for any unexpected errors during validation
        return Response(content="OK", media_type="text/plain")


@router.post("/subscribe")
async def create_subscription(request: Request):
    """Create a new webhook subscription for email notifications"""
    try:
        logger.info("=== Starting webhook subscription creation ===")

        # Log request details
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request URL: {request.url}")
        logger.info(f"Request headers: {dict(request.headers)}")

        # Get and log request body
        body_bytes = await request.body()
        logger.info(f"Request body (raw): {body_bytes}")
        logger.info(f"Request body length: {len(body_bytes)}")

        # Parse JSON body
        try:
            body = await request.json()
            logger.info(f"Request body (parsed): {body}")
        except Exception as json_error:
            logger.error(f"Failed to parse JSON body: {str(json_error)}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON in request body: {str(json_error)}",
            )

        # Extract and validate parameters
        user_id = body.get("user_id")
        notification_url = body.get("notification_url")

        logger.info(f"Extracted user_id: {user_id}")
        logger.info(f"Extracted notification_url: {notification_url}")

        if not user_id:
            logger.error("Missing user_id in request body")
            raise HTTPException(status_code=400, detail="user_id is required")

        if not notification_url:
            logger.error("Missing notification_url in request body")
            raise HTTPException(status_code=400, detail="notification_url is required")

        logger.info("=== Calling webhook_manager.create_webhook_subscription ===")
        subscription = await webhook_manager.create_webhook_subscription(
            user_id, notification_url
        )

        logger.info(f"=== Subscription created successfully: {subscription} ===")
        return {"status": "success", "subscription": subscription}
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"=== Unexpected error creating subscription: {str(e)} ===")
        logger.error(f"Error type: {type(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/subscriptions/{user_id}")
async def list_subscriptions(user_id: str):
    """List webhook subscriptions for a user"""
    try:
        subscriptions = await webhook_manager.list_webhook_subscriptions(user_id)
        return {"status": "success", "subscriptions": subscriptions}
    except Exception as e:
        logger.error(f"Error listing subscriptions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/subscriptions/{user_id}/{subscription_id}")
async def delete_subscription(user_id: str, subscription_id: str):
    """Delete a webhook subscription"""
    try:
        success = await webhook_manager.delete_webhook_subscription(
            user_id, subscription_id
        )
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
            "delete_subscription": "/api/webhooks/microsoft/subscriptions/{user_id}/{subscription_id}",
        },
    }


@router.get("/status/{user_id}")
async def get_webhook_processing_status(user_id: str):
    """Get webhook processing status and recent email processing results"""
    try:
        # Get recent emails processed via webhook
        recent_emails = (
            supabase_manager.client.table("emails")
            .select("*")
            .eq("user_id", user_id)
            .order("webhook_received_at", desc=True)
            .limit(10)
            .execute()
        )

        # Get webhook subscription status
        subscriptions = (
            supabase_manager.client.table("webhook_subscriptions")
            .select("*")
            .eq("user_id", user_id)
            .eq("is_active", True)
            .execute()
        )

        # Calculate processing statistics
        total_emails = len(recent_emails.data) if recent_emails.data else 0
        ai_processed = (
            sum(1 for email in recent_emails.data if email.get("ai_analyzed", False))
            if recent_emails.data
            else 0
        )
        opportunities_detected = (
            sum(
                1
                for email in recent_emails.data
                if email.get("opportunity_detected", False)
            )
            if recent_emails.data
            else 0
        )

        return {
            "status": "success",
            "user_id": user_id,
            "webhook_subscriptions": {
                "active_count": len(subscriptions.data) if subscriptions.data else 0,
                "subscriptions": subscriptions.data or [],
            },
            "recent_processing": {
                "total_emails": total_emails,
                "ai_processed": ai_processed,
                "opportunities_detected": opportunities_detected,
                "recent_emails": recent_emails.data or [],
            },
        }

    except Exception as e:
        logger.error(f"Error getting webhook processing status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
