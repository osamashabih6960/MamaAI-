from pydantic import BaseModel
from typing import Optional, List
from src.schemas.base_schema import BaseResponse


class VerdictResponse(BaseResponse):
    """
    Output schema for Module C — Moms Verdict.
    Synthesizes 200+ reviews into bilingual structured verdict.
    verdict_badge: e.g. "Highly Recommended", "Mixed Reviews", "Avoid"
    """
    product_name: Optional[str] = None
    verdict_badge_en: Optional[str] = None
    verdict_badge_ar: Optional[str] = None
    pros_en: Optional[List[str]] = None
    pros_ar: Optional[List[str]] = None
    cons_en: Optional[List[str]] = None
    cons_ar: Optional[List[str]] = None
    summary_en: Optional[str] = None
    summary_ar: Optional[str] = None
    review_count_used: Optional[int] = None