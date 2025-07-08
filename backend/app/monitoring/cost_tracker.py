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
from app.lib.supabase_client import supabase_manager

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

    async def record_api_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        operation: str,
        correlation_id: str,
        user_id: Optional[str] = None,
    ) -> CostRecord:
        """Record an API call and its cost to the database"""
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

        # Store in database
        try:
            supabase_manager.client.table("cost_records").insert(
                {
                    "timestamp": record.timestamp,
                    "model": record.model,
                    "input_tokens": record.input_tokens,
                    "output_tokens": record.output_tokens,
                    "cost_usd": float(record.cost_usd),
                    "operation": record.operation,
                    "correlation_id": record.correlation_id,
                    "user_id": record.user_id,
                }
            ).execute()
        except Exception as e:
            logger.error(f"Failed to store cost record in database: {str(e)}")
            # Continue execution even if database storage fails

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

    async def get_daily_cost(self, date: Optional[datetime] = None) -> float:
        """Get total cost for a specific date (defaults to today) from database"""
        if date is None:
            date = datetime.utcnow()

        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        try:
            result = (
                supabase_manager.client.table("cost_records")
                .select("cost_usd")
                .gte("timestamp", start_of_day.isoformat())
                .lt("timestamp", end_of_day.isoformat())
                .execute()
            )

            total_cost = sum(record["cost_usd"] for record in result.data)
            return total_cost
        except Exception as e:
            logger.error(f"Failed to get daily cost from database: {str(e)}")
            return 0.0

    async def get_user_daily_cost(
        self, user_id: str, date: Optional[datetime] = None
    ) -> float:
        """Get total cost for a specific user on a specific date from database"""
        if date is None:
            date = datetime.utcnow()

        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        try:
            result = (
                supabase_manager.client.table("cost_records")
                .select("cost_usd")
                .eq("user_id", user_id)
                .gte("timestamp", start_of_day.isoformat())
                .lt("timestamp", end_of_day.isoformat())
                .execute()
            )

            total_cost = sum(record["cost_usd"] for record in result.data)
            return total_cost
        except Exception as e:
            logger.error(f"Failed to get user daily cost from database: {str(e)}")
            return 0.0

    async def check_daily_limit(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Check if daily cost limit has been reached"""
        daily_cost = (
            await self.get_user_daily_cost(user_id)
            if user_id
            else await self.get_daily_cost()
        )
        limit = self.daily_limits.get(user_id, self.daily_limits["default"])

        return {
            "daily_cost": daily_cost,
            "daily_limit": limit,
            "limit_reached": daily_cost >= limit,
            "remaining_budget": max(0, limit - daily_cost),
        }

    async def get_cost_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get cost summary for the last N days from database"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        try:
            # Get all records in the date range
            result = (
                supabase_manager.client.table("cost_records")
                .select("*")
                .gte("timestamp", start_date.isoformat())
                .lte("timestamp", end_date.isoformat())
                .execute()
            )

            records = result.data

            # Calculate totals
            total_cost = sum(record["cost_usd"] for record in records)
            total_calls = len(records)

            # Group by date
            daily_costs = {}
            for record in records:
                date = (
                    datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
                    .date()
                    .isoformat()
                )
                daily_costs[date] = daily_costs.get(date, 0) + record["cost_usd"]

            # Group by model
            model_costs = {}
            for record in records:
                model = record["model"]
                model_costs[model] = model_costs.get(model, 0) + record["cost_usd"]

            return {
                "total_cost": total_cost,
                "total_calls": total_calls,
                "daily_costs": daily_costs,
                "model_costs": model_costs,
                "period_days": days,
            }
        except Exception as e:
            logger.error(f"Failed to get cost summary from database: {str(e)}")
            return {
                "total_cost": 0.0,
                "total_calls": 0,
                "daily_costs": {},
                "model_costs": {},
                "period_days": days,
            }

    async def get_model_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics by model from database"""
        try:
            result = supabase_manager.client.table("cost_records").select("*").execute()

            model_stats = {}
            for record in result.data:
                model = record["model"]
                if model not in model_stats:
                    model_stats[model] = {
                        "total_calls": 0,
                        "total_cost": 0.0,
                        "total_input_tokens": 0,
                        "total_output_tokens": 0,
                    }

                model_stats[model]["total_calls"] += 1
                model_stats[model]["total_cost"] += record["cost_usd"]
                model_stats[model]["total_input_tokens"] += record["input_tokens"]
                model_stats[model]["total_output_tokens"] += record["output_tokens"]

            return model_stats
        except Exception as e:
            logger.error(f"Failed to get model usage stats from database: {str(e)}")
            return {}

    async def export_cost_data(self, format: str = "json") -> str:
        """Export cost data in specified format"""
        try:
            result = supabase_manager.client.table("cost_records").select("*").execute()

            if format.lower() == "json":
                return json.dumps(result.data, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported format: {format}")
        except Exception as e:
            logger.error(f"Failed to export cost data: {str(e)}")
            return "[]"

    async def clear_old_records(self, days_to_keep: int = 30):
        """Clear old cost records from database"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        try:
            supabase_manager.client.table("cost_records").delete().lt(
                "timestamp", cutoff_date.isoformat()
            ).execute()
            logger.info(f"Cleared cost records older than {days_to_keep} days")
        except Exception as e:
            logger.error(f"Failed to clear old cost records: {str(e)}")


# Create singleton instance
cost_tracker = CostTracker()
