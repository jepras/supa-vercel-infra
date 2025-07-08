#!/usr/bin/env python3
"""
Check Opportunity Logs

This script checks the opportunity_logs table to verify that data is being stored correctly.
"""

import os
import asyncio
from dotenv import load_dotenv
from app.lib.supabase_client import supabase_manager


async def check_opportunity_logs():
    """Check the opportunity_logs table for recent entries."""
    print("🔍 Checking Opportunity Logs")
    print("=" * 50)

    try:
        # Get recent opportunity logs
        result = (
            supabase_manager.client.table("opportunity_logs")
            .select("*")
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )

        if result.data:
            print(f"✅ Found {len(result.data)} recent opportunity logs:")
            print()

            for i, log in enumerate(result.data, 1):
                print(f"📧 Log {i}:")
                print(f"   📧 Email: {log.get('recipient_email')}")
                print(f"   📝 Subject: {log.get('subject', 'N/A')}")
                print(
                    f"   🎯 Opportunity: {'✅ Yes' if log.get('opportunity_detected') else '❌ No'}"
                )
                print(f"   📊 Confidence: {log.get('confidence_score', 'N/A')}")
                print(f"   🕒 Created: {log.get('created_at')}")
                print(f"   🔗 Hash: {log.get('email_hash', 'N/A')[:16]}...")

                # Check if Pipedrive data is in metadata
                metadata = log.get("metadata", {})
                pipedrive_result = metadata.get("pipedrive_result")
                if pipedrive_result:
                    deal_created = pipedrive_result.get("deal_created", False)
                    print(
                        f"   💼 Deal Created: {'✅ Yes' if deal_created else '❌ No'}"
                    )
                    if deal_created and pipedrive_result.get("deal"):
                        print(
                            f"   🏷️  Deal Title: {pipedrive_result['deal'].get('title', 'N/A')}"
                        )
                else:
                    print(f"   💼 Deal Created: N/A (no Pipedrive result)")

                print("-" * 40)
        else:
            print("❌ No opportunity logs found")

    except Exception as e:
        print(f"❌ Error checking opportunity logs: {e}")


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(check_opportunity_logs())
