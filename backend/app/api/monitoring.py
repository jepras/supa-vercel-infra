"""
Monitoring API Endpoints

This module provides API endpoints for monitoring system performance, costs, and metrics.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
from app.monitoring.cost_tracker import cost_tracker
from app.monitoring.metrics import metrics_tracker
from app.config.rate_limits import rate_limiter
from app.config.ai_models import ai_model_manager
from app.monitoring.agent_logger import agent_logger

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("/costs/summary")
async def get_cost_summary(days: int = 7) -> Dict[str, Any]:
    """Get cost summary for the last N days"""
    try:
        summary = cost_tracker.get_cost_summary(days)
        agent_logger.info(f"Cost summary requested for {days} days")
        return summary
    except Exception as e:
        logger.error(f"Error getting cost summary: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting cost summary: {str(e)}"
        )


@router.get("/costs/daily")
async def get_daily_cost(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get daily cost for a specific user or global"""
    try:
        daily_cost = (
            cost_tracker.get_user_daily_cost(user_id)
            if user_id
            else cost_tracker.get_daily_cost()
        )
        limit_check = cost_tracker.check_daily_limit(user_id)

        result = {"daily_cost": daily_cost, "limit_check": limit_check}

        agent_logger.info(f"Daily cost requested for user: {user_id or 'global'}")
        return result
    except Exception as e:
        logger.error(f"Error getting daily cost: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting daily cost: {str(e)}"
        )


@router.get("/costs/model-usage")
async def get_model_usage_stats() -> Dict[str, Any]:
    """Get usage statistics by model"""
    try:
        stats = cost_tracker.get_model_usage_stats()
        agent_logger.info("Model usage stats requested")
        return stats
    except Exception as e:
        logger.error(f"Error getting model usage stats: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting model usage stats: {str(e)}"
        )


@router.get("/performance/summary")
async def get_performance_summary(hours: int = 24) -> Dict[str, Any]:
    """Get performance summary for the last N hours"""
    try:
        summary = metrics_tracker.get_performance_summary(hours)
        agent_logger.info(f"Performance summary requested for {hours} hours")
        return summary
    except Exception as e:
        logger.error(f"Error getting performance summary: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting performance summary: {str(e)}"
        )


@router.get("/performance/operations")
async def get_operation_stats(operation: Optional[str] = None) -> Dict[str, Any]:
    """Get performance statistics for operations"""
    try:
        stats = metrics_tracker.get_operation_stats(operation)
        agent_logger.info(
            f"Operation stats requested for: {operation or 'all operations'}"
        )
        return stats
    except Exception as e:
        logger.error(f"Error getting operation stats: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting operation stats: {str(e)}"
        )


@router.get("/performance/slowest")
async def get_slowest_operations(limit: int = 10) -> Dict[str, Any]:
    """Get the slowest operations"""
    try:
        slowest = metrics_tracker.get_slowest_operations(limit)
        agent_logger.info(f"Slowest operations requested (limit: {limit})")
        return {"slowest_operations": slowest, "limit": limit}
    except Exception as e:
        logger.error(f"Error getting slowest operations: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting slowest operations: {str(e)}"
        )


@router.get("/performance/failed")
async def get_failed_operations(hours: int = 24) -> Dict[str, Any]:
    """Get failed operations in the last N hours"""
    try:
        failed = metrics_tracker.get_failed_operations(hours)
        agent_logger.info(f"Failed operations requested for {hours} hours")
        return {"failed_operations": failed, "period_hours": hours}
    except Exception as e:
        logger.error(f"Error getting failed operations: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting failed operations: {str(e)}"
        )


@router.get("/rate-limits/status")
async def get_rate_limit_status(
    operation: Optional[str] = None, user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get rate limit status"""
    try:
        if operation:
            status = rate_limiter.get_rate_limit_status(operation, user_id)
        else:
            status = rate_limiter.get_all_rate_limits_status(user_id)

        agent_logger.info(
            f"Rate limit status requested for operation: {operation or 'all'}, user: {user_id or 'global'}"
        )
        return status
    except Exception as e:
        logger.error(f"Error getting rate limit status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting rate limit status: {str(e)}"
        )


@router.get("/rate-limits/blocked")
async def get_blocked_requests(hours: int = 24) -> Dict[str, Any]:
    """Get blocked requests in the last N hours"""
    try:
        blocked = rate_limiter.get_blocked_requests(hours)
        agent_logger.info(f"Blocked requests requested for {hours} hours")
        return {"blocked_requests": blocked, "period_hours": hours}
    except Exception as e:
        logger.error(f"Error getting blocked requests: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting blocked requests: {str(e)}"
        )


@router.post("/rate-limits/reset")
async def reset_rate_limits(
    user_id: Optional[str] = None, operation: Optional[str] = None
) -> Dict[str, Any]:
    """Reset rate limits"""
    try:
        rate_limiter.reset_rate_limits(user_id, operation)
        agent_logger.info(
            f"Rate limits reset for user: {user_id or 'all'}, operation: {operation or 'all'}"
        )
        return {"message": "Rate limits reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting rate limits: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error resetting rate limits: {str(e)}"
        )


@router.get("/ai-models/available")
async def get_available_models(capability: Optional[str] = None) -> Dict[str, Any]:
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
async def get_model_comparison(capability: str = "email_analysis") -> Dict[str, Any]:
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
async def get_model_stats() -> Dict[str, Any]:
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
async def set_default_model(model_id: str) -> Dict[str, Any]:
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
async def get_system_health() -> Dict[str, Any]:
    """Get overall system health status"""
    try:
        # Get various health indicators
        cost_status = cost_tracker.check_daily_limit()
        performance_summary = metrics_tracker.get_performance_summary(1)  # Last hour
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
            "timestamp": (
                metrics_tracker.performance_metrics[-1].timestamp
                if metrics_tracker.performance_metrics
                else None
            ),
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
async def export_cost_data(format: str = "json") -> Dict[str, Any]:
    """Export cost data"""
    try:
        if format not in ["json"]:
            raise HTTPException(
                status_code=400, detail="Unsupported format. Use 'json'"
            )

        data = cost_tracker.export_cost_data(format)
        agent_logger.info(f"Cost data exported in {format} format")
        return {"data": data, "format": format}
    except Exception as e:
        logger.error(f"Error exporting cost data: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error exporting cost data: {str(e)}"
        )


@router.get("/export/metrics")
async def export_metrics_data(format: str = "json") -> Dict[str, Any]:
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
async def clear_old_data(cost_days: int = 30, metrics_days: int = 30) -> Dict[str, Any]:
    """Clear old cost and metrics data"""
    try:
        cost_tracker.clear_old_records(cost_days)
        metrics_tracker.clear_old_metrics(metrics_days)

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
async def reset_all_data() -> Dict[str, Any]:
    """Reset all monitoring data (use with caution)"""
    try:
        cost_tracker.cost_records.clear()
        metrics_tracker.reset_metrics()
        rate_limiter.reset_rate_limits()

        agent_logger.warning("All monitoring data has been reset")
        return {"message": "All monitoring data reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting all data: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error resetting all data: {str(e)}"
        )
