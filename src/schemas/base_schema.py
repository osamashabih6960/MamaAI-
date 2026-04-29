from pydantic import BaseModel
from typing import Optional


class BaseResponse(BaseModel):
    """
    Shared base for all MamaAI module responses.
    - success=False means model explicitly could not answer.
    - confidence: 0.0 to 1.0
    - null_reason: human-readable reason why answer is null
    """
    success: bool = True
    confidence: float = 1.0
    null_reason: Optional[str] = None

    def is_confident(self, threshold: float = 0.5) -> bool:
        return self.success and self.confidence >= threshold