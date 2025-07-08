"""
Monitoring API Endpoints

This module provides API endpoints for monitoring system performance, costs, and metrics.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from app.monitoring.cost_tracker import cost_tracker
from app.monitoring.metrics import metrics_tracker
from app.config.rate_limits import rate_limiter
from app.config.ai_models import ai_model_manager
from app.monitoring.agent_logger import agent_logger
from app.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("/test")
async def test_monitoring():
    """Test endpoint that doesn't require authentication"""
    return {
        "success": True,
        "message": "Monitoring API is working",
        "timestamp": "2024-01-01T00:00:00Z",
    }


@router.get("/costs/summary")
async def get_cost_summary(
    days: int = 7, user_id: Optional[str] = Depends(get_current_user)
):
    """Get cost summary for the last N days"""
    try:
        summary = await cost_tracker.get_cost_summary(days)
        agent_logger.info(f"Cost summary requested for {days} days")
        return {
            "success": True,
            "data": summary,
        }
    except Exception as e:
        logger.error(f"Error getting cost summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get cost summary")


@router.get("/costs/daily")
async def get_daily_cost(user_id: Optional[str] = Depends(get_current_user)):
    """Get today's total cost"""
    try:
        daily_cost = await cost_tracker.get_daily_cost()
        return {
            "success": True,
            "data": {
                "daily_cost": daily_cost,
            },
        }
    except Exception as e:
        logger.error(f"Error getting daily cost: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get daily cost")


@router.get("/costs/user-daily")
async def get_user_daily_cost(user_id: str = Depends(get_current_user)):
    """Get today's total cost for a specific user"""
    try:
        daily_cost = await cost_tracker.get_user_daily_cost(user_id)
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "daily_cost": daily_cost,
            },
        }
    except Exception as e:
        logger.error(f"Error getting user daily cost: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user daily cost")


@router.get("/costs/limit-check")
async def check_daily_limit(user_id: Optional[str] = Depends(get_current_user)):
    """Check if daily cost limit has been reached"""
    try:
        limit_status = await cost_tracker.check_daily_limit(user_id)
        return {
            "success": True,
            "data": limit_status,
        }
    except Exception as e:
        logger.error(f"Error checking daily limit: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check daily limit")


@router.get("/costs/model-usage")
async def get_model_usage_stats(user_id: Optional[str] = Depends(get_current_user)):
    """Get usage statistics by model"""
    try:
        model_stats = await cost_tracker.get_model_usage_stats()
        agent_logger.info("Model usage stats requested")
        return {
            "success": True,
            "data": model_stats,
        }
    except Exception as e:
        logger.error(f"Error getting model usage stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get model usage stats")


@router.get("/performance/summary")
async def get_performance_summary(
    hours: int = 24, user_id: Optional[str] = Depends(get_current_user)
):
    """Get performance summary for the last N hours"""
    try:
        summary = await metrics_tracker.get_performance_summary(hours)
        agent_logger.info(f"Performance summary requested for {hours} hours")
        return {
            "success": True,
            "data": summary,
        }
    except Exception as e:
        logger.error(f"Error getting performance summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get performance summary")


@router.get("/performance/operation/{operation}")
async def get_operation_stats(
    operation: str, user_id: Optional[str] = Depends(get_current_user)
):
    """Get statistics for a specific operation"""
    try:
        stats = await metrics_tracker.get_operation_stats(operation)
        agent_logger.info(
            f"Operation stats requested for: {operation or 'all operations'}"
        )
        return {
            "success": True,
            "data": stats,
        }
    except Exception as e:
        logger.error(f"Error getting operation stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get operation stats")


@router.get("/performance/slowest")
async def get_slowest_operations(
    limit: int = 10, user_id: Optional[str] = Depends(get_current_user)
):
    """Get the slowest operations"""
    try:
        slowest = await metrics_tracker.get_slowest_operations(limit)
        agent_logger.info(f"Slowest operations requested (limit: {limit})")
        return {
            "success": True,
            "data": slowest,
        }
    except Exception as e:
        logger.error(f"Error getting slowest operations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get slowest operations")


@router.get("/performance/failed")
async def get_failed_operations(
    hours: int = 24, user_id: Optional[str] = Depends(get_current_user)
):
    """Get failed operations from the last N hours"""
    try:
        failed = await metrics_tracker.get_failed_operations(hours)
        agent_logger.info(f"Failed operations requested for {hours} hours")
        return {
            "success": True,
            "data": failed,
        }
    except Exception as e:
        logger.error(f"Error getting failed operations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get failed operations")


