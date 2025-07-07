#!/usr/bin/env python3
"""
Test script for webhook infrastructure
Run this to verify webhook endpoints are working
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Change to Railway URL for production testing

async def test_webhook_endpoints():
    """Test all webhook endpoints"""
    print("🧪 Testing Webhook Infrastructure")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Test webhook endpoint
        print("\n1. Testing webhook test endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/webhooks/microsoft/test")
            if response.status_code == 200:
                print("✅ Webhook test endpoint working")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Webhook test endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing webhook endpoint: {str(e)}")
        
        # Test 2: Test health endpoint
        print("\n2. Testing health endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing health endpoint: {str(e)}")
        
        # Test 3: Test OAuth infrastructure
        print("\n3. Testing OAuth infrastructure...")
        try:
            response = await client.get(f"{BASE_URL}/api/oauth/test")
            if response.status_code == 200:
                print("✅ OAuth infrastructure working")
                oauth_data = response.json()
                print(f"   Encryption working: {oauth_data.get('encryption_works', False)}")
                print(f"   Microsoft config: {oauth_data.get('microsoft_config', {})}")
            else:
                print(f"❌ OAuth infrastructure failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing OAuth infrastructure: {str(e)}")
        
        # Test 4: Test webhook subscription creation (requires valid user_id and notification_url)
        print("\n4. Testing webhook subscription creation...")
        print("   ⚠️  This requires a valid user_id and Microsoft integration")
        print("   ⚠️  Skipping for now - will be tested with real data")
        
        # Test 5: Test webhook payload processing
        print("\n5. Testing webhook payload processing...")
        test_webhook_payload = {
            "value": [
                {
                    "id": "test_email_id_123",
                    "subject": "Test Email Subject",
                    "from": {
                        "emailAddress": {
                            "address": "sender@example.com"
                        }
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": "recipient@example.com"
                            }
                        }
                    ],
                    "sentDateTime": datetime.utcnow().isoformat() + "Z"
                }
            ],
            "subscriptionId": "test_subscription_123",
            "clientState": "user_test_user_123"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/webhooks/microsoft/email",
                json=test_webhook_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 202:
                print("✅ Webhook payload processing working")
                print(f"   Response: {response.json()}")
            elif response.status_code == 400:
                print("⚠️  Webhook payload processing failed (expected - no valid subscription)")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Webhook payload processing failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error testing webhook payload processing: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Webhook Infrastructure Test Complete")
    print("\nNext steps:")
    print("1. Set up ngrok for local webhook testing")
    print("2. Configure Microsoft Graph webhook permissions")
    print("3. Create webhook subscriptions with real user data")
    print("4. Test with actual email webhooks")

if __name__ == "__main__":
    asyncio.run(test_webhook_endpoints()) 