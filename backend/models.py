"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class ScoreDetail(BaseModel):
    category: str
    score: int
    maxScore: int = Field(default=10, alias="maxScore")
    strengths: List[str]
    weaknesses: List[str]


class CritiqueDomain(BaseModel):
    domain: str
    score: float  # Changed from int to float for decimal precision


class SectionScore(BaseModel):
    section: str
    score: int


class CritiqueIssue(BaseModel):
    severity: Literal["high", "medium", "low"]
    category: str
    domain: Optional[str] = None  # Added for domain filtering
    description: str


class CritiqueRecommendation(BaseModel):
    priority: Literal["high", "medium", "low"]
    domain: Optional[str] = None  # Added for domain filtering
    recommendation: str


class FullCritique(BaseModel):
    summary: str
    issues: List[CritiqueIssue]
    recommendations: List[CritiqueRecommendation]


class BudgetItem(BaseModel):
    category: str
    amount: float
    percentage: float


class BudgetFlag(BaseModel):
    type: Literal["warning", "error", "info"]
    message: str


class BudgetAnalysis(BaseModel):
    totalBudget: float = Field(alias="totalBudget")
    breakdown: List[BudgetItem]
    flags: List[BudgetFlag]
    summary: str


class PlagiarismCheck(BaseModel):
    similarity_score: Optional[float] = None
    matched_reference_text: Optional[str] = None
    risk_level: Literal["HIGH", "MEDIUM", "LOW", "UNKNOWN"]
    error: Optional[str] = None


class EvaluationCreate(BaseModel):
    file_name: str
    file_size: int
    decision: Literal["ACCEPT", "REJECT", "REVISE", "CONDITIONALLY ACCEPT"]
    overall_score: float
    domain: str
    scores: List[ScoreDetail]
    critique_domains: List[CritiqueDomain]
    section_scores: List[SectionScore]
    full_critique: FullCritique
    budget_analysis: BudgetAnalysis
    summary: Optional[dict] = None
    plagiarism_check: Optional[PlagiarismCheck] = None


class EvaluationResponse(EvaluationCreate):
    id: str
    created_at: str
    updated_at: str
    
    class Config:
        populate_by_name = True


class SettingsModel(BaseModel):
    id: Optional[str] = None
    max_budget: int = 50000
    chunk_size: int = 1000
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        populate_by_name = True
