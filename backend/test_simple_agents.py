#!/usr/bin/env python3
"""
Simple Test for Production Agents

This script tests the core AI analysis functionality without complex imports.
"""

import asyncio
import os
import json
import time
import httpx
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SimpleEmailAnalyzer:
    """Simplified email analyzer for testing."""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("AI_MODEL", "openai/gpt-4o-mini")

        if not self.api_key:
            raise ValueError("OpenRouter API key not found")

    async def analyze_email(self, email_data: dict) -> dict:
        """Analyze email content using OpenRouter API."""
        print(f"🤖 Analyzing email: {email_data['to']} - {email_data['subject']}")

        # Build conversation context
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
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                    },
                    timeout=30.0,
                )

                if response.status_code != 200:
                    print(
                        f"❌ OpenRouter API error: {response.status_code} - {response.text}"
                    )
                    return None

                data = response.json()
                content = data["choices"][0]["message"]["content"]

                # Parse JSON response
                start = content.find("{")
                end = content.rfind("}") + 1
                if start != -1 and end != 0:
                    json_str = content[start:end]
                    result = json.loads(json_str)

                    # Ensure all required fields are present
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
                    print(f"❌ No JSON found in response: {content}")
                    return None

        except Exception as e:
            print(f"❌ Error analyzing email: {str(e)}")
            return None


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
    ]

    print(f"✅ Loaded {len(sample_emails)} sample emails")
    return sample_emails


async def test_simple_agents():
    """Test the simple email analyzer with sample emails."""
    print("🚀 Testing Simple Email Analyzer")
    print("=" * 60)

    # Check required environment variables
    required_vars = ["OPENROUTER_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set the required environment variables and try again.")
        return

    # Load sample emails
    sample_emails = load_sample_emails()

    # Create analyzer
    analyzer = SimpleEmailAnalyzer()

    results = []

    for i, email_data in enumerate(sample_emails, 1):
        print(
            f"\n📧 Email {i}/{len(sample_emails)}: {email_data['to']} - {email_data['subject']}"
        )

        try:
            start_time = time.time()

            # Analyze email
            ai_result = await analyzer.analyze_email(email_data)

            processing_time = time.time() - start_time

            if ai_result:
                print(
                    f"🤖 AI: {ai_result.get('is_sales_opportunity')} | {ai_result.get('confidence')} | {ai_result.get('person_name')} | {ai_result.get('organization_name')}"
                )
                print(
                    f"💰 Value: {ai_result.get('estimated_value')} {ai_result.get('currency')}"
                )
                print(f"🎯 Type: {ai_result.get('opportunity_type')}")
                print(f"⏱️  Processing time: {processing_time:.2f}s")

                results.append(
                    {
                        "success": True,
                        "ai_result": ai_result,
                        "processing_time": processing_time,
                    }
                )
            else:
                print(f"❌ AI analysis failed")
                results.append(
                    {
                        "success": False,
                        "error": "AI analysis failed",
                        "processing_time": processing_time,
                    }
                )

        except Exception as e:
            print(f"❌ Error processing email: {str(e)}")
            results.append(
                {"success": False, "error": str(e), "email_id": email_data["id"]}
            )

        print("-" * 40)

    # Analyze results
    analyze_results(results)


def analyze_results(results: list):
    """Analyze and display test results."""
    print("\n📊 RESULTS SUMMARY")
    print("=" * 60)

    total_emails = len(results)
    successful_analysis = sum(1 for r in results if r["success"])
    sales_opportunities = sum(
        1
        for r in results
        if r["success"] and r.get("ai_result", {}).get("is_sales_opportunity", False)
    )

    # Count opportunity types
    opportunity_types = {}
    for result in results:
        if result["success"]:
            opp_type = result.get("ai_result", {}).get("opportunity_type", "unknown")
            opportunity_types[opp_type] = opportunity_types.get(opp_type, 0) + 1

    print(
        f"📈 {total_emails} emails | {successful_analysis} analyzed | {sales_opportunities} opportunities"
    )

    print(f"\n🎯 OPPORTUNITY TYPES:")
    for opp_type, count in opportunity_types.items():
        print(f"  {opp_type}: {count}")

    print(f"\n✅ Simple email analyzer test completed!")


if __name__ == "__main__":
    asyncio.run(test_simple_agents())
