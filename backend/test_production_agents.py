#!/usr/bin/env python3
"""
Test Production Agents with Sample Emails

This script tests the production modular agents with the same sample emails used in the prototype.
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

# Now we can import from the app package
from agents.orchestrator import AgentOrchestrator
from monitoring.agent_logger import agent_logger


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
        # DUPLICATE 1: Peter Hansen - same recipient, different subject
        {
            "id": 5,
            "from": "mathias@besafe.dk",
            "to": "peter.hansen@microsoft.com",
            "subject": "Opfølgning på tilbud - Microsoft Danmark (DUPLICATE)",
            "content": """Hej Peter,

Jeg følger op på vores tidligere tilbud på sikkerhedsløsninger til Microsoft Danmark.

Har du haft mulighed for at gennemgå forslaget? Jeg er klar til at booke et møde for at diskutere detaljerne.

Vi kan tilbyde:
- Avancerede firewall-løsninger
- Endpoint protection
- Security awareness træning
- 24/7 support

Det samlede beløb er DKK 45.000 ekskl. moms for et års løsning.

Med venlig hilsen,
Mathias Jensen
BeSafe Security Solutions
Tlf: +45 70 12 34 56
Email: mathias@besafe.dk""",
            "received_at": "2024-01-20T10:30:00Z",
            "conversation_id": "conv_001_dup",
            "email_thread": [],
        },
        # DUPLICATE 2: Anna Jensen - same recipient, different subject
        {
            "id": 6,
            "from": "mathias@besafe.dk",
            "to": "anna.jensen@novonordisk.com",
            "subject": "Opfølgning på sikkerhedsforbedringer - Novo Nordisk (DUPLICATE)",
            "content": """Kære Anna,

Jeg følger op på vores tidligere forslag til sikkerhedsforbedringer for jeres nye kontor.

Har du haft mulighed for at gennemgå forslaget? Jeg er klar til at diskutere implementeringen.

Baseret på vores analyse foreslår jeg:
- Implementering af Zero Trust arkitektur
- Multi-factor authentication for alle systemer
- Regelmæssige security audits
- Backup og disaster recovery løsninger

Det samlede budget er DKK 125.000 ekskl. moms.

Bedste hilsner,
Mathias
BeSafe Security""",
            "received_at": "2024-01-21T14:15:00Z",
            "conversation_id": "conv_002_dup",
            "email_thread": [],
        },
    ]

    print(f"✅ Loaded {len(sample_emails)} sample emails")
    return sample_emails


async def test_production_agents():
    """Test the production agents with sample emails."""
    print("🚀 Testing Production Agents")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Check required environment variables
    required_vars = [
        "OPENROUTER_API_KEY",
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set the required environment variables and try again.")
        return

    # Load sample emails
    sample_emails = load_sample_emails()

    # Test user ID (you can change this to test with different users)
    test_user_id = "0babb68e-4bd5-4b2d-ac57-49826369178d"

    results = []

    for i, email_data in enumerate(sample_emails, 1):
        print(
            f"\n📧 Email {i}/{len(sample_emails)}: {email_data['to']} - {email_data['subject']}"
        )

        try:
            # Create orchestrator
            orchestrator = AgentOrchestrator(test_user_id)

            # Process email
            result = await orchestrator.process_email(email_data)

            if result["success"]:
                ai_result = result.get("ai_result")
                pipedrive_result = result.get("pipedrive_result")
                outcome = result.get("outcome")

                print(
                    f"🤖 AI: {ai_result.get('is_sales_opportunity')} | {ai_result.get('confidence')} | {ai_result.get('person_name')} | {ai_result.get('organization_name')}"
                )

                if pipedrive_result:
                    print(
                        f"📊 Pipedrive: Contact={pipedrive_result.get('contact_exists')} | Deals={len(pipedrive_result.get('deals', []))}"
                    )

                print(f"🎯 Outcome: {outcome}")
                print(f"⏱️  Processing time: {result.get('processing_time', 0):.2f}s")

                if pipedrive_result and pipedrive_result.get("deal_created"):
                    print(f"✅ New deal: {pipedrive_result['deal']['title']}")

            else:
                print(f"❌ Processing failed: {result.get('error')}")

            results.append(result)

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
    successful_processing = sum(
        1 for r in results if r is not None and r.get("success")
    )
    sales_opportunities = sum(
        1
        for r in results
        if r is not None
        and r.get("success")
        and r.get("ai_result", {}).get("is_sales_opportunity", False)
    )
    deals_created = sum(
        1
        for r in results
        if r is not None
        and r.get("success")
        and r.get("pipedrive_result") is not None
        and r.get("pipedrive_result", {}).get("deal_created", False)
    )
    contacts_created = sum(
        1
        for r in results
        if r is not None
        and r.get("success")
        and r.get("pipedrive_result") is not None
        and r.get("pipedrive_result", {}).get("contact_created", False)
    )
    deals_updated = sum(
        1
        for r in results
        if r is not None
        and r.get("success")
        and r.get("pipedrive_result") is not None
        and r.get("pipedrive_result", {}).get("deal_updated", False)
    )

    # Count outcomes
    outcome_counts = {}
    for result in results:
        if result is not None and result.get("success"):
            outcome = result.get("outcome", "Unknown")
            outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

    print(
        f"📈 {total_emails} emails | {successful_processing} processed | {sales_opportunities} opportunities | {deals_created} deals created | {contacts_created} contacts created | {deals_updated} deals updated"
    )

    print(f"\n🎯 OUTCOMES:")
    for outcome, count in outcome_counts.items():
        print(f"  {outcome}: {count}")

    print(f"\n✅ Production agents test completed!")


if __name__ == "__main__":
    asyncio.run(test_production_agents())
