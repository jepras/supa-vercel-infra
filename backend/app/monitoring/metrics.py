"""
Performance Metrics Tracker

This module tracks performance metrics for system operations and provides analytics.
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging
from app.monitoring.agent_logger import agent_logger
from app.lib.supabase_client import supabase_manager

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric record"""

    timestamp: str
    operation: str
    duration_ms: int
    success: bool
    correlation_id: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class SystemMetric:
    """System-level metric record"""

    timestamp: str
    metric_name: str
    metric_value: float
    metric_unit: str


class MetricsTracker:
    """Tracks and analyzes performance metrics"""

    def __init__(self):
        self.operation_stats = {}

    async def record_performance(
        self,
        operation: str,
        duration_ms: int,
        success: bool,
        correlation_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PerformanceMetric:
        """Record a performance metric to the database"""
        if metadata is None:
            metadata = {}

        metric = PerformanceMetric(
            timestamp=datetime.utcnow().isoformat(),
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            correlation_id=correlation_id,
            user_id=user_id,
            metadata=metadata,
        )

        # Store in database
        try:
            supabase_manager.client.table("performance_metrics").insert(
                {
                    "timestamp": metric.timestamp,
                    "operation": metric.operation,
                    "duration_ms": metric.duration_ms,
                    "success": metric.success,
                    "correlation_id": metric.correlation_id,
                    "user_id": metric.user_id,
                    "metadata": metric.metadata,
                }
            ).execute()
        except Exception as e:
            logger.error(f"Failed to store performance metric in database: {str(e)}")
            # Continue execution even if database storage fails

        # Log the metric
        agent_logger.info(
            f"Performance metric recorded: {operation} took {duration_ms}ms, success={success}",
            {
                "operation": "performance_tracking",
                "operation_type": operation,
                "duration_ms": duration_ms,
                "success": success,
                "correlation_id": correlation_id,
                "user_id": user_id,
                "metadata": metadata,
            },
        )

        return metric

    async def record_system_metric(
        self, metric_name: str, metric_value: float, metric_unit: str
    ) -> SystemMetric:
        """Record a system-level metric to the database"""
        metric = SystemMetric(
            timestamp=datetime.utcnow().isoformat(),
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=metric_unit,
        )

        # Store in database
        try:
            supabase_manager.client.table("system_metrics").insert(
                {
                    "timestamp": metric.timestamp,
                    "metric_name": metric.metric_name,
                    "metric_value": metric.metric_value,
                    "metric_unit": metric.metric_unit,
                }
            ).execute()
        except Exception as e:
            logger.error(f"Failed to store system metric in database: {str(e)}")

        return metric

    async def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours from database"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        try:
            result = (
                supabase_manager.client.table("performance_metrics")
                .select("*")
                .gte("timestamp", start_time.isoformat())
                .lte("timestamp", end_time.isoformat())
                .execute()
            )

            metrics = result.data

            if not metrics:
                return {
                    "period_hours": hours,
                    "total_operations": 0,
                    "successful_operations": 0,
                    "failed_operations": 0,
                    "success_rate": 0.0,
                    "avg_duration_ms": 0.0,
                    "min_duration_ms": 0.0,
                    "max_duration_ms": 0.0,
                    "operation_breakdown": {},
                }

            # Calculate basic stats
            total_operations = len(metrics)
            successful_operations = sum(1 for m in metrics if m["success"])
            failed_operations = total_operations - successful_operations
            success_rate = (
                (successful_operations / total_operations) * 100
                if total_operations > 0
                else 0
            )

            durations = [m["duration_ms"] for m in metrics]
            avg_duration_ms = sum(durations) / len(durations) if durations else 0
            min_duration_ms = min(durations) if durations else 0
            max_duration_ms = max(durations) if durations else 0

            # Group by operation
            operation_breakdown = {}
            for metric in metrics:
                op = metric["operation"]
                if op not in operation_breakdown:
                    operation_breakdown[op] = {
                        "total": 0,
                        "successful": 0,
                        "failed": 0,
                        "total_duration_ms": 0,
                        "durations": [],
                    }

                breakdown = operation_breakdown[op]
                breakdown["total"] += 1
                breakdown["total_duration_ms"] += metric["duration_ms"]
                breakdown["durations"].append(metric["duration_ms"])

                if metric["success"]:
                    breakdown["successful"] += 1
                else:
                    breakdown["failed"] += 1

            # Calculate averages for each operation
            for op_stats in operation_breakdown.values():
                if op_stats["durations"]:
                    op_stats["avg_duration_ms"] = sum(op_stats["durations"]) / len(
                        op_stats["durations"]
                    )
                else:
                    op_stats["avg_duration_ms"] = 0
                del op_stats["durations"]  # Remove the list to keep response clean

            return {
                "period_hours": hours,
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "failed_operations": failed_operations,
                "success_rate": success_rate,
                "avg_duration_ms": avg_duration_ms,
                "min_duration_ms": min_duration_ms,
                "max_duration_ms": max_duration_ms,
                "operation_breakdown": operation_breakdown,
            }
        except Exception as e:
            logger.error(f"Failed to get performance summary from database: {str(e)}")
            return {
                "period_hours": hours,
                "total_operations": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "min_duration_ms": 0.0,
                "max_duration_ms": 0.0,
                "operation_breakdown": {},
            }

    async def get_operation_stats(
        self, operation: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get statistics for a specific operation or all operations from database"""
        try:
            query = supabase_manager.client.table("performance_metrics").select("*")
            if operation:
                query = query.eq("operation", operation)

            result = await query.execute()
            metrics = result.data

            if not metrics:
                return {
                    "operation": operation or "all",
                    "total_operations": 0,
                    "success_rate": 0.0,
                    "avg_duration_ms": 0.0,
                    "min_duration_ms": 0.0,
                    "max_duration_ms": 0.0,
                }

            total_operations = len(metrics)
            successful_operations = sum(1 for m in metrics if m["success"])
            success_rate = (
                (successful_operations / total_operations) * 100
                if total_operations > 0
                else 0
            )

            durations = [m["duration_ms"] for m in metrics]
            avg_duration_ms = sum(durations) / len(durations) if durations else 0
            min_duration_ms = min(durations) if durations else 0
            max_duration_ms = max(durations) if durations else 0

            return {
                "operation": operation or "all",
                "total_operations": total_operations,
                "success_rate": success_rate,
                "avg_duration_ms": avg_duration_ms,
                "min_duration_ms": min_duration_ms,
                "max_duration_ms": max_duration_ms,
            }
        except Exception as e:
            logger.error(f"Failed to get operation stats from database: {str(e)}")
            return {
                "operation": operation or "all",
                "total_operations": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "min_duration_ms": 0.0,
                "max_duration_ms": 0.0,
            }

    async def get_slowest_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the slowest operations from database"""
        try:
            result = (
                supabase_manager.client.table("performance_metrics")
                .select("*")
                .order("duration_ms", desc=True)
                .limit(limit)
                .execute()
            )

            return [
                {
                    "operation": record["operation"],
                    "duration_ms": record["duration_ms"],
                    "success": record["success"],
                    "timestamp": record["timestamp"],
                    "correlation_id": record["correlation_id"],
                    "user_id": record["user_id"],
                }
                for record in result.data
            ]
        except Exception as e:
            logger.error(f"Failed to get slowest operations from database: {str(e)}")
            return []

    async def get_failed_operations(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get failed operations from the last N hours from database"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        try:
            result = (
                supabase_manager.client.table("performance_metrics")
                .select("*")
                .eq("success", False)
                .gte("timestamp", start_time.isoformat())
                .lte("timestamp", end_time.isoformat())
                .order("timestamp", desc=True)
                .execute()
            )

            return [
                {
                    "operation": record["operation"],
                    "duration_ms": record["duration_ms"],
                    "timestamp": record["timestamp"],
                    "correlation_id": record["correlation_id"],
                    "user_id": record["user_id"],
                    "metadata": record["metadata"],
                }
                for record in result.data
            ]
        except Exception as e:
            logger.error(f"Failed to get failed operations from database: {str(e)}")
            return []

    async def get_system_metrics(
        self, metric_name: Optional[str] = None, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get system metrics from database"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        try:
            query = (
                supabase_manager.client.table("system_metrics")
                .select("*")
                .gte("timestamp", start_time.isoformat())
                .lte("timestamp", end_time.isoformat())
            )
            if metric_name:
                query = query.eq("metric_name", metric_name)

            result = await query.order("timestamp", desc=True).execute()

            return [
                {
                    "metric_name": record["metric_name"],
                    "metric_value": record["metric_value"],
                    "metric_unit": record["metric_unit"],
                    "timestamp": record["timestamp"],
                }
                for record in result.data
            ]
        except Exception as e:
            logger.error(f"Failed to get system metrics from database: {str(e)}")
            return []

    async def clear_old_metrics(self, days_to_keep: int = 30):
        """Clear old metrics from database"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        try:
            # Clear old performance metrics
            supabase_manager.client.table("performance_metrics").delete().lt(
                "timestamp", cutoff_date.isoformat()
            ).execute()

            # Clear old system metrics
            supabase_manager.client.table("system_metrics").delete().lt(
                "timestamp", cutoff_date.isoformat()
            ).execute()

            logger.info(f"Cleared metrics older than {days_to_keep} days")
        except Exception as e:
            logger.error(f"Failed to clear old metrics: {str(e)}")


# Create singleton instance
metrics_tracker = MetricsTracker()


# Performance tracking decorator
def track_performance(operation: str):
    """Decorator to track performance of functions"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            correlation_id = kwargs.get("correlation_id", "unknown")
            user_id = kwargs.get("user_id")

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                metrics_tracker.record_performance(
                    operation=operation,
                    duration_ms=duration_ms,
                    success=True,
                    correlation_id=correlation_id,
                    user_id=user_id,
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                metrics_tracker.record_performance(
                    operation=operation,
                    duration_ms=duration_ms,
                    success=False,
                    correlation_id=correlation_id,
                    user_id=user_id,
                    metadata={"error": str(e)},
                )

                raise

        return wrapper

    return decorator
