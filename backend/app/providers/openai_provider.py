"""
OpenAI provider implementation.
"""
import time
from openai import AsyncOpenAI
from app.providers.base import BaseProvider, ModelResponse, ProviderError


class OpenAIProvider(BaseProvider):
    """Provider for OpenAI GPT models."""

    # Pricing per 1M tokens (update as pricing changes)
    PRICING = {
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "gpt-4-turbo-preview": {"input": 10.0, "output": 30.0},
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-4-32k": {"input": 60.0, "output": 120.0},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        "gpt-3.5-turbo-16k": {"input": 3.0, "output": 4.0},
    }

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        model: str = "gpt-4-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> ModelResponse:
        """Generate response from GPT."""
        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            response_time_ms = (time.time() - start_time) * 1000

            # Extract token usage
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0

            # Calculate cost
            cost = self.calculate_cost(input_tokens, output_tokens, model)

            # Extract text from response
            text = response.choices[0].message.content if response.choices else ""

            return ModelResponse(
                text=text,
                model=model,
                provider=self.provider_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                response_time_ms=response_time_ms,
                estimated_cost=cost,
                metadata={
                    "finish_reason": response.choices[0].finish_reason if response.choices else None,
                    "id": response.id,
                }
            )

        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            raise ProviderError(
                provider=self.provider_name,
                message=f"Failed to generate response: {str(e)}",
                original_error=e
            )

    def get_available_models(self) -> list[str]:
        """Return list of available GPT models."""
        return list(self.PRICING.keys())

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate estimated cost in USD."""
        if model not in self.PRICING:
            return 0.0

        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    @property
    def provider_name(self) -> str:
        return "openai"
