#!/usr/bin/env python3
"""
AI Email Analysis Prototype - Python Script Version

This script prototypes the AI email analysis system using OpenRouter API.
Divided into chunks like a notebook for easy execution and testing.

Usage:
    python ai_analysis_prototype.py

Prerequisites:
    1. Set OPENROUTER_API_KEY environment variable
    2. Set PIPEDRIVE_ACCESS_TOKEN environment variable (decrypted)
    3. Install: pip install python-dotenv pandas httpx
"""

import os
import json
import pandas as pd
import httpx
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any

# =============================================================================
# CHUNK 1: Setup and Configuration
# =============================================================================


def setup_environment():
    """Setup environment and configure OpenRouter client."""
    print("🔧 Setting up environment...")

    # Load environment variables
    load_dotenv()

    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("❌ OPENROUTER_API_KEY not found in environment variables")

    print(f"✅ OpenRouter API key found: {api_key[:10]}...")

    # Default model
    default_model = os.getenv(
        "AI_MODEL", "openai/gpt-4o-mini"
    )  # Using GPT-4o Mini for cost efficiency

    print(f"✅ Using model: {default_model}")
    print(f"✅ OpenRouter client configured")

    return api_key, default_model


# =============================================================================
# CHUNK 2: Pipedrive Integration
# =============================================================================


