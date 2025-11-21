"""
Unit tests for evaluation engine.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session

from app.evaluation_engine import EvaluationEngine
from app.models import EvaluationRun, TestCase, ModelResponse
from tests.conftest import MockProvider


@pytest.mark.unit
class TestEvaluationEngine:
    """Test evaluation engine functionality."""
    
    def test_engine_initialization(self):
        """Test evaluation engine can be initialized."""
        engine = EvaluationEngine()
        assert engine.providers is not None
        assert isinstance(engine.providers, dict)
    
    def test_engine_get_available_models(self):
        """Test getting available models from providers."""
        engine = EvaluationEngine()
        
        # Mock providers
        engine.providers = {
            "mock1": MockProvider(),
            "mock2": MockProvider()
        }
        
        models = engine.get_available_models()
        
        assert "mock1" in models
        assert "mock2" in models
        assert len(models["mock1"]) == 2
        assert len(models["mock2"]) == 2
    
    @pytest.mark.asyncio
    async def test_evaluate_single_success(
        self,
        test_db: Session,
        sample_evaluation_run: EvaluationRun,
        sample_test_case: TestCase
    ):
        """Test evaluating single prompt with single model."""
        engine = EvaluationEngine()
        mock_provider = MockProvider()
        mock_provider.set_response("Test response from model")
        
        engine.providers = {"mock": mock_provider}
        
        response = await engine._evaluate_single(
            db=test_db,
            evaluation_run_id=sample_evaluation_run.id,
            test_case_id=sample_test_case.id,
            prompt="Test prompt",
            provider_name="mock",
            model_name="mock-model-1",
            temperature=0.7,
            max_tokens=1000
        )
        
        assert response is not None
        assert response.response_text == "Test response from model"
        assert response.provider == "mock"
        assert response.model_name == "mock-model-1"
        assert response.response_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_evaluate_single_failure(
        self,
        test_db: Session,
        sample_evaluation_run: EvaluationRun,
        sample_test_case: TestCase
    ):
        """Test handling provider failure."""
        engine = EvaluationEngine()
        mock_provider = MockProvider()
        mock_provider.set_failure(True)
        
        engine.providers = {"mock": mock_provider}
        
        with pytest.raises(Exception):
            await engine._evaluate_single(
                db=test_db,
                evaluation_run_id=sample_evaluation_run.id,
                test_case_id=sample_test_case.id,
                prompt="Test prompt",
                provider_name="mock",
                model_name="mock-model-1",
                temperature=0.7,
                max_tokens=1000
            )
        
        # Check that error was logged to database
        error_response = test_db.query(ModelResponse).filter(
            ModelResponse.test_case_id == sample_test_case.id
        ).first()
        
        assert error_response is not None
        assert error_response.error_message is not None
    
    def test_generate_summary(
        self,
        test_db: Session,
        sample_evaluation_run: EvaluationRun,
        sample_model_response: ModelResponse
    ):
        """Test summary generation."""
        engine = EvaluationEngine()
        
        summary = engine._generate_summary(test_db, sample_evaluation_run.id)
        
        assert "total_responses" in summary
        assert "model_statistics" in summary
        assert summary["total_responses"] == 1
        assert len(summary["model_statistics"]) == 1
        
        stats = summary["model_statistics"][0]
        assert stats["provider"] == "anthropic"
        assert stats["model"] == "claude-3-5-sonnet"
        assert stats["total_requests"] == 1
        assert stats["successful_requests"] == 1
        assert stats["failed_requests"] == 0
    
    def test_generate_summary_with_failures(
        self,
        test_db: Session,
        sample_evaluation_run: EvaluationRun,
        sample_test_case: TestCase
    ):
        """Test summary generation with failed responses."""
        # Add a failed response
        failed_response = ModelResponse(
            evaluation_run_id=sample_evaluation_run.id,
            test_case_id=sample_test_case.id,
            model_name="gpt-4",
            provider="openai",
            response_text="",
            response_time_ms=0,
            error_message="API call failed"
        )
        test_db.add(failed_response)
        test_db.commit()
        
        engine = EvaluationEngine()
        summary = engine._generate_summary(test_db, sample_evaluation_run.id)
        
        assert summary["total_responses"] == 1
        stats = summary["model_statistics"][0]
        assert stats["failed_requests"] == 1
        assert stats["successful_requests"] == 0
    
    @pytest.mark.asyncio
    async def test_run_evaluation_parallel(
        self,
        test_db: Session,
        sample_evaluation_run: EvaluationRun
    ):
        """Test running evaluation with multiple models in parallel."""
        engine = EvaluationEngine()
        
        # Create mock providers
        mock1 = MockProvider()
        mock1.set_response("Response from model 1")
        mock2 = MockProvider()
        mock2.set_response("Response from model 2")
        
        engine.providers = {
            "mock1": mock1,
            "mock2": mock2
        }
        
        result = await engine.run_evaluation(
            db=test_db,
            evaluation_run_id=sample_evaluation_run.id,
            prompts=["Test prompt"],
            models=[
                {"provider": "mock1", "model": "mock-model-1"},
                {"provider": "mock2", "model": "mock-model-2"}
            ],
            temperature=0.7,
            max_tokens=1000,
            include_constitutional=False
        )
        
        assert result["status"] == "completed"
        assert result["total_evaluations"] == 2
        assert result["successful"] == 2
        assert result["failed"] == 0
        
        # Check database
        test_db.refresh(sample_evaluation_run)
        assert sample_evaluation_run.status == "completed"
        assert sample_evaluation_run.completed_at is not None
        
        # Check responses were saved
        responses = test_db.query(ModelResponse).filter(
            ModelResponse.evaluation_run_id == sample_evaluation_run.id
        ).all()
        assert len(responses) == 2


@pytest.mark.integration
class TestEvaluationEngineIntegration:
    """Integration tests for evaluation engine."""
    
    @pytest.mark.asyncio
    async def test_full_evaluation_flow(
        self,
        test_db: Session
    ):
        """Test complete evaluation flow from start to finish."""
        # Create evaluation run
        eval_run = EvaluationRun(
            name="Integration Test",
            description="Full flow test",
            status="pending",
            include_constitutional=0
        )
        test_db.add(eval_run)
        test_db.commit()
        test_db.refresh(eval_run)
        
        # Run evaluation
        engine = EvaluationEngine()
        mock_provider = MockProvider()
        mock_provider.set_response("Response 1")
        mock_provider.set_response("Response 2")
        engine.providers = {"mock": mock_provider}
        
        result = await engine.run_evaluation(
            db=test_db,
            evaluation_run_id=eval_run.id,
            prompts=["Prompt 1", "Prompt 2"],
            models=[{"provider": "mock", "model": "mock-model-1"}],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Verify results
        assert result["status"] == "completed"
        assert result["total_evaluations"] == 2
        
        # Check test cases created
        test_cases = test_db.query(TestCase).filter(
            TestCase.evaluation_run_id == eval_run.id
        ).all()
        assert len(test_cases) == 2
        
        # Check responses created
        responses = test_db.query(ModelResponse).filter(
            ModelResponse.evaluation_run_id == eval_run.id
        ).all()
        assert len(responses) == 2
