#!/usr/bin/env python3
"""
AI Email Analysis Prototype - Python Script Version

This script prototypes the AI email analysis system using OpenRouter API.
Divided into chunks like a notebook for easy execution and testing.

Usage:
    python ai_analysis_prototype.py

Prerequisites:
    1. Set OPENROUTER_API_KEY environment variable
    2. Install: pip install openai python-dotenv pandas
"""

import os
import json
import openai
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Optional

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

    # Configure OpenRouter client
    client = openai.OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

    # Default model
    default_model = os.getenv(
        "AI_MODEL", "openai/gpt-4o-mini"
    )  # Using GPT-4o Mini for cost efficiency

    print(f"✅ Using model: {default_model}")
    print(f"✅ OpenRouter client configured")

    return client, default_model


# =============================================================================
# CHUNK 2: Sample Emails Data
# =============================================================================


def load_sample_emails():
    """Load sample emails for testing."""
    print("\n📧 Loading sample emails...")

    sample_emails = [
        {
            "id": 1,
            "subject": "Special offer: 20% off enterprise software",
            "recipient": "john.doe@acme.com",
            "content": "Hi John, I wanted to follow up on our discussion about your company's software needs. I'm excited to offer you a special 20% discount on our enterprise solution if you sign up this month. This includes all premium features, 24/7 support, and a free migration service. Would you be interested in a demo to see the features in action? Best regards, Sarah",
        },
        {
            "id": 2,
            "subject": "Lunch invitation to discuss collaboration",
            "recipient": "jane.smith@techcorp.com",
            "content": "Hi Jane, I hope you're doing well! I was wondering if you'd like to grab lunch sometime this week? It would be great to catch up and discuss potential collaboration opportunities. Let me know what works for you. Cheers, Mike",
        },
        {
            "id": 3,
            "subject": "Proposal with pricing for your review",
            "recipient": "ceo@startup.com",
            "content": "Dear CEO, I'm excited to share our comprehensive proposal for your company's digital transformation project. Based on our analysis, we can help you increase efficiency by 40% and reduce costs by $200K annually. The total investment would be $150K with a 6-month implementation timeline. The proposal includes detailed ROI projections showing a 12-month payback period. Please let me know if you have any questions. Best regards, David",
        },
        {
            "id": 4,
            "subject": "Thanks for the coffee",
            "recipient": "friend@personal.com",
            "content": "Hey! Thanks for the coffee yesterday. It was great catching up. Let's do it again soon!",
        },
    ]

    print(f"✅ Loaded {len(sample_emails)} sample emails")

    # Expected results (manual assessment)
    expected_results = {
        1: True,  # Special offer with discount - opportunity
        2: False,  # Lunch invitation without offer - not opportunity
        3: True,  # Proposal with pricing - opportunity
        4: False,  # Thanks for coffee - not opportunity
    }

    return sample_emails, expected_results


# =============================================================================
# CHUNK 3: AI Analysis Function
# =============================================================================


def analyze_email_with_ai(client, email_data: Dict, model: str) -> Dict:
    """
    Analyze an email for sales opportunities using OpenRouter AI.

    Args:
        client: OpenRouter client
        email_data: Dictionary containing email information
        model: OpenRouter model to use

    Returns:
        Dictionary with analysis results
    """

    # Create the prompt for AI analysis
    prompt = f"""
Analyze this email to determine if it contains a specific offer or deal. Consider:
- Does the email contain a concrete offer (discount, pricing, special terms)?
- Is there a specific product or service being offered with clear value?
- Does the email include pricing, discounts, or specific deal terms?
- Is the recipient being offered something tangible to purchase or sign up for?

IMPORTANT: Only mark as opportunity if there is a specific offer or deal in the email. 
General invitations for coffee, meetings without offers, or vague collaboration discussions are NOT opportunities.

Email Details:
- Subject: {email_data['subject']}
- Recipient: {email_data['recipient']}
- Content: {email_data['content']}

Respond with a JSON object containing:
{{
    "is_opportunity": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation of why this is or isn't an opportunity",
    "deal_title": "suggested deal name or null if not an opportunity",
    "deal_value": estimated_value_or_null,
    "deal_stage": "prospecting/proposal/negotiation/closed or null",
    "next_action": "suggested next step or null"
}}

Be conservative in your assessment. Only mark as opportunity if there's a specific offer or deal.
"""

    try:
        # Call OpenRouter API
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,  # Low temperature for consistent results
        )

        # Parse the response
        result = json.loads(response.choices[0].message.content)

        # Add metadata
        result["model_used"] = model
        result["timestamp"] = datetime.now().isoformat()
        result["email_id"] = email_data["id"]
        result["tokens_used"] = response.usage.total_tokens if response.usage else None

        return result

    except Exception as e:
        return {
            "error": str(e),
            "is_opportunity": False,
            "confidence": 0.0,
            "reasoning": f"Error during analysis: {str(e)}",
            "model_used": model,
            "timestamp": datetime.now().isoformat(),
            "email_id": email_data["id"],
        }


