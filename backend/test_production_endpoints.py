#!/usr/bin/env python3
"""
Test Production Backend Endpoints

This script tests all backend endpoints in production to ensure they're working
before connecting webhooks. It tests:
- Health checks
- AI endpoints
- OAuth infrastructure
- Monitoring endpoints
- Sample email processing
"""

import asyncio
import os
import sys
import httpx
import json
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ProductionEndpointTester:
    def __init__(self, base_url: str = None):
        """Initialize the tester with the production URL."""
        self.base_url = base_url or os.getenv(
            "PRODUCTION_BACKEND_URL", "http://localhost:8000"
        )
        self.results = []
        self.session = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()

    async def test_endpoint(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        expected_status: int = 200,
        description: str = "",
    ) -> Dict[str, Any]:
        """Test a single endpoint and return results."""
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = await self.session.get(url)
            elif method.upper() == "POST":
                response = await self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            result = {
                "endpoint": endpoint,
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "success": success,
                "description": description,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "timestamp": datetime.now().isoformat(),
            }

            if success:
                try:
                    result["response_data"] = response.json()
                except:
                    result["response_text"] = response.text
            else:
                result["error"] = (
                    f"Expected {expected_status}, got {response.status_code}"
                )
                try:
                    result["error_details"] = response.json()
                except:
                    result["error_text"] = response.text

        except Exception as e:
            result = {
                "endpoint": endpoint,
                "method": method,
                "url": url,
                "success": False,
                "description": description,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

        self.results.append(result)
        return result

    async def test_health_endpoints(self):
        """Test all health check endpoints."""
        print("🏥 Testing health endpoints...")

        await self.test_endpoint("GET", "/", description="Root endpoint")
        await self.test_endpoint("GET", "/api/health", description="Main health check")
        await self.test_endpoint(
            "GET", "/api/ai/health", description="AI service health check"
        )
        await self.test_endpoint(
            "GET", "/api/monitoring/test", description="Monitoring test endpoint"
        )

    async def test_oauth_infrastructure(self):
        """Test OAuth infrastructure setup."""
        print("🔐 Testing OAuth infrastructure...")

        await self.test_endpoint(
            "GET", "/api/oauth/test", description="OAuth infrastructure test"
        )

    async def test_ai_endpoints(self):
        """Test AI-related endpoints."""
        print("🤖 Testing AI endpoints...")

        # Test basic OpenRouter connectivity
        test_message = {
            "message": "Hello, this is a test message from production testing.",
            "model": "openai/gpt-3.5-turbo",
        }

        await self.test_endpoint(
            "POST",
            "/api/ai/test",
            data=test_message,
            description="OpenRouter connectivity test",
        )

        # Test production agents with sample emails
        await self.test_endpoint(
            "POST",
            "/api/ai/test-production-agents",
            description="Production AI agents test with sample emails",
        )

    async def test_ngrok_endpoint(self):
        """Test ngrok URL endpoint (for webhook testing)."""
        print("🌐 Testing ngrok endpoint...")

        await self.test_endpoint(
            "GET", "/api/ngrok/url", description="Get ngrok URL for webhook testing"
        )

    async def test_monitoring_endpoints(self):
        """Test monitoring endpoints (those that don't require authentication)."""
        print("📊 Testing monitoring endpoints...")

        # Test endpoints that don't require authentication
        await self.test_endpoint(
            "GET", "/api/monitoring/test", description="Monitoring test endpoint"
        )

    def print_results(self):
        """Print formatted test results."""
        print("\n" + "=" * 80)
        print("PRODUCTION ENDPOINT TEST RESULTS")
        print("=" * 80)

        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.get("success", False))
        failed_tests = total_tests - successful_tests

        print(f"\n📈 SUMMARY:")
        print(f"   Total tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success rate: {(successful_tests/total_tests)*100:.1f}%")

        if successful_tests > 0:
            print(f"\n✅ SUCCESSFUL TESTS:")
            for result in self.results:
                if result.get("success"):
                    response_time = result.get("response_time_ms", 0)
                    print(
                        f"   ✓ {result['description']} ({result['method']} {result['endpoint']}) - {response_time:.0f}ms"
                    )

        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if not result.get("success"):
                    error = result.get("error", "Unknown error")
                    print(
                        f"   ✗ {result['description']} ({result['method']} {result['endpoint']})"
                    )
                    print(f"     Error: {error}")

        # Print detailed results for AI production test
        ai_production_test = next(
            (
                r
                for r in self.results
                if "Production AI agents test" in r.get("description", "")
            ),
            None,
        )

        if ai_production_test and ai_production_test.get("success"):
            print(f"\n🤖 AI PRODUCTION TEST DETAILS:")
            response_data = ai_production_test.get("response_data", {})
            summary = response_data.get("summary", {})

            print(f"   Total emails processed: {summary.get('total_emails', 0)}")
            print(
                f"   Successful processing: {summary.get('successful_processing', 0)}"
            )
            print(
                f"   Sales opportunities detected: {summary.get('sales_opportunities', 0)}"
            )
            print(f"   Deals created: {summary.get('deals_created', 0)}")

            outcome_counts = summary.get("outcome_counts", {})
            if outcome_counts:
                print(f"   Outcomes:")
                for outcome, count in outcome_counts.items():
                    print(f"     - {outcome}: {count}")

        # Print OAuth infrastructure details
        oauth_test = next(
            (
                r
                for r in self.results
                if "OAuth infrastructure test" in r.get("description", "")
            ),
            None,
        )

        if oauth_test and oauth_test.get("success"):
            print(f"\n🔐 OAUTH INFRASTRUCTURE STATUS:")
            response_data = oauth_test.get("response_data", {})

            if response_data.get("status") == "success":
                print("   ✓ OAuth infrastructure is properly configured")

                pipedrive_config = response_data.get("pipedrive_config", {})
                microsoft_config = response_data.get("microsoft_config", {})

                print(
                    f"   Pipedrive config: {'✓' if all(pipedrive_config.values()) else '✗'}"
                )
                print(
                    f"   Microsoft config: {'✓' if all(microsoft_config.values()) else '✗'}"
                )
                print(
                    f"   Encryption: {'✓' if response_data.get("encryption_works") else '✗'}"
                )
            else:
                print(
                    f"   ✗ OAuth infrastructure test failed: {response_data.get('message')}"
                )

        # Print ngrok URL if available
        ngrok_test = next(
            (r for r in self.results if "ngrok URL" in r.get("description", "")), None
        )

        if ngrok_test and ngrok_test.get("success"):
            response_data = ngrok_test.get("response_data", {})
            ngrok_url = response_data.get("ngrok_url")
            if ngrok_url:
                print(f"\n🌐 NGROK URL FOR WEBHOOK TESTING:")
                print(f"   {ngrok_url}")
                print(f"   Use this URL to configure webhooks in production")

        print(f"\n" + "=" * 80)

    def save_results(self, filename: str = None):
        """Save test results to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"production_test_results_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(
                {
                    "test_run": {
                        "timestamp": datetime.now().isoformat(),
                        "base_url": self.base_url,
                        "total_tests": len(self.results),
                        "successful_tests": sum(
                            1 for r in self.results if r.get("success", False)
                        ),
                        "failed_tests": sum(
                            1 for r in self.results if not r.get("success", False)
                        ),
                    },
                    "results": self.results,
                },
                f,
                indent=2,
            )

        print(f"\n💾 Test results saved to: {filename}")


async def main():
    """Main test function."""
    print("🚀 Starting Production Backend Endpoint Tests")
    print("=" * 60)

    # Get production URL from environment or use default
    production_url = os.getenv("PRODUCTION_BACKEND_URL")
    if not production_url:
        print("⚠️  PRODUCTION_BACKEND_URL not set, using localhost:8000")
        print("   Set PRODUCTION_BACKEND_URL environment variable to test production")
        production_url = "http://localhost:8000"

    print(f"🎯 Testing backend at: {production_url}")
    print()

    async with ProductionEndpointTester(production_url) as tester:
        # Run all tests
        await tester.test_health_endpoints()
        await tester.test_oauth_infrastructure()
        await tester.test_ai_endpoints()
        await tester.test_ngrok_endpoint()
        await tester.test_monitoring_endpoints()

        # Print and save results
        tester.print_results()
        tester.save_results()

    print("\n✨ Testing complete!")


if __name__ == "__main__":
    asyncio.run(main())
