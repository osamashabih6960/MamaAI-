from pydantic import BaseModel
from typing import Optional, List
from src.schemas.base_schema import BaseResponse


class ProductRec(BaseModel):
    name_en: str
    name_ar: str
    reason_en: str
    reason_ar: str
    price_range: Optional[str] = None


class ShoppingListResponse(BaseResponse):
    """
    Output schema for Module A — Smart Shopper.
    items_en: English shopping list
    items_ar: Arabic shopping list (native, not translated)
    recommendations: product suggestions with reasoning
    """
    items_en: Optional[List[str]] = None
    items_ar: Optional[List[str]] = None
    recommendations: Optional[List[ProductRec]] = None
    summary_en: Optional[str] = None
    summary_ar: Optional[str] = None