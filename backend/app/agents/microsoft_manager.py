"""
Microsoft Manager Agent

This module handles Microsoft Graph API operations with token refresh logic.
"""

import os
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Use absolute imports for testing compatibility
try:
    from app.lib.error_handler import (
        handle_microsoft_errors,
        handle_token_refresh_errors,
        MicrosoftError,
        TokenRefreshError,
    )
    from app.monitoring.agent_logger import agent_logger
    from app.lib.supabase_client import supabase_manager
    from app.lib.encryption import token_encryption
except ImportError:
    # Fallback for when running as module
    from ..lib.error_handler import (
        handle_microsoft_errors,
        handle_token_refresh_errors,
        MicrosoftError,
        TokenRefreshError,
    )
    from ..monitoring.agent_logger import agent_logger
    from ..lib.supabase_client import supabase_manager
    from ..lib.encryption import token_encryption


class MicrosoftManager:
    """Microsoft Graph API client with token refresh and email operations."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.graph_base_url = "https://graph.microsoft.com/v1.0"
        self.tokens = None
        self.microsoft_user_id = None

        # Load tokens from Supabase
        self._load_tokens()

    def _load_tokens(self):
        """Load access and refresh tokens from Supabase."""
        try:
            # Check if we're in testing mode (using environment variables)
            if os.getenv("MICROSOFT_ACCESS_TOKEN"):
                agent_logger.info(
                    "Loading Microsoft tokens from environment (testing mode)"
                )
                access_token = os.getenv("MICROSOFT_ACCESS_TOKEN")
                refresh_token = os.getenv("MICROSOFT_REFRESH_TOKEN")

                self.tokens = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }

                if not self.tokens["access_token"]:
                    raise MicrosoftError("No Microsoft access token found")

                agent_logger.info("Microsoft tokens loaded from environment")
                return

            # Production mode: Load tokens from Supabase
            agent_logger.info(
                f"Loading Microsoft tokens from Supabase for user: {self.user_id}"
            )

            result = (
                supabase_manager.client.table("integrations")
                .select("*")
                .eq("provider", "microsoft")
                .eq("user_id", self.user_id)
                .execute()
            )

            if not result.data:
                raise MicrosoftError("No Microsoft integration found for user")

            integration = result.data[0]

            # Decrypt tokens from Supabase
            try:
                access_token = token_encryption.decrypt_token(
                    integration["access_token"]
                )
                refresh_token = (
                    token_encryption.decrypt_token(integration["refresh_token"])
                    if integration["refresh_token"]
                    else None
                )

                self.tokens = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }

                # Store Microsoft user ID for API calls
                self.microsoft_user_id = integration.get("microsoft_user_id")

                agent_logger.info("Microsoft tokens loaded from Supabase successfully")

            except Exception as e:
                agent_logger.error(
                    "Failed to decrypt tokens from Supabase", {"error": str(e)}
                )
                raise MicrosoftError(
                    f"Failed to decrypt tokens from Supabase: {str(e)}"
                )

        except Exception as e:
            agent_logger.error("Failed to load Microsoft tokens", {"error": str(e)})
            raise MicrosoftError(f"Failed to load tokens: {str(e)}")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with current access token."""
        if not self.tokens or not self.tokens.get("access_token"):
            raise MicrosoftError("No access token available")

        return {
            "Authorization": f"Bearer {self.tokens['access_token']}",
            "Content-Type": "application/json",
        }

    @handle_token_refresh_errors
    async def _refresh_access_token(self):
        """Refresh access token using refresh token."""
        if not self.tokens or not self.tokens.get("refresh_token"):
            raise TokenRefreshError("No refresh token available")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": self.tokens["refresh_token"],
                        "client_id": os.getenv("MICROSOFT_CLIENT_ID"),
                        "client_secret": os.getenv("MICROSOFT_CLIENT_SECRET"),
                    },
                    timeout=10.0,
                )

                if response.status_code != 200:
                    raise TokenRefreshError(
                        f"Token refresh failed: {response.status_code}"
                    )

                data = response.json()

                # Update tokens
                self.tokens["access_token"] = data["access_token"]
                if "refresh_token" in data:
                    self.tokens["refresh_token"] = data["refresh_token"]

                # Update tokens in Supabase
                supabase_manager.client.table("integrations").update(
                    {
                        "access_token": token_encryption.encrypt_token(
                            self.tokens["access_token"]
                        ),
                        "refresh_token": token_encryption.encrypt_token(
                            self.tokens["refresh_token"]
                        ),
                        "token_expires_at": datetime.utcnow()
                        + timedelta(seconds=data.get("expires_in", 3600)),
                    }
                ).eq("user_id", self.user_id).eq("provider", "microsoft").execute()

                agent_logger.info("Microsoft tokens refreshed successfully")

        except Exception as e:
            agent_logger.error("Token refresh failed", {"error": str(e)})
            raise TokenRefreshError(f"Token refresh failed: {str(e)}")

    async def _make_api_call(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make API call with automatic token refresh."""
        try:
            headers = self._get_headers()
            kwargs["headers"] = headers

            async with httpx.AsyncClient() as client:
                response = await client.request(method, url, **kwargs)

                if response.status_code == 401:
                    # Token expired, refresh and retry
                    agent_logger.info("Access token expired, refreshing...")
                    await self._refresh_access_token()

                    # Retry with new token
                    headers = self._get_headers()
                    kwargs["headers"] = headers
                    response = await client.request(method, url, **kwargs)

                if response.status_code not in (200, 201):
                    raise MicrosoftError(
                        f"Microsoft Graph API error: {response.status_code} - {response.text}"
                    )

                return response.json()

        except Exception as e:
            agent_logger.error(f"API call failed: {method} {url}", {"error": str(e)})
            raise

    @handle_microsoft_errors
    async def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get current user information from Microsoft Graph."""
        try:
            result = await self._make_api_call("GET", f"{self.graph_base_url}/me")

            return {
                "id": result.get("id"),
                "display_name": result.get("displayName"),
                "email": result.get("mail") or result.get("userPrincipalName"),
                "given_name": result.get("givenName"),
                "surname": result.get("surname"),
            }

        except Exception as e:
            agent_logger.error("Failed to get user info", {"error": str(e)})
            return None

    @handle_microsoft_errors
    async def get_email(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific email by message ID."""
        try:
            # Use Microsoft user ID if available, otherwise use /me
            if self.microsoft_user_id:
                url = f"{self.graph_base_url}/users/{self.microsoft_user_id}/messages/{message_id}"
            else:
                url = f"{self.graph_base_url}/me/messages/{message_id}"

            result = await self._make_api_call("GET", url)

            return {
                "id": result.get("id"),
                "subject": result.get("subject"),
                "from": result.get("from", {}).get("emailAddress", {}).get("address"),
                "to": [
                    recipient.get("emailAddress", {}).get("address")
                    for recipient in result.get("toRecipients", [])
                ],
                "cc": [
                    recipient.get("emailAddress", {}).get("address")
                    for recipient in result.get("ccRecipients", [])
                ],
                "body": result.get("body", {}).get("content"),
                "received_at": result.get("receivedDateTime"),
                "sent_at": result.get("sentDateTime"),
                "importance": result.get("importance"),
                "has_attachments": result.get("hasAttachments", False),
            }

        except Exception as e:
            agent_logger.error(
                "Failed to get email", {"error": str(e), "message_id": message_id}
            )
            return None

    @handle_microsoft_errors
    async def get_recent_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent emails from the user's inbox."""
        try:
            # Use Microsoft user ID if available, otherwise use /me
            if self.microsoft_user_id:
                url = f"{self.graph_base_url}/users/{self.microsoft_user_id}/messages"
            else:
                url = f"{self.graph_base_url}/me/messages"

            result = await self._make_api_call(
                "GET",
                url,
                params={
                    "$top": limit,
                    "$orderby": "receivedDateTime desc",
                    "$select": "id,subject,from,toRecipients,receivedDateTime,importance,hasAttachments",
                },
            )

            emails = result.get("value", [])

            return [
                {
                    "id": email.get("id"),
                    "subject": email.get("subject"),
                    "from": email.get("from", {})
                    .get("emailAddress", {})
                    .get("address"),
                    "to": [
                        recipient.get("emailAddress", {}).get("address")
                        for recipient in email.get("toRecipients", [])
                    ],
                    "received_at": email.get("receivedDateTime"),
                    "importance": email.get("importance"),
                    "has_attachments": email.get("hasAttachments", False),
                }
                for email in emails
            ]

        except Exception as e:
            agent_logger.error("Failed to get recent emails", {"error": str(e)})
            return []

    @handle_microsoft_errors
    async def create_webhook_subscription(
        self, notification_url: str, resource: str = "/me/messages"
    ) -> Optional[Dict[str, Any]]:
        """Create a webhook subscription for email notifications."""
        try:
            # Calculate expiration date (3 days from now, max allowed by Microsoft)
            expiration_date = datetime.utcnow() + timedelta(days=3)

            subscription_data = {
                "changeType": "created",
                "notificationUrl": notification_url,
                "resource": resource,
                "expirationDateTime": expiration_date.isoformat() + "Z",
                "clientState": f"user_{self.user_id}",
            }

            result = await self._make_api_call(
                "POST", f"{self.graph_base_url}/subscriptions", json=subscription_data
            )

            return {
                "id": result.get("id"),
                "resource": result.get("resource"),
                "expiration_date": result.get("expirationDateTime"),
                "notification_url": result.get("notificationUrl"),
            }

        except Exception as e:
            agent_logger.error(
                "Failed to create webhook subscription", {"error": str(e)}
            )
            return None

    @handle_microsoft_errors
    async def list_webhook_subscriptions(self) -> List[Dict[str, Any]]:
        """List all webhook subscriptions for the user."""
        try:
            result = await self._make_api_call(
                "GET", f"{self.graph_base_url}/subscriptions"
            )

            subscriptions = result.get("value", [])

            return [
                {
                    "id": sub.get("id"),
                    "resource": sub.get("resource"),
                    "expiration_date": sub.get("expirationDateTime"),
                    "notification_url": sub.get("notificationUrl"),
                    "client_state": sub.get("clientState"),
                }
                for sub in subscriptions
            ]

        except Exception as e:
            agent_logger.error(
                "Failed to list webhook subscriptions", {"error": str(e)}
            )
            return []

    @handle_microsoft_errors
    async def delete_webhook_subscription(self, subscription_id: str) -> bool:
        """Delete a webhook subscription."""
        try:
            await self._make_api_call(
                "DELETE", f"{self.graph_base_url}/subscriptions/{subscription_id}"
            )
            agent_logger.info(f"Deleted webhook subscription: {subscription_id}")
            return True

        except Exception as e:
            agent_logger.error(
                "Failed to delete webhook subscription",
                {"error": str(e), "subscription_id": subscription_id},
            )
            return False

    @handle_microsoft_errors
    async def renew_webhook_subscription(
        self, subscription_id: str
    ) -> Optional[Dict[str, Any]]:
        """Renew a webhook subscription (extend expiration)."""
        try:
            # Calculate new expiration date (3 days from now)
            expiration_date = datetime.utcnow() + timedelta(days=3)

            renewal_data = {"expirationDateTime": expiration_date.isoformat() + "Z"}

            result = await self._make_api_call(
                "PATCH",
                f"{self.graph_base_url}/subscriptions/{subscription_id}",
                json=renewal_data,
            )

            return {
                "id": result.get("id"),
                "expiration_date": result.get("expirationDateTime"),
            }

        except Exception as e:
            agent_logger.error(
                "Failed to renew webhook subscription",
                {"error": str(e), "subscription_id": subscription_id},
            )
            return None
