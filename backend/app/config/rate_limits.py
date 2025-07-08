"""
Rate Limiting Configuration

This module provides rate limiting functionality for API operations.
"""

import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
from app.monitoring.agent_logger import agent_logger
from app.lib.supabase_client import supabase_manager

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration for an operation"""

    operation: str
    max_requests: int
    window_seconds: int
    description: str


@dataclass
class RateLimitStatus:
    """Current rate limit status"""

    operation: str
    user_id: Optional[str]
    requests_in_window: int
    max_requests: int
    window_seconds: int
    remaining_requests: int
    window_resets_at: str
    description: str


class RateLimiter:
    """Rate limiting implementation with database persistence"""

    def __init__(self):
        self.rate_limits = self._initialize_rate_limits()

    def _initialize_rate_limits(self) -> Dict[str, RateLimitConfig]:
        """Initialize rate limit configurations"""
        return {
            "ai_analysis_per_minute": RateLimitConfig(
                operation="ai_analysis_per_minute",
                max_requests=10,
                window_seconds=60,
                description="AI analysis requests per minute per user",
            ),
            "ai_analysis_per_hour": RateLimitConfig(
                operation="ai_analysis_per_hour",
                max_requests=100,
                window_seconds=3600,
                description="AI analysis requests per hour per user",
            ),
            "ai_analysis_per_day": RateLimitConfig(
                operation="ai_analysis_per_day",
                max_requests=1000,
                window_seconds=86400,
                description="AI analysis requests per day per user",
            ),
            "webhook_processing_per_minute": RateLimitConfig(
                operation="webhook_processing_per_minute",
                max_requests=30,
                window_seconds=60,
                description="Webhook processing requests per minute per user",
            ),
            "webhook_processing_per_hour": RateLimitConfig(
                operation="webhook_processing_per_hour",
                max_requests=300,
                window_seconds=3600,
                description="Webhook processing requests per hour per user",
            ),
            "pipedrive_api_per_minute": RateLimitConfig(
                operation="pipedrive_api_per_minute",
                max_requests=20,
                window_seconds=60,
                description="Pipedrive API calls per minute per user",
            ),
            "pipedrive_api_per_hour": RateLimitConfig(
                operation="pipedrive_api_per_hour",
                max_requests=200,
                window_seconds=3600,
                description="Pipedrive API calls per hour per user",
            ),
            "global_requests_per_minute": RateLimitConfig(
                operation="global_requests_per_minute",
                max_requests=100,
                window_seconds=60,
                description="Global requests per minute",
            ),
            "global_requests_per_hour": RateLimitConfig(
                operation="global_requests_per_hour",
                max_requests=1000,
                window_seconds=3600,
                description="Global requests per hour",
            ),
        }

    async def check_rate_limit(
        self,
        operation: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> bool:
        """Check if a request is within rate limits"""
        if operation not in self.rate_limits:
            logger.warning(f"Unknown rate limit operation: {operation}")
            return True

        config = self.rate_limits[operation]
        now = datetime.utcnow()
        window_start = now.replace(microsecond=0)
        window_end = window_start + timedelta(seconds=config.window_seconds)

        try:
            # Get or create rate limit window
            window_data = await self._get_or_create_window(
                operation,
                user_id,
                window_start,
                window_end,
                config.max_requests,
                config.window_seconds,
            )

            # Check if limit is exceeded
            is_blocked = window_data["requests_count"] >= config.max_requests

            # Record the rate limit check
            await self._record_rate_limit_check(
                operation, user_id, ip_address, user_agent, correlation_id, is_blocked
            )

            if is_blocked:
                agent_logger.warning(
                    f"Rate limit exceeded for {operation}",
                    {
                        "operation": "rate_limiting",
                        "rate_limit_operation": operation,
                        "user_id": user_id,
                        "requests_count": window_data["requests_count"],
                        "max_requests": config.max_requests,
                        "correlation_id": correlation_id,
                    },
                )
                return False

            # Increment request count
            await self._increment_request_count(window_data["id"])

            return True

        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            # Allow request to proceed if rate limiting fails
            return True

    async def _get_or_create_window(
        self,
        operation: str,
        user_id: Optional[str],
        window_start: datetime,
        window_end: datetime,
        max_requests: int,
        window_seconds: int,
    ) -> Dict[str, Any]:
        """Get or create a rate limit window in the database"""
        try:
            # Try to get existing window
            query = (
                supabase_manager.client.table("rate_limit_windows")
                .select("*")
                .eq("operation", operation)
                .eq("window_start", window_start.isoformat())
            )

            if user_id:
                query = query.eq("user_id", user_id)
            else:
                query = query.is_("user_id", "null")

            result = query.execute()

            if result.data:
                return result.data[0]

            # Create new window
            window_data = {
                "operation": operation,
                "user_id": user_id,
                "window_start": window_start.isoformat(),
                "window_end": window_end.isoformat(),
                "requests_count": 0,
                "max_requests": max_requests,
                "window_seconds": window_seconds,
            }

            result = (
                supabase_manager.client.table("rate_limit_windows")
                .insert(window_data)
                .execute()
            )
            return result.data[0]

        except Exception as e:
            logger.error(f"Error getting/creating rate limit window: {str(e)}")
            # Return a default window if database fails
            return {
                "id": "default",
                "operation": operation,
                "user_id": user_id,
                "window_start": window_start.isoformat(),
                "window_end": window_end.isoformat(),
                "requests_count": 0,
                "max_requests": max_requests,
                "window_seconds": window_seconds,
            }

    async def _increment_request_count(self, window_id: str):
        """Increment the request count for a window"""
        try:
            supabase_manager.client.table("rate_limit_windows").update(
                {"requests_count": supabase_manager.client.rpc("increment", {"x": 1})}
            ).eq("id", window_id).execute()
        except Exception as e:
            logger.error(f"Error incrementing request count: {str(e)}")

    async def _record_rate_limit_check(
        self,
        operation: str,
        user_id: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str],
        correlation_id: Optional[str],
        was_blocked: bool,
    ):
        """Record a rate limit check in the database"""
        try:
            supabase_manager.client.table("rate_limit_records").insert(
                {
                    "operation": operation,
                    "user_id": user_id,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "correlation_id": correlation_id or "unknown",
                    "was_blocked": was_blocked,
                }
            ).execute()
        except Exception as e:
            logger.error(f"Error recording rate limit check: {str(e)}")

    async def get_rate_limit_status(
        self, operation: str, user_id: Optional[str] = None
    ) -> RateLimitStatus:
        """Get current rate limit status for an operation"""
        if operation not in self.rate_limits:
            raise ValueError(f"Unknown rate limit operation: {operation}")

        config = self.rate_limits[operation]
        now = datetime.utcnow()
        window_start = now.replace(microsecond=0)
        window_end = window_start + timedelta(seconds=config.window_seconds)

        try:
            # Get current window
            window_data = await self._get_or_create_window(
                operation,
                user_id,
                window_start,
                window_end,
                config.max_requests,
                config.window_seconds,
            )

            return RateLimitStatus(
                operation=operation,
                user_id=user_id,
                requests_in_window=window_data["requests_count"],
                max_requests=config.max_requests,
                window_seconds=config.window_seconds,
                remaining_requests=max(
                    0, config.max_requests - window_data["requests_count"]
                ),
                window_resets_at=window_end.isoformat(),
                description=config.description,
            )
        except Exception as e:
            logger.error(f"Error getting rate limit status: {str(e)}")
            # Return default status if database fails
            return RateLimitStatus(
                operation=operation,
                user_id=user_id,
                requests_in_window=0,
                max_requests=config.max_requests,
                window_seconds=config.window_seconds,
                remaining_requests=config.max_requests,
                window_resets_at=window_end.isoformat(),
                description=config.description,
            )

    async def get_all_rate_limits_status(
        self, user_id: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get status for all rate limits"""
        status_dict = {}

        for operation in self.rate_limits.keys():
            try:
                status = await self.get_rate_limit_status(operation, user_id)
                status_dict[operation] = {
                    "operation": status.operation,
                    "user_id": status.user_id,
                    "requests_in_window": status.requests_in_window,
                    "max_requests": status.max_requests,
                    "window_seconds": status.window_seconds,
                    "remaining_requests": status.remaining_requests,
                    "window_resets_at": status.window_resets_at,
                    "description": status.description,
                }
            except Exception as e:
                logger.error(f"Error getting status for {operation}: {str(e)}")
                # Add default status for failed operations
                config = self.rate_limits[operation]
                status_dict[operation] = {
                    "operation": operation,
                    "user_id": user_id,
                    "requests_in_window": 0,
                    "max_requests": config.max_requests,
                    "window_seconds": config.window_seconds,
                    "remaining_requests": config.max_requests,
                    "window_resets_at": (
                        datetime.utcnow() + timedelta(seconds=config.window_seconds)
                    ).isoformat(),
                    "description": config.description,
                }

        return status_dict

    async def get_blocked_requests(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get blocked requests from the last N hours"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        try:
            result = (
                supabase_manager.client.table("rate_limit_records")
                .select("*")
                .eq("was_blocked", True)
                .gte("timestamp", start_time.isoformat())
                .lte("timestamp", end_time.isoformat())
                .order("timestamp", desc=True)
                .execute()
            )

            return [
                {
                    "operation": record["operation"],
                    "user_id": record["user_id"],
                    "timestamp": record["timestamp"],
                    "ip_address": record["ip_address"],
                    "user_agent": record["user_agent"],
                    "correlation_id": record["correlation_id"],
                }
                for record in result.data
            ]
        except Exception as e:
            logger.error(f"Error getting blocked requests: {str(e)}")
            return []

    async def reset_rate_limits(
        self, user_id: Optional[str] = None, operation: Optional[str] = None
    ):
        """Reset rate limits for a user and/or operation"""
        try:
            # Clear rate limit windows
            query = supabase_client.table("rate_limit_windows").delete()

            if user_id:
                query = query.eq("user_id", user_id)
            if operation:
                query = query.eq("operation", operation)

            await query.execute()

            agent_logger.info(
                f"Rate limits reset for user: {user_id or 'all'}, operation: {operation or 'all'}"
            )
        except Exception as e:
            logger.error(f"Error resetting rate limits: {str(e)}")

    async def cleanup_expired_windows(self):
        """Clean up expired rate limit windows"""
        try:
            now = datetime.utcnow()
            await supabase_client.table("rate_limit_windows").delete().lt(
                "window_end", now.isoformat()
            ).execute()
        except Exception as e:
            logger.error(f"Error cleaning up expired windows: {str(e)}")


# Create singleton instance
rate_limiter = RateLimiter()
