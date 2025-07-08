"""
Agent Logger for AI Operations

This module provides structured logging for AI agent operations.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


class AgentLogger:
    """Structured logger for AI agent operations."""

    def __init__(self, logger_name: str = "ai_agents"):
        self.logger = logging.getLogger(logger_name)
        self.correlation_id = str(uuid.uuid4())

    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for tracking operations across services."""
        self.correlation_id = correlation_id

    def _log(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """Internal logging method with structured data."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": self.correlation_id,
            "message": message,
            "level": level,
        }

        if extra:
            log_data.update(extra)

        log_message = json.dumps(log_data)

        if level == "INFO":
            self.logger.info(log_message)
        elif level == "ERROR":
            self.logger.error(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        elif level == "DEBUG":
            self.logger.debug(log_message)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message with structured data."""
        self._log("INFO", message, extra)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message with structured data."""
        self._log("ERROR", message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message with structured data."""
        self._log("WARNING", message, extra)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message with structured data."""
        self._log("DEBUG", message, extra)

    def log_ai_analysis_start(self, email_data: Dict[str, Any]):
        """Log the start of AI analysis."""
        self.info(
            "AI analysis started",
            {
                "operation": "ai_analysis_start",
                "email_from": email_data.get("from"),
                "email_to": email_data.get("to"),
                "email_subject": email_data.get("subject"),
                "content_length": len(email_data.get("content", "")),
                "has_thread": bool(email_data.get("email_thread")),
            },
        )

    def log_ai_analysis_complete(
        self, ai_result: Dict[str, Any], processing_time: float
    ):
        """Log the completion of AI analysis."""
        self.info(
            "AI analysis completed",
            {
                "operation": "ai_analysis_complete",
                "is_sales_opportunity": ai_result.get("is_sales_opportunity"),
                "confidence": ai_result.get("confidence"),
                "opportunity_type": ai_result.get("opportunity_type"),
                "estimated_value": ai_result.get("estimated_value"),
                "processing_time_seconds": processing_time,
            },
        )

    def log_pipedrive_operation(
        self, operation: str, success: bool, extra: Optional[Dict[str, Any]] = None
    ):
        """Log Pipedrive API operations."""
        log_data = {"operation": f"pipedrive_{operation}", "success": success}
        if extra:
            log_data.update(extra)

        level = "INFO" if success else "ERROR"
        self._log(
            level,
            f"Pipedrive {operation} {'completed' if success else 'failed'}",
            log_data,
        )

    def log_microsoft_operation(
        self, operation: str, success: bool, extra: Optional[Dict[str, Any]] = None
    ):
        """Log Microsoft Graph API operations."""
        log_data = {"operation": f"microsoft_{operation}", "success": success}
        if extra:
            log_data.update(extra)

        level = "INFO" if success else "ERROR"
        self._log(
            level,
            f"Microsoft {operation} {'completed' if success else 'failed'}",
            log_data,
        )

    def log_token_refresh(self, success: bool, provider: str = "pipedrive"):
        """Log token refresh operations."""
        self._log(
            "INFO" if success else "ERROR",
            f"{provider} token refresh {'completed' if success else 'failed'}",
            {"operation": "token_refresh", "provider": provider, "success": success},
        )

    def log_webhook_outcome(self, outcome: str, email_data: Dict[str, Any]):
        """Log webhook processing outcomes."""
        self.info(
            f"Webhook outcome: {outcome}",
            {
                "operation": "webhook_outcome",
                "outcome": outcome,
                "email_to": email_data.get("to"),
                "email_subject": email_data.get("subject"),
            },
        )


# Global logger instance
agent_logger = AgentLogger()