# =============================================================================
# CHUNK 4: Test AI Analysis
# =============================================================================


def test_ai_analysis(
    client, model: str, sample_emails: List[Dict], expected_results: Dict
):
    """Test AI analysis on all sample emails."""
    print(f"\n🤖 Testing AI analysis with model: {model}")
    print("=" * 60)

    results = []
    total_cost_estimate = 0.0

    for email in sample_emails:
        print(f"📧 Analyzing email {email['id']}: {email['subject']}")

        result = analyze_email_with_ai(client, email, model)
        results.append(result)

        # Add expected result for comparison
        result["expected_opportunity"] = expected_results[email["id"]]
        result["correct"] = result["is_opportunity"] == expected_results[email["id"]]

        # Estimate cost (rough calculation)
        if result.get("tokens_used"):
            # GPT-4o Mini: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens
            cost_estimate = (result["tokens_used"] / 1_000_000) * 0.75  # Average cost
            total_cost_estimate += cost_estimate

        status = (
            "✅ OPPORTUNITY" if result.get("is_opportunity") else "❌ NOT OPPORTUNITY"
        )
        confidence = result.get("confidence", 0)
        correct = "✅" if result.get("correct") else "❌"

        print(f"  {status} (confidence: {confidence:.2f}) {correct}")

        if result.get("reasoning"):
            print(f"  Reasoning: {result['reasoning'][:100]}...")

        print()

    print(f"✅ Analysis complete for {len(results)} emails")
    print(f"💰 Estimated total cost: ${total_cost_estimate:.4f}")

    return results


# =============================================================================
# CHUNK 5: Results Analysis
# =============================================================================


def analyze_results(results: List[Dict], expected_results: Dict):
    """Analyze and display results."""
    print("\n📊 RESULTS ANALYSIS")
    print("=" * 60)

    # Create a summary DataFrame
    df_results = pd.DataFrame(results)

    # Calculate accuracy
    correct_predictions = sum(1 for r in results if r.get("correct", False))
    accuracy = correct_predictions / len(results)

    # Display summary statistics
    print(f"📈 SUMMARY STATISTICS:")
    print(f"   Total emails analyzed: {len(df_results)}")
    print(f"   Opportunities detected: {df_results['is_opportunity'].sum()}")
    print(f"   Non-opportunities: {(~df_results['is_opportunity']).sum()}")
    print(f"   Correct predictions: {correct_predictions}/{len(results)}")
    print(f"   Accuracy: {accuracy:.2%}")
    print(f"   Average confidence: {df_results['confidence'].mean():.2f}")
    print(f"   Model used: {df_results['model_used'].iloc[0]}")

    # Show detailed results
    print(f"\n📋 DETAILED RESULTS:")
    for idx, row in df_results.iterrows():
        email_id = row["email_id"]
        status = "✅ OPPORTUNITY" if row["is_opportunity"] else "❌ NOT OPPORTUNITY"
        correct = "✅" if row.get("correct") else "❌"
        confidence = row["confidence"]

        print(f"\nEmail {email_id}: {status} {correct}")
        print(f"  Confidence: {confidence:.2f}")
        print(
            f"  Expected: {'Opportunity' if expected_results[email_id] else 'Not Opportunity'}"
        )

        if row.get("reasoning"):
            print(f"  Reasoning: {row['reasoning']}")

        if row.get("deal_title"):
            print(f"  Deal Title: {row['deal_title']}")

        if row.get("next_action"):
            print(f"  Next Action: {row['next_action']}")

        print("-" * 40)

    return df_results, accuracy


