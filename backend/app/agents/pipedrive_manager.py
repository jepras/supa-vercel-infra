"""
Pipedrive Manager Agent

This module handles Pipedrive API operations with token refresh logic.
"""

import os
import httpx
from typing import Dict, Any, Optional, List

# Use absolute imports for testing compatibility
try:
    from app.lib.error_handler import (
        handle_pipedrive_errors,
        handle_token_refresh_errors,
        PipedriveError,
        TokenRefreshError,
    )
    from app.monitoring.agent_logger import agent_logger
    from app.lib.supabase_client import supabase_manager
    from app.agents.analyze_email import EmailAnalyzer
    from app.lib.encryption import token_encryption
except ImportError:
    # Fallback for when running as module
    from ..lib.error_handler import (
        handle_pipedrive_errors,
        handle_token_refresh_errors,
        PipedriveError,
        TokenRefreshError,
    )
    from ..monitoring.agent_logger import agent_logger
    from ..lib.supabase_client import supabase_manager
    from .analyze_email import EmailAnalyzer


class PipedriveManager:
    """Pipedrive API client with token refresh and all operations."""

    def __init__(self, user_id: str, company_domain: str = "jeppe-sandbox"):
        self.user_id = user_id
        self.company_domain = company_domain
        self.base_url = f"https://{company_domain}.pipedrive.com/api/v2"
        self.v1_base_url = f"https://{company_domain}.pipedrive.com/api/v1"
        self.tokens = None
        self.email_analyzer = EmailAnalyzer()

        # Load tokens from Supabase
        self._load_tokens()

    def _load_tokens(self):
        """Load access and refresh tokens from Supabase."""
        try:
            # Check if we're in testing mode (using environment variables)
            if os.getenv("PIPEDRIVE_ACCESS_TOKEN"):
                agent_logger.info(
                    "Loading Pipedrive tokens from environment (testing mode)"
                )
                access_token = os.getenv("PIPEDRIVE_ACCESS_TOKEN")
                refresh_token = os.getenv("PIPEDRIVE_REFRESH_TOKEN")

                # Decrypt refresh token if it looks encrypted
                if (
                    refresh_token
                    and len(refresh_token) > 60
                    and not refresh_token.startswith("v1u:")
                ):
                    try:
                        agent_logger.info("Attempting to decrypt refresh token...")
                        refresh_token = token_encryption.decrypt_token(refresh_token)
                        agent_logger.info("Refresh token decrypted successfully.")
                    except Exception as e:
                        agent_logger.error(
                            "Failed to decrypt refresh token", {"error": str(e)}
                        )
                        raise PipedriveError(
                            f"Failed to decrypt refresh token: {str(e)}"
                        )

                self.tokens = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }

                if not self.tokens["access_token"]:
                    raise PipedriveError("No Pipedrive access token found")

                agent_logger.info("Pipedrive tokens loaded from environment")
                return

            # Production mode: Load tokens from Supabase
            agent_logger.info(
                f"Loading Pipedrive tokens from Supabase for user: {self.user_id}"
            )

            result = (
                supabase_manager.client.table("integrations")
                .select("*")
                .eq("provider", "pipedrive")
                .eq("user_id", self.user_id)
                .execute()
            )

            if not result.data:
                raise PipedriveError("No Pipedrive integration found for user")

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

                agent_logger.info("Pipedrive tokens loaded from Supabase successfully")

            except Exception as e:
                agent_logger.error(
                    "Failed to decrypt tokens from Supabase", {"error": str(e)}
                )
                raise PipedriveError(
                    f"Failed to decrypt tokens from Supabase: {str(e)}"
                )

        except Exception as e:
            agent_logger.error("Failed to load Pipedrive tokens", {"error": str(e)})
            raise PipedriveError(f"Failed to load tokens: {str(e)}")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with current access token."""
        if not self.tokens or not self.tokens.get("access_token"):
            raise PipedriveError("No access token available")

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
                    "https://oauth.pipedrive.com/oauth/token",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": self.tokens["refresh_token"],
                        "client_id": os.getenv("PIPEDRIVE_CLIENT_ID"),
                        "client_secret": os.getenv("PIPEDRIVE_CLIENT_SECRET"),
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
                        "access_token": self.tokens["access_token"],
                        "refresh_token": self.tokens["refresh_token"],
                    }
                ).eq("user_id", self.user_id).eq("provider", "pipedrive").execute()

                agent_logger.info("Pipedrive tokens refreshed successfully")

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
                    raise PipedriveError(
                        f"Pipedrive API error: {response.status_code} - {response.text}"
                    )

                return response.json()

        except Exception as e:
            agent_logger.error(f"API call failed: {method} {url}", {"error": str(e)})
            raise

    @handle_pipedrive_errors
    async def search_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Search for a contact by email address."""
        try:
            agent_logger.info(f"Searching for contact with email: {email}")

            result = await self._make_api_call(
                "GET",
                f"{self.base_url}/persons/search",
                params={"term": email, "fields": "email"},
            )

            items = result.get("data", {}).get("items", [])
            agent_logger.info(f"Found {len(items)} search results for email: {email}")

            # Check if any contact has this exact email
            for item in items:
                person = item.get("item", {})
                if isinstance(person, dict):
                    person_emails = person.get("emails", [])
                    agent_logger.info(
                        f"Contact {person.get('name')} has emails: {person_emails}"
                    )
                    for person_email in person_emails:
                        if (
                            isinstance(person_email, str)
                            and person_email.lower() == email.lower()
                        ):
                            agent_logger.info(f"Found exact match for email: {email}")
                            return {
                                "id": person.get("id"),
                                "name": person.get("name"),
                                "email": email,
                                "company_id": person.get("organization", {}).get("id"),
                                "company_name": person.get("organization", {}).get(
                                    "name"
                                ),
                                "phone": person.get("phones", []),
                                "created_at": person.get("add_time"),
                                "updated_at": person.get("update_time"),
                            }

            agent_logger.info(f"No exact match found for email: {email}")
            return None

        except Exception as e:
            agent_logger.error(
                "Contact search failed", {"error": str(e), "email": email}
            )
            return None

    @handle_pipedrive_errors
    async def get_contact_deals(self, contact_id: int) -> List[Dict[str, Any]]:
        """Get all deals associated with a contact."""
        try:
            result = await self._make_api_call(
                "GET", f"{self.base_url}/deals", params={"person_id": contact_id}
            )

            deals = result.get("data", [])

            return [
                {
                    "id": deal.get("id"),
                    "title": deal.get("title"),
                    "value": deal.get("value"),
                    "currency": deal.get("currency"),
                    "stage_id": deal.get("stage_id"),
                    "stage_name": deal.get("stage_name"),
                    "status": deal.get("status"),
                    "created_at": deal.get("add_time"),
                    "updated_at": deal.get("update_time"),
                }
                for deal in deals
            ]

        except Exception as e:
            agent_logger.error(
                "Failed to get contact deals",
                {"error": str(e), "contact_id": contact_id},
            )
            return []

    @handle_pipedrive_errors
    async def contact_has_deals(self, email: str) -> Dict[str, Any]:
        """Check if a contact exists and has associated deals."""
        try:
            # Search for contact
            contact = await self.search_contact_by_email(email)

            if not contact:
                return {
                    "contact_exists": False,
                    "contact": None,
                    "deals": [],
                    "has_deals": False,
                }

            # Get deals for the contact
            deals = await self.get_contact_deals(contact["id"])

            return {
                "contact_exists": True,
                "contact": contact,
                "deals": deals,
                "has_deals": len(deals) > 0,
            }

        except Exception as e:
            agent_logger.error(
                "Contact deal check failed", {"error": str(e), "email": email}
            )
            return {
                "contact_exists": False,
                "contact": None,
                "deals": [],
                "has_deals": False,
            }

    @handle_pipedrive_errors
    async def create_contact(
        self, contact_data: Dict[str, Any], email: str = None, email_content: str = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new contact in Pipedrive."""
        try:
            # Use organization name from contact_data if provided
            org_name = contact_data.get("org_name")

            # Prepare contact payload
            contact_payload = {
                "name": contact_data.get("name", "Unknown"),
                "emails": [{"value": contact_data.get("email"), "primary": True}],
            }

            # Add phone if available
            if contact_data.get("phone"):
                contact_payload["phone"] = [
                    {"value": contact_data["phone"], "primary": True}
                ]

            # If we have an organization name, try to find or create it
            if org_name:
                org = await self.search_organization_by_name(org_name)
                if org:
                    contact_payload["org_id"] = org["id"]
                else:
                    # Create new organization
                    new_org = await self.create_organization({"name": org_name})
                    if new_org:
                        contact_payload["org_id"] = new_org["id"]

            result = await self._make_api_call(
                "POST", f"{self.base_url}/persons", json=contact_payload
            )

            contact = result.get("data", {})

            return {
                "id": contact.get("id"),
                "name": contact.get("name"),
                "email": contact_data.get("email"),
                "company_id": contact.get("org_id"),
                "company_name": contact.get("org_name"),
                "phone": contact.get("phone", []),
                "created_at": contact.get("add_time"),
                "updated_at": contact.get("update_time"),
            }

        except Exception as e:
            agent_logger.error("Contact creation failed", {"error": str(e)})
            return None

    @handle_pipedrive_errors
    async def search_organization_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Search for an organization by name."""
        try:
            result = await self._make_api_call(
                "GET", f"{self.base_url}/organizations/search", params={"term": name}
            )

            items = result.get("data", {}).get("items", [])

            for item in items:
                org = item.get("item", {})
                if org.get("name", "").lower() == name.lower():
                    return {
                        "id": org.get("id"),
                        "name": org.get("name"),
                        "created_at": org.get("add_time"),
                        "updated_at": org.get("update_time"),
                    }

            return None

        except Exception as e:
            agent_logger.error(
                "Organization search failed", {"error": str(e), "name": name}
            )
            return None

    @handle_pipedrive_errors
    async def create_organization(
        self, org_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new organization in Pipedrive."""
        try:
            payload = {"name": org_data.get("name", "Unknown")}

            result = await self._make_api_call(
                "POST", f"{self.base_url}/organizations", json=payload
            )

            org = result.get("data", {})

            return {
                "id": org.get("id"),
                "name": org.get("name"),
                "created_at": org.get("add_time"),
                "updated_at": org.get("update_time"),
            }

        except Exception as e:
            agent_logger.error("Organization creation failed", {"error": str(e)})
            return None

    @handle_pipedrive_errors
    async def create_deal(
        self, contact_id: int, deal_data: Dict[str, Any], org_id: int = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new deal in Pipedrive."""
        try:
            payload = {
                "title": deal_data.get("title", "AI Generated Deal"),
                "person_id": contact_id,
                "value": deal_data.get("value", 0),
                "currency": deal_data.get("currency", "DKK"),
            }

            if org_id:
                payload["org_id"] = org_id

            result = await self._make_api_call(
                "POST", f"{self.base_url}/deals", json=payload
            )

            deal = result.get("data", {})

            if not deal:
                raise PipedriveError("No deal data in response")

            return {
                "id": deal.get("id"),
                "title": deal.get("title"),
                "value": deal.get("value"),
                "currency": deal.get("currency"),
                "stage_id": deal.get("stage_id"),
                "status": deal.get("status"),
                "created_at": deal.get("add_time"),
                "updated_at": deal.get("update_time"),
            }

        except Exception as e:
            agent_logger.error("Deal creation failed", {"error": str(e)})
            return None

    @handle_pipedrive_errors
    async def has_open_deal(self, contact_id: int) -> bool:
        """Return True if the person has any open deal, else False."""
        try:
            result = await self._make_api_call(
                "GET",
                f"{self.base_url}/deals",
                params={"person_id": contact_id, "status": "open"},
            )

            deals = result.get("data", [])
            return len(deals) > 0

        except Exception as e:
            agent_logger.error(
                "Open deal check failed", {"error": str(e), "contact_id": contact_id}
            )
            return False

    @handle_pipedrive_errors
    async def log_note(self, note_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Log a note using the Pipedrive API v2."""
        try:
            agent_logger.info(f"Creating note for deal {note_data.get('deal_id')}")

            payload = {
                "content": note_data.get("content", ""),
                "deal_id": note_data.get("deal_id"),
            }

            agent_logger.info(f"Note payload: {payload}")

            result = await self._make_api_call(
                "POST", f"{self.base_url}/notes", json=payload
            )

            agent_logger.info(f"Note creation response: {result}")
            return result.get("data", {})

        except Exception as e:
            agent_logger.error(f"Note logging failed: {str(e)}")
            return None
