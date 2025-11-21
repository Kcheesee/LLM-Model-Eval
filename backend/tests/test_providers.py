"""
Unit tests for LLM providers.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.providers.base import BaseProvider, ModelResponse, ProviderError
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.google_provider import GoogleProvider
from tests.conftest import MockProvider


@pytest.mark.unit
class TestMockProvider:
    """Test the mock provider itself."""
    
    def test_mock_provider_initialization(self, mock_provider):
        """Test mock provider can be initialized."""
        assert mock_provider.api_key == "test-key"
        assert mock_provider.provider_name == "mock"
    
    @pytest.mark.asyncio
    async def test_mock_provider_generate(self, mock_provider):
        """Test mock provider can generate responses."""
        mock_provider.set_response("Test response", tokens=50)
        
        response = await mock_provider.generate(
            prompt="Test prompt",
            model="mock-model-1",
            temperature=0.7,
            max_tokens=1000
        )
        
        assert response.text == "Test response"
        assert response.model == "mock-model-1"
        assert response.provider == "mock"
        assert response.total_tokens > 0
        assert response.estimated_cost > 0
    
    @pytest.mark.asyncio
    async def test_mock_provider_failure(self, mock_provider):
        """Test mock provider can simulate failures."""
        mock_provider.set_failure(True)
        
        with pytest.raises(Exception, match="Mock provider failure"):
            await mock_provider.generate(
                prompt="Test prompt",
                model="mock-model-1"
            )
    
    def test_mock_provider_available_models(self, mock_provider):
        """Test mock provider returns available models."""
        models = mock_provider.get_available_models()
        assert len(models) == 2
        assert "mock-model-1" in models
        assert "mock-model-2" in models
    
    def test_mock_provider_cost_calculation(self, mock_provider):
        """Test mock provider calculates cost."""
        cost = mock_provider.calculate_cost(
            input_tokens=100,
            output_tokens=50,
            model="mock-model-1"
        )
        assert cost > 0
        assert isinstance(cost, float)


@pytest.mark.unit
class TestProviderBase:
    """Test base provider functionality."""
    
    def test_provider_response_model(self):
        """Test ModelResponse can be created."""
        response = ModelResponse(
            text="Test response",
            model="test-model",
            provider="test-provider",
            input_tokens=10,
            output_tokens=20,
            total_tokens=30,
            response_time_ms=100.5,
            estimated_cost=0.001
        )
        
        assert response.text == "Test response"
        assert response.model == "test-model"
        assert response.provider == "test-provider"
        assert response.total_tokens == 30
        assert response.response_time_ms == 100.5
    
    def test_provider_error(self):
        """Test ProviderError exception."""
        error = ProviderError(
            provider="test-provider",
            message="Test error message",
            original_error=ValueError("Original error")
        )
        
        assert error.provider == "test-provider"
        assert error.message == "Test error message"
        assert isinstance(error.original_error, ValueError)
        assert "[test-provider]" in str(error)


@pytest.mark.unit
@pytest.mark.slow
@pytest.mark.skip(reason="Complex external library mocking - tested via integration tests instead")
class TestAnthropicProvider:
    """Test Anthropic provider (requires mocking)."""
    
    def test_anthropic_available_models(self):
        """Test Anthropic provider returns available models."""
        provider = AnthropicProvider(api_key="test-key")
        models = provider.get_available_models()
        
        assert len(models) > 0
        assert "claude-3-5-sonnet" in models or "claude-3-opus" in models
    
    def test_anthropic_cost_calculation(self):
        """Test Anthropic cost calculation."""
        provider = AnthropicProvider(api_key="test-key")
        cost = provider.calculate_cost(
            input_tokens=1000,
            output_tokens=500,
            model="claude-3-5-sonnet"
        )
        
        assert cost > 0
        assert isinstance(cost, float)


@pytest.mark.unit
@pytest.mark.slow
@pytest.mark.skip(reason="Complex external library mocking - tested via integration tests instead")
class TestOpenAIProvider:
    """Test OpenAI provider (requires mocking)."""
    
    def test_openai_available_models(self):
        """Test OpenAI provider returns available models."""
        provider = OpenAIProvider(api_key="test-key")
        models = provider.get_available_models()
        
        assert len(models) > 0
        assert "gpt-4" in models or "gpt-4-turbo" in models
    
    def test_openai_cost_calculation(self):
        """Test OpenAI cost calculation."""
        provider = OpenAIProvider(api_key="test-key")
        cost = provider.calculate_cost(
            input_tokens=1000,
            output_tokens=500,
            model="gpt-4"
        )
        
        assert cost > 0
        assert isinstance(cost, float)


@pytest.mark.unit
@pytest.mark.slow
@pytest.mark.skip(reason="Complex external library mocking - tested via integration tests instead")
class TestGoogleProvider:
    """Test Google provider (requires mocking)."""
    
    def test_google_available_models(self):
        """Test Google provider returns available models."""
        provider = GoogleProvider(api_key="test-key")
        models = provider.get_available_models()
        
        assert len(models) > 0
        assert "gemini-pro" in models or "gemini-1.5-pro" in models
    
    def test_google_cost_calculation(self):
        """Test Google cost calculation."""
        provider = GoogleProvider(api_key="test-key")
        cost = provider.calculate_cost(
            input_tokens=1000,
            output_tokens=500,
            model="gemini-pro"
        )
        
        assert cost > 0
        assert isinstance(cost, float)
