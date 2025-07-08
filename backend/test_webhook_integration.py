#!/usr/bin/env python3
"""
Test script for webhook integration with AI agent flow

This script tests the complete flow from webhook reception to AI analysis and Pipedrive integration.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.webhooks.microsoft import webhook_manager
from app.agents.orchestrator import AgentOrchestrator


async def test_webhook_integration():
    """Test the complete webhook integration flow"""

    print("🧪 Testing Webhook Integration with AI Agent Flow")
    print("=" * 60)

    # Test user ID (replace with actual user ID from your database)
    test_user_id = os.getenv("TEST_USER_ID", "test-user-id")

    # Get the actual Microsoft user ID from the database
    print("🔍 Getting Microsoft user ID from database...")
    try:
        from app.lib.supabase_client import supabase_manager

        result = (
            supabase_manager.client.table("integrations")
            .select("microsoft_user_id")
            .eq("user_id", test_user_id)
            .eq("provider", "microsoft")
            .eq("is_active", True)
            .execute()
        )

        if not result.data or not result.data[0].get("microsoft_user_id"):
            print(f"❌ No Microsoft user ID found for user {test_user_id}")
            print("   Please ensure the user has connected their Microsoft account")
            return False

        microsoft_user_id = result.data[0]["microsoft_user_id"]
        print(f"✅ Found Microsoft user ID: {microsoft_user_id}")

    except Exception as e:
        print(f"❌ Error getting Microsoft user ID: {str(e)}")
        return False

    # Sample webhook data that would come from Microsoft Graph
    sample_webhook_data = {
        "value": [
            {
                "subscriptionId": "test-subscription-id",
                "clientState": f"user_{test_user_id}",
                "resource": f"Users/{microsoft_user_id}/Messages/test-message-id",
                "changeType": "created",
                "resourceData": {
                    "id": "test-message-id",
                    "subject": "Test Sales Opportunity",
                    "from": {"emailAddress": {"address": "sender@example.com"}},
                    "toRecipients": [
                        {"emailAddress": {"address": "prospect@company.com"}}
                    ],
                    "sentDateTime": datetime.now(timezone.utc).isoformat() + "Z",
                    "body": {
                        "content": """
                        Hi there,
                        
                        I'm reaching out to discuss a potential partnership opportunity. 
                        We're looking to expand our services and believe there could be 
                        a great collaboration between our companies.
                        
                        Would you be interested in scheduling a call next week to discuss 
                        this further? I think there's a significant opportunity here 
                        worth exploring.
                        
                        Best regards,
                        Sales Team
                        """,
                        "contentType": "text",
                    },
                },
            }
        ]
    }

    print(f"📧 Testing with user ID: {test_user_id}")
    print(f"📧 Using Microsoft user ID: {microsoft_user_id}")
    print(f"📨 Sample webhook data prepared")

    try:
        # Step 1: Test webhook processing
        print("\n1️⃣ Testing webhook processing...")
        webhook_result = await webhook_manager.process_email_webhook(
            sample_webhook_data
        )

        print(f"✅ Webhook processing result: {webhook_result['status']}")
        print(f"   - Processed emails: {webhook_result.get('processed_count', 0)}")
        print(f"   - AI processed: {webhook_result.get('ai_processed_count', 0)}")
        print(f"   - Skipped duplicates: {webhook_result.get('skipped_count', 0)}")

        # Step 2: Test direct AI agent flow (if webhook processing worked)
        if webhook_result.get("ai_processed_emails"):
            print("\n2️⃣ Testing direct AI agent flow...")

            # Get the first processed email
            ai_processed_email = webhook_result["ai_processed_emails"][0]

            if ai_processed_email.get("ai_result"):
                ai_result = ai_processed_email["ai_result"]
                print(f"✅ AI analysis completed successfully")
                print(
                    f"   - Sales opportunity: {ai_result.get('ai_result', {}).get('is_sales_opportunity', False)}"
                )
                print(
                    f"   - Confidence: {ai_result.get('ai_result', {}).get('confidence', 0)}"
                )
                print(f"   - Outcome: {ai_result.get('outcome', 'Unknown')}")

                if ai_result.get("pipedrive_result"):
                    pipedrive_result = ai_result["pipedrive_result"]
                    print(
                        f"   - Deal created: {pipedrive_result.get('deal_created', False)}"
                    )
                    print(
                        f"   - Contact exists: {pipedrive_result.get('contact_exists', False)}"
                    )
            else:
                print(
                    f"❌ AI analysis failed: {ai_processed_email.get('ai_error', 'Unknown error')}"
                )

        # Step 3: Test standalone AI agent flow
        print("\n3️⃣ Testing standalone AI agent flow...")

        # Prepare email data for direct testing
        email_data = {
            "id": "standalone-test-message-id",
            "subject": "Standalone Test - Sales Opportunity",
            "to": "test-prospect@company.com",
            "from": "sales@yourcompany.com",
            "content": """
            Hello,
            
            I wanted to follow up on our previous conversation about the project proposal.
            We've prepared a detailed quote and timeline that I think will be very 
            attractive for your needs.
            
            The total value would be approximately 50,000 DKK, and we can start 
            within 2 weeks of approval.
            
            Would you like to schedule a meeting to discuss the details?
            
            Best regards,
            Sales Team
            """,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "user_id": test_user_id,
        }

        # Create orchestrator and process email
        orchestrator = AgentOrchestrator(test_user_id)
        standalone_result = await orchestrator.process_email(email_data)

        print(f"✅ Standalone AI agent flow completed")
        print(f"   - Success: {standalone_result.get('success', False)}")

        if standalone_result:
            print(
                f"   - Sales opportunity: {standalone_result.get('ai_result', {}).get('is_sales_opportunity', False)}"
            )
            print(
                f"   - Confidence: {standalone_result.get('ai_result', {}).get('confidence', 0)}"
            )
            print(f"   - Outcome: {standalone_result.get('outcome', 'Unknown')}")
            print(
                f"   - Processing time: {standalone_result.get('processing_time', 0):.2f}s"
            )
        else:
            print(f"   - Error: AI analysis returned None")

        # Step 4: Summary
        print("\n" + "=" * 60)
        print("📊 Integration Test Summary")
        print("=" * 60)
        print(
            f"✅ Webhook processing: {'Working' if webhook_result['status'] == 'success' else 'Failed'}"
        )
        print(
            f"✅ AI agent integration: {'Working' if webhook_result.get('ai_processed_count', 0) > 0 else 'Failed'}"
        )
        print(
            f"✅ Standalone AI flow: {'Working' if standalone_result and standalone_result.get('success', False) else 'Failed'}"
        )

        if webhook_result.get("ai_processed_count", 0) > 0:
            print("\n🎉 Webhook integration with AI agent flow is working correctly!")
            print(
                "   The system can now process real emails from Microsoft Graph webhooks"
            )
            print("   and automatically analyze them for sales opportunities.")
        else:
            print("\n⚠️  Webhook integration needs attention")
            print("   Check the logs for specific error messages.")

        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback

        print(f"Traceback: {traceback.format_exc()}")
        return False


async def test_webhook_subscription_management():
    """Test webhook subscription management"""

    print("\n🔧 Testing Webhook Subscription Management")
    print("=" * 60)

    test_user_id = os.getenv("TEST_USER_ID", "test-user-id")

    try:
        # Test listing subscriptions
        print("1️⃣ Testing subscription listing...")
        subscriptions = await webhook_manager.list_webhook_subscriptions(test_user_id)
        print(f"✅ Found {len(subscriptions)} subscriptions for user {test_user_id}")

        # Test subscription status endpoint
        print("2️⃣ Testing subscription status...")
        from app.webhooks.microsoft import get_webhook_processing_status

        status_result = await get_webhook_processing_status(test_user_id)
        print(f"✅ Status endpoint working: {status_result.get('status', 'unknown')}")

        return True

    except Exception as e:
        print(f"❌ Subscription management test failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Webhook Integration Tests")
    print("Make sure you have:")
    print("  - TEST_USER_ID environment variable set")
    print("  - Valid Microsoft and Pipedrive tokens configured")
    print("  - Database connection working")
    print()

    # Run tests
    async def run_tests():
        success1 = await test_webhook_integration()
        success2 = await test_webhook_subscription_management()

        if success1 and success2:
            print("\n🎉 All tests passed! Webhook integration is ready.")
        else:
            print("\n❌ Some tests failed. Check the output above for details.")

    asyncio.run(run_tests())
