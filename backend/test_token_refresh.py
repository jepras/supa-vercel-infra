#!/usr/bin/env python3
"""
Test Token Refresh Functionality

This script tests the token refresh mechanisms for both Pipedrive and Microsoft.
"""

import asyncio
import os
import sys
import httpx
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

# Environment variables
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
USER_ID = os.getenv("TEST_USER_ID", "your-user-id-here")  # Replace with actual user ID


async def test_token_refresh():
    """Test token refresh functionality for both providers."""

    print("🔄 Testing Token Refresh Functionality")
    print("=" * 50)

    if USER_ID == "your-user-id-here":
        print("❌ Please set TEST_USER_ID environment variable with a valid user ID")
        print("   Example: export TEST_USER_ID='your-actual-user-id'")
        return

    print(f"👤 Testing with user ID: {USER_ID}")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print()

    try:
        async with httpx.AsyncClient() as client:
            # Test the token refresh endpoint
            response = await client.post(
                f"{BACKEND_URL}/api/ai/test-token-refresh/{USER_ID}", timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("success"):
                    print("✅ Token refresh test completed successfully!")
                    print()

                    # Display summary
                    summary = data.get("summary", {})
                    print("📊 Summary:")
                    print(
                        f"   Pipedrive Status: {summary.get('pipedrive_status', 'unknown')}"
                    )
                    print(
                        f"   Microsoft Status: {summary.get('microsoft_status', 'unknown')}"
                    )
                    print(
                        f"   Pipedrive Token Valid: {summary.get('pipedrive_token_valid', False)}"
                    )
                    print(
                        f"   Microsoft Token Valid: {summary.get('microsoft_token_valid', False)}"
                    )
                    print()

                    # Display detailed results
                    results = data.get("results", [])
                    for result in results:
                        provider = result.get("provider", "unknown")
                        success = result.get("success", False)

                        if success:
                            print(
                                f"✅ {provider.upper()}: {result.get('message', 'Success')}"
                            )
                            user_info = result.get("user_info", {})
                            if user_info:
                                if provider == "pipedrive":
                                    print(f"   👤 Name: {user_info.get('name', 'N/A')}")
                                    print(
                                        f"   📧 Email: {user_info.get('email', 'N/A')}"
                                    )
                                elif provider == "microsoft":
                                    print(
                                        f"   👤 Name: {user_info.get('display_name', 'N/A')}"
                                    )
                                    print(
                                        f"   📧 Email: {user_info.get('email', 'N/A')}"
                                    )
                                    print(f"   🆔 ID: {user_info.get('id', 'N/A')}")
                        else:
                            print(
                                f"❌ {provider.upper()}: {result.get('error', 'Failed')}"
                            )
                        print()

                else:
                    print("❌ Token refresh test failed!")
                    print(f"   Error: {data.get('error', 'Unknown error')}")

            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")

    except httpx.ConnectError:
        print("❌ Failed to connect to backend server")
        print(f"   Make sure the backend is running at: {BACKEND_URL}")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")


async def test_individual_providers():
    """Test individual provider connections."""

    print("\n🔍 Testing Individual Provider Connections")
    print("=" * 50)

    try:
        async with httpx.AsyncClient() as client:
            # Test Pipedrive connection
            print("📊 Testing Pipedrive connection...")
            try:
                response = await client.post(
                    f"{BACKEND_URL}/api/oauth/pipedrive/test",
                    headers={
                        "Authorization": f"Bearer {USER_ID}"
                    },  # This won't work, but shows the endpoint
                    timeout=10.0,
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Pipedrive connection test endpoint available")
                else:
                    print(f"   ⚠️  Pipedrive test returned: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Pipedrive test failed: {str(e)}")

            # Test Microsoft connection
            print("📧 Testing Microsoft connection...")
            try:
                response = await client.post(
                    f"{BACKEND_URL}/api/oauth/microsoft/test",
                    headers={
                        "Authorization": f"Bearer {USER_ID}"
                    },  # This won't work, but shows the endpoint
                    timeout=10.0,
                )
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Microsoft connection test endpoint available")
                else:
                    print(f"   ⚠️  Microsoft test returned: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Microsoft test failed: {str(e)}")

    except Exception as e:
        print(f"❌ Individual provider tests failed: {str(e)}")


async def main():
    """Main test function."""
    print("🚀 Starting Token Refresh Tests")
    print("=" * 50)

    # Test token refresh functionality
    await test_token_refresh()

    # Test individual provider connections
    await test_individual_providers()

    print("\n" + "=" * 50)
    print("🏁 Token refresh tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
