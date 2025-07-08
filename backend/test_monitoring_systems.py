#!/usr/bin/env python3
"""
Test Monitoring Systems

This script tests all the monitoring systems to ensure they work correctly.
"""

import asyncio
import time
import uuid
from datetime import datetime
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.monitoring.agent_logger import agent_logger
from app.monitoring.cost_tracker import cost_tracker
from app.monitoring.metrics import metrics_tracker
from app.config.rate_limits import rate_limiter
from app.config.ai_models import ai_model_manager


async def test_structured_logging():
    """Test structured logging with correlation IDs"""
    print("🧪 Testing Structured Logging...")

    # Create a correlation ID
    correlation_id = str(uuid.uuid4())
    agent_logger.set_correlation_id(correlation_id)

    # Test different log levels
    agent_logger.info(
        "Test info message", {"test": True, "correlation_id": correlation_id}
    )
    agent_logger.warning(
        "Test warning message", {"test": True, "correlation_id": correlation_id}
    )
    agent_logger.error(
        "Test error message", {"test": True, "correlation_id": correlation_id}
    )

    # Test AI-specific logging
    email_data = {
        "from": "test@example.com",
        "to": "recipient@example.com",
        "subject": "Test Email",
        "content": "This is a test email content",
    }

    agent_logger.log_ai_analysis_start(email_data)

    ai_result = {
        "is_sales_opportunity": True,
        "confidence": 0.85,
        "opportunity_type": "new_business",
        "estimated_value": 50000,
    }

    agent_logger.log_ai_analysis_complete(ai_result, 2.5)
    agent_logger.log_pipedrive_operation("create_deal", True, {"deal_id": "12345"})
    agent_logger.log_token_refresh(True, "pipedrive")
    agent_logger.log_webhook_outcome("Deal created successfully", email_data)

    print("✅ Structured logging tests completed")


async def test_cost_tracking():
    """Test cost tracking system"""
    print("\n💰 Testing Cost Tracking...")

    correlation_id = str(uuid.uuid4())
    user_id = "test_user_123"

    # Test cost calculation
    cost = cost_tracker.calculate_cost("openai/gpt-4o-mini", 1000, 500)
    print(f"   Calculated cost for GPT-4o-mini: ${cost:.6f}")

    # Test recording API calls
    record1 = cost_tracker.record_api_call(
        model="openai/gpt-4o-mini",
        input_tokens=1000,
        output_tokens=500,
        operation="email_analysis",
        correlation_id=correlation_id,
        user_id=user_id,
    )

    record2 = cost_tracker.record_api_call(
        model="anthropic/claude-3-5-sonnet",
        input_tokens=2000,
        output_tokens=1000,
        operation="email_analysis",
        correlation_id=correlation_id,
        user_id=user_id,
    )

    # Test daily cost tracking
    daily_cost = cost_tracker.get_user_daily_cost(user_id)
    print(f"   Daily cost for user: ${daily_cost:.6f}")

    # Test limit checking
    limit_check = cost_tracker.check_daily_limit(user_id)
    print(f"   Limit check: {limit_check}")

    # Test cost summary
    summary = cost_tracker.get_cost_summary(7)
    print(f"   7-day cost summary: ${summary['total_cost']:.6f}")

    # Test model usage stats
    model_stats = cost_tracker.get_model_usage_stats()
    print(f"   Model usage stats: {len(model_stats)} models used")

    print("✅ Cost tracking tests completed")


async def test_rate_limiting():
    """Test rate limiting system"""
    print("\n🚦 Testing Rate Limiting...")

    user_id = "test_user_123"
    correlation_id = str(uuid.uuid4())

    # Test rate limit checking
    for i in range(5):
        limit_check = rate_limiter.check_rate_limit(
            "ai_analysis_per_minute", user_id=user_id, correlation_id=correlation_id
        )
        print(f"   Request {i+1}: {limit_check['allowed']} - {limit_check['reason']}")

    # Test rate limit status
    status = rate_limiter.get_rate_limit_status("ai_analysis_per_minute", user_id)
    print(f"   Rate limit status: {status}")

    # Test global rate limits
    global_status = rate_limiter.get_all_rate_limits_status()
    print(f"   Global rate limits: {len(global_status)} operations configured")

    # Test rate limit reset
    rate_limiter.reset_rate_limits(user_id, "ai_analysis_per_minute")
    print("   Rate limits reset for user")

    print("✅ Rate limiting tests completed")


