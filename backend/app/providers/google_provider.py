"""
Google Gemini provider implementation.
"""
import time
import google.generativeai as genai
from app.providers.base import BaseProvider, ModelResponse, ProviderError


class GoogleProvider(BaseProvider):
    """Provider for Google Gemini models."""

    # Pricing per 1M tokens (update as pricing changes)
    PRICING = {
        "gemini-pro": {"input": 0.5, "output": 1.5},
        "gemini-1.5-pro": {"input": 3.5, "output": 10.5},
        "gemini-1.5-flash": {"input": 0.35, "output": 1.05},
    }

    def __init__(self, api_key: str):
        super().__init__(api_key)
        genai.configure(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        model: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> ModelResponse:
        """Generate response from Gemini."""
        start_time = time.time()

        try:
            # Create model instance
            model_instance = genai.GenerativeModel(model)

            # Configure generation
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                **kwargs
            )

            # Generate response
            response = await model_instance.generate_content_async(
                prompt,
                generation_config=generation_config
            )

            response_time_ms = (time.time() - start_time) * 1000

            # Extract text
            text = response.text if hasattr(response, 'text') else ""

            # Token counting is approximate for Gemini
            # You might need to use the count_tokens API for accuracy
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(text.split()) * 1.3  # Rough estimate
            total_tokens = int(input_tokens + output_tokens)

            input_tokens = int(input_tokens)
            output_tokens = int(output_tokens)

            # Calculate cost
            cost = self.calculate_cost(input_tokens, output_tokens, model)

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
                    "finish_reason": response.candidates[0].finish_reason.name if response.candidates else None,
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
        """Return list of available Gemini models."""
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
        return "google"
