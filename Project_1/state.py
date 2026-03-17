from typing import TypedDict, Literal, Dict, Any, List, Optional


QualityStatus = Literal["passed", "warning", "failed"]
FinalStatus = Literal["approved", "needs_review", "rejected"]


class AgentResult(TypedDict, total=False):
    name: str
    score: float
    status: QualityStatus
    issues: List[str]
    suggestions: List[str]
    details: Dict[str, Any]


class ProductData(TypedDict, total=False):
    id: Optional[str]
    title: str
    description: str
    price: float
    category: str
    images: List[str]
    reviews: List[Dict[str, Any]]


class Metadata(TypedDict, total=False):
    started_at: Optional[str]
    completed_at: Optional[str]
    decision_reason: Optional[str]
    stats: Dict[str, Any]


class ProductQualityState(TypedDict, total=False):
    product: ProductData
    errors: List[str]
    quality_results: Dict[str, AgentResult]
    overall_score: float
    all_issues: List[str]
    recommendations: List[str]
    metadata: Metadata
    final_status: Optional[FinalStatus]

