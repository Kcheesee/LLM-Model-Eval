"""
Tests for cost analytics functionality.
"""
import pytest
from sqlalchemy.orm import Session

from app.cost_analytics import CostAnalytics, get_cost_analytics
from app.models import EvaluationRun, TestCase, ModelResponse


@pytest.mark.unit
class TestCostAnalytics:
    """Test cost analytics calculations."""
    
    def test_calculate_cost_anthropic(self):
        """Test cost calculation for Anthropic models."""
        analytics = CostAnalytics()
        
        # Claude 3.5 Sonnet: $3/M input, $15/M output
        cost = analytics.calculate_cost(
            provider="anthropic",
            model="claude-3-5-sonnet",
            input_tokens=1000,
            output_tokens=500
        )
        
        # (1000/1M * $3) + (500/1M * $15) = $0.003 + $0.0075 = $0.0105
        assert cost == pytest.approx(0.0105, rel=1e-4)
    
    def test_calculate_cost_openai(self):
        """Test cost calculation for OpenAI models."""
        analytics = CostAnalytics()
        
        # GPT-4: $30/M input, $60/M output
        cost = analytics.calculate_cost(
            provider="openai",
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500
        )
        
        # (1000/1M * $30) + (500/1M * $60) = $0.03 + $0.03 = $0.06
        assert cost == pytest.approx(0.06, rel=1e-4)
    
    def test_calculate_cost_google(self):
        """Test cost calculation for Google models."""
        analytics = CostAnalytics()
        
        # Gemini Pro: $0.50/M input, $1.50/M output
        cost = analytics.calculate_cost(
            provider="google",
            model="gemini-pro",
            input_tokens=1000,
            output_tokens=500
        )
        
        # (1000/1M * $0.50) + (500/1M * $1.50) = $0.0005 + $0.00075 = $0.00125
        assert cost == pytest.approx(0.00125, rel=1e-4)
    
    def test_calculate_cost_unknown_model(self):
        """Test cost calculation for unknown model (fallback)."""
        analytics = CostAnalytics()
        
        cost = analytics.calculate_cost(
            provider="unknown",
            model="unknown-model",
            input_tokens=1000,
            output_tokens=500
        )
        
        # Should use fallback pricing
        assert cost > 0
        assert isinstance(cost, float)
    
    def test_get_evaluation_cost_breakdown(
        self,
        test_db: Session,
        sample_evaluation_run: EvaluationRun,
        sample_test_case: TestCase,
        sample_model_response: ModelResponse
    ):
        """Test comprehensive cost breakdown for evaluation."""
        analytics = CostAnalytics()
        
        breakdown = analytics.get_evaluation_cost_breakdown(
            test_db,
            sample_evaluation_run.id
        )
        
        # Verify structure
        assert "total_cost" in breakdown
        assert "total_tokens" in breakdown
        assert "models" in breakdown
        assert "cost_analysis" in breakdown
        assert "projections" in breakdown
        
        # Verify data
        assert breakdown["total_cost"] > 0
        assert breakdown["total_tokens"] > 0
        assert len(breakdown["models"]) == 1
        
        # Verify model data
        model = breakdown["models"][0]
        assert model["provider"] == "anthropic"
        assert model["model"] == "claude-3-5-sonnet"
        assert model["total_cost"] > 0
        assert model["request_count"] == 1
        
        # Verify cost analysis
        assert breakdown["cost_analysis"]["cheapest_model"] is not None
        assert breakdown["cost_analysis"]["most_expensive_model"] is not None
        
        # Verify projections
        assert "cost_per_100_requests" in breakdown["projections"]
        assert "cost_per_1000_requests" in breakdown["projections"]
        assert "cost_per_10000_requests" in breakdown["projections"]
    
    def test_get_cost_comparison(
        self,
        test_db: Session,
        sample_evaluation_run: EvaluationRun,
        sample_test_case: TestCase,
        sample_model_response: ModelResponse
    ):
        """Test simplified cost comparison."""
        analytics = CostAnalytics()
        
        comparison = analytics.get_cost_comparison(
            test_db,
            sample_evaluation_run.id
        )
        
        # Verify structure
        assert "summary" in comparison
        assert "models" in comparison
        assert "total_cost" in comparison
        assert "projections" in comparison
        
        # Verify model comparison
        assert len(comparison["models"]) == 1
        model = comparison["models"][0]
        assert "rank" in model
        assert "cost_per_request" in model
        assert model["rank"] == 1
    
    def test_get_cost_analytics_singleton(self):
        """Test get_cost_analytics returns CostAnalytics instance."""
        analytics = get_cost_analytics()
        assert isinstance(analytics, CostAnalytics)


@pytest.mark.integration
class TestCostAnalyticsAPI:
    """Test cost analytics API endpoints."""
    
    def test_get_evaluation_cost_breakdown_endpoint(
        self,
        client,
        sample_evaluation_run: EvaluationRun,
        sample_model_response: ModelResponse
    ):
        """Test cost breakdown API endpoint."""
        response = client.get(f"/api/cost/evaluation/{sample_evaluation_run.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_cost" in data
        assert "models" in data
        assert "cost_analysis" in data
    
    def test_get_cost_comparison_endpoint(
        self,
        client,
        sample_evaluation_run: EvaluationRun,
        sample_model_response: ModelResponse
    ):
        """Test cost comparison API endpoint."""
        response = client.get(f"/api/cost/evaluation/{sample_evaluation_run.id}/comparison")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "summary" in data
        assert "models" in data
        assert "total_cost" in data
    
    def test_get_pricing_endpoint(self, client):
        """Test pricing reference endpoint."""
        response = client.get("/api/cost/pricing")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "pricing" in data
        assert "anthropic" in data["pricing"]
        assert "openai" in data["pricing"]
        assert "google" in data["pricing"]
        
        # Verify pricing structure
        claude_pricing = data["pricing"]["anthropic"]["claude-3-5-sonnet"]
        assert "input" in claude_pricing
        assert "output" in claude_pricing
    
    def test_cost_breakdown_not_found(self, client):
        """Test cost breakdown for non-existent evaluation."""
        response = client.get("/api/cost/evaluation/99999")
        
        assert response.status_code == 404
