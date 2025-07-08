"""
AI Prompt Templates

This module contains all AI prompt templates used for email analysis.
"""

# Email Analysis Prompt
EMAIL_ANALYSIS_PROMPT = """Analyze this email conversation and extract sales opportunity information:

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

# Organization Name Extraction Prompt
ORG_NAME_PROMPT = """Extract the most likely real company name from this email domain and content. If it's a personal email, return an empty string.
Domain: {domain}
Email content: {email_content}
Company name: """

# Danish Email Summary Prompt
DANISH_SUMMARY_PROMPT = """Opsummer denne e-mail samtale på dansk i 2-3 sætninger, med fokus på vigtige forretningspunkter, krav og næste skridt:

{conversation}

Opsummering:"""


def build_email_analysis_prompt(email_data: dict) -> str:
    """Build the full email analysis prompt with conversation context."""
    # Build full conversation context including current email and thread
    full_conversation = f"Current Email:\nFrom: {email_data['from']}\nTo: {email_data['to']}\nSubject: {email_data['subject']}\nContent: {email_data['content']}\n"

    if email_data.get("email_thread"):
        full_conversation += "\nPrevious emails in thread:\n"
        for i, thread_email in enumerate(email_data["email_thread"], 1):
            full_conversation += f"\nEmail {i}:\nFrom: {thread_email['from']}\nTo: {thread_email['to']}\nSubject: {thread_email['subject']}\nContent: {thread_email['content']}\n"

    return EMAIL_ANALYSIS_PROMPT.format(full_conversation=full_conversation)


def build_org_name_prompt(domain: str, email_content: str) -> str:
    """Build the organization name extraction prompt."""
    return ORG_NAME_PROMPT.format(domain=domain, email_content=email_content)


def build_danish_summary_prompt(conversation: str) -> str:
    """Build the Danish summary prompt."""
    return DANISH_SUMMARY_PROMPT.format(conversation=conversation)
