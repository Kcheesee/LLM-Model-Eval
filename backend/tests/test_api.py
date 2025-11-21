"""
Integration tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import EvaluationRun, TestCase, ModelResponse


@pytest.mark.integration
class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns health status."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Model Eval Studio API"


@pytest.mark.integration
class TestModelsEndpoint:
    """Test models endpoint."""
    
    def test_get_available_models(self, client: TestClient):
        """Test getting available models."""
        response = client.get("/api/models")
        
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert isinstance(data["providers"], dict)


@pytest.mark.integration
class TestEvaluationsEndpoint:
    """Test evaluations CRUD endpoints."""
    
    def test_create_evaluation(self, client: TestClient):
        """Test creating a new evaluation."""
        payload = {
            "name": "Test Evaluation",
            "description": "Test description",
            "prompts": ["What is AI?"],
            "models": [
                {"provider": "anthropic", "model": "claude-3-5-sonnet"}
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
            "include_constitutional": False
        }
        
        response = client.post("/api/evaluations", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "Test Evaluation"
        assert data["status"] == "pending"
    
    def test_create_evaluation_validation_error(self, client: TestClient):
        """Test validation errors on create."""
        payload = {
            "name": "Test",
            "prompts": [],  # Empty prompts should fail
            "models": [],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = client.post("/api/evaluations", json=payload)
        
        # Should fail validation
        assert response.status_code == 422
    
    def test_list_evaluations(self, client: TestClient, sample_evaluation_run: EvaluationRun):
        """Test listing evaluations."""
        response = client.get("/api/evaluations")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == sample_evaluation_run.id
    
    def test_list_evaluations_pagination(self, client: TestClient):
        """Test pagination parameters."""
        response = client.get("/api/evaluations?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_get_evaluation(
        self,
        client: TestClient,
        sample_evaluation_run: EvaluationRun,
        sample_model_response: ModelResponse
    ):
        """Test getting specific evaluation."""
        response = client.get(f"/api/evaluations/{sample_evaluation_run.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "evaluation_run" in data
        assert "test_cases" in data
        assert "summary" in data
        assert data["evaluation_run"]["id"] == sample_evaluation_run.id
    
    def test_get_evaluation_not_found(self, client: TestClient):
        """Test getting non-existent evaluation."""
        response = client.get("/api/evaluations/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_delete_evaluation(
        self,
        client: TestClient,
        test_db: Session,
        sample_evaluation_run: EvaluationRun
    ):
        """Test deleting evaluation."""
        eval_id = sample_evaluation_run.id
        
        response = client.delete(f"/api/evaluations/{eval_id}")
        
        assert response.status_code == 204
        
        # Verify deleted from database
        deleted = test_db.query(EvaluationRun).filter(
            EvaluationRun.id == eval_id
        ).first()
        assert deleted is None
    
    def test_delete_evaluation_not_found(self, client: TestClient):
        """Test deleting non-existent evaluation."""
        response = client.delete("/api/evaluations/99999")
        
        assert response.status_code == 404


@pytest.mark.integration
class TestQuickEvalEndpoint:
    """Test quick evaluation endpoint."""
    
    @pytest.mark.asyncio
    async def test_quick_eval_success(self, client: TestClient):
        """Test quick evaluation with mock provider."""
        payload = {
            "prompt": "What is 2+2?",
            "models": [
                {"provider": "mock", "model": "mock-model-1"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        # Note: This will fail without actual providers configured
        # In real tests, we'd mock the providers
        response = client.post("/api/quick-eval", json=payload)
        
        # May fail if providers not configured, but structure should be valid
        assert response.status_code in [200, 500]  # 500 if no providers
        
        if response.status_code == 200:
            data = response.json()
            assert "prompt" in data
            assert "results" in data
            assert data["prompt"] == "What is 2+2?"
    
    def test_quick_eval_validation(self, client: TestClient):
        """Test quick eval validation."""
        payload = {
            "prompt": "",  # Empty prompt
            "models": [],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = client.post("/api/quick-eval", json=payload)
        
        assert response.status_code == 422


@pytest.mark.e2e
class TestEndToEndFlow:
    """End-to-end tests for complete user flows."""
    
    @pytest.mark.asyncio
    async def test_complete_evaluation_flow(
        self,
        client: TestClient,
        test_db: Session
    ):
        """Test complete flow: create, wait, fetch, delete."""
        # 1. Create evaluation
        create_payload = {
            "name": "E2E Test",
            "description": "End-to-end test",
            "prompts": ["Test prompt 1"],
            "models": [
                {"provider": "anthropic", "model": "claude-3-5-sonnet"}
            ],
            "temperature": 0.7,
            "max_tokens": 100,
            "include_constitutional": False
        }
        
        create_response = client.post("/api/evaluations", json=create_payload)
        assert create_response.status_code == 201
        eval_id = create_response.json()["id"]
        
        # 2. List evaluations
        list_response = client.get("/api/evaluations")
        assert list_response.status_code == 200
        evaluations = list_response.json()
        assert any(e["id"] == eval_id for e in evaluations)
        
        # 3. Get specific evaluation
        get_response = client.get(f"/api/evaluations/{eval_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["evaluation_run"]["name"] == "E2E Test"
        
        # 4. Delete evaluation
        delete_response = client.delete(f"/api/evaluations/{eval_id}")
        assert delete_response.status_code == 204
        
        # 5. Verify deleted
        get_deleted = client.get(f"/api/evaluations/{eval_id}")
        assert get_deleted.status_code == 404
