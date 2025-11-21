"""
FastAPI application for Model Eval Studio.
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from typing import List
import asyncio

from app.config import get_settings
from app.database import get_db, init_db
from app.models import EvaluationRun, TestCase, ModelResponse
from app.schemas import (
    EvaluationRunCreate,
    EvaluationRunResponse,
    EvaluationResultsResponse,
    AvailableModelsResponse,
    QuickEvaluationRequest,
    QuickEvaluationResponse,
)
from app.evaluation_engine import EvaluationEngine
from app.security import limiter, rate_limit_exceeded_handler, add_security_headers_middleware, RATE_LIMITS
from app.cost_analytics import get_cost_analytics
from slowapi.errors import RateLimitExceeded

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="Model Eval Studio API",
    description="API for evaluating and comparing LLM performance",
    version="0.1.0",
)

# CORS middleware (Hardened for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,  # Whitelist specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],  # Only allow specific methods
    allow_headers=["Content-Type", "Authorization"],  # Only allow specific headers
)

# Security headers middleware
app.middleware("http")(add_security_headers_middleware)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Initialize evaluation engine
evaluation_engine = EvaluationEngine()

# Register routers
from app.routes import cost_analytics
app.include_router(cost_analytics.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Model Eval Studio API",
        "version": "0.1.0",
    }


@app.get("/api/models", response_model=AvailableModelsResponse)
async def get_available_models():
    """Get all available models from configured providers."""
    providers = evaluation_engine.get_available_models()
    return {"providers": providers}


@app.post("/api/evaluations", response_model=EvaluationRunResponse, status_code=201)
@limiter.limit(RATE_LIMITS["evaluation_create"])
async def create_evaluation(
    request: Request,
    data: EvaluationRunCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Create a new evaluation run and start it in the background.
    """
    # Create evaluation run in database
    eval_run = EvaluationRun(
        name=data.name,
        description=data.description,
        status="pending",
        include_constitutional=1 if data.include_constitutional else 0,
    )
    db.add(eval_run)
    db.commit()
    db.refresh(eval_run)

    # Start evaluation in background
    background_tasks.add_task(
        run_evaluation_task,
        eval_run.id,
        data.prompts,
        data.models,
        data.temperature,
        data.max_tokens,
        data.include_constitutional,
    )

    return eval_run


async def run_evaluation_task(
    evaluation_run_id: int,
    prompts: List[str],
    models: List[dict],
    temperature: float,
    max_tokens: int,
    include_constitutional: bool = False,
):
    """Background task to run evaluation."""
    from app.database import SessionLocal
    import logging

    # Use context manager to ensure session is properly closed
    db = SessionLocal()
    try:
        await evaluation_engine.run_evaluation(
            db=db,
            evaluation_run_id=evaluation_run_id,
            prompts=prompts,
            models=models,
            temperature=temperature,
            max_tokens=max_tokens,
            include_constitutional=include_constitutional,
        )
        logging.info(f"Evaluation {evaluation_run_id} completed successfully")
    except Exception as e:
        logging.error(f"Evaluation {evaluation_run_id} failed: {str(e)}", exc_info=True)
        # Update evaluation run status to failed
        try:
            from app.models import EvaluationRun
            eval_run = db.query(EvaluationRun).filter(EvaluationRun.id == evaluation_run_id).first()
            if eval_run:
                eval_run.status = "failed"
                db.commit()
        except Exception:
            pass  # Best effort - don't fail if status update fails
        raise e
    finally:
        db.close()


@app.get("/api/evaluations", response_model=List[EvaluationRunResponse])
@limiter.limit(RATE_LIMITS["list"])
async def list_evaluations(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List all evaluation runs."""
    evaluations = (
        db.query(EvaluationRun)
        .order_by(EvaluationRun.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return evaluations


@app.get("/api/evaluations/{evaluation_id}", response_model=EvaluationResultsResponse)
async def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
):
    """Get detailed results for a specific evaluation run."""
    eval_run = (
        db.query(EvaluationRun)
        .filter(EvaluationRun.id == evaluation_id)
        .first()
    )

    if not eval_run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")

    # Get test cases with responses
    test_cases = (
        db.query(TestCase)
        .options(joinedload(TestCase.model_responses))
        .filter(TestCase.evaluation_run_id == evaluation_id)
        .order_by(TestCase.order_index)
        .all()
    )

    # Generate summary with cost analytics
    summary = evaluation_engine._generate_summary(db, evaluation_id)
    
    # Add comprehensive cost breakdown
    cost_analytics = get_cost_analytics()
    cost_breakdown = cost_analytics.get_evaluation_cost_breakdown(db, evaluation_id)
    summary["cost_analytics"] = cost_breakdown

    return {
        "evaluation_run": eval_run,
        "test_cases": test_cases,
        "summary": summary,
    }


@app.delete("/api/evaluations/{evaluation_id}", status_code=204)
async def delete_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
):
    """Delete an evaluation run and all associated data."""
    eval_run = (
        db.query(EvaluationRun)
        .filter(EvaluationRun.id == evaluation_id)
        .first()
    )

    if not eval_run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")

    db.delete(eval_run)
    db.commit()
    return None


@app.post("/api/quick-eval", response_model=QuickEvaluationResponse)
@limiter.limit(RATE_LIMITS["quick_eval"])
async def quick_evaluation(request: Request, data: QuickEvaluationRequest):
    """
    Quick one-off evaluation without saving to database.
    Useful for rapid testing and comparisons.
    """
    tasks = []
    for model_config in data.models:
        provider_name = model_config["provider"]
        model_name = model_config["model"]

        provider = evaluation_engine.providers.get(provider_name)
        if not provider:
            continue

        task = provider.generate(
            prompt=data.prompt,
            model=model_name,
            temperature=data.temperature,
            max_tokens=data.max_tokens,
        )
        tasks.append(task)

    # Run in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Format results
    formatted_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            formatted_results.append({
                "provider": data.models[i]["provider"],
                "model": data.models[i]["model"],
                "error": str(result),
            })
        else:
            formatted_results.append({
                "provider": result.provider,
                "model": result.model,
                "text": result.text,
                "response_time_ms": result.response_time_ms,
                "tokens": result.total_tokens,
                "cost": result.estimated_cost,
            })

    return {
        "prompt": data.prompt,
        "results": formatted_results,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
