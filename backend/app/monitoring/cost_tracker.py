"""
Cost Tracker for OpenRouter API

This module tracks and monitors costs for AI operations using OpenRouter API.
"""

import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging
from app.monitoring.agent_logger import agent_logger

logger = logging.getLogger(__name__)


@dataclass
class CostRecord:
    """Record of an API call cost"""

    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    operation: str
    correlation_id: str
    user_id: Optional[str] = None


@dataclass
class ModelCost:
    """Cost configuration for a specific model"""

    model_name: str
    input_cost_per_1k: float  # Cost per 1K input tokens
    output_cost_per_1k: float  # Cost per 1K output tokens
    max_daily_cost: float  # Maximum daily cost limit
    is_active: bool = True


class CostTracker:
    """Tracks and monitors OpenRouter API costs"""

    def __init__(self):
        self.cost_records: List[CostRecord] = []
        self.model_costs = self._initialize_model_costs()
        self.daily_limits = self._load_daily_limits()

    def _initialize_model_costs(self) -> Dict[str, ModelCost]:
        """Initialize cost configurations for different models"""
        return {
            "openai/gpt-4o-mini": ModelCost(
                model_name="openai/gpt-4o-mini",
                input_cost_per_1k=0.00015,  # $0.15 per 1M tokens
                output_cost_per_1k=0.0006,  # $0.60 per 1M tokens
                max_daily_cost=10.0,  # $10 per day
            ),
            "openai/gpt-4o": ModelCost(
                model_name="openai/gpt-4o",
                input_cost_per_1k=0.0025,  # $2.50 per 1M tokens
                output_cost_per_1k=0.01,  # $10.00 per 1M tokens
                max_daily_cost=50.0,  # $50 per day
            ),
            "anthropic/claude-3-5-sonnet": ModelCost(
                model_name="anthropic/claude-3-5-sonnet",
                input_cost_per_1k=0.003,  # $3.00 per 1M tokens
                output_cost_per_1k=0.015,  # $15.00 per 1M tokens
                max_daily_cost=100.0,  # $100 per day
            ),
            "meta-llama/llama-3.1-8b-instruct": ModelCost(
                model_name="meta-llama/llama-3.1-8b-instruct",
                input_cost_per_1k=0.00005,  # $0.05 per 1M tokens
                output_cost_per_1k=0.0002,  # $0.20 per 1M tokens
                max_daily_cost=5.0,  # $5 per day
            ),
        }

    def _load_daily_limits(self) -> Dict[str, float]:
        """Load daily cost limits from environment variables"""
        return {
            "default": float(
                os.getenv("OPENROUTER_DAILY_LIMIT", "20.0")
            ),  # $20 default
            "user_specific": {},  # Can be populated from database
        }

    def calculate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate the cost for a specific API call"""
        if model not in self.model_costs:
            logger.warning(f"Unknown model {model}, using default cost")
            return 0.0

        model_cost = self.model_costs[model]
        input_cost = (input_tokens / 1000) * model_cost.input_cost_per_1k
        output_cost = (output_tokens / 1000) * model_cost.output_cost_per_1k

        return input_cost + output_cost

    def record_api_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        operation: str,
        correlation_id: str,
        user_id: Optional[str] = None,
    ) -> CostRecord:
        """Record an API call and its cost"""
        cost = self.calculate_cost(model, input_tokens, output_tokens)

        record = CostRecord(
            timestamp=datetime.utcnow().isoformat(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            operation=operation,
            correlation_id=correlation_id,
            user_id=user_id,
        )

        self.cost_records.append(record)

        # Log the cost
        agent_logger.info(
            f"API call cost recorded: ${cost:.4f}",
            {
                "operation": "cost_tracking",
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost,
                "operation_type": operation,
                "correlation_id": correlation_id,
                "user_id": user_id,
            },
        )

        return record

    def get_daily_cost(self, date: Optional[datetime] = None) -> float:
        """Get total cost for a specific date (defaults to today)"""
        if date is None:
            date = datetime.utcnow()

        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        daily_records = [
            record
            for record in self.cost_records
            if start_of_day <= datetime.fromisoformat(record.timestamp) < end_of_day
        ]

        return sum(record.cost_usd for record in daily_records)

    def get_user_daily_cost(
        self, user_id: str, date: Optional[datetime] = None
    ) -> float:
        """Get total cost for a specific user on a specific date"""
        if date is None:
            date = datetime.utcnow()

        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        user_records = [
            record
            for record in self.cost_records
            if (
                record.user_id == user_id
                and start_of_day
                <= datetime.fromisoformat(record.timestamp)
                < end_of_day
            )
        ]

        return sum(record.cost_usd for record in user_records)

    def check_daily_limit(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Check if daily cost limit has been reached"""
        daily_cost = (
            self.get_user_daily_cost(user_id) if user_id else self.get_daily_cost()
        )
        limit = self.daily_limits.get(user_id, self.daily_limits["default"])

        return {
            "daily_cost": daily_cost,
            "daily_limit": limit,
            "limit_reached": daily_cost >= limit,
            "remaining_budget": max(0, limit - daily_cost),
        }

    def get_cost_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get cost summary for the last N days"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Filter records for the date range
        recent_records = [
            record
            for record in self.cost_records
            if start_date <= datetime.fromisoformat(record.timestamp) <= end_date
        ]

        # Group by date
        daily_costs = {}
        for record in recent_records:
            date = datetime.fromisoformat(record.timestamp).date().isoformat()
            daily_costs[date] = daily_costs.get(date, 0) + record.cost_usd

        # Group by model
        model_costs = {}
        for record in recent_records:
            model_costs[record.model] = (
                model_costs.get(record.model, 0) + record.cost_usd
            )

        return {
            "total_cost": sum(record.cost_usd for record in recent_records),
            "total_calls": len(recent_records),
            "daily_costs": daily_costs,
            "model_costs": model_costs,
            "period_days": days,
        }

    def get_model_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics by model"""
        model_stats = {}

        for record in self.cost_records:
            if record.model not in model_stats:
                model_stats[record.model] = {
                    "total_calls": 0,
                    "total_cost": 0.0,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                }

            stats = model_stats[record.model]
            stats["total_calls"] += 1
            stats["total_cost"] += record.cost_usd
            stats["total_input_tokens"] += record.input_tokens
            stats["total_output_tokens"] += record.output_tokens

        return model_stats

    def export_cost_data(self, format: str = "json") -> str:
        """Export cost data in specified format"""
        if format.lower() == "json":
            return json.dumps(
                {
                    "cost_records": [asdict(record) for record in self.cost_records],
                    "model_costs": {
                        name: asdict(cost) for name, cost in self.model_costs.items()
                    },
                    "daily_limits": self.daily_limits,
                },
                indent=2,
            )
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def clear_old_records(self, days_to_keep: int = 30):
        """Clear cost records older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        original_count = len(self.cost_records)
        self.cost_records = [
            record
            for record in self.cost_records
            if datetime.fromisoformat(record.timestamp) > cutoff_date
        ]

        cleared_count = original_count - len(self.cost_records)
        logger.info(f"Cleared {cleared_count} old cost records")


# Global cost tracker instance
cost_tracker = CostTracker()
