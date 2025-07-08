"""
AI Model Configuration

This module manages AI model configurations for OpenRouter API.
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging
from app.monitoring.agent_logger import agent_logger

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """AI model providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    META = "meta"
    GOOGLE = "google"
    MISTRAL = "mistral"


@dataclass
class ModelConfig:
    """Configuration for an AI model"""

    model_id: str
    provider: ModelProvider
    display_name: str
    max_tokens: int
    temperature: float
    cost_per_1k_input: float
    cost_per_1k_output: float
    is_available: bool = True
    is_default: bool = False
    description: str = ""
    capabilities: List[str] = None


class AIModelManager:
    """Manages AI model configurations and selection"""

    def __init__(self):
        self.models = self._initialize_models()
        self.default_model = os.getenv("DEFAULT_AI_MODEL", "openai/gpt-4o-mini")

    def _initialize_models(self) -> Dict[str, ModelConfig]:
        """Initialize available AI models"""
        return {
            # OpenAI Models
            "openai/gpt-4o-mini": ModelConfig(
                model_id="openai/gpt-4o-mini",
                provider=ModelProvider.OPENAI,
                display_name="GPT-4o Mini",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.00015,
                cost_per_1k_output=0.0006,
                is_default=True,
                description="Fast and cost-effective model for email analysis",
                capabilities=["email_analysis", "text_generation", "classification"],
            ),
            "openai/gpt-4o": ModelConfig(
                model_id="openai/gpt-4o",
                provider=ModelProvider.OPENAI,
                display_name="GPT-4o",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.0025,
                cost_per_1k_output=0.01,
                description="High-performance model for complex analysis",
                capabilities=[
                    "email_analysis",
                    "text_generation",
                    "classification",
                    "reasoning",
                ],
            ),
            # Anthropic Models
            "anthropic/claude-3-5-sonnet": ModelConfig(
                model_id="anthropic/claude-3-5-sonnet",
                provider=ModelProvider.ANTHROPIC,
                display_name="Claude 3.5 Sonnet",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                description="Advanced reasoning and analysis capabilities",
                capabilities=[
                    "email_analysis",
                    "text_generation",
                    "classification",
                    "reasoning",
                    "code_generation",
                ],
            ),
            "anthropic/claude-3-haiku": ModelConfig(
                model_id="anthropic/claude-3-haiku",
                provider=ModelProvider.ANTHROPIC,
                display_name="Claude 3 Haiku",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.00025,
                cost_per_1k_output=0.00125,
                description="Fast and efficient model for basic analysis",
                capabilities=["email_analysis", "text_generation", "classification"],
            ),
            # Meta Models
            "meta-llama/llama-3.1-8b-instruct": ModelConfig(
                model_id="meta-llama/llama-3.1-8b-instruct",
                provider=ModelProvider.META,
                display_name="Llama 3.1 8B Instruct",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.00005,
                cost_per_1k_output=0.0002,
                description="Open-source model with good performance",
                capabilities=["email_analysis", "text_generation", "classification"],
            ),
            "meta-llama/llama-3.1-70b-instruct": ModelConfig(
                model_id="meta-llama/llama-3.1-70b-instruct",
                provider=ModelProvider.META,
                display_name="Llama 3.1 70B Instruct",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.0007,
                cost_per_1k_output=0.0008,
                description="High-performance open-source model",
                capabilities=[
                    "email_analysis",
                    "text_generation",
                    "classification",
                    "reasoning",
                ],
            ),
            # Google Models
            "google/gemini-pro": ModelConfig(
                model_id="google/gemini-pro",
                provider=ModelProvider.GOOGLE,
                display_name="Gemini Pro",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.0005,
                cost_per_1k_output=0.0015,
                description="Google's advanced language model",
                capabilities=[
                    "email_analysis",
                    "text_generation",
                    "classification",
                    "reasoning",
                ],
            ),
            # Mistral Models
            "mistralai/mistral-7b-instruct": ModelConfig(
                model_id="mistralai/mistral-7b-instruct",
                provider=ModelProvider.MISTRAL,
                display_name="Mistral 7B Instruct",
                max_tokens=4096,
                temperature=0.1,
                cost_per_1k_input=0.00014,
                cost_per_1k_output=0.00042,
                description="Efficient and capable open-source model",
                capabilities=["email_analysis", "text_generation", "classification"],
            ),
        }

    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model"""
        return self.models.get(model_id)

    def get_available_models(
        self, capability: Optional[str] = None
    ) -> List[ModelConfig]:
        """Get list of available models, optionally filtered by capability"""
        available_models = [
            model for model in self.models.values() if model.is_available
        ]

        if capability:
            available_models = [
                model
                for model in available_models
                if capability in (model.capabilities or [])
            ]

        return available_models

    def get_default_model(self) -> ModelConfig:
        """Get the default model configuration"""
        default_model = self.models.get(self.default_model)
        if not default_model:
            # Fallback to first available model
            available_models = self.get_available_models()
            if available_models:
                default_model = available_models[0]
            else:
                raise Exception("No available AI models found")

        return default_model

    def get_model_by_cost(
        self, max_cost_per_1k: float, capability: str = "email_analysis"
    ) -> Optional[ModelConfig]:
        """Get the best model within cost constraints"""
        available_models = self.get_available_models(capability)

        # Filter by cost
        affordable_models = [
            model
            for model in available_models
            if model.cost_per_1k_input <= max_cost_per_1k
        ]

        if not affordable_models:
            return None

        # Sort by cost (cheapest first)
        affordable_models.sort(key=lambda m: m.cost_per_1k_input)

        return affordable_models[0]

    def get_model_by_performance(
        self, capability: str = "email_analysis"
    ) -> ModelConfig:
        """Get the highest performance model for a capability"""
        available_models = self.get_available_models(capability)

        if not available_models:
            raise Exception(f"No available models for capability: {capability}")

        # Sort by cost (more expensive = better performance, generally)
        available_models.sort(key=lambda m: m.cost_per_1k_input, reverse=True)

        return available_models[0]

    def calculate_cost_estimate(
        self, model_id: str, input_tokens: int, output_tokens: int
    ) -> Dict[str, Any]:
        """Calculate estimated cost for a model operation"""
        model_config = self.get_model_config(model_id)
        if not model_config:
            return {"error": f"Unknown model: {model_id}"}

        input_cost = (input_tokens / 1000) * model_config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * model_config.cost_per_1k_output
        total_cost = input_cost + output_cost

        return {
            "model_id": model_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "cost_per_1k_input": model_config.cost_per_1k_input,
            "cost_per_1k_output": model_config.cost_per_1k_output,
        }

    def get_model_comparison(
        self, capability: str = "email_analysis"
    ) -> List[Dict[str, Any]]:
        """Get comparison of models for a specific capability"""
        available_models = self.get_available_models(capability)

        comparison = []
        for model in available_models:
            comparison.append(
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

        # Sort by cost (cheapest first)
        comparison.sort(key=lambda m: m["cost_per_1k_input"])

        return comparison

    def update_model_availability(self, model_id: str, is_available: bool):
        """Update model availability"""
        if model_id in self.models:
            self.models[model_id].is_available = is_available
            agent_logger.info(
                f"Updated model availability: {model_id} = {is_available}",
                {
                    "operation": "model_availability_update",
                    "model_id": model_id,
                    "is_available": is_available,
                },
            )
        else:
            logger.warning(f"Attempted to update unknown model: {model_id}")

    def set_default_model(self, model_id: str):
        """Set the default model"""
        if model_id in self.models:
            # Clear previous default
            for model in self.models.values():
                model.is_default = False

            # Set new default
            self.models[model_id].is_default = True
            self.default_model = model_id

            agent_logger.info(
                f"Set default model to: {model_id}",
                {"operation": "default_model_update", "model_id": model_id},
            )
        else:
            raise Exception(f"Unknown model: {model_id}")

    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about available models"""
        total_models = len(self.models)
        available_models = len([m for m in self.models.values() if m.is_available])

        providers = {}
        for model in self.models.values():
            provider = model.provider.value
            if provider not in providers:
                providers[provider] = {"total": 0, "available": 0}
            providers[provider]["total"] += 1
            if model.is_available:
                providers[provider]["available"] += 1

        return {
            "total_models": total_models,
            "available_models": available_models,
            "default_model": self.default_model,
            "providers": providers,
        }


# Global AI model manager instance
ai_model_manager = AIModelManager()
