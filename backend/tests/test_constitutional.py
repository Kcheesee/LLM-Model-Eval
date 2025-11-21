"""
Comprehensive tests for Constitutional AI functionality.
"""
import pytest
from sqlalchemy.orm import Session
from unittest.mock import AsyncMock

from app.constitutional import (
    ConstitutionalJudge,
    ConstitutionalPrinciple,
    ConstitutionalScore,
    DEFAULT_PRINCIPLES,
    evaluate_multiple_responses
)
from app.providers.base import ModelResponse as ProviderResponse
from tests.conftest import MockProvider


@pytest.mark.unit
class TestConstitutionalPrinciples:
    """Test constitutional principles and models."""
    
    def test_default_principles_exist(self):
        """Test that default principles areproperly defined."""
        assert len(DEFAULT_PRINCIPLES) == 5
        
        principle_names = [p.name for p in DEFAULT_PRINCIPLES]
        assert "helpfulness" in principle_names
        assert "harmlessness" in principle_names
        assert "honesty" in principle_names
        assert "respect" in principle_names
        assert "clarity" in principle_names
    
    def test_constitutional_principle_creation(self):
        """Test creating custom constitutional principle."""
        principle = ConstitutionalPrinciple(
            name="accuracy",
            description="Response should be factually accurate",
            weight=1.5
        )
        
        assert principle.name == "accuracy"
        assert principle.weight == 1.5
    
    def test_constitutional_score_creation(self):
        """Test creating constitutional score."""
        score = ConstitutionalScore(
            principle_name="helpfulness",
            score=8.5,
            explanation="Very helpful response",
            violations=[]
        )
        
        assert score.principle_name == "helpfulness"
        assert score.score == 8.5
        assert len(score.violations) == 0


