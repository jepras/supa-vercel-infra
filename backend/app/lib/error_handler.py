"""
Error Handler Utilities

This module provides error handling decorators and utilities for the application.
"""

import functools
import time
from typing import Callable, Any, Dict, Optional

# Use absolute imports for testing compatibility
try:
    from app.lib.supabase_client import supabase_manager
    from app.monitoring.agent_logger import agent_logger
except ImportError:
    # Fallback for when running as module
    from .supabase_client import supabase_manager
    from ..monitoring.agent_logger import agent_logger


class AIAnalysisError(Exception):
    """Custom exception for AI analysis errors."""

    pass


class PipedriveError(Exception):
    """Custom exception for Pipedrive API errors."""

    pass


class TokenRefreshError(Exception):
    """Custom exception for token refresh errors."""

    pass


class MicrosoftError(Exception):
    """Custom exception for Microsoft Graph API errors."""

    pass


def handle_ai_errors(func: Callable) -> Callable:
    """Decorator to handle AI analysis errors with logging and retry logic."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                start_time = time.time()
                result = await func(*args, **kwargs)
                processing_time = time.time() - start_time

                # Log successful operation
                if hasattr(func, "__name__"):
                    agent_logger.info(
                        f"AI operation {func.__name__} completed successfully",
                        {
                            "operation": func.__name__,
                            "processing_time": processing_time,
                            "attempt": attempt + 1,
                        },
                    )

                return result

            except Exception as e:
                agent_logger.error(
                    f"AI operation {func.__name__} failed",
                    {
                        "operation": func.__name__,
                        "error": str(e),
                        "attempt": attempt + 1,
                        "max_retries": max_retries,
                    },
                )

                if attempt == max_retries - 1:
                    # Last attempt failed, raise the error
                    raise AIAnalysisError(
                        f"AI operation failed after {max_retries} attempts: {str(e)}"
                    )

                # Wait before retrying
                time.sleep(retry_delay * (attempt + 1))

    return wrapper


def handle_pipedrive_errors(func: Callable) -> Callable:
    """Decorator to handle Pipedrive API errors with logging and retry logic."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                result = await func(*args, **kwargs)

                # Log successful operation
                if hasattr(func, "__name__"):
                    agent_logger.log_pipedrive_operation(
                        func.__name__, True, {"attempt": attempt + 1}
                    )

                return result

            except Exception as e:
                agent_logger.log_pipedrive_operation(
                    func.__name__,
                    False,
                    {
                        "error": str(e),
                        "attempt": attempt + 1,
                        "max_retries": max_retries,
                    },
                )

                if attempt == max_retries - 1:
                    # Last attempt failed, raise the error
                    raise PipedriveError(
                        f"Pipedrive operation failed after {max_retries} attempts: {str(e)}"
                    )

                # Wait before retrying
                time.sleep(retry_delay * (attempt + 1))

    return wrapper


def handle_token_refresh_errors(func: Callable) -> Callable:
    """Decorator to handle token refresh errors."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            agent_logger.log_token_refresh(True)
            return result

        except Exception as e:
            agent_logger.log_token_refresh(False, {"error": str(e)})
            raise TokenRefreshError(f"Token refresh failed: {str(e)}")

    return wrapper


def handle_microsoft_errors(func: Callable) -> Callable:
    """Decorator to handle Microsoft Graph API errors with logging and retry logic."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                result = await func(*args, **kwargs)

                # Log successful operation
                if hasattr(func, "__name__"):
                    agent_logger.log_microsoft_operation(
                        func.__name__, True, {"attempt": attempt + 1}
                    )

                return result

            except Exception as e:
                agent_logger.log_microsoft_operation(
                    func.__name__,
                    False,
                    {
                        "error": str(e),
                        "attempt": attempt + 1,
                        "max_retries": max_retries,
                    },
                )

                if attempt == max_retries - 1:
                    # Last attempt failed, raise the error
                    raise MicrosoftError(
                        f"Microsoft operation failed after {max_retries} attempts: {str(e)}"
                    )

                # Wait before retrying
                time.sleep(retry_delay * (attempt + 1))

    return wrapper


async def log_activity_to_supabase(
    user_id: str,
    activity_type: str,
    status: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Log activity to Supabase for real-time updates."""
    try:
        await supabase_manager.log_activity(
            user_id, activity_type, status, message, metadata
        )

    except Exception as e:
        # Log the error but don't fail the main operation
        print(f"Error logging activity: {e}")
        agent_logger.error(
            "Failed to log activity to Supabase",
            {"error": str(e), "activity_type": activity_type, "user_id": user_id},
        )


async def log_opportunity_to_supabase(
    user_id: str,
    email_data: Dict[str, Any],
    ai_result: Dict[str, Any],
    pipedrive_result: Optional[Dict[str, Any]] = None,
):
    """Log opportunity analysis to Supabase for tracking and analytics."""
    try:
        await supabase_manager.log_opportunity(
            user_id, email_data, ai_result, pipedrive_result
        )

    except Exception as e:
        # Log the error but don't fail the main operation
        print(f"Error logging opportunity: {e}")
        agent_logger.error(
            "Failed to log opportunity to Supabase",
            {"error": str(e), "user_id": user_id, "email_to": email_data.get("to")},
        )


def create_correlation_id() -> str:
    """Create a unique correlation ID for tracking operations."""
    import uuid

    return str(uuid.uuid4())
