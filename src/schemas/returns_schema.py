from pydantic import BaseModel
from typing import Optional, Literal
from src.schemas.base_schema import BaseResponse


class ReturnResponse(BaseResponse):
    """
    Output schema for Module D — Return Classifier.
    """

    decision: Optional[Literal["REFUND", "EXCHANGE", "STORE_CREDIT", "ESCALATE"]] = None

    reasoning_en: Optional[str] = None
    reasoning_ar: Optional[str] = None

    escalation_flag: bool = False


# mapping alag rakho (class ke bahar)
decision_map = {
    "REFUND": "Refund",
    "EXCHANGE": "Exchange",
    "STORE_CREDIT": "StoreCredit",
    "ESCALATE": "Escalate"
}