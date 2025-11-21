"""
Cost analytics service for Model Eval Studio.

Provides comprehensive cost analysis and projections for LLM evaluations.
"""
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.models import EvaluationRun, ModelResponse
from app.config import get_settings

settings = get_settings()


class CostAnalytics:
    """Service for calculating and analyzing LLM costs."""
    
    # Updated pricing per 1M tokens (as of November 2024)
    PRICING = {
        "anthropic": {
            "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
            "claude-3-5-haiku": {"input": 0.80, "output": 4.00},
            "claude-3-opus": {"input": 15.00, "output": 75.00},
            "claude-3-sonnet": {"input": 3.00, "output": 15.00},
            "claude-3-haiku": {"input": 0.25, "output": 1.25},
        },
        "openai": {
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        },
        "google": {
            "gemini-pro": {"input": 0.50, "output": 1.50},
            "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
            "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
        }
    }
    
    @classmethod
    def calculate_cost(
        cls,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost in USD for given token usage.
        
        Args:
            provider: Provider name (anthropic, openai, google)
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD (e.g., 0.00025 = $0.00025)
        """
        pricing = cls.PRICING.get(provider.lower(), {}).get(model, None)
        
        if not pricing:
            # Fallback to generic estimation if model not found
            return (input_tokens * 0.00001) + (output_tokens * 0.00003)
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
    
    @classmethod
    def get_evaluation_cost_breakdown(
        cls,
        db: Session,
        evaluation_run_id: int
    ) -> Dict[str, Any]:
        """
        Get comprehensive cost breakdown for an evaluation run.
        
        Returns detailed cost analysis including:
        - Per-model costs
        - Per-prompt costs
        - Total costs
        - Cost efficiency metrics
        """
        responses = db.query(ModelResponse).filter(
            ModelResponse.evaluation_run_id == evaluation_run_id,
            ModelResponse.error_message.is_(None)  # Only successful responses
        ).all()
        
        if not responses:
            return {
                "total_cost": 0,
                "total_tokens": 0,
                "models": [],
                "prompts": []
            }
        
        # Calculate per-model costs
        model_costs = {}
        prompt_costs = {}
        
        for response in responses:
            model_key = f"{response.provider}:{response.model_name}"
            
            # Calculate accurate cost
            cost = cls.calculate_cost(
                response.provider,
                response.model_name,
                response.input_tokens or 0,
                response.output_tokens or 0
            )
            
            # Aggregate by model
            if model_key not in model_costs:
                model_costs[model_key] = {
                    "provider": response.provider,
                    "model": response.model_name,
                    "total_cost": 0,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "total_tokens": 0,
                    "request_count": 0,
                    "avg_cost_per_request": 0,
                    "avg_response_time_ms": 0,
                    "response_times": []
                }
            
            model_costs[model_key]["total_cost"] += cost
            model_costs[model_key]["total_input_tokens"] += response.input_tokens or 0
            model_costs[model_key]["total_output_tokens"] += response.output_tokens or 0
            model_costs[model_key]["total_tokens"] += response.total_tokens or 0
            model_costs[model_key]["request_count"] += 1
            model_costs[model_key]["response_times"].append(response.response_time_ms)
            
            # Aggregate by prompt
            prompt_key = response.test_case_id
            if prompt_key not in prompt_costs:
                prompt_costs[prompt_key] = {
                    "test_case_id": prompt_key,
                    "total_cost": 0,
                    "models": {}
                }
            
            prompt_costs[prompt_key]["total_cost"] += cost
            prompt_costs[prompt_key]["models"][model_key] = {
                "cost": cost,
                "tokens": response.total_tokens or 0
            }
        
        # Calculate averages and rankings
        for model_key, stats in model_costs.items():
            stats["avg_cost_per_request"] = stats["total_cost"] / stats["request_count"]
            stats["avg_response_time_ms"] = sum(stats["response_times"]) / len(stats["response_times"])
            stats["cost_per_1k_tokens"] = (stats["total_cost"] / stats["total_tokens"] * 1000) if stats["total_tokens"] > 0 else 0
            # Cost efficiency: lower is better (cost / quality proxy using response time)
            stats["efficiency_score"] = stats["total_cost"] / (stats["avg_response_time_ms"] / 1000) if stats["avg_response_time_ms"] > 0 else 0
            del stats["response_times"]  # Remove raw data
        
        # Sort models by cost (cheapest first)
        sorted_models = sorted(
            model_costs.values(),
            key=lambda x: x["total_cost"]
        )
        
        # Calculate total cost
        total_cost = sum(m["total_cost"] for m in sorted_models)
        total_tokens = sum(m["total_tokens"] for m in sorted_models)
        
        # Find most/least cost-effective
        if sorted_models:
            cheapest = sorted_models[0]
            most_expensive = sorted_models[-1]
            cost_savings = most_expensive["total_cost"] - cheapest["total_cost"]
            savings_percentage = (cost_savings / most_expensive["total_cost"] * 100) if most_expensive["total_cost"] > 0 else 0
        else:
            cheapest = None
            most_expensive = None
            cost_savings = 0
            savings_percentage = 0
        
        return {
            "total_cost": round(total_cost, 6),
            "total_cost_formatted": f"${total_cost:.6f}",
            "total_tokens": total_tokens,
            "total_input_tokens": sum(m["total_input_tokens"] for m in sorted_models),
            "total_output_tokens": sum(m["total_output_tokens"] for m in sorted_models),
            "models": sorted_models,
            "prompts": list(prompt_costs.values()),
            "cost_analysis": {
                "cheapest_model": cheapest,
                "most_expensive_model": most_expensive,
                "cost_savings": round(cost_savings, 6),
                "savings_percentage": round(savings_percentage, 2),
                "avg_cost_per_model": round(total_cost / len(sorted_models), 6) if sorted_models else 0
            },
            "projections": {
                "cost_per_100_requests": round(total_cost / len(responses) * 100, 4) if responses else 0,
                "cost_per_1000_requests": round(total_cost / len(responses) * 1000, 4) if responses else 0,
                "cost_per_10000_requests": round(total_cost / len(responses) * 10000, 2) if responses else 0,
            }
        }
    
    @classmethod
    def get_cost_comparison(
        cls,
        db: Session,
        evaluation_run_id: int
    ) -> Dict[str, Any]:
        """
        Get a simplified cost comparison for quick reference.
        
        Returns a concise comparison of costs across models.
        """
        breakdown = cls.get_evaluation_cost_breakdown(db, evaluation_run_id)
        
        if not breakdown["models"]:
            return {
                "summary": "No cost data available",
                "models": []
            }
        
        comparison = [
            {
                "provider": model["provider"],
                "model": model["model"],
                "total_cost": f"${model['total_cost']:.6f}",
                "cost_per_request": f"${model['avg_cost_per_request']:.6f}",
                "tokens": model["total_tokens"],
                "avg_response_time": f"{model['avg_response_time_ms']:.0f}ms",
                "rank": idx + 1
            }
            for idx, model in enumerate(breakdown["models"])
        ]
        
        return {
            "summary": f"Evaluated {len(comparison)} models. "
                      f"Cheapest: {comparison[0]['model']} (${breakdown['models'][0]['total_cost']:.6f}), "
                      f"Most expensive: {comparison[-1]['model']} (${breakdown['models'][-1]['total_cost']:.6f}). "
                      f"Potential savings: {breakdown['cost_analysis']['savings_percentage']:.1f}%",
            "models": comparison,
            "total_cost": breakdown["total_cost_formatted"],
            "projections": breakdown["projections"]
        }


def get_cost_analytics() -> CostAnalytics:
    """Get CostAnalytics singleton instance."""
    return CostAnalytics()
