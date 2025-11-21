"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


# Evaluation Run Schemas
class EvaluationRunCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    prompts: List[str] = Field(..., min_length=1, max_length=100)
    models: List[Dict[str, str]] = Field(..., min_length=1, max_length=10)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=100000)
    include_constitutional: bool = Field(default=False, description="Include Constitutional AI evaluation")
    
    @field_validator('prompts')
    @classmethod
    def validate_prompts(cls, v: List[str]) -> List[str]:
        """Validate that prompts are not empty strings."""
        for i, prompt in enumerate(v):
            if not prompt or not prompt.strip():
                raise ValueError(f"Prompt at index {i} cannot be empty")
        return v
    
    @field_validator('models')
    @classmethod
    def validate_models(cls, v: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Validate that models have required fields."""
        for i, model in enumerate(v):
            if 'provider' not in model or 'model' not in model:
                raise ValueError(f"Model at index {i} must have 'provider' and 'model' fields")
            if not model['provider'] or not model['model']:
                raise ValueError(f"Model at index {i} cannot have empty provider or model")
        return v


class EvaluationRunResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Constitutional AI Schemas
class ConstitutionalScoreSchema(BaseModel):
    principle_name: str
    score: float
    explanation: str
    violations: List[str] = []


class ConstitutionalEvaluationSchema(BaseModel):
    overall_score: float
    passed: bool
    summary: str
    principle_scores: List[ConstitutionalScoreSchema]


# Model Response Schemas
class ModelResponseSchema(BaseModel):
    id: int
    test_case_id: int
    model_name: str
    provider: str
    response_text: str
    response_time_ms: float
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    estimated_cost: Optional[float]
    constitutional_score: Optional[float]
    constitutional_passed: Optional[bool]
    constitutional_data: Optional[ConstitutionalEvaluationSchema]
    error_message: Optional[str]
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# Test Case Schemas
class TestCaseSchema(BaseModel):
    id: int
    prompt: str
    order_index: int
    responses: List[ModelResponseSchema] = []

    class Config:
        from_attributes = True


# Evaluation Results Schema
class EvaluationResultsResponse(BaseModel):
    evaluation_run: EvaluationRunResponse
    test_cases: List[TestCaseSchema]
    summary: Dict[str, Any]


# Available Models Schema
class AvailableModelsResponse(BaseModel):
    providers: Dict[str, List[str]]


# Quick Evaluation Schema (for simple one-off comparisons)
class QuickEvaluationRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    models: List[Dict[str, str]] = Field(..., min_length=1, max_length=5)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=100000)
    
    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """Validate that prompt is not empty."""
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v
    
    @field_validator('models')
    @classmethod
    def validate_models(cls, v: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Validate that models have required fields."""
        for i, model in enumerate(v):
            if 'provider' not in model or 'model' not in model:
                raise ValueError(f"Model at index {i} must have 'provider' and 'model' fields")
        return v


class QuickEvaluationResponse(BaseModel):
    prompt: str
    results: List[Dict[str, Any]]