@pytest.mark.integration
class TestConstitutionalJudge:
    """Test constitutional judge functionality."""
    
    @pytest.mark.asyncio
    async def test_build_evaluation_prompt(self):
        """Test evaluation prompt generation."""
        mock_provider = MockProvider()
        judge = ConstitutionalJudge(judge_provider=mock_provider)
        
        prompt = judge._build_evaluation_prompt(
            prompt="What is 2+2?",
            response="2+2 equals 4."
        )
        
        # Should include all principles
        assert "Helpfulness" in prompt
        assert "Harmlessness" in prompt
        assert "Honesty" in prompt
        assert "What is 2+2?" in prompt
        assert "2+2 equals 4." in prompt
    
    def test_parse_judge_response_valid(self):
        """Test parsing well-formatted judge response."""
        mock_provider = MockProvider()
        judge = ConstitutionalJudge(judge_provider=mock_provider)
        
        judge_text = """
PRINCIPLE: Helpfulness
SCORE: 9
EXPLANATION: The response directly answers the question.
VIOLATIONS: None

PRINCIPLE: Harmlessness
SCORE: 10
EXPLANATION: No harmful content present.
VIOLATIONS: None

PRINCIPLE: Honesty
SCORE: 9
EXPLANATION: The answer is factually correct.
VIOLATIONS: None
"""
        
        scores = judge._parse_judge_response(judge_text)
        
        assert len(scores) >= 3
        helpfulness = next(s for s in scores if s.principle_name == "helpfulness")
        assert helpfulness.score == 9.0
        assert len(helpfulness.violations) == 0
    
    def test_parse_judge_response_with_violations(self):
        """Test parsing response with violations."""
        mock_provider = MockProvider()
        judge = ConstitutionalJudge(judge_provider=mock_provider)
        
        judge_text = """
PRINCIPLE: Harmlessness
SCORE: 3
EXPLANATION: Response contains potentially harmful advice.
VIOLATIONS: Suggests dangerous activity
Lacks safety warnings
"""
        
        scores = judge._parse_judge_response(judge_text)
        
        harmless_score = next(s for s in scores if s.principle_name == "harmlessness")
        assert harmless_score.score == 3.0
        assert len(harmless_score.violations) > 0
    
    def test_parse_judge_response_malformed(self):
        """Test parsing malformed response falls back gracefully."""
        mock_provider = MockProvider()
        judge = ConstitutionalJudge(judge_provider=mock_provider)
        
        judge_text = "This is completely malformed text without proper structure"
        
        scores = judge._parse_judge_response(judge_text)
        
        # Should still return scores for all principles with default values
        assert len(scores) == len(DEFAULT_PRINCIPLES)
    
    def test_calculate_overall_score(self):
        """Test weighted score calculation."""
        mock_provider = MockProvider()
        judge = ConstitutionalJudge(judge_provider=mock_provider)
        
        principle_scores = [
            ConstitutionalScore(
                principle_name="helpfulness",
                score=8.0,
                explanation="Good",
                violations=[]
            ),
            ConstitutionalScore(
                principle_name="harmlessness",
                score=10.0,
                explanation="Perfect",
                violations=[]
            ),
            ConstitutionalScore(
                principle_name="honesty",
                score=9.0,
                explanation="Great",
                violations=[]
            )
        ]
        
        overall = judge._calculate_overall_score(principle_scores)
        
        # Should be weighted average
        assert 8.0 <= overall <= 10.0
        assert isinstance(overall, float)
    
    def test_generate_summary_excellent(self):
        """Test summary generation for excellent score."""
        mock_provider = MockProvider()
        judge = ConstitutionalJudge(judge_provider=mock_provider)
        
        scores = [
            ConstitutionalScore(
                principle_name="helpfulness",
                score=9.0,
                explanation="Excellent",
                violations=[]
            ),
            ConstitutionalScore(
                principle_name="harmlessness",
                score=10.0,
                explanation="Perfect",
                violations=[]
            )
        ]
        
        summary = judge._generate_summary(scores, 9.5)
        
        assert "Excellent" in summary
        assert "Helpfulness" in summary or "Harmlessness" in summary
    
    def test_generate_summary_with_concerns(self):
        """Test summary generation with concerns."""
        mock_provider = MockProvider()
        judge = ConstitutionalJudge(judge_provider=mock_provider)
        
        scores = [
            ConstitutionalScore(
                principle_name="helpfulness",
                score=6.0,
                explanation="Could be better",
                violations=[]
            ),
            ConstitutionalScore(
                principle_name="harmlessness",
                score=4.0,
                explanation="Has issues",
                violations=["Safety concern"]
            )
        ]
        
        summary = judge._generate_summary(scores, 5.0)
        
        assert "improvement" in summary.lower() or "concern" in summary.lower()
        assert "violation" in summary.lower()
    
    @pytest.mark.asyncio
    async def test_evaluate_response_integration(self):
        """Test full evaluate_response flow with mocked provider."""
        # Create mock provider that returns structured evaluation
        mock_provider = MockProvider()
        mock_provider.set_response("""
PRINCIPLE: Helpfulness
SCORE: 9
EXPLANATION: Very helpful and informative response.
VIOLATIONS: None

PRINCIPLE: Harmlessness
SCORE: 10
EXPLANATION: No harmful content whatsoever.
VIOLATIONS: None

PRINCIPLE: Honesty
SCORE: 8
EXPLANATION: Truthful but could acknowledge more nuance.
VIOLATIONS: None

PRINCIPLE: Respect
SCORE: 9
EXPLANATION: Respectful and inclusive language.
VIOLATIONS: None

PRINCIPLE: Clarity
SCORE: 7
EXPLANATION: Generally clear but could be more structured.
VIOLATIONS: None
""")
        
        judge = ConstitutionalJudge(judge_provider=mock_provider)
        
        evaluation = await judge.evaluate_response(
            prompt="What is AI?",
            response="AI stands for Artificial Intelligence...",
            model_name="gpt-4",
            provider_name="openai"
        )
        
        # Verify evaluation structure
        assert evaluation.model == "gpt-4"
        assert evaluation.provider == "openai"
        assert 0 <= evaluation.overall_score <= 10
        assert len(evaluation.principle_scores) > 0
        assert isinstance(evaluation.summary, str)
        assert isinstance(evaluation.passed, bool)
    
    @pytest.mark.asyncio
    async def test_evaluate_response_failing_score(self):
        """Test evaluation that should fail threshold."""
        mock_provider = MockProvider()
        mock_provider.set_response("""
PRINCIPLE: Helpfulness
SCORE: 3
EXPLANATION: Not very helpful.
VIOLATIONS: Does not answer the question

PRINCIPLE: Harmlessness
SCORE: 5
EXPLANATION: Some concerning elements.
VIOLATIONS: Potential safety issue

PRINCIPLE: Honesty
SCORE: 4
EXPLANATION: Contains inaccuracies.
VIOLATIONS: Factual errors

PRINCIPLE: Respect
SCORE: 4
EXPLANATION: Could be more respectful.
VIOLATIONS: None

PRINCIPLE: Clarity
SCORE: 3
EXPLANATION: Confusing structure.
VIOLATIONS: None
""")
        
        judge = ConstitutionalJudge(judge_provider=mock_provider)
        
        evaluation = await judge.evaluate_response(
            prompt="Explain quantum physics",
            response="Quantum is magic!",
            model_name="bad-model",
            provider_name="test"
        )
        
        # Should fail (threshold is 7.0)
        assert evaluation.overall_score < 7.0
        assert evaluation.passed is False
    
    def test_custom_principles(self):
        """Test using custom constitutional principles."""
        custom_principles = [
            ConstitutionalPrinciple(
                name="brevity",
                description="Responses should be concise",
                weight=1.0
            ),
            ConstitutionalPrinciple(
                name="technical_accuracy",
                description="Technical details must be correct",
                weight=2.0
            )
        ]
        
        mock_provider = MockProvider()
        judge = ConstitutionalJudge(
            judge_provider=mock_provider,
            principles=custom_principles
        )
        
        assert len(judge.principles) == 2
        assert judge.principles[0].name == "brevity"
        assert judge.principles[1].weight == 2.0


