"""
Email Analyzer Agent

This module handles AI-powered email analysis using OpenRouter API.
"""

import os
import json
import time
import httpx
from typing import Dict, Any, Optional

# Use absolute imports for testing compatibility
try:
    from app.lib.error_handler import handle_ai_errors, AIAnalysisError
    from app.monitoring.agent_logger import agent_logger
    from app.agents.prompts import (
        build_email_analysis_prompt,
        build_org_name_prompt,
        build_danish_summary_prompt,
    )
except ImportError:
    # Fallback for when running as module
    from ..lib.error_handler import handle_ai_errors, AIAnalysisError
    from ..monitoring.agent_logger import agent_logger
    from .prompts import (
        build_email_analysis_prompt,
        build_org_name_prompt,
        build_danish_summary_prompt,
    )


class EmailAnalyzer:
    """AI-powered email analyzer using OpenRouter API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("AI_MODEL", "openai/gpt-4o-mini")

        if not self.api_key:
            raise ValueError("OpenRouter API key not found")

    @handle_ai_errors
    async def analyze_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze email content using OpenRouter API."""
        agent_logger.log_ai_analysis_start(email_data)

        start_time = time.time()

        # Build the analysis prompt
        prompt = build_email_analysis_prompt(email_data)

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
                    raise AIAnalysisError(
                        f"OpenRouter API error: {response.status_code} - {response.text}"
                    )

                data = response.json()
                content = data["choices"][0]["message"]["content"]

                # Parse JSON response
                result = self._parse_ai_response(content)

                processing_time = time.time() - start_time
                agent_logger.log_ai_analysis_complete(result, processing_time)

                return result

        except Exception as e:
            agent_logger.error(
                "AI analysis failed",
                {
                    "error": str(e),
                    "email_to": email_data.get("to"),
                    "email_subject": email_data.get("subject"),
                },
            )
            raise

    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response and ensure all required fields are present."""
        try:
            # Extract JSON from response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")

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

        except json.JSONDecodeError as e:
            agent_logger.error(
                "Failed to parse AI response",
                {
                    "error": str(e),
                    "content": content[:200] + "..." if len(content) > 200 else content,
                },
            )

            # Return default result on parsing failure
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

    @handle_ai_errors
    async def extract_organization_name(
        self, domain: str, email_content: str
    ) -> Optional[str]:
        """Use AI to suggest a proper organization name from email domain and content."""
        prompt = build_org_name_prompt(domain, email_content)

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
                        "max_tokens": 16,
                        "temperature": 0.2,
                    },
                    timeout=15.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    name = data["choices"][0]["message"]["content"].strip()

                    # Filter out personal email providers
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
            agent_logger.error(
                "Organization name extraction failed",
                {"error": str(e), "domain": domain},
            )
            return None

    @handle_ai_errors
    async def generate_danish_summary(self, conversation: str) -> str:
        """Generate Danish summary of email conversation."""
        prompt = build_danish_summary_prompt(conversation)

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
                        "max_tokens": 150,
                        "temperature": 0.3,
                    },
                    timeout=20.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    raise AIAnalysisError(
                        f"OpenRouter API error: {response.status_code}"
                    )

        except Exception as e:
            agent_logger.error("Danish summary generation failed", {"error": str(e)})
            # Return fallback summary
            return "E-mail samtale blev analyseret af AI system."
