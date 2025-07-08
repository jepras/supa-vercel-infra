import os
import openai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import sys

# Add the app directory to the Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.orchestrator import AgentOrchestrator

router = APIRouter()

# Configure OpenRouter client
client = openai.OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1"
)


class TestRequest(BaseModel):
    message: str
    model: Optional[str] = "openai/gpt-3.5-turbo"


class TestResponse(BaseModel):
    success: bool
    response: str
    model_used: str
    error: Optional[str] = None


class ProductionTestResponse(BaseModel):
    success: bool
    results: list
    summary: Dict[str, Any]
    error: Optional[str] = None


@router.post("/test", response_model=TestResponse)
async def test_openrouter(request: TestRequest):
    """Test OpenRouter connectivity with a simple message."""

    if not os.getenv("OPENROUTER_API_KEY"):
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")

    try:
        response = client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.message}],
            max_tokens=100,
            temperature=0.1,
        )

        return TestResponse(
            success=True,
            response=response.choices[0].message.content,
            model_used=request.model,
        )

    except Exception as e:
        return TestResponse(
            success=False, response="", model_used=request.model, error=str(e)
        )


@router.get("/health")
async def ai_health_check():
    """Health check for AI service."""
    return {
        "status": "healthy",
        "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY")),
        "default_model": os.getenv("AI_MODEL", "openai/gpt-4-1106-preview"),
    }


@router.post("/test-production-agents", response_model=ProductionTestResponse)
async def test_production_agents():
    """Test production AI agents with sample emails in production environment."""

    # Check required environment variables
    required_vars = [
        "OPENROUTER_API_KEY",
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        return ProductionTestResponse(
            success=False,
            results=[],
            summary={},
            error=f"Missing required environment variables: {missing_vars}",
        )

    # Sample emails for testing
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
        },
        {
            "id": 3,
            "from": "mathias@besafe.dk",
            "to": "support@besafe.dk",
            "subject": "IT Support - Printer problem",
            "content": """Hej IT Support,

Jeg har problemer med min printer. Den printer ikke korrekt og viser en fejlmeddelelse.

Kan I hjælpe mig med at løse dette?

Tak,
Mathias""",
            "received_at": "2024-01-18T11:20:00Z",
        },
    ]

    # Test user ID (you can change this to test with different users)
    test_user_id = "0babb68e-4bd5-4b2d-ac57-49826369178d"

    results = []

    try:
        for i, email_data in enumerate(sample_emails, 1):
            try:
                # Create orchestrator
                orchestrator = AgentOrchestrator(test_user_id)

                # Process email
                result = await orchestrator.process_email(email_data)

                # Add email info to result
                result["email_info"] = {
                    "id": email_data["id"],
                    "to": email_data["to"],
                    "subject": email_data["subject"],
                }

                results.append(result)

            except Exception as e:
                results.append(
                    {
                        "success": False,
                        "error": str(e),
                        "email_info": {
                            "id": email_data["id"],
                            "to": email_data["to"],
                            "subject": email_data["subject"],
                        },
                    }
                )

        # Calculate summary
        total_emails = len(results)
        successful_processing = sum(1 for r in results if r.get("success"))
        sales_opportunities = sum(
            1
            for r in results
            if r.get("success")
            and r.get("ai_result", {}).get("is_sales_opportunity", False)
        )
        deals_created = sum(
            1
            for r in results
            if r.get("success")
            and r.get("pipedrive_result", {}).get("deal_created", False)
        )

        # Count outcomes
        outcome_counts = {}
        for result in results:
            if result.get("success"):
                outcome = result.get("outcome", "Unknown")
                outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

        summary = {
            "total_emails": total_emails,
            "successful_processing": successful_processing,
            "sales_opportunities": sales_opportunities,
            "deals_created": deals_created,
            "outcome_counts": outcome_counts,
        }

        return ProductionTestResponse(success=True, results=results, summary=summary)

    except Exception as e:
        return ProductionTestResponse(
            success=False,
            results=[],
            summary={},
            error=f"Production test failed: {str(e)}",
        )