@pytest.mark.integration
class TestEvaluateMultipleResponses:
    """Test parallel evaluation of multiple responses."""
    
    @pytest.mark.asyncio
    async def test_evaluate_multiple_responses(self):
        """Test evaluating multiple responses in parallel."""
        mock_provider = MockProvider()
        # Set 3 responses for 3 evaluations
        for _ in range(3):
            mock_provider.set_response("""
PRINCIPLE: Helpfulness
SCORE: 8
EXPLANATION: Helpful.
VIOLATIONS: None

PRINCIPLE: Harmlessness
SCORE: 9
EXPLANATION: Safe.
VIOLATIONS: None

PRINCIPLE: Honesty
SCORE: 8
EXPLANATION: Honest.
VIOLATIONS: None

PRINCIPLE: Respect
SCORE: 9
EXPLANATION: Respectful.
VIOLATIONS: None

PRINCIPLE: Clarity
SCORE: 7
EXPLANATION: Clear.
VIOLATIONS: None
""")
        
        judge = ConstitutionalJudge(judge_provider=mock_provider)
        
        responses = [
            {"model": "gpt-4", "provider": "openai", "text": "Response 1"},
            {"model": "claude-3-5-sonnet", "provider": "anthropic", "text": "Response 2"},
            {"model": "gemini-pro", "provider": "google", "text": "Response 3"}
        ]
        
        evaluations = await evaluate_multiple_responses(
            judge=judge,
            prompt="Test prompt",
            responses=responses
        )
        
        assert len(evaluations) == 3
        assert all(isinstance(e, type(evaluations[0])) for e in evaluations)
        assert evaluations[0].model == "gpt-4"
        assert evaluations[1].model == "claude-3-5-sonnet"
        assert evaluations[2].model == "gemini-pro"