class PipedriveClient:
    """Simple Pipedrive API client for contact and deal operations"""

    def __init__(self, access_token: str, company_domain: str = "jeppe-sandbox"):
        self.access_token = access_token
        self.company_domain = company_domain
        self.base_url = f"https://{company_domain}.pipedrive.com/api/v2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def test_token(self) -> bool:
        """Test if the access token is valid"""
        try:
            url = f"{self.base_url}/users/me"
            print(f"🔍 Testing token with URL: {url}")
            print(f"🔍 Headers: {self.headers}")

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                print(f"🔍 Response status: {response.status_code}")
                print(f"🔍 Response text: {response.text[:200]}...")

                return response.status_code == 200
        except Exception as e:
            print(f"❌ Error testing token: {str(e)}")
            return False

    async def get_ai_organization_name(
        self, email: str, email_content: str, api_key: str, model: str
    ) -> str:
        """Use AI to suggest a proper organization name from email and content"""
        domain = email.split("@")[1].lower()
        prompt = f"Extract the most likely real company name from this email domain and content. If it's a personal email, return an empty string.\nDomain: {domain}\nEmail content: {email_content}\nCompany name: "

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 16,
                        "temperature": 0.2,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    name = data["choices"][0]["message"]["content"].strip()
                    if name and name.lower() not in [
                        "gmail",
                        "hotmail",
                        "outlook",
                        "yahoo",
                        "icloud",
                        "live",
                    ]:
                        return name
                return None
        except Exception as e:
            print(f"❌ Error with AI org name: {str(e)}")
            return None

    async def search_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Search for a contact by email address"""
        try:
            url = f"{self.base_url}/persons/search"
            params = {"term": email, "fields": "email"}

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code != 200:
                    print(
                        f"❌ Pipedrive API error: {response.status_code} - {response.text}"
                    )
                    return None

                data = response.json()
                items = data.get("data", {}).get("items", [])

                # Simple check: does any contact have this exact email?
                for item in items:
                    person = item.get("item", {})
                    if isinstance(person, dict):
                        person_emails = person.get("emails", [])
                        for person_email in person_emails:
                            # Pipedrive returns emails as strings, not dicts
                            if (
                                isinstance(person_email, str)
                                and person_email.lower() == email.lower()
                            ):
                                return {
                                    "id": person.get("id"),
                                    "name": person.get("name"),
                                    "email": email,
                                    "company_id": person.get("organization", {}).get(
                                        "id"
                                    ),
                                    "company_name": person.get("organization", {}).get(
                                        "name"
                                    ),
                                    "phone": person.get("phones", []),
                                    "created_at": person.get("add_time"),
                                    "updated_at": person.get("update_time"),
                                }

                return None
        except Exception as e:
            print(f"❌ Error searching contact by email: {str(e)}")
            return None

    async def get_contact_deals(self, contact_id: int) -> List[Dict[str, Any]]:
        """Get all deals associated with a contact"""
        try:
            # Use the deals endpoint with person_id filter
            url = f"{self.base_url}/deals"
            params = {"person_id": contact_id}

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)

                if response.status_code != 200:
                    print(
                        f"❌ Pipedrive API error: {response.status_code} - {response.text}"
                    )
                    return []

                data = response.json()
                deals = data.get("data", [])

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
            print(f"❌ Error getting contact deals: {str(e)}")
            return []

    async def contact_has_deals(self, email: str) -> Dict[str, Any]:
        """Check if a contact exists and has associated deals"""
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

            # Log when we find an existing contact
            print(f"👤 Found existing contact: {contact.get('name')} ({email})")

            # Get deals for the contact
            deals = await self.get_contact_deals(contact["id"])

            return {
                "contact_exists": True,
                "contact": contact,
                "deals": deals,
                "has_deals": len(deals) > 0,
            }

        except Exception as e:
            print(f"❌ Error checking contact deals: {str(e)}")
            return {
                "contact_exists": False,
                "contact": None,
                "deals": [],
                "has_deals": False,
            }

    async def create_contact(
        self,
        contact_data: Dict[str, Any],
        email: str = None,
        email_content: str = None,
        api_key: str = None,
        model: str = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new contact in Pipedrive"""
        try:
            # Use organization name from contact_data if provided (from domain)
            org_name = contact_data.get("org_name")

            # Prepare contact data
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
                    print(f"🔗 Found existing organization: {org_name}")
                else:
                    # Create new organization
                    new_org = await self.create_organization({"name": org_name})
                    if new_org:
                        contact_payload["org_id"] = new_org["id"]
                        print(f"🏢 Created new organization: {org_name}")

            url = f"{self.base_url}/persons"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, headers=self.headers, json=contact_payload
                )

                if response.status_code not in (200, 201):
                    print(
                        f"❌ Pipedrive API error: {response.status_code} - {response.text}"
                    )
                    return None

                data = response.json()
                contact = data.get("data", {})

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
            print(f"❌ Error creating contact: {str(e)}")
            return None

    async def search_organization_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Search for an organization by name"""
        try:
            url = f"{self.base_url}/organizations/search"
            params = {"term": name}

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)

                if response.status_code != 200:
                    return None

                data = response.json()
                items = data.get("data", {}).get("items", [])

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
            print(f"❌ Error searching organization: {str(e)}")
            return None

    async def create_organization(
        self, org_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new organization in Pipedrive"""
        try:
            url = f"{self.base_url}/organizations"
            payload = {"name": org_data.get("name", "Unknown")}

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload)

                if response.status_code not in (200, 201):
                    print(
                        f"❌ Pipedrive API error: {response.status_code} - {response.text}"
                    )
                    return None

                data = response.json()
                org = data.get("data", {})

                return {
                    "id": org.get("id"),
                    "name": org.get("name"),
                    "created_at": org.get("add_time"),
                    "updated_at": org.get("update_time"),
                }

        except Exception as e:
            print(f"❌ Error creating organization: {str(e)}")
            return None

    async def create_deal(
        self, contact_id: int, deal_data: Dict[str, Any], org_id: int = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new deal in Pipedrive"""
        try:
            url = f"{self.base_url}/deals"
            payload = {
                "title": deal_data.get("title", "AI Generated Deal"),
                "person_id": contact_id,
                "value": deal_data.get("value", 0),
                "currency": deal_data.get("currency", "DKK"),  # Default to DKK
            }

            if org_id:
                payload["org_id"] = org_id

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload)

                if response.status_code not in (200, 201):
                    print(
                        f"❌ Pipedrive API error: {response.status_code} - {response.text}"
                    )
                    return None

                data = response.json()
                deal = data.get("data", {})

                if not deal:
                    print(f"❌ No deal data in response")
                    return None

                print(
                    f"✅ Deal created successfully: {deal.get('title')} (ID: {deal.get('id')})"
                )

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
            print(f"❌ Error creating deal: {str(e)}")
            return None

    async def check_for_similar_deals(
        self, contact_id: int, deal_title: str
    ) -> List[Dict[str, Any]]:
        """Check if similar OPEN deals already exist for this contact"""
        try:
            url = f"{self.base_url}/deals"
            params = {"person_id": contact_id, "status": "open"}
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code != 200:
                    return []
                data = response.json()
                deals = data.get("data", [])
                # Only consider open deals with similar titles
                similar_deals = []
                for deal in deals:
                    if deal.get("status") != "open":
                        continue
                    existing_title = deal.get("title", "").lower()
                    new_title = deal_title.lower()
                    if any(
                        word in existing_title
                        for word in new_title.split()
                        if len(word) > 3
                    ):
                        similar_deals.append(deal)
                return similar_deals
        except Exception as e:
            print(f"❌ Error checking for similar deals: {str(e)}")
            return []

    async def log_note(self, note_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Log a note using the proper Notes API v1"""
        try:
            # Use v1 API for notes
            url = f"https://{self.company_domain}.pipedrive.com/api/v1/notes"
            payload = {
                "content": note_data.get("content", ""),
                "deal_id": note_data.get("deal_id"),
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload)

                if response.status_code not in (200, 201):
                    print(
                        f"❌ Pipedrive API error: {response.status_code} - {response.text}"
                    )
                    return None

                data = response.json()
                print(f"✅ Note created successfully: {data.get('data', {}).get('id')}")
                return data.get("data", {})

        except Exception as e:
            print(f"❌ Error logging note: {str(e)}")
            return None

    async def has_open_deal(self, contact_id: int) -> bool:
        """Return True if the person has any open deal, else False."""
        try:
            url = f"{self.base_url}/deals"
            params = {"person_id": contact_id, "status": "open"}
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code != 200:
                    return False
                data = response.json()
                deals = data.get("data", [])
                return len(deals) > 0
        except Exception as e:
            print(f"❌ Error checking for open deals: {str(e)}")
            return False


def setup_pipedrive():
    """Setup Pipedrive client with encrypted or raw token."""
    print("🔧 Setting up Pipedrive client...")

    # Load environment variables
    load_dotenv()

    # Get token
    token = os.getenv("PIPEDRIVE_ACCESS_TOKEN")
    if not token:
        raise ValueError("❌ PIPEDRIVE_ACCESS_TOKEN not found in environment variables")

    # Check if token is already decrypted (starts with v1u:)
    if token.startswith("v1u:"):
        print("🔓 Using raw (decrypted) token as-is.")
        access_token = token
    else:
        # Heuristic: if token is long and looks like base64, try to decrypt, else use as-is
        import re

        is_base64 = bool(re.fullmatch(r"[A-Za-z0-9_\-]+=*", token)) and len(token) > 60
        try:
            if is_base64:
                print("🔒 Detected encrypted token, attempting decryption...")
                import sys

                sys.path.append(os.path.join(os.path.dirname(__file__), "app", "lib"))
                from encryption import token_encryption

                access_token = token_encryption.decrypt_token(token)
                print(f"✅ Pipedrive token decrypted: {access_token[:10]}...")
            else:
                print("🔓 Using raw (decrypted) token as-is.")
                access_token = token
        except Exception as e:
            print(f"❌ Error decrypting token: {str(e)}")
            raise

    # Create client
    client = PipedriveClient(access_token)
    print(f"✅ Pipedrive client configured for domain: {client.company_domain}")

    return client


# =============================================================================
# CHUNK 3: Sample Data
# =============================================================================


def load_sample_emails():
    """Load sample emails for testing."""
    print("📧 Loading sample emails...")

    sample_emails = [
        {
            "id": 1,
            "from": "mathias@besafe.dk",
            "to": "peter.hansen@microsoft.com",
            "subject": "Tilbud på sikkerhedsløsninger - Microsoft Danmark",
            "content": """Hej Peter,

Jeg håber, du har haft en god uge. Som aftalt sender jeg dig et tilbud på vores sikkerhedsløsninger til Microsoft Danmark.

Vi kan tilbyde:
- Avancerede firewall-løsninger
- Endpoint protection
- Security awareness træning
- 24/7 support

Det samlede beløb er DKK 45.000 ekskl. moms for et års løsning.

Vil du have mig til at booke et møde til næste uge, så vi kan gennemgå detaljerne?

Med venlig hilsen,
Mathias Jensen
BeSafe Security Solutions
Tlf: +45 70 12 34 56
Email: mathias@besafe.dk""",
            "received_at": "2024-01-15T10:30:00Z",
            "conversation_id": "conv_001",
            "email_thread": [
                {
                    "from": "peter.hansen@microsoft.com",
                    "to": "mathias@besafe.dk",
                    "subject": "Re: Sikkerhedsbehov - Microsoft Danmark",
                    "content": """Hej Mathias, tak for mødet i går. Kan du sende mig et tilbud på jeres sikkerhedsløsninger?

Med venlig hilsen,
Peter Hansen
IT Security Manager
Microsoft Danmark
Tlf: +45 33 25 50 00""",
                    "received_at": "2024-01-14T15:20:00Z",
                }
            ],
        },
        # Duplicate of the first email for duplicate detection test
        {
            "id": 6,
            "from": "mathias@besafe.dk",
            "to": "peter.hansen@microsoft.com",
            "subject": "Tilbud på sikkerhedsløsninger - Microsoft Danmark (DUPLICATE)",
            "content": """Hej Peter,

Jeg håber, du har haft en god uge. Som aftalt sender jeg dig et tilbud på vores sikkerhedsløsninger til Microsoft Danmark.

Vi kan tilbyde:
- Avancerede firewall-løsninger
- Endpoint protection
- Security awareness træning
- 24/7 support

Det samlede beløb er DKK 45.000 ekskl. moms for et års løsning.

Vil du have mig til at booke et møde til næste uge, så vi kan gennemgå detaljerne?

Med venlig hilsen,
Mathias Jensen
BeSafe Security Solutions
Tlf: +45 70 12 34 56
Email: mathias@besafe.dk""",
            "received_at": "2024-01-20T10:30:00Z",
            "conversation_id": "conv_001_dup",
            "email_thread": [
                {
                    "from": "peter.hansen@microsoft.com",
                    "to": "mathias@besafe.dk",
                    "subject": "Re: Sikkerhedsbehov - Microsoft Danmark",
                    "content": """Hej Mathias, tak for mødet i går. Kan du sende mig et tilbud på jeres sikkerhedsløsninger?

Med venlig hilsen,
Peter Hansen
IT Security Manager
Microsoft Danmark
Tlf: +45 33 25 50 00""",
                    "received_at": "2024-01-14T15:20:00Z",
                }
            ],
        },
        {
            "id": 2,
            "from": "mathias@besafe.dk",
            "to": "anna.jensen@novonordisk.com",
            "subject": "Forslag til sikkerhedsforbedringer - Novo Nordisk",
            "content": """Kære Anna,

Tak for mødet i går. Som lovet sender jeg dig et forslag til sikkerhedsforbedringer for jeres nye kontor.

Baseret på vores analyse foreslår jeg:
- Implementering af Zero Trust arkitektur
- Multi-factor authentication for alle systemer
- Regelmæssige security audits
- Backup og disaster recovery løsninger

Det samlede budget er DKK 125.000 ekskl. moms.

Kan du sende mig jeres feedback, så vi kan tilpasse løsningen?

Bedste hilsner,
Mathias
BeSafe Security""",
            "received_at": "2024-01-16T14:15:00Z",
            "conversation_id": "conv_002",
            "email_thread": [],
        },
        {
            "id": 3,
            "from": "mathias@besafe.dk",
            "to": "mads.nielsen@maersk.com",
            "subject": "Opfølgning på mødet - Maersk sikkerhedsprojekt",
            "content": """Hej Mads,

Tak for det gode møde i sidste uge om jeres sikkerhedsprojekt.

Som aftalt har jeg udarbejdet en detaljeret plan for implementeringen:
- Fase 1: Grundlæggende sikkerhed (DKK 35.000)
- Fase 2: Avancerede funktioner (DKK 35.000)
- Fase 3: Integration og træning (DKK 19.000)

Total: DKK 89.000 ekskl. moms

Kan vi booke et opfølgningsmøde til næste uge?

Med venlig hilsen,
Mathias Jensen
BeSafe Security Solutions
Tlf: +45 70 12 34 56""",
            "received_at": "2024-01-17T09:45:00Z",
            "conversation_id": "conv_003",
            "email_thread": [
                {
                    "from": "mads.nielsen@maersk.com",
                    "to": "mathias@besafe.dk",
                    "subject": "Re: Sikkerhedsprojekt - Maersk",
                    "content": """Hej Mathias, tak for mødet. Kan du sende mig en detaljeret plan?

Med venlig hilsen,
Mads Nielsen
Head of IT Security
Maersk Line
Tlf: +45 33 63 33 63""",
                    "received_at": "2024-01-16T11:30:00Z",
                },
                {
                    "from": "mathias@besafe.dk",
                    "to": "mads.nielsen@maersk.com",
                    "subject": "Re: Sikkerhedsprojekt - Maersk",
                    "content": """Hej Mads, jeg sender dig planen i morgen.

Med venlig hilsen,
Mathias Jensen
BeSafe Security Solutions""",
                    "received_at": "2024-01-16T16:45:00Z",
                },
            ],
        },
        {
            "id": 4,
            "from": "mathias@besafe.dk",
            "to": "support@besafe.dk",
            "subject": "IT Support - Printer problem",
            "content": """Hej IT Support,

Jeg har problemer med min printer. Den printer ikke korrekt og viser en fejlmeddelelse.

Kan I hjælpe mig med at løse dette?

Tak,
Mathias""",
            "received_at": "2024-01-18T11:20:00Z",
            "conversation_id": "conv_004",
            "email_thread": [],
        },
        {
            "id": 5,
            "from": "mathias@besafe.dk",
            "to": "lars.pedersen@grundfos.com",
            "subject": "Ny sikkerhedsløsning - Grundfos",
            "content": """Kære Lars,

Jeg håber, du har det godt. Jeg skriver fordi jeg har hørt om jeres nye kontor og tænkte, at I måske kunne have brug for vores sikkerhedsløsninger.

Vi tilbyder:
- Komplet sikkerhedspakke
- 24/7 overvågning
- Regelmæssige rapporter

Pris: DKK 75.000 ekskl. moms per år.

Vil du have mig til at sende et detaljeret tilbud?

Med venlig hilsen,
Mathias
BeSafe Security""",
            "received_at": "2024-01-19T15:30:00Z",
            "conversation_id": "conv_005",
            "email_thread": [],
        },
        {
            "id": 7,
            "from": "mathias@besafe.dk",
            "to": "test@example.com",
            "subject": "Test af nyt system - Example Corp",
            "content": """Hej Test Person,

Jeg håber, du har det godt. Jeg skriver fordi jeg har hørt om jeres nye projekt og tænkte, at I måske kunne have brug for vores sikkerhedsløsninger.

Vi tilbyder:
- Komplet sikkerhedspakke
- 24/7 overvågning
- Regelmæssige rapporter

Pris: DKK 50.000 ekskl. moms per år.

Vil du have mig til at sende et detaljeret tilbud?

Med venlig hilsen,
Mathias
BeSafe Security""",
            "received_at": "2024-01-21T15:30:00Z",
            "conversation_id": "conv_007",
            "email_thread": [],
        },
    ]

    print(f"✅ Loaded {len(sample_emails)} sample emails")
    return sample_emails


# =============================================================================
# CHUNK 4: AI Analysis
# =============================================================================


async def analyze_email_with_ai(api_key: str, email_data: Dict, model: str) -> Dict:
    """Analyze email content using OpenRouter API."""
    # Build full conversation context including current email and thread
    full_conversation = f"Current Email:\nFrom: {email_data['from']}\nTo: {email_data['to']}\nSubject: {email_data['subject']}\nContent: {email_data['content']}\n"
    if email_data.get("email_thread"):
        full_conversation += "\nPrevious emails in thread:\n"
        for i, thread_email in enumerate(email_data["email_thread"], 1):
            full_conversation += f"\nEmail {i}:\nFrom: {thread_email['from']}\nTo: {thread_email['to']}\nSubject: {thread_email['subject']}\nContent: {thread_email['content']}\n"

    prompt = f"""Analyze this email conversation and extract sales opportunity information:

{full_conversation}

Please provide a JSON response with the following structure:
{{
    "is_sales_opportunity": true/false,
    "confidence": 0.0-1.0,
    "opportunity_type": "new_business|upsell|follow_up|inquiry|other",
    "estimated_value": 0,
    "currency": "DKK",
    "urgency": "high|medium|low",
    "next_action": "schedule_meeting|send_proposal|follow_up|no_action",
    "person_name": "extracted_full_name_from_emails",
    "organization_name": "recipient_organization_from_signature_or_domain",
    "offering_type": "security_solution|software|crm|consulting|web_design|other",
    "key_points": ["point1", "point2"],
    "ai_generated": true
}}

Instructions:
1. Extract the recipient's full name from email addresses, signatures, or email content.
2. Extract the recipient's organization from the thread, signature, or the domain of the recipient's email address (e.g., lars.pedersen@grundfos.com -> Grundfos). Never use the sender's organization.
3. Determine the offering type from the conversation context.
4. Only respond with valid JSON. Use DKK as the default currency."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
            )
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                try:
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    if start != -1 and end != 0:
                        json_str = content[start:end]
                        result = json.loads(json_str)
                        required_fields = [
                            "is_sales_opportunity",
                            "confidence",
                            "opportunity_type",
                            "estimated_value",
                            "currency",
                            "urgency",
                            "next_action",
                            "person_name",
                            "organization_name",
                            "key_points",
                            "ai_generated",
                        ]
                        for field in required_fields:
                            if field not in result:
                                if field == "ai_generated":
                                    result[field] = True
                                elif field == "key_points":
                                    result[field] = []
                                elif field == "estimated_value":
                                    result[field] = 0
                                elif field == "currency":
                                    result[field] = "DKK"
                                else:
                                    result[field] = ""
                        return result
                    else:
                        raise ValueError("No JSON found in response")
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing JSON: {str(e)}")
                    print(f"Response content: {content}")
                    return {
                        "is_sales_opportunity": False,
                        "confidence": 0.0,
                        "opportunity_type": "other",
                        "estimated_value": 0,
                        "currency": "DKK",
                        "urgency": "low",
                        "next_action": "no_action",
                        "person_name": "",
                        "organization_name": "",
                        "key_points": [],
                        "ai_generated": True,
                    }
            else:
                print(
                    f"❌ OpenRouter API error: {response.status_code} - {response.text}"
                )
                return None
    except Exception as e:
        print(f"❌ Error analyzing email: {str(e)}")
        return {
            "is_sales_opportunity": False,
            "confidence": 0.0,
            "opportunity_type": "other",
            "estimated_value": 0,
            "currency": "DKK",
            "urgency": "low",
            "next_action": "no_action",
            "person_name": "",
            "organization_name": "",
            "key_points": [],
            "ai_generated": True,
        }


# =============================================================================
# CHUNK 5: Deal Management
# =============================================================================


async def check_and_manage_deals(
    pipedrive_client, email_data: Dict, ai_result: Dict, api_key: str, model: str
) -> Dict[str, Any]:
    """Check if contact exists and manage deals accordingly."""
    print(f"🔍 Checking deals for {email_data['to']}...")

    try:
        # Check if Pipedrive client is available
        if not pipedrive_client:
            print(f"⚠️  No Pipedrive client available - skipping contact/deal creation")
            return {
                "contact_exists": False,
                "contact": None,
                "deals": [],
                "has_deals": False,
                "deal_created": False,
            }

        # Step 1: Only proceed if it's a sales opportunity
        if not ai_result.get("is_sales_opportunity", False):
            print(f"⚠️  Not a sales opportunity - skipping contact/deal creation")
            return {
                "contact_exists": False,
                "contact": None,
                "deals": [],
                "has_deals": False,
                "deal_created": False,
            }

        # Step 2: Do all checks first
        deal_check = await pipedrive_client.contact_has_deals(email_data["to"])
        contact = deal_check.get("contact")
        contact_existed = bool(contact)

        # Check if contact has open deals
        has_open_deal = False
        if contact:
            has_open_deal = await pipedrive_client.has_open_deal(contact["id"])

        # Determine organization from email domain
        domain = email_data["to"].split("@")[-1].split(".")[0]
        organization_name = domain.capitalize()

        # Check if organization exists
        org_exists = False
        if organization_name:
            existing_org = await pipedrive_client.search_organization_by_name(
                organization_name
            )
            org_exists = bool(existing_org)
            if org_exists:
                print(f"🏢 Found existing organization: {organization_name}")

        # Step 3: Log the decision based on checks (before creation)
        if contact_existed:
            if org_exists:
                print(f"📋 Decision: Contact & organization already exist")
            else:
                print(f"📋 Decision: Contact exists, organization doesn't")
        else:
            if org_exists:
                print(f"📋 Decision: Organization exists, contact doesn't")
            else:
                print(f"📋 Decision: Neither contact nor organization exist")

        # Step 4: Create contact if it doesn't exist
        if not contact_existed:
            print(f"📝 Creating new contact...")
            person_name = ai_result.get("person_name") or email_data["to"].split("@")[0]
            contact_data = {
                "name": person_name,
                "email": email_data["to"],
            }
            if organization_name:
                contact_data["org_name"] = organization_name
            contact = await pipedrive_client.create_contact(
                contact_data,
                email=email_data["to"],
                email_content=email_data["content"],
                api_key=api_key,
                model=model,
            )
            if contact:
                deal_check["contact"] = contact
                deal_check["contact_exists"] = True
                print(f"✅ Created new contact: {contact['name']}")
            else:
                print(f"❌ Failed to create contact")
                return deal_check

        # Step 5: Create deal if no open deal exists
        if not has_open_deal:
            deal_result = await create_deal_if_needed(
                pipedrive_client, email_data, ai_result, deal_check, api_key, model
            )
            deal_check.update(deal_result)
        else:
            print(f"⚠️  Open deal exists - skipping deal creation")
            deal_check["deal_created"] = False
            deal_check["reason"] = "Open deal already exists for this person."

        # Add decision information to result for webhook categorization
        deal_check["contact_existed_before"] = contact_existed
        deal_check["org_existed_before"] = org_exists

        return deal_check

    except Exception as e:
        print(f"❌ Error in deal management: {str(e)}")
        return {
            "contact_exists": False,
            "contact": None,
            "deals": [],
            "has_deals": False,
            "deal_created": False,
        }


async def create_deal_if_needed(
    pipedrive_client,
    email_data: Dict,
    ai_result: Dict,
    deal_check: Dict,
    api_key: str,
    model: str,
) -> Dict[str, Any]:
    """Create a new deal if it's a sales opportunity."""

    try:
        existing_deals = deal_check.get("deals", [])
        contact = deal_check["contact"]
        if not contact:
            print(f"❌ No contact available for deal creation")
            return {"deal_created": False, "deal": None}

        # Check for any open deal for this person
        has_open = await pipedrive_client.has_open_deal(contact["id"])
        if has_open:
            print(f"⚠️  Open deal exists - skipping")
            return {
                "deal_created": False,
                "deal": None,
                "reason": "Open deal already exists for this person.",
            }

        person_name = ai_result.get("person_name", contact.get("name", "Unknown"))

        # Get organization name with fallbacks
        organization_name = contact.get("company_name")
        if not organization_name:
            organization_name = ai_result.get("organization_name")
        if not organization_name:
            # Fallback to domain-based organization name
            domain = email_data["to"].split("@")[-1].split(".")[0]
            organization_name = domain.capitalize()

        deal_title = f"AI: {person_name} - {organization_name}"

        deal_data = {
            "title": deal_title,
            "value": ai_result.get("estimated_value", 0),
            "currency": ai_result.get("currency", "DKK"),
        }
        deal = await pipedrive_client.create_deal(
            contact["id"], deal_data, org_id=contact.get("company_id")
        )
        if deal:
            print(f"✅ Deal created: {deal['title']}")
            await log_email_note(
                pipedrive_client, email_data, deal["id"], api_key, model
            )
            return {
                "deal_created": True,
                "deal": deal,
                "deals": existing_deals + [deal],
                "has_deals": True,
            }
        else:
            print(f"❌ Failed to create deal")
            return {"deal_created": False, "deal": None}
    except Exception as e:
        print(f"❌ Error creating deal: {str(e)}")
        return {"deal_created": False, "deal": None}


async def log_email_note(
    pipedrive_client, email_data: Dict, deal_id: int, api_key: str, model: str
):
    """Log the email conversation as a summary note in Pipedrive."""
    try:
        # Always create a conversation summary, even for single emails
        conversation = f"Latest email:\nFrom: {email_data['from']}\nTo: {email_data['to']}\nSubject: {email_data['subject']}\nContent: {email_data['content']}\n\n"

        if email_data.get("email_thread"):
            for i, thread_email in enumerate(reversed(email_data["email_thread"]), 1):
                conversation += f"Previous email {i}:\nFrom: {thread_email['from']}\nTo: {thread_email['to']}\nSubject: {thread_email['subject']}\nContent: {thread_email['content']}\n\n"

        # Generate AI summary of the entire conversation in Danish
        summary_prompt = f"""Opsummer denne e-mail samtale på dansk i 2-3 sætninger, med fokus på vigtige forretningspunkter, krav og næste skridt:

{conversation}

Opsummering:"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": summary_prompt}],
                        "max_tokens": 150,
                        "temperature": 0.3,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    summary = data["choices"][0]["message"]["content"].strip()
                    note_content = f"""Samtale Opsummering:

{summary}

E-mail Detaljer:
Fra: {email_data['from']}
Til: {email_data['to']}
Emne: {email_data['subject']}
Modtaget: {email_data['received_at']}
Antal e-mails: {len(email_data.get('email_thread', [])) + 1}

---
AI-genereret opsummering af e-mail analyse system."""
                else:
                    # Fallback to simple note if AI summary fails
                    note_content = f"""E-mail Samtale:

Fra: {email_data['from']}
Til: {email_data['to']}
Emne: {email_data['subject']}
Modtaget: {email_data['received_at']}

Indhold:
{email_data['content']}

Antal e-mails: {len(email_data.get('email_thread', [])) + 1}
---
Denne note blev automatisk genereret af AI e-mail analyse system."""
        except Exception as e:
            print(f"⚠️  AI summary failed, using simple note: {str(e)}")
            note_content = f"""E-mail Samtale:

Fra: {email_data['from']}
Til: {email_data['to']}
Emne: {email_data['subject']}
Modtaget: {email_data['received_at']}

Indhold:
{email_data['content']}

Antal e-mails: {len(email_data.get('email_thread', [])) + 1}
---
Denne note blev automatisk genereret af AI e-mail analyse system."""

        note_data = {
            "subject": f"Email: {email_data['subject']}",
            "content": note_content,
            "deal_id": deal_id,
        }

        note = await pipedrive_client.log_note(note_data)
        if note:
            print(f"✅ Note logged")
        else:
            print(f"❌ Note failed")

    except Exception as e:
        print(f"❌ Error logging note: {str(e)}")


# =============================================================================
# CHUNK 6: Main Testing Function
# =============================================================================


async def test_ai_analysis_with_pipedrive(
    api_key: str,
    model: str,
    sample_emails: List[Dict],
    expected_results: Dict,
    pipedrive_client,
):
    """Test the complete AI analysis and Pipedrive integration."""
    print("🚀 Starting AI analysis and Pipedrive integration test...")

    results = []

    for i, email_data in enumerate(sample_emails, 1):
        print(
            f"\n📧 Email {i}/{len(sample_emails)}: {email_data['to']} - {email_data['subject']}"
        )

        # Step 1: AI Analysis
        ai_result = await analyze_email_with_ai(api_key, email_data, model)

        if ai_result:
            print(
                f"🤖 AI: {ai_result.get('is_sales_opportunity')} | {ai_result.get('confidence')} | {ai_result.get('person_name')} | {ai_result.get('organization_name')}"
            )

            # Step 2: Pipedrive Integration
            deal_result = await check_and_manage_deals(
                pipedrive_client, email_data, ai_result, api_key, model
            )

            print(
                f"📊 Pipedrive: Contact={deal_result.get('contact_exists')} | Deals={len(deal_result.get('deals', []))}"
            )

            if deal_result.get("deal_created"):
                print(f"✅ New deal: {deal_result['deal']['title']}")

            # Categorize webhook outcome
            outcome = categorize_webhook_outcome(ai_result, deal_result)

            # Log the webhook outcome
            log_webhook_outcome(email_data, outcome, ai_result, deal_result)

            # Store results
            results.append(
                {
                    "email_id": email_data["id"],
                    "from": email_data["from"],
                    "to": email_data["to"],
                    "subject": email_data["subject"],
                    "ai_result": ai_result,
                    "pipedrive_result": deal_result,
                    "webhook_outcome": outcome,
                    "success": True,
                }
            )
        else:
            print(f"❌ AI analysis failed")
            results.append(
                {
                    "email_id": email_data["id"],
                    "from": email_data["from"],
                    "to": email_data["to"],
                    "subject": email_data["subject"],
                    "ai_result": None,
                    "pipedrive_result": None,
                    "success": False,
                }
            )

        print("-" * 40)

    return results


# =============================================================================
# CHUNK 7: Webhook Outcome Categorization
# =============================================================================


def categorize_webhook_outcome(ai_result: Dict, pipedrive_result: Dict) -> str:
    """
    Categorize the webhook outcome based on AI analysis and Pipedrive results.

    Returns one of:
    1. "Ignored: Not a sales deal"
    2. "Not created: Deal already exists"
    3. "Created: Contact & company already exists"
    4. "Created: Contact already exists"
    5. "Created: Company already exists"
    6. "Created: New contact, company & deal created"
    7. "Error: Failed to process"
    8. "Created: New contact created (no company)"
    9. "Skipped: Low confidence score"
    10. "Skipped: Invalid email format"
    11. "Skipped: Duplicate email detected"
    """

    # Check if AI analysis failed
    if not ai_result:
        return "Error: Failed to process"

    # Check for low confidence (optional - you can adjust threshold)
    confidence = ai_result.get("confidence", 0)
    if confidence < 0.3:  # Adjust threshold as needed
        return "Skipped: Low confidence score"

    # Check if it's not a sales opportunity
    if not ai_result.get("is_sales_opportunity", False):
        return "Ignored: Not a sales deal"

    # Check if Pipedrive integration failed
    if not pipedrive_result:
        return "Error: Failed to process"

    # Check if deal creation was skipped due to existing open deal
    if (
        pipedrive_result.get("deal_created") == False
        and pipedrive_result.get("reason")
        == "Open deal already exists for this person."
    ):
        return "Not created: Deal already exists"

    # Check if deal was created
    if pipedrive_result.get("deal_created", False):
        contact = pipedrive_result.get("contact", {})
        company_id = contact.get("company_id")
        company_name = contact.get("company_name")

        # Use the decision information from checks
        contact_existed = pipedrive_result.get("contact_existed_before", False)
        org_existed = pipedrive_result.get("org_existed_before", False)

        if contact_existed:  # Contact existed before
            if org_existed:  # Organization also existed
                return "Created: Contact & company already exists"
            else:  # Only contact existed
                return "Created: Contact already exists"
        else:  # New contact
            if org_existed:  # Organization existed
                return "Created: Company already exists"
            else:  # Neither existed
                return "Created: New contact, company & deal created"

    # Check if contact exists but no deal was created
    if pipedrive_result.get("contact_exists") and not pipedrive_result.get(
        "deal_created"
    ):
        contact = pipedrive_result.get("contact", {})
        if contact and contact.get("created_at") == contact.get(
            "updated_at"
        ):  # New contact
            return "Created: New contact created (no company)"
        else:  # Existing contact, no deal created
            return "Not created: Deal already exists"

    # If we get here, something went wrong
    return "Error: Failed to process"


def log_webhook_outcome(
    email_data: Dict,
    outcome: str,
    ai_result: Dict = None,
    pipedrive_result: Dict = None,
):
    """Log the webhook outcome in a structured format."""
    print(f"🎯 {outcome}")


# =============================================================================
# CHUNK 8: Results Analysis
# =============================================================================


def analyze_results(results: List[Dict], expected_results: Dict):
    """Analyze and display test results."""
    print("\n📊 RESULTS SUMMARY")

    total_emails = len(results)
    successful_analysis = sum(1 for r in results if r["success"])
    sales_opportunities = sum(
        1
        for r in results
        if r["success"] and r["ai_result"].get("is_sales_opportunity", False)
    )
    deals_created = sum(
        1
        for r in results
        if r["success"] and r["pipedrive_result"].get("deal_created", False)
    )

    # Count webhook outcomes
    outcome_counts = {}
    for result in results:
        if result["success"]:
            outcome = result.get("webhook_outcome", "Unknown")
            outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

    print(
        f"📈 {total_emails} emails | {successful_analysis} analyzed | {sales_opportunities} opportunities | {deals_created} deals created"
    )

    print(f"\n🎯 OUTCOMES:")
    for outcome, count in outcome_counts.items():
        print(f"  {outcome}: {count}")


# =============================================================================
# CHUNK 8: Main Execution
# =============================================================================


async def main():
    """Main execution function."""
    print("🚀 AI Email Analysis Prototype")
    print("=" * 60)

    try:
        # Setup
        api_key, model = setup_environment()
        sample_emails = load_sample_emails()

        # Try to setup Pipedrive, but continue if it fails
        pipedrive_client = None
        try:
            pipedrive_client = setup_pipedrive()
            print("\n🔗 Testing Pipedrive connection...")
            is_connected = await pipedrive_client.test_token()
            if not is_connected:
                print(
                    "❌ Failed to connect to Pipedrive - continuing with AI analysis only"
                )
                pipedrive_client = None
            else:
                print("✅ Pipedrive connection successful")
        except Exception as e:
            print(
                f"❌ Pipedrive setup failed: {str(e)} - continuing with AI analysis only"
            )
            pipedrive_client = None

        # Expected results for validation
        expected_results = {
            "microsoft.com": {"opportunity_type": "new_business", "has_deals": False},
            "novonordisk.com": {"opportunity_type": "inquiry", "has_deals": False},
            "maersk.com": {"opportunity_type": "follow_up", "has_deals": False},
        }

        # Run the complete test
        results = await test_ai_analysis_with_pipedrive(
            api_key, model, sample_emails, expected_results, pipedrive_client
        )

        # Analyze results
        analyze_results(results, expected_results)

        print("\n✅ Prototype completed successfully!")

    except Exception as e:
        print(f"❌ Error in main execution: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
