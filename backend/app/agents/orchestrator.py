"""
Agent Orchestrator

This module coordinates the email processing flow between AI analysis and Pipedrive operations.
"""

import time
from typing import Dict, Any, Optional

# Use absolute imports for testing compatibility
try:
    from app.lib.error_handler import (
        log_activity_to_supabase,
        log_opportunity_to_supabase,
        create_correlation_id,
    )
    from app.monitoring.agent_logger import agent_logger
    from app.agents.analyze_email import EmailAnalyzer
    from app.agents.pipedrive_manager import PipedriveManager
except ImportError:
    # Fallback for when running as module
    from ..lib.error_handler import (
        log_activity_to_supabase,
        log_opportunity_to_supabase,
        create_correlation_id,
    )
    from ..monitoring.agent_logger import agent_logger
    from .analyze_email import EmailAnalyzer
    from .pipedrive_manager import PipedriveManager


class AgentOrchestrator:
    """Coordinates AI analysis and Pipedrive operations for email processing."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.email_analyzer = EmailAnalyzer()
        self.pipedrive_manager = PipedriveManager(user_id)
        self.correlation_id = create_correlation_id()

        # Set correlation ID for logging
        agent_logger.set_correlation_id(self.correlation_id)

    async def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email through the complete AI analysis and Pipedrive integration flow."""
        start_time = time.time()

        agent_logger.info(
            "Starting email processing",
            {
                "correlation_id": self.correlation_id,
                "email_to": email_data.get("to"),
                "email_subject": email_data.get("subject"),
            },
        )

        try:
            # Step 1: AI Analysis
            ai_result = await self._analyze_email(email_data)

            if not ai_result:
                return self._create_error_result("AI analysis failed")

            # Step 2: Check if it's a sales opportunity
            if not ai_result.get("is_sales_opportunity", False):
                outcome = "Ignored: Not a sales deal"
                agent_logger.log_webhook_outcome(outcome, email_data)

                # Log activity for non-opportunities (GDPR compliant - no email storage)
                await log_activity_to_supabase(
                    self.user_id,
                    "email_analyzed",
                    "success",
                    f"Email analyzed for {email_data.get('to')} - No opportunity detected",
                    {
                        "opportunity_detected": False,
                        "confidence": ai_result.get("confidence", 0),
                        "correlation_id": self.correlation_id,
                    },
                )

                return {
                    "success": True,
                    "ai_result": ai_result,
                    "pipedrive_result": None,
                    "outcome": outcome,
                    "processing_time": time.time() - start_time,
                }

            # Step 3: Pipedrive Integration
            pipedrive_result = await self._handle_pipedrive_operations(
                email_data, ai_result
            )

            # Step 4: Categorize outcome
            outcome = self._categorize_webhook_outcome(ai_result, pipedrive_result)
            agent_logger.log_webhook_outcome(outcome, email_data)

            # Step 5: Log opportunity analysis only if deal was created (GDPR compliant)
            if pipedrive_result and pipedrive_result.get("deal_created", False):
                await log_opportunity_to_supabase(
                    self.user_id, email_data, ai_result, pipedrive_result
                )

            # Step 6: Log activity
            await self._log_activity(email_data, ai_result, pipedrive_result, outcome)

            processing_time = time.time() - start_time

            agent_logger.info(
                "Email processing completed",
                {
                    "correlation_id": self.correlation_id,
                    "outcome": outcome,
                    "processing_time": processing_time,
                },
            )

            return {
                "success": True,
                "ai_result": ai_result,
                "pipedrive_result": pipedrive_result,
                "outcome": outcome,
                "processing_time": processing_time,
                "correlation_id": self.correlation_id,
            }

        except Exception as e:
            processing_time = time.time() - start_time
            agent_logger.error(
                "Email processing failed",
                {
                    "correlation_id": self.correlation_id,
                    "error": str(e),
                    "processing_time": processing_time,
                },
            )

            return self._create_error_result(
                f"Processing failed: {str(e)}", processing_time
            )

    async def _analyze_email(
        self, email_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Analyze email using AI."""
        try:
            return await self.email_analyzer.analyze_email(email_data)
        except Exception as e:
            agent_logger.error("AI analysis failed", {"error": str(e)})
            return None

    async def _handle_pipedrive_operations(
        self, email_data: Dict[str, Any], ai_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle all Pipedrive operations for the email."""
        try:
            # Check if Pipedrive is available
            if not self.pipedrive_manager:
                return {
                    "contact_exists": False,
                    "contact": None,
                    "deals": [],
                    "has_deals": False,
                    "deal_created": False,
                    "error": "Pipedrive not available",
                }

            # Step 1: Check existing contact and deals
            deal_check = await self.pipedrive_manager.contact_has_deals(
                email_data["to"]
            )
            contact = deal_check.get("contact")
            contact_existed = bool(contact)

            # Check if contact has open deals
            has_open_deal = False
            if contact:
                has_open_deal = await self.pipedrive_manager.has_open_deal(
                    contact["id"]
                )

            # Determine organization from email domain
            domain = email_data["to"].split("@")[-1].split(".")[0]
            organization_name = domain.capitalize()

            # Check if organization exists
            org_exists = False
            if organization_name:
                existing_org = await self.pipedrive_manager.search_organization_by_name(
                    organization_name
                )
                org_exists = bool(existing_org)

            # Step 2: Create contact if it doesn't exist
            if not contact_existed:
                person_name = (
                    ai_result.get("person_name") or email_data["to"].split("@")[0]
                )
                contact_data = {
                    "name": person_name,
                    "email": email_data["to"],
                }
                if organization_name:
                    contact_data["org_name"] = organization_name

                contact = await self.pipedrive_manager.create_contact(contact_data)
                if contact:
                    deal_check["contact"] = contact
                    deal_check["contact_exists"] = True

            # Step 3: Create deal if no open deal exists
            if not has_open_deal:
                deal_result = await self._create_deal_if_needed(
                    email_data, ai_result, deal_check
                )
                deal_check.update(deal_result)
            else:
                deal_check["deal_created"] = False
                deal_check["reason"] = "Open deal already exists for this person."

            # Add decision information
            deal_check["contact_existed_before"] = contact_existed
            deal_check["org_existed_before"] = org_exists

            return deal_check

        except Exception as e:
            agent_logger.error("Pipedrive operations failed", {"error": str(e)})
            return {
                "contact_exists": False,
                "contact": None,
                "deals": [],
                "has_deals": False,
                "deal_created": False,
                "error": str(e),
            }

    async def _create_deal_if_needed(
        self,
        email_data: Dict[str, Any],
        ai_result: Dict[str, Any],
        deal_check: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new deal if it's a sales opportunity."""
        try:
            existing_deals = deal_check.get("deals", [])
            contact = deal_check["contact"]

            if not contact:
                return {"deal_created": False, "deal": None}

            # Check for any open deal for this person
            has_open = await self.pipedrive_manager.has_open_deal(contact["id"])
            if has_open:
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

            deal = await self.pipedrive_manager.create_deal(
                contact["id"], deal_data, org_id=contact.get("company_id")
            )

            if deal:
                # Log email note
                await self._log_email_note(email_data, deal["id"])

                return {
                    "deal_created": True,
                    "deal": deal,
                    "deals": existing_deals + [deal],
                    "has_deals": True,
                }
            else:
                return {"deal_created": False, "deal": None}

        except Exception as e:
            agent_logger.error("Deal creation failed", {"error": str(e)})
            return {"deal_created": False, "deal": None}

    async def _log_email_note(self, email_data: Dict[str, Any], deal_id: int):
        """Log the email conversation as a summary note in Pipedrive."""
        try:
            # Build conversation text
            conversation = f"Latest email:\nFrom: {email_data['from']}\nTo: {email_data['to']}\nSubject: {email_data['subject']}\nContent: {email_data['content']}\n\n"

            if email_data.get("email_thread"):
                for i, thread_email in enumerate(
                    reversed(email_data["email_thread"]), 1
                ):
                    conversation += f"Previous email {i}:\nFrom: {thread_email['from']}\nTo: {thread_email['to']}\nSubject: {thread_email['subject']}\nContent: {thread_email['content']}\n\n"

            # Generate AI summary
            summary = await self.email_analyzer.generate_danish_summary(conversation)

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

            note_data = {
                "content": note_content,
                "deal_id": deal_id,
            }

            await self.pipedrive_manager.log_note(note_data)

        except Exception as e:
            agent_logger.error("Note logging failed", {"error": str(e)})

    def _categorize_webhook_outcome(
        self, ai_result: Dict[str, Any], pipedrive_result: Dict[str, Any]
    ) -> str:
        """Categorize the webhook outcome based on AI analysis and Pipedrive results."""
        # Check if AI analysis failed
        if not ai_result:
            return "Error: Failed to process"

        # Check for low confidence
        confidence = ai_result.get("confidence", 0)
        if confidence < 0.3:
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
            contact_existed = pipedrive_result.get("contact_existed_before", False)
            org_existed = pipedrive_result.get("org_existed_before", False)

            if contact_existed:
                if org_existed:
                    return "Created: Contact & company already exists"
                else:
                    return "Created: Contact already exists"
            else:
                if org_existed:
                    return "Created: Company already exists"
                else:
                    return "Created: New contact, company & deal created"

        # Check if contact exists but no deal was created
        if pipedrive_result.get("contact_exists") and not pipedrive_result.get(
            "deal_created"
        ):
            contact = pipedrive_result.get("contact", {})
            if contact and contact.get("created_at") == contact.get("updated_at"):
                return "Created: New contact created (no company)"
            else:
                return "Not created: Deal already exists"

        # If we get here, something went wrong
        return "Error: Failed to process"

    async def _log_activity(
        self,
        email_data: Dict[str, Any],
        ai_result: Dict[str, Any],
        pipedrive_result: Dict[str, Any],
        outcome: str,
    ):
        """Log activity to Supabase for real-time updates."""
        try:
            # Always log the analysis activity
            await log_activity_to_supabase(
                self.user_id,
                "email_analyzed",
                "success",
                f"Email analyzed for {email_data.get('to')} - {outcome}",
                {
                    "opportunity_detected": ai_result.get(
                        "is_sales_opportunity", False
                    ),
                    "confidence": ai_result.get("confidence", 0),
                    "outcome": outcome,
                    "correlation_id": self.correlation_id,
                    "deal_created": (
                        pipedrive_result.get("deal_created", False)
                        if pipedrive_result
                        else False
                    ),
                },
            )

        except Exception as e:
            agent_logger.error("Failed to log activity", {"error": str(e)})

    def _create_error_result(
        self, error_message: str, processing_time: float = 0
    ) -> Dict[str, Any]:
        """Create error result structure."""
        return {
            "success": False,
            "error": error_message,
            "ai_result": None,
            "pipedrive_result": None,
            "outcome": f"Error: {error_message}",
            "processing_time": processing_time,
            "correlation_id": self.correlation_id,
        }
