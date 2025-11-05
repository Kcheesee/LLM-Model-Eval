"""
SQLAlchemy database models for evaluation storage.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class EvaluationRun(Base):
    """Represents a complete evaluation run comparing multiple models."""
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="pending")  # pending, running, completed, failed

    # Relationships
    test_cases = relationship("TestCase", back_populates="evaluation_run", cascade="all, delete-orphan")
    model_responses = relationship("ModelResponse", back_populates="evaluation_run", cascade="all, delete-orphan")


class TestCase(Base):
    """Individual test prompt within an evaluation run."""
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_run_id = Column(Integer, ForeignKey("evaluation_runs.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=True)  # Optional, for accuracy scoring
    category = Column(String(100), nullable=True)  # e.g., "summarization", "code_generation"
    order_index = Column(Integer, default=0)

    # Relationships
    evaluation_run = relationship("EvaluationRun", back_populates="test_cases")
    model_responses = relationship("ModelResponse", back_populates="test_case", cascade="all, delete-orphan")


class ModelResponse(Base):
    """Response from a specific model for a specific test case."""
    __tablename__ = "model_responses"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_run_id = Column(Integer, ForeignKey("evaluation_runs.id"), nullable=False)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)

    # Model info
    model_name = Column(String(100), nullable=False)  # e.g., "claude-sonnet-4", "gpt-4-turbo"
    provider = Column(String(50), nullable=False)  # e.g., "anthropic", "openai", "google"

    # Response data
    response_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Metrics
    response_time_ms = Column(Float, nullable=False)  # Latency in milliseconds
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    estimated_cost = Column(Float, nullable=True)  # Cost in USD

    # Additional metadata
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Store additional model-specific data

    # Relationships
    evaluation_run = relationship("EvaluationRun", back_populates="model_responses")
    test_case = relationship("TestCase", back_populates="model_responses")


class ModelConfig(Base):
    """Saved model configurations for reuse."""
    __tablename__ = "model_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    provider = Column(String(50), nullable=False)
    model_name = Column(String(100), nullable=False)

    # Model parameters
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1000)
    top_p = Column(Float, default=1.0)

    # Additional config
    config_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
