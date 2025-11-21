"""
Pytest fixtures and configuration for Model Eval Studio tests.
"""
import os
import pytest
import asyncio
from typing import Generator, AsyncGenerator

# CRITICAL: Set test database URL BEFORE importing app modules
# This ensures all imports use the test database instead of production
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from app.models import Base, EvaluationRun, TestCase, ModelResponse
from app.database import get_db
from app.main import app
from app.providers.base import ModelResponse as ProviderResponse, BaseProvider


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create a fresh test database for each test.
    
    Uses SQLite in-memory database for speed.
    """
    # Create test engine
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    Create test client with test database.
    
    Overrides the get_db dependency to use test database.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_evaluation_run(test_db: Session) -> EvaluationRun:
    """Create a sample evaluation run for testing."""
    eval_run = EvaluationRun(
        name="Test Evaluation",
        description="Test evaluation for unit tests",
        status="pending",
        include_constitutional=0
    )
    test_db.add(eval_run)
    test_db.commit()
    test_db.refresh(eval_run)
    return eval_run


@pytest.fixture
def sample_test_case(test_db: Session, sample_evaluation_run: EvaluationRun) -> TestCase:
    """Create a sample test case for testing."""
    test_case = TestCase(
        evaluation_run_id=sample_evaluation_run.id,
        prompt="What is the capital of France?",
        order_index=0
    )
    test_db.add(test_case)
    test_db.commit()
    test_db.refresh(test_case)
    return test_case


@pytest.fixture
def sample_model_response(
    test_db: Session,
    sample_evaluation_run: EvaluationRun,
    sample_test_case: TestCase
) -> ModelResponse:
    """Create a sample model response for testing."""
    response = ModelResponse(
        evaluation_run_id=sample_evaluation_run.id,
        test_case_id=sample_test_case.id,
        model_name="claude-3-5-sonnet",
        provider="anthropic",
        response_text="The capital of France is Paris.",
        response_time_ms=1234.56,
        input_tokens=10,
        output_tokens=8,
        total_tokens=18,
        estimated_cost=0.00054,
        response_metadata={}
    )
    test_db.add(response)
    test_db.commit()
    test_db.refresh(response)
    return response


# Mock provider for testing
class MockProvider(BaseProvider):
    """Mock LLM provider for testing."""
    
    def __init__(self, api_key: str = "test-key"):
        super().__init__(api_key)
        self._responses = []
        self._should_fail = False
    
    def set_response(self, text: str, tokens: int = 100):
        """Set the mock response."""
        self._responses.append(text)
    
    def set_failure(self, should_fail: bool = True):
        """Make the provider fail."""
        self._should_fail = should_fail
    
    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> ProviderResponse:
        """Generate mock response."""
        if self._should_fail:
            raise Exception("Mock provider failure")
        
        text = self._responses.pop(0) if self._responses else "Mock response"
        
        return ProviderResponse(
            text=text,
            model=model,
            provider=self.provider_name,
            input_tokens=len(prompt.split()),
            output_tokens=len(text.split()),
            total_tokens=len(prompt.split()) + len(text.split()),
            response_time_ms=100.0,
            estimated_cost=0.001,
            metadata={"mock": True}
        )
    
    def get_available_models(self) -> list[str]:
        """Return mock models."""
        return ["mock-model-1", "mock-model-2"]
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate mock cost."""
        return (input_tokens * 0.00001) + (output_tokens * 0.00003)
    
    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "mock"


@pytest.fixture
def mock_provider() -> MockProvider:
    """Create mock provider for testing."""
    return MockProvider()


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response."""
    return ProviderResponse(
        text="This is a mock response from Claude.",
        model="claude-3-5-sonnet",
        provider="anthropic",
        input_tokens=10,
        output_tokens=8,
        total_tokens=18,
        response_time_ms=1234.56,
        estimated_cost=0.00054,
        metadata={}
    )


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return ProviderResponse(
        text="This is a mock response from GPT-4.",
        model="gpt-4",
        provider="openai",
        input_tokens=10,
        output_tokens=8,
        total_tokens=18,
        response_time_ms=987.65,
        estimated_cost=0.00048,
        metadata={}
    )


@pytest.fixture
def mock_google_response():
    """Mock Google API response."""
    return ProviderResponse(
        text="This is a mock response from Gemini.",
        model="gemini-pro",
        provider="google",
        input_tokens=10,
        output_tokens=8,
        total_tokens=18,
        response_time_ms=876.54,
        estimated_cost=0.00024,
        metadata={}
    )
