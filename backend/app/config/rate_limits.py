"""
Rate Limiting Configuration

This module provides rate limiting for API endpoints and AI operations.
"""

import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
from app.monitoring.agent_logger import agent_logger

logger = logging.getLogger(__name__)


@dataclass
class RateLimit:
    """Rate limit configuration"""

    max_requests: int
    window_seconds: int
    description: str


@dataclass
class RateLimitRecord:
    """Record of a rate-limited request"""

    timestamp: float
    user_id: Optional[str]
    operation: str
    correlation_id: str


class RateLimiter:
    """Rate limiter for API operations"""

    def __init__(self):
        self.rate_limits = self._initialize_rate_limits()
        self.request_records: Dict[str, List[RateLimitRecord]] = {}

    def _initialize_rate_limits(self) -> Dict[str, RateLimit]:
        """Initialize rate limit configurations"""
        return {
            # AI Analysis rate limits
            "ai_analysis_per_minute": RateLimit(
                max_requests=10,
                window_seconds=60,
                description="AI analysis requests per minute per user",
            ),
            "ai_analysis_per_hour": RateLimit(
                max_requests=100,
                window_seconds=3600,
                description="AI analysis requests per hour per user",
            ),
            "ai_analysis_per_day": RateLimit(
                max_requests=1000,
                window_seconds=86400,
                description="AI analysis requests per day per user",
            ),
            # Webhook rate limits
            "webhook_processing_per_minute": RateLimit(
                max_requests=30,
                window_seconds=60,
                description="Webhook processing requests per minute per user",
            ),
            "webhook_processing_per_hour": RateLimit(
                max_requests=300,
                window_seconds=3600,
                description="Webhook processing requests per hour per user",
            ),
            # Pipedrive API rate limits
            "pipedrive_api_per_minute": RateLimit(
                max_requests=20,
                window_seconds=60,
                description="Pipedrive API calls per minute per user",
            ),
            "pipedrive_api_per_hour": RateLimit(
                max_requests=200,
                window_seconds=3600,
                description="Pipedrive API calls per hour per user",
            ),
            # Global rate limits
            "global_requests_per_minute": RateLimit(
                max_requests=100,
                window_seconds=60,
                description="Global requests per minute",
            ),
            "global_requests_per_hour": RateLimit(
                max_requests=1000,
                window_seconds=3600,
                description="Global requests per hour",
            ),
        }

    def _get_user_key(self, user_id: Optional[str], operation: str) -> str:
        """Generate a key for user-specific rate limiting"""
        if user_id:
            return f"user:{user_id}:{operation}"
        else:
            return f"global:{operation}"

    def _cleanup_old_records(self, operation: str, window_seconds: int):
        """Remove old rate limit records"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds

        # Clean up user-specific records
        keys_to_remove = []
        for key, records in self.request_records.items():
            if operation in key:
                # Filter out old records
                self.request_records[key] = [
                    record for record in records if record.timestamp > cutoff_time
                ]
                # Remove empty lists
                if not self.request_records[key]:
                    keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.request_records[key]

    def check_rate_limit(
        self,
        operation: str,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Check if a request is within rate limits"""
        if operation not in self.rate_limits:
            logger.warning(f"Unknown rate limit operation: {operation}")
            return {"allowed": True, "reason": "No rate limit configured"}

        rate_limit = self.rate_limits[operation]
        user_key = self._get_user_key(user_id, operation)

        # Clean up old records
        self._cleanup_old_records(operation, rate_limit.window_seconds)

        # Get current records for this user/operation
        current_records = self.request_records.get(user_key, [])
        current_time = time.time()

        # Count requests in the current window
        window_start = current_time - rate_limit.window_seconds
        requests_in_window = len(
            [record for record in current_records if record.timestamp > window_start]
        )

        # Check if limit is exceeded
        if requests_in_window >= rate_limit.max_requests:
            # Calculate when the next request will be allowed
            oldest_record = min(current_records, key=lambda r: r.timestamp)
            next_allowed_time = oldest_record.timestamp + rate_limit.window_seconds
            wait_time = max(0, next_allowed_time - current_time)

            agent_logger.warning(
                f"Rate limit exceeded for {operation}",
                {
                    "operation": "rate_limit_exceeded",
                    "user_id": user_id,
                    "operation_type": operation,
                    "requests_in_window": requests_in_window,
                    "max_requests": rate_limit.max_requests,
                    "window_seconds": rate_limit.window_seconds,
                    "wait_time_seconds": wait_time,
                    "correlation_id": correlation_id,
                },
            )

            return {
                "allowed": False,
                "reason": f"Rate limit exceeded: {requests_in_window}/{rate_limit.max_requests} requests in {rate_limit.window_seconds}s",
                "requests_in_window": requests_in_window,
                "max_requests": rate_limit.max_requests,
                "window_seconds": rate_limit.window_seconds,
                "wait_time_seconds": wait_time,
                "next_allowed_time": datetime.fromtimestamp(
                    next_allowed_time
                ).isoformat(),
            }

        # Record this request
        record = RateLimitRecord(
            timestamp=current_time,
            user_id=user_id,
            operation=operation,
            correlation_id=correlation_id or "unknown",
        )

        if user_key not in self.request_records:
            self.request_records[user_key] = []

        self.request_records[user_key].append(record)

        return {
            "allowed": True,
            "reason": "Within rate limits",
            "requests_in_window": requests_in_window + 1,
            "max_requests": rate_limit.max_requests,
            "window_seconds": rate_limit.window_seconds,
        }

    def get_rate_limit_status(
        self, operation: str, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get current rate limit status for an operation"""
        if operation not in self.rate_limits:
            return {"error": f"Unknown operation: {operation}"}

        rate_limit = self.rate_limits[operation]
        user_key = self._get_user_key(user_id, operation)

        # Clean up old records
        self._cleanup_old_records(operation, rate_limit.window_seconds)

        # Get current records
        current_records = self.request_records.get(user_key, [])
        current_time = time.time()
        window_start = current_time - rate_limit.window_seconds

        requests_in_window = len(
            [record for record in current_records if record.timestamp > window_start]
        )

        return {
            "operation": operation,
            "user_id": user_id,
            "requests_in_window": requests_in_window,
            "max_requests": rate_limit.max_requests,
            "window_seconds": rate_limit.window_seconds,
            "remaining_requests": max(0, rate_limit.max_requests - requests_in_window),
            "window_resets_at": datetime.fromtimestamp(
                window_start + rate_limit.window_seconds
            ).isoformat(),
            "description": rate_limit.description,
        }

    def get_all_rate_limits_status(
        self, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get status for all rate limits"""
        status = {}

        for operation in self.rate_limits.keys():
            status[operation] = self.get_rate_limit_status(operation, user_id)

        return status

    def reset_rate_limits(
        self, user_id: Optional[str] = None, operation: Optional[str] = None
    ):
        """Reset rate limits for a user or operation"""
        if user_id and operation:
            # Reset specific user/operation
            user_key = self._get_user_key(user_id, operation)
            if user_key in self.request_records:
                del self.request_records[user_key]
                logger.info(
                    f"Reset rate limits for user {user_id}, operation {operation}"
                )
        elif user_id:
            # Reset all operations for user
            keys_to_remove = [
                key for key in self.request_records.keys() if f"user:{user_id}:" in key
            ]
            for key in keys_to_remove:
                del self.request_records[key]
            logger.info(f"Reset all rate limits for user {user_id}")
        elif operation:
            # Reset all users for operation
            keys_to_remove = [
                key for key in self.request_records.keys() if operation in key
            ]
            for key in keys_to_remove:
                del self.request_records[key]
            logger.info(f"Reset all rate limits for operation {operation}")
        else:
            # Reset all rate limits
            self.request_records.clear()
            logger.info("Reset all rate limits")


# Global rate limiter instance
rate_limiter = RateLimiter()


# Decorator for rate limiting
def rate_limit(operation: str, user_id_param: str = "user_id"):
    """Decorator to apply rate limiting to functions"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user_id from function parameters
            user_id = kwargs.get(user_id_param)

            # Check rate limit
            limit_check = rate_limiter.check_rate_limit(operation, user_id)

            if not limit_check["allowed"]:
                raise Exception(f"Rate limit exceeded: {limit_check['reason']}")

            # Call the original function
            return await func(*args, **kwargs)

        return wrapper

    return decorator