# =============================================================================
# CHUNK 6: Save Results
# =============================================================================


def save_results(results: List[Dict], model: str, accuracy: float):
    """Save results to JSON file for comparison."""
    print(f"\n💾 Saving results...")

    results_data = {
        "model": model,
        "timestamp": datetime.now().isoformat(),
        "total_emails": len(results),
        "accuracy": accuracy,
        "results": results,
    }

    filename = f"results_{model.replace('/', '_')}.json"
    with open(filename, "w") as f:
        json.dump(results_data, f, indent=2)

    print(f"✅ Results saved to: {filename}")
    return filename


# =============================================================================
# CHUNK 7: Cost Analysis
# =============================================================================


def analyze_costs(results: List[Dict], model: str):
    """Analyze costs for the analysis."""
    print(f"\n💰 COST ANALYSIS")
    print("=" * 60)

    total_tokens = sum(r.get("tokens_used", 0) for r in results)
    avg_tokens = total_tokens / len(results) if results else 0

    # Cost estimates for different models (per 1M tokens)
    model_costs = {
        "openai/gpt-4o-mini": 0.75,  # Average of input/output
        "openai/gpt-4-1106-preview": 20.0,
        "openai/gpt-3.5-turbo": 1.0,
        "anthropic/claude-3-sonnet": 9.0,
        "google/gemini-pro": 1.0,
        "meta-llama/llama-2-70b-chat": 0.2,
    }

    cost_per_million = model_costs.get(model, 1.0)
    total_cost = (total_tokens / 1_000_000) * cost_per_million

    print(f"📊 TOKEN USAGE:")
    print(f"   Total tokens used: {total_tokens:,}")
    print(f"   Average tokens per email: {avg_tokens:.0f}")
    print(f"   Cost per 1M tokens: ${cost_per_million:.2f}")
    print(f"   Total cost: ${total_cost:.4f}")

    # Monthly projections
    monthly_scenarios = {
        "Low Volume (100 emails)": 100,
        "Medium Volume (500 emails)": 500,
        "High Volume (2000 emails)": 2000,
        "Enterprise (10000 emails)": 10000,
    }

    print(f"\n📈 MONTHLY COST PROJECTIONS:")
    for scenario, emails in monthly_scenarios.items():
        monthly_cost = (avg_tokens * emails / 1_000_000) * cost_per_million
        print(f"   {scenario}: ${monthly_cost:.2f}/month")

    return total_cost, avg_tokens


# =============================================================================
# CHUNK 8: Main Execution
# =============================================================================


def main():
    """Main execution function."""
    print("🚀 AI Email Analysis Prototype")
    print("=" * 60)

    try:
        # Chunk 1: Setup
        client, model = setup_environment()

        # Chunk 2: Load data
        sample_emails, expected_results = load_sample_emails()

        # Chunk 3-4: Test analysis
        results = test_ai_analysis(client, model, sample_emails, expected_results)

        # Chunk 5: Analyze results
        df_results, accuracy = analyze_results(results, expected_results)

        # Summary
        print(f"\n🎉 ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"✅ Model: {model}")
        print(f"✅ Accuracy: {accuracy:.2%}")

        if accuracy >= 0.8:
            print(f"🎯 EXCELLENT! Accuracy above 80% threshold")
        elif accuracy >= 0.7:
            print(f"👍 GOOD! Accuracy above 70% threshold")
        else:
            print(f"⚠️  NEEDS IMPROVEMENT! Accuracy below 70%")

        print(f"\n📝 Next steps:")
        print(f"   1. Review detailed results above")
        print(f"   2. Run with different models for comparison")
        print(f"   3. Integrate into webhook pipeline")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"💡 Make sure OPENROUTER_API_KEY is set in your environment")


if __name__ == "__main__":
    main()
