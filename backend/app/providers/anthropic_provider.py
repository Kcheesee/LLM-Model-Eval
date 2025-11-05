"""
Anthropic Claude provider implementation.
"""
import time
from anthropic import AsyncAnthropic
from app.providers.base import BaseProvider, ModelResponse, ProviderError
from app.config import get_settings


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic Claude models."""

    # Pricing per 1M tokens (update as pricing changes)
    PRICING = {
        "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
        "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
        "claude-3-5-sonnet-20240620": {"input": 3.0, "output": 15.0},
        "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    }

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> ModelResponse:
        """Generate response from Claude."""
        start_time = time.time()

        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )

            response_time_ms = (time.time() - start_time) * 1000

            # Extract token usage
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens

            # Calculate cost
            cost = self.calculate_cost(input_tokens, output_tokens, model)

            # Extract text from response
            text = response.content[0].text if response.content else ""

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
                    "stop_reason": response.stop_reason,
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
        """Return list of available Claude models."""
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
        return "anthropic"