@router.get("/performance/system-metrics")
async def get_system_metrics(
    metric_name: Optional[str] = None,
    hours: int = 24,
    user_id: Optional[str] = Depends(get_current_user),
):
    """Get system metrics"""
    try:
        metrics = await metrics_tracker.get_system_metrics(metric_name, hours)
        return {
            "success": True,
            "data": metrics,
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system metrics")


@router.get("/rate-limits/status")
async def get_rate_limits_status(user_id: Optional[str] = Depends(get_current_user)):
    """Get status for all rate limits"""
    try:
        status = await rate_limiter.get_all_rate_limits_status(user_id)
        return {
            "success": True,
            "data": status,
        }
    except Exception as e:
        logger.error(f"Error getting rate limits status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get rate limits status")


@router.get("/rate-limits/status/{operation}")
async def get_rate_limit_status(
    operation: str, user_id: Optional[str] = Depends(get_current_user)
):
    """Get status for a specific rate limit operation"""
    try:
        status = await rate_limiter.get_rate_limit_status(operation, user_id)
        return {
            "success": True,
            "data": {
                "operation": status.operation,
                "user_id": status.user_id,
                "requests_in_window": status.requests_in_window,
                "max_requests": status.max_requests,
                "window_seconds": status.window_seconds,
                "remaining_requests": status.remaining_requests,
                "window_resets_at": status.window_resets_at,
                "description": status.description,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting rate limit status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get rate limit status")


@router.get("/rate-limits/blocked")
async def get_blocked_requests(hours: int = 24, user_id: Optional[str] = None):
    """Get blocked requests from the last N hours"""
    try:
        blocked = await rate_limiter.get_blocked_requests(hours)
        agent_logger.info(f"Blocked requests requested for {hours} hours")
        return {
            "success": True,
            "data": blocked,
        }
    except Exception as e:
        logger.error(f"Error getting blocked requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get blocked requests")


@router.post("/rate-limits/reset")
async def reset_rate_limits(
    operation: Optional[str] = None, user_id: Optional[str] = Depends(get_current_user)
):
    """Reset rate limits for a user and/or operation"""
    try:
        await rate_limiter.reset_rate_limits(user_id, operation)
        agent_logger.info(
            f"Rate limits reset for user: {user_id or 'all'}, operation: {operation or 'all'}"
        )
        return {
            "success": True,
            "message": f"Rate limits reset for user: {user_id or 'all'}, operation: {operation or 'all'}",
        }
    except Exception as e:
        logger.error(f"Error resetting rate limits: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reset rate limits")


@router.get("/ai-models/available")
async def get_available_models(
    capability: Optional[str] = None, user_id: Optional[str] = Depends(get_current_user)
):
    """Get available AI models"""
    try:
        models = ai_model_manager.get_available_models(capability)
        model_data = []

        for model in models:
            model_data.append(
                {
                    "model_id": model.model_id,
                    "display_name": model.display_name,
                    "provider": model.provider.value,
                    "cost_per_1k_input": model.cost_per_1k_input,
                    "cost_per_1k_output": model.cost_per_1k_output,
                    "max_tokens": model.max_tokens,
                    "temperature": model.temperature,
                    "is_default": model.is_default,
                    "description": model.description,
                    "capabilities": model.capabilities,
                }
            )

        agent_logger.info(
            f"Available models requested for capability: {capability or 'all'}"
        )
        return {"models": model_data, "capability": capability}
    except Exception as e:
        logger.error(f"Error getting available models: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting available models: {str(e)}"
        )


@router.get("/ai-models/comparison")
async def get_model_comparison(
    capability: str = "email_analysis",
    user_id: Optional[str] = Depends(get_current_user),
):
    """Get model comparison for a specific capability"""
    try:
        comparison = ai_model_manager.get_model_comparison(capability)
        agent_logger.info(f"Model comparison requested for capability: {capability}")
        return {"comparison": comparison, "capability": capability}
    except Exception as e:
        logger.error(f"Error getting model comparison: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting model comparison: {str(e)}"
        )


@router.get("/ai-models/stats")
async def get_model_stats(user_id: Optional[str] = Depends(get_current_user)):
    """Get AI model statistics"""
    try:
        stats = ai_model_manager.get_model_stats()
        agent_logger.info("AI model stats requested")
        return stats
    except Exception as e:
        logger.error(f"Error getting model stats: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting model stats: {str(e)}"
        )


@router.post("/ai-models/set-default")
async def set_default_model(
    model_id: str, user_id: Optional[str] = Depends(get_current_user)
):
    """Set the default AI model"""
    try:
        ai_model_manager.set_default_model(model_id)
        agent_logger.info(f"Default model set to: {model_id}")
        return {"message": f"Default model set to {model_id}", "model_id": model_id}
    except Exception as e:
        logger.error(f"Error setting default model: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error setting default model: {str(e)}"
        )


@router.get("/system/health")
async def get_system_health(user_id: Optional[str] = Depends(get_current_user)):
    """Get overall system health status"""
    try:
        # Get various health indicators
        cost_status = await cost_tracker.check_daily_limit()
        performance_summary = await metrics_tracker.get_performance_summary(
            1
        )  # Last hour
        model_stats = ai_model_manager.get_model_stats()

        # Calculate health score (0-100)
        health_score = 100

        # Deduct points for high costs
        if cost_status["limit_reached"]:
            health_score -= 20

        # Deduct points for high failure rate
        if performance_summary.get("success_rate", 100) < 95:
            health_score -= 15

        # Deduct points for no available models
        if model_stats["available_models"] == 0:
            health_score -= 30

        health_status = (
            "healthy"
            if health_score >= 80
            else "warning" if health_score >= 60 else "critical"
        )

        result = {
            "health_score": health_score,
            "status": health_status,
            "cost_status": cost_status,
            "performance_summary": performance_summary,
            "model_stats": model_stats,
            "timestamp": datetime.utcnow().isoformat(),
        }

        agent_logger.info(
            f"System health check - Score: {health_score}, Status: {health_status}"
        )
        return result
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting system health: {str(e)}"
        )


@router.get("/export/costs")
async def export_cost_data(
    format: str = "json", user_id: Optional[str] = Depends(get_current_user)
):
    """Export cost data"""
    try:
        if format not in ["json"]:
            raise HTTPException(
                status_code=400, detail="Unsupported format. Use 'json'"
            )

        data = await cost_tracker.export_cost_data(format)
        agent_logger.info(f"Cost data exported in {format} format")
        return {"data": data, "format": format}
    except Exception as e:
        logger.error(f"Error exporting cost data: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error exporting cost data: {str(e)}"
        )


@router.get("/export/metrics")
async def export_metrics_data(
    format: str = "json", user_id: Optional[str] = Depends(get_current_user)
):
    """Export metrics data"""
    try:
        if format not in ["json"]:
            raise HTTPException(
                status_code=400, detail="Unsupported format. Use 'json'"
            )

        data = metrics_tracker.export_metrics(format)
        agent_logger.info(f"Metrics data exported in {format} format")
        return {"data": data, "format": format}
    except Exception as e:
        logger.error(f"Error exporting metrics data: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error exporting metrics data: {str(e)}"
        )


@router.post("/maintenance/clear-old-data")
async def clear_old_data(
    cost_days: int = 30,
    metrics_days: int = 30,
    user_id: Optional[str] = Depends(get_current_user),
):
    """Clear old cost and metrics data"""
    try:
        await cost_tracker.clear_old_records(cost_days)
        await metrics_tracker.clear_old_metrics(metrics_days)

        agent_logger.info(
            f"Old data cleared - costs: {cost_days} days, metrics: {metrics_days} days"
        )
        return {
            "message": "Old data cleared successfully",
            "cost_days_kept": cost_days,
            "metrics_days_kept": metrics_days,
        }
    except Exception as e:
        logger.error(f"Error clearing old data: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error clearing old data: {str(e)}"
        )


@router.post("/maintenance/reset-all")
async def reset_all_data(user_id: Optional[str] = Depends(get_current_user)):
    """Reset all monitoring data (use with caution)"""
    try:
        await cost_tracker.cost_records.clear()
        await metrics_tracker.reset_metrics()
        await rate_limiter.reset_rate_limits()

        agent_logger.warning("All monitoring data has been reset")
        return {"message": "All monitoring data reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting all data: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error resetting all data: {str(e)}"
        )


@router.get("/overview")
async def get_monitoring_overview(user_id: Optional[str] = Depends(get_current_user)):
    """Get comprehensive monitoring overview"""
    try:
        # Get cost overview
        cost_summary = await cost_tracker.get_cost_summary(days=1)
        daily_cost = await cost_tracker.get_daily_cost()
        limit_status = await cost_tracker.check_daily_limit(user_id)

        # Get performance overview
        performance_summary = await metrics_tracker.get_performance_summary(hours=1)

        # Get rate limits overview
        rate_limits_status = await rate_limiter.get_all_rate_limits_status(user_id)

        return {
            "success": True,
            "data": {
                "costs": {
                    "daily_cost": daily_cost,
                    "limit_status": limit_status,
                    "recent_activity": cost_summary,
                },
                "performance": {
                    "recent_summary": performance_summary,
                },
                "rate_limits": {
                    "status": rate_limits_status,
                },
            },
        }
    except Exception as e:
        logger.error(f"Error getting monitoring overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get monitoring overview")