async def test_metrics_tracking():
    """Test performance metrics tracking"""
    print("\n📊 Testing Performance Metrics...")

    correlation_id = str(uuid.uuid4())
    user_id = "test_user_123"

    # Test performance recording
    for i in range(3):
        duration_ms = 100 + (i * 50)  # Simulate different durations
        success = i < 2  # First two succeed, third fails

        metric = metrics_tracker.record_performance(
            operation="test_operation",
            duration_ms=duration_ms,
            success=success,
            correlation_id=correlation_id,
            user_id=user_id,
            metadata={"test_iteration": i},
        )
        print(f"   Recorded metric {i+1}: {duration_ms}ms, success={success}")

    # Test system metrics
    metrics_tracker.record_system_metric("cpu_usage", 45.2, "percent")
    metrics_tracker.record_system_metric("memory_usage", 1024.5, "MB")
    metrics_tracker.record_system_metric("api_requests", 150, "requests/min")

    # Test performance summary
    summary = metrics_tracker.get_performance_summary(1)  # Last hour
    print(
        f"   Performance summary: {summary['total_operations']} operations, {summary['success_rate']:.1f}% success rate"
    )

    # Test operation stats
    stats = metrics_tracker.get_operation_stats("test_operation")
    print(
        f"   Operation stats: avg={stats['avg_duration_ms']:.2f}ms, min={stats['min_duration_ms']:.2f}ms, max={stats['max_duration_ms']:.2f}ms"
    )

    # Test slowest operations
    slowest = metrics_tracker.get_slowest_operations(5)
    print(f"   Slowest operations: {len(slowest)} found")

    # Test failed operations
    failed = metrics_tracker.get_failed_operations(1)
    print(f"   Failed operations: {len(failed)} found")

    print("✅ Performance metrics tests completed")


async def test_ai_model_management():
    """Test AI model management"""
    print("\n🤖 Testing AI Model Management...")

    # Test getting available models
    available_models = ai_model_manager.get_available_models("email_analysis")
    print(f"   Available models for email analysis: {len(available_models)}")

    # Test default model
    default_model = ai_model_manager.get_default_model()
    print(f"   Default model: {default_model.model_id}")

    # Test model comparison
    comparison = ai_model_manager.get_model_comparison("email_analysis")
    print(f"   Model comparison: {len(comparison)} models compared")

    # Test cost estimation
    cost_estimate = ai_model_manager.calculate_cost_estimate(
        "openai/gpt-4o-mini", input_tokens=1000, output_tokens=500
    )
    print(f"   Cost estimate: ${cost_estimate['total_cost']:.6f}")

    # Test model selection by cost
    affordable_model = ai_model_manager.get_model_by_cost(0.001, "email_analysis")
    if affordable_model:
        print(f"   Affordable model: {affordable_model.model_id}")

    # Test model selection by performance
    performance_model = ai_model_manager.get_model_by_performance("email_analysis")
    print(f"   Performance model: {performance_model.model_id}")

    # Test model stats
    stats = ai_model_manager.get_model_stats()
    print(
        f"   Model stats: {stats['total_models']} total, {stats['available_models']} available"
    )

    print("✅ AI model management tests completed")


async def test_integration():
    """Test integration between all systems"""
    print("\n🔗 Testing System Integration...")

    correlation_id = str(uuid.uuid4())
    user_id = "test_user_123"

    # Simulate a complete AI analysis workflow
    start_time = time.time()

    # 1. Check rate limits
    rate_check = rate_limiter.check_rate_limit(
        "ai_analysis_per_minute", user_id, correlation_id
    )
    if not rate_check["allowed"]:
        print("   Rate limit exceeded, skipping test")
        return

    # 2. Record performance start
    agent_logger.info(
        "Starting integrated test",
        {"correlation_id": correlation_id, "user_id": user_id},
    )

    # 3. Simulate AI analysis
    await asyncio.sleep(0.1)  # Simulate processing time

    # 4. Record cost
    cost_record = cost_tracker.record_api_call(
        model="openai/gpt-4o-mini",
        input_tokens=1500,
        output_tokens=800,
        operation="email_analysis",
        correlation_id=correlation_id,
        user_id=user_id,
    )

    # 5. Record performance
    duration_ms = (time.time() - start_time) * 1000
    metrics_tracker.record_performance(
        operation="integrated_test",
        duration_ms=duration_ms,
        success=True,
        correlation_id=correlation_id,
        user_id=user_id,
    )

    # 6. Log completion
    agent_logger.info(
        "Integrated test completed",
        {
            "correlation_id": correlation_id,
            "duration_ms": duration_ms,
            "cost_usd": cost_record.cost_usd,
        },
    )

    print(
        f"   Integrated test completed: {duration_ms:.2f}ms, ${cost_record.cost_usd:.6f}"
    )
    print("✅ System integration tests completed")


async def main():
    """Run all monitoring system tests"""
    print("🚀 Starting Monitoring Systems Test Suite")
    print("=" * 50)

    try:
        await test_structured_logging()
        await test_cost_tracking()
        await test_rate_limiting()
        await test_metrics_tracking()
        await test_ai_model_management()
        await test_integration()

        print("\n" + "=" * 50)
        print("🎉 All monitoring systems tests completed successfully!")
        print("\n📋 Summary of tested systems:")
        print("   ✅ Structured logging with correlation IDs")
        print("   ✅ Cost tracking and monitoring")
        print("   ✅ Rate limiting and protection")
        print("   ✅ Performance metrics tracking")
        print("   ✅ AI model management")
        print("   ✅ System integration")

        print("\n🔧 Next steps:")
        print("   1. Deploy to Railway")
        print("   2. Test with real webhook data")
        print("   3. Connect AI agents to webhook pipeline")
        print("   4. Monitor costs and performance in production")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
