from pydantic import BaseModel
from typing import Optional, List
from src.schemas.base_schema import BaseResponse


class HealthResponse(BaseResponse):
    """
    Output schema for Module B — Health Assistant.
    defer_to_doctor: True means model is NOT confident — tell mom to see a doctor.
    week: pregnancy week if applicable
    advice_en / advice_ar: bilingual health guidance
    symptoms_flagged: list of symptoms that triggered a doctor referral
    """
    defer_to_doctor: bool = False
    week: Optional[int] = None
    advice_en: Optional[str] = None
    advice_ar: Optional[str] = None
    symptoms_flagged: Optional[List[str]] = None
    doctor_message_en: Optional[str] = None
    doctor_message_ar: Optional[str] = None