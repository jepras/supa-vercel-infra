"""
Performance Metrics Tracking

This module tracks performance metrics for AI operations and system monitoring.
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging
from app.monitoring.agent_logger import agent_logger

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric record"""

    timestamp: str
    operation: str
    duration_ms: float
    success: bool
    correlation_id: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class SystemMetric:
    """System-level metric"""

    timestamp: str
    metric_type: str
    value: float
    unit: str
    metadata: Dict[str, Any] = None


class MetricsTracker:
    """Tracks performance and system metrics"""

    def __init__(self):
        self.performance_metrics: List[PerformanceMetric] = []
        self.system_metrics: List[SystemMetric] = []
        self.operation_stats = {}

    def record_performance(
        self,
        operation: str,
        duration_ms: float,
        success: bool,
        correlation_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PerformanceMetric:
        """Record a performance metric"""
        metric = PerformanceMetric(
            timestamp=datetime.utcnow().isoformat(),
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            correlation_id=correlation_id,
            user_id=user_id,
            metadata=metadata or {},
        )

        self.performance_metrics.append(metric)

        # Update operation statistics
        if operation not in self.operation_stats:
            self.operation_stats[operation] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_duration_ms": 0,
                "avg_duration_ms": 0,
                "min_duration_ms": float("inf"),
                "max_duration_ms": 0,
            }

        stats = self.operation_stats[operation]
        stats["total_calls"] += 1
        stats["total_duration_ms"] += duration_ms

        if success:
            stats["successful_calls"] += 1
        else:
            stats["failed_calls"] += 1

        stats["avg_duration_ms"] = stats["total_duration_ms"] / stats["total_calls"]
        stats["min_duration_ms"] = min(stats["min_duration_ms"], duration_ms)
        stats["max_duration_ms"] = max(stats["max_duration_ms"], duration_ms)

        # Log the metric
        agent_logger.info(
            f"Performance metric recorded: {operation} took {duration_ms:.2f}ms",
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

    def record_system_metric(
        self,
        metric_type: str,
        value: float,
        unit: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SystemMetric:
        """Record a system metric"""
        metric = SystemMetric(
            timestamp=datetime.utcnow().isoformat(),
            metric_type=metric_type,
            value=value,
            unit=unit,
            metadata=metadata or {},
        )

        self.system_metrics.append(metric)

        # Log the metric
        agent_logger.info(
            f"System metric recorded: {metric_type} = {value} {unit}",
            {
                "operation": "system_metrics",
                "metric_type": metric_type,
                "value": value,
                "unit": unit,
                "metadata": metadata,
            },
        )

        return metric

    def get_operation_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics for operations"""
        if operation:
            return self.operation_stats.get(operation, {})
        else:
            return self.operation_stats

    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Filter recent metrics
        recent_metrics = [
            metric
            for metric in self.performance_metrics
            if datetime.fromisoformat(metric.timestamp) > cutoff_time
        ]

        if not recent_metrics:
            return {"error": "No metrics found for the specified time period"}

        # Calculate summary statistics
        total_operations = len(recent_metrics)
        successful_operations = len([m for m in recent_metrics if m.success])
        failed_operations = total_operations - successful_operations

        durations = [m.duration_ms for m in recent_metrics]
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)

        # Group by operation
        operation_breakdown = {}
        for metric in recent_metrics:
            if metric.operation not in operation_breakdown:
                operation_breakdown[metric.operation] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_duration_ms": 0,
                    "total_duration_ms": 0,
                }

            op_stats = operation_breakdown[metric.operation]
            op_stats["total"] += 1
            op_stats["total_duration_ms"] += metric.duration_ms

            if metric.success:
                op_stats["successful"] += 1
            else:
                op_stats["failed"] += 1

        # Calculate averages for each operation
        for op_stats in operation_breakdown.values():
            op_stats["avg_duration_ms"] = (
                op_stats["total_duration_ms"] / op_stats["total"]
            )

        return {
            "period_hours": hours,
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": (
                (successful_operations / total_operations) * 100
                if total_operations > 0
                else 0
            ),
            "avg_duration_ms": avg_duration,
            "min_duration_ms": min_duration,
            "max_duration_ms": max_duration,
            "operation_breakdown": operation_breakdown,
        }

    def get_system_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get system metrics summary for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Filter recent metrics
        recent_metrics = [
            metric
            for metric in self.system_metrics
            if datetime.fromisoformat(metric.timestamp) > cutoff_time
        ]

        if not recent_metrics:
            return {"error": "No system metrics found for the specified time period"}

        # Group by metric type
        metric_breakdown = {}
        for metric in recent_metrics:
            if metric.metric_type not in metric_breakdown:
                metric_breakdown[metric.metric_type] = {
                    "values": [],
                    "unit": metric.unit,
                    "avg": 0,
                    "min": float("inf"),
                    "max": 0,
                }

            breakdown = metric_breakdown[metric.metric_type]
            breakdown["values"].append(metric.value)
            breakdown["min"] = min(breakdown["min"], metric.value)
            breakdown["max"] = max(breakdown["max"], metric.value)

        # Calculate averages
        for breakdown in metric_breakdown.values():
            breakdown["avg"] = sum(breakdown["values"]) / len(breakdown["values"])

        return {"period_hours": hours, "metric_breakdown": metric_breakdown}

    def get_slowest_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the slowest operations"""
        if not self.performance_metrics:
            return []

        # Sort by duration (descending)
        sorted_metrics = sorted(
            self.performance_metrics, key=lambda m: m.duration_ms, reverse=True
        )

        # Return top N
        return [
            {
                "operation": metric.operation,
                "duration_ms": metric.duration_ms,
                "success": metric.success,
                "timestamp": metric.timestamp,
                "correlation_id": metric.correlation_id,
                "user_id": metric.user_id,
            }
            for metric in sorted_metrics[:limit]
        ]

    def get_failed_operations(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get failed operations in the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        failed_metrics = [
            metric
            for metric in self.performance_metrics
            if (
                not metric.success
                and datetime.fromisoformat(metric.timestamp) > cutoff_time
            )
        ]

        return [
            {
                "operation": metric.operation,
                "duration_ms": metric.duration_ms,
                "timestamp": metric.timestamp,
                "correlation_id": metric.correlation_id,
                "user_id": metric.user_id,
                "metadata": metric.metadata,
            }
            for metric in failed_metrics
        ]

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics data"""
        if format.lower() == "json":
            return json.dumps(
                {
                    "performance_metrics": [
                        asdict(metric) for metric in self.performance_metrics
                    ],
                    "system_metrics": [
                        asdict(metric) for metric in self.system_metrics
                    ],
                    "operation_stats": self.operation_stats,
                },
                indent=2,
            )
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def clear_old_metrics(self, days_to_keep: int = 30):
        """Clear metrics older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        # Clear performance metrics
        original_perf_count = len(self.performance_metrics)
        self.performance_metrics = [
            metric
            for metric in self.performance_metrics
            if datetime.fromisoformat(metric.timestamp) > cutoff_date
        ]

        # Clear system metrics
        original_sys_count = len(self.system_metrics)
        self.system_metrics = [
            metric
            for metric in self.system_metrics
            if datetime.fromisoformat(metric.timestamp) > cutoff_date
        ]

        cleared_perf = original_perf_count - len(self.performance_metrics)
        cleared_sys = original_sys_count - len(self.system_metrics)

        logger.info(
            f"Cleared {cleared_perf} old performance metrics and {cleared_sys} old system metrics"
        )

    def reset_metrics(self):
        """Reset all metrics"""
        self.performance_metrics.clear()
        self.system_metrics.clear()
        self.operation_stats.clear()
        logger.info("All metrics have been reset")


# Global metrics tracker instance
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
