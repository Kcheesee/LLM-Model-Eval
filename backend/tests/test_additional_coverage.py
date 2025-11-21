"""
Additional integration tests to increase coverage.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, AsyncMock

from app.models import EvaluationRun, TestCase, ModelResponse
from app.evaluation_engine import EvaluationEngine
from tests.conftest import MockProvider


@pytest.mark.integration
class TestAdditionalAPITests:
    """Additional API tests for increased coverage."""
    
    def test_get_evaluation_with_cost_analytics(
        self,
        client: TestClient,
        sample_evaluation_run: EvaluationRun,
        sample_model_response: ModelResponse
    ):
        """Test that evaluation includes cost analytics."""
        response = client.get(f"/api/evaluations/{sample_evaluation_run.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should include cost analytics in summary
        assert "summary" in data
        assert "cost_analytics" in data["summary"]
        assert "total_cost" in data["summary"]["cost_analytics"]
        assert "models" in data["summary"]["cost_analytics"]
    
    def test_create_evaluation_with_constitutional(self, client: TestClient):
        """Test creating evaluation with constitutional AI enabled."""
        payload = {
            "name": "Constitutional Test",
            "description": "Test with constitutional AI",
            "prompts": ["Is this ethical?"],
            "models": [{"provider": "anthropic", "model": "claude-3-5-sonnet"}],
            "temperature": 0.7,
            "max_tokens": 1000,
            "include_constitutional": True
        }
        
        response = client.post("/api/evaluations", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Constitutional Test"
    
    def test_create_evaluation_invalid_temperature(self, client: TestClient):
        """Test validation for temperature out of range."""
        payload = {
            "name": "Invalid Temp",
            "prompts": ["Test"],
            "models": [{"provider": "anthropic", "model": "test"}],
            "temperature": 3.0,  # Too high (max is 2.0)
            "max_tokens": 1000
        }
        
        response = client.post("/api/evaluations", json=payload)
        assert response.status_code == 422
    
    def test_create_evaluation_invalid_max_tokens(self, client: TestClient):
        """Test validation for max_tokens out of range."""
        payload = {
            "name": "Invalid Tokens",
            "prompts": ["Test"],
            "models": [{"provider": "anthropic", "model": "test"}],
            "temperature": 0.7,
            "max_tokens": 200000  # Too high (max is 100000)
        }
        
        response = client.post("/api/evaluations", json=payload)
        assert response.status_code == 422
    
    def test_create_evaluation_empty_prompt(self, client: TestClient):
        """Test validation for empty prompt strings."""
        payload = {
            "name": "Empty Prompt",
            "prompts": ["   "],  # Whitespace only
            "models": [{"provider": "anthropic", "model": "test"}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = client.post("/api/evaluations", json=payload)
        assert response.status_code == 422
    
    def test_create_evaluation_invalid_model_config(self, client: TestClient):
        """Test validation for malformed model configuration."""
        payload = {
            "name": "Invalid Model",
            "prompts": ["Test"],
            "models": [{"provider": "anthropic"}],  # Missing 'model' field
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = client.post("/api/evaluations", json=payload)
        assert response.status_code == 422


@pytest.mark.integration
class TestEvaluationEngineIntegration:
    """Additional evaluation engine integration tests."""
    
    @pytest.mark.asyncio
    async def test_evaluation_with_multiple_prompts(
        self,
        test_db: Session,
        sample_evaluation_run: EvaluationRun
    ):
        """Test evaluation with multiple prompts."""
        # Create mock providers
        mock_provider1 = MockProvider(api_key="key1")
        mock_provider1.set_response("Response 1 for prompt 1")
        mock_provider1.set_response("Response 2 for prompt 1")
        
        mock_provider2 = MockProvider(api_key="key2")
        mock_provider2.set_response("Response 1 for prompt 2")
        mock_provider2.set_response("Response 2 for prompt 2")
        
        engine = EvaluationEngine()
        engine.providers = {
            "mock1": mock_provider1,
            "mock2": mock_provider2
        }
        
        result = await engine.run_evaluation(
            db=test_db,
            evaluation_run_id=sample_evaluation_run.id,
            prompts=["Prompt 1", "Prompt 2"],
            models=[
                {"provider": "mock1", "model": "model-1"},
                {"provider": "mock2", "model": "model-2"}
            ],
            temperature=0.7,
            max_tokens=100,
            include_constitutional=False
        )
        
        assert result["status"] == "completed"
        assert result["total_evaluations"] == 4  # 2 prompts × 2 models
        assert result["successful"] == 4
    
    @pytest.mark.asyncio
    async def test_evaluation_with_provider_failure(
        self,
        test_db: Session,
        sample_evaluation_run: EvaluationRun
    ):
        """Test evaluation handles provider failures gracefully."""
        # Create one successful and one failing provider
        mock_provider_ok = MockProvider(api_key="key1")
        mock_provider_ok.set_response("Success")
        
        mock_provider_fail = MockProvider(api_key="key2")
        mock_provider_fail.set_failure(True)
        
        engine = EvaluationEngine()
        engine.providers = {
            "mock_ok": mock_provider_ok,
            "mock_fail": mock_provider_fail
        }
        
        result = await engine.run_evaluation(
            db=test_db,
            evaluation_run_id=sample_evaluation_run.id,
            prompts=["Test prompt"],
            models=[
                {"provider": "mock_ok", "model": "model-ok"},
                {"provider": "mock_fail", "model": "model-fail"}
            ],
            temperature=0.7,
            max_tokens=100,
            include_constitutional=False
        )
        
        # Should complete even with one failure
        assert result["status"] == "completed"
        assert result["successful"] == 1
        assert result["failed"] == 1
    
    @pytest.mark.asyncio
    async def test_evaluation_missing_provider(
        self,
        test_db: Session,
        sample_evaluation_run: EvaluationRun
    ):
        """Test evaluation handles missing provider."""
        engine = EvaluationEngine()
        engine.providers = {}  # No providers available
        
        # Evaluation completes but all requests fail
        result = await engine.run_evaluation(
            db=test_db,
            evaluation_run_id=sample_evaluation_run.id,
            prompts=["Test"],
            models=[{"provider": "nonexistent", "model": "test"}],
            temperature=0.7,
            max_tokens=100,
            include_constitutional=False
        )
        
        # Should complete with all failures
        assert result["status"] == "completed"
        assert result["successful"] == 0
        assert result["failed"] == 1


@pytest.mark.integration
class TestDatabaseEdgeCases:
    """Test database edge cases and error handling."""
    
    def test_list_empty_evaluations(self, client: TestClient):
        """Test listing evaluations when database is empty."""
        response = client.get("/api/evaluations")
        
        # Should return empty list, not error
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_pagination_out_of_bounds(self, client: TestClient):
        """Test pagination with out-of-bounds values."""
        response = client.get("/api/evaluations?skip=1000&limit=50")
        
        # Should return empty list, not error
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.integration
class TestSchemaValidation:
    """Test Pydantic schema validation edge cases."""
    
    def test_prompt_validation_whitespace(self, client: TestClient):
        """Test that whitespace-only prompts are rejected."""
        payload = {
            "name": "Test",
            "prompts": ["   \n\t  "],  # Only whitespace
            "models": [{"provider": "test", "model": "test"}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = client.post("/api/evaluations", json=payload)
        assert response.status_code == 422
    
    def test_temperature_boundary_valid(self, client: TestClient):
        """Test temperature at valid boundaries."""
        payload = {
            "name": "Boundary Test",
            "prompts": ["Test"],
            "models": [{"provider": "test", "model": "test"}],
            "temperature": 0.0,  # Min valid
            "max_tokens": 1000
        }
        
        response = client.post("/api/evaluations", json=payload)
        assert response.status_code == 201
        
        payload["temperature"] = 2.0  # Max valid
        response = client.post("/api/evaluations", json=payload)
        assert response.status_code == 201
    
    def test_max_tokens_boundary(self, client: TestClient):
        """Test max_tokens at boundaries."""
        payload = {
            "name": "Token Boundary",
            "prompts": ["Test"],
            "models": [{"provider": "test", "model": "test"}],
            "temperature": 0.7,
            "max_tokens": 1  # Min valid
        }
        
        response = client.post("/api/evaluations", json=payload)
        assert response.status_code == 201
    
    def test_quick_eval_empty_prompt(self, client: TestClient):
        """Test quick eval rejects empty prompt."""
        payload = {
            "prompt": "  ",  # Whitespace
            "models": [{"provider": "test", "model": "test"}],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = client.post("/api/quick-eval", json=payload)
        assert response.status_code == 422
    
    def test_quick_eval_invalid_model(self, client: TestClient):
        """Test quick eval with invalid model config."""
        payload = {
            "prompt": "Test",
            "models": [{"provider": ""}],  # Missing model field
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = client.post("/api/quick-eval", json=payload)
        assert response.status_code == 422
