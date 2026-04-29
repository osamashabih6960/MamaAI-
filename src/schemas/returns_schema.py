from pydantic import BaseModel
from typing import Optional, Literal
from src.schemas.base_schema import BaseResponse


class ReturnResponse(BaseResponse):
    """
    Output schema for Module D — Return Classifier.
    decision: one of Refund / Exchange / StoreCredit / Escalate
    confidence: 0.0 to 1.0
    reasoning_en / reasoning_ar: why this decision was made
    """
    decision: Optional[Literal["Refund", "Exchange", "StoreCredit", "Escalate"]] = None
    reasoning_en: Optional[str] = None
    reasoning_ar: Optional[str] = None
    escalation_flag: bool = False