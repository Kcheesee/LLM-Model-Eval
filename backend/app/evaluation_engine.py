"""
Core evaluation engine for running parallel model comparisons.
"""
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import EvaluationRun, TestCase, ModelResponse as DBModelResponse
from app.providers import AnthropicProvider, OpenAIProvider, GoogleProvider, BaseProvider
from app.config import get_settings

settings = get_settings()


class EvaluationEngine:
    """Orchestrates parallel evaluation across multiple LLM providers."""

    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize available providers based on API keys."""
        if settings.ANTHROPIC_API_KEY:
            self.providers["anthropic"] = AnthropicProvider(settings.ANTHROPIC_API_KEY)

        if settings.OPENAI_API_KEY:
            self.providers["openai"] = OpenAIProvider(settings.OPENAI_API_KEY)

        if settings.GOOGLE_API_KEY:
            self.providers["google"] = GoogleProvider(settings.GOOGLE_API_KEY)

    async def run_evaluation(
        self,
        db: Session,
        evaluation_run_id: int,
        prompts: List[str],
        models: List[Dict[str, str]],  # [{"provider": "anthropic", "model": "claude-3-5-sonnet"}]
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """
        Run evaluation across multiple models and prompts in parallel.

        Args:
            db: Database session
            evaluation_run_id: ID of the evaluation run
            prompts: List of test prompts
            models: List of model configurations
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Dictionary with evaluation results and summary
        """
        # Update evaluation run status
        eval_run = db.query(EvaluationRun).filter(EvaluationRun.id == evaluation_run_id).first()
        eval_run.status = "running"
        db.commit()

        try:
            # Create all evaluation tasks
            tasks = []
            for prompt_idx, prompt in enumerate(prompts):
                # Create test case in database
                test_case = TestCase(
                    evaluation_run_id=evaluation_run_id,
                    prompt=prompt,
                    order_index=prompt_idx
                )
                db.add(test_case)
                db.flush()  # Get the test_case.id

                # Create tasks for each model
                for model_config in models:
                    task = self._evaluate_single(
                        db=db,
                        evaluation_run_id=evaluation_run_id,
                        test_case_id=test_case.id,
                        prompt=prompt,
                        provider_name=model_config["provider"],
                        model_name=model_config["model"],
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    tasks.append(task)

            db.commit()

            # Run all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Update evaluation run status
            eval_run.status = "completed"
            eval_run.completed_at = datetime.utcnow()
            db.commit()

            # Generate summary
            summary = self._generate_summary(db, evaluation_run_id)

            return {
                "status": "completed",
                "evaluation_run_id": evaluation_run_id,
                "total_evaluations": len(tasks),
                "successful": len([r for r in results if not isinstance(r, Exception)]),
                "failed": len([r for r in results if isinstance(r, Exception)]),
                "summary": summary,
            }

        except Exception as e:
            # Update evaluation run status on failure
            eval_run.status = "failed"
            db.commit()
            raise e

    async def _evaluate_single(
        self,
        db: Session,
        evaluation_run_id: int,
        test_case_id: int,
        prompt: str,
        provider_name: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
    ) -> DBModelResponse:
        """Evaluate a single prompt with a single model."""
        try:
            # Get provider
            provider = self.providers.get(provider_name)
            if not provider:
                raise ValueError(f"Provider {provider_name} not available")

            # Generate response
            response = await provider.generate(
                prompt=prompt,
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Save to database
            db_response = DBModelResponse(
                evaluation_run_id=evaluation_run_id,
                test_case_id=test_case_id,
                model_name=model_name,
                provider=provider_name,
                response_text=response.text,
                response_time_ms=response.response_time_ms,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                total_tokens=response.total_tokens,
                estimated_cost=response.estimated_cost,
                metadata=response.metadata,
            )
            db.add(db_response)
            db.commit()
            db.refresh(db_response)

            return db_response

        except Exception as e:
            # Log error to database
            db_response = DBModelResponse(
                evaluation_run_id=evaluation_run_id,
                test_case_id=test_case_id,
                model_name=model_name,
                provider=provider_name,
                response_text="",
                response_time_ms=0,
                error_message=str(e),
            )
            db.add(db_response)
            db.commit()
            raise e

    def _generate_summary(self, db: Session, evaluation_run_id: int) -> Dict[str, Any]:
        """Generate summary statistics for an evaluation run."""
        responses = db.query(DBModelResponse).filter(
            DBModelResponse.evaluation_run_id == evaluation_run_id
        ).all()

        if not responses:
            return {}

        # Calculate aggregate metrics by model
        model_stats = {}
        for response in responses:
            model_key = f"{response.provider}:{response.model_name}"

            if model_key not in model_stats:
                model_stats[model_key] = {
                    "provider": response.provider,
                    "model": response.model_name,
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "avg_response_time_ms": 0,
                    "total_tokens": 0,
                    "total_cost": 0,
                    "response_times": [],
                }

            stats = model_stats[model_key]
            stats["total_requests"] += 1

            if response.error_message:
                stats["failed_requests"] += 1
            else:
                stats["successful_requests"] += 1
                stats["response_times"].append(response.response_time_ms)
                stats["total_tokens"] += response.total_tokens or 0
                stats["total_cost"] += response.estimated_cost or 0

        # Calculate averages
        for model_key, stats in model_stats.items():
            if stats["response_times"]:
                stats["avg_response_time_ms"] = sum(stats["response_times"]) / len(stats["response_times"])
            del stats["response_times"]  # Remove raw data

        return {
            "total_responses": len(responses),
            "model_statistics": list(model_stats.values()),
        }

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get all available models from all providers."""
        return {
            provider_name: provider.get_available_models()
            for provider_name, provider in self.providers.items()
        }
