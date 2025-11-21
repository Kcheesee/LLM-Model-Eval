"""
API endpoints for cost analytics.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.cost_analytics import get_cost_analytics
from app.models import EvaluationRun

router = APIRouter(prefix="/api/cost", tags=["cost-analytics"])


@router.get("/evaluation/{evaluation_id}", response_model=Dict[str, Any])
async def get_evaluation_cost_breakdown(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed cost breakdown for an evaluation.
    
    Returns:
        - Total cost in USD
        - Per-model costs and token usage
        - Per-prompt costs
        - Cost projections (100/1000/10000 requests)
        - Cost efficiency analysis
        - Cheapest vs most expensive comparison
    """
    # Verify evaluation exists
    eval_run = db.query(EvaluationRun).filter(EvaluationRun.id == evaluation_id).first()
    if not eval_run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    
    analytics = get_cost_analytics()
    breakdown = analytics.get_evaluation_cost_breakdown(db, evaluation_id)
    
    return breakdown


@router.get("/evaluation/{evaluation_id}/comparison", response_model=Dict[str, Any])
async def get_cost_comparison(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get simplified cost comparison across models.
    
    Returns a concise summary perfect for quick reference or dashboards.
    """
    # Verify evaluation exists
    eval_run = db.query(EvaluationRun).filter(EvaluationRun.id == evaluation_id).first()
    if not eval_run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    
    analytics = get_cost_analytics()
    comparison = analytics.get_cost_comparison(db, evaluation_id)
    
    return comparison


@router.get("/pricing", response_model=Dict[str, Any])
async def get_current_pricing():
    """
    Get current pricing for all supported models.
    
    Returns pricing per 1M tokens (input/output) for all providers.
    Useful for cost estimation before running evaluations.
    """
    analytics = get_cost_analytics()
    
    return {
        "pricing": analytics.PRICING,
        "note": "Prices are per 1 million tokens in USD",
        "last_updated": "2024-11-21"
    }
