#!/usr/bin/env python3
"""
Test User Tokens Endpoint

This script tests the new endpoint that uses stored user tokens from Supabase.
"""

import asyncio
import os
import sys
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_user_tokens_endpoint(user_id: str, base_url: str = None):
    """Test the new endpoint that uses user tokens from Supabase."""

    if not base_url:
        base_url = os.getenv("PRODUCTION_BACKEND_URL", "http://localhost:8000")

    print(f"🚀 Testing user tokens endpoint")
    print(f"🎯 URL: {base_url}")
    print(f"👤 User ID: {user_id}")
    print("=" * 60)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/api/ai/test-with-user-tokens/{user_id}"
            )

            print(f"📊 Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS!")
                print(f"📧 Total emails: {data['summary']['total_emails']}")
                print(
                    f"✅ Successful processing: {data['summary']['successful_processing']}"
                )
                print(
                    f"💰 Sales opportunities: {data['summary']['sales_opportunities']}"
                )
                print(f"🎯 Deals created: {data['summary']['deals_created']}")

                if data["results"]:
                    result = data["results"][0]
                    if result.get("success"):
                        print(f"\n📋 Outcome: {result.get('outcome')}")
                        if result.get("ai_result"):
                            ai_result = result["ai_result"]
                            print(
                                f"🤖 AI Confidence: {ai_result.get('confidence', 'N/A')}"
                            )
                            print(
                                f"🤖 Is Sales Opportunity: {ai_result.get('is_sales_opportunity', False)}"
                            )

                        if result.get("pipedrive_result"):
                            pipedrive_result = result["pipedrive_result"]
                            print(
                                f"📊 Deal Created: {pipedrive_result.get('deal_created', False)}"
                            )
                            if pipedrive_result.get("deal_created"):
                                print(
                                    f"🎯 Deal ID: {pipedrive_result.get('deal_id', 'N/A')}"
                                )
                    else:
                        print(f"❌ Error: {result.get('error')}")

                print(
                    f"\n⏱️  Processing time: {result.get('processing_time', 'N/A')} seconds"
                )

            else:
                print(f"❌ FAILED!")
                print(f"Error: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")


async def main():
    """Main test function."""

    # Get user ID from command line or use default
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        # Default test user ID - replace with your actual user ID
        user_id = "0babb68e-4bd5-4b2d-ac57-49826369178d"
        print(
            "⚠️  Using default test user ID. Pass your user ID as argument to test with your tokens."
        )

    # Get production URL
    production_url = os.getenv("PRODUCTION_BACKEND_URL")
    if not production_url:
        print("⚠️  PRODUCTION_BACKEND_URL not set, using localhost:8000")
        production_url = "http://localhost:8000"

    await test_user_tokens_endpoint(user_id, production_url)


if __name__ == "__main__":
    asyncio.run(main())
