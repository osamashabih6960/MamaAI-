from src.utils.llm_client import call_llm
from src.utils.validator import parse_llm_json
from src.utils.language_detect import get_response_language_instruction
from src.schemas.returns_schema import ReturnResponse

SYSTEM_PROMPT = """
You are MamaAI's Return Classifier for Mumzworld's customer operations team.

Given a customer's return reason, classify it and explain the decision bilingually.

Decision options:
- Refund       : Product defective, wrong item, or major quality issue
- Exchange     : Size/color wrong, minor mismatch, preference issue
- StoreCredit  : Partial dissatisfaction, buyer's remorse, minor issue
- Escalate     : Threat, fraud suspicion, unusual pattern, safety concern

Rules:
- confidence must reflect how clearly the reason maps to a decision.
- If confidence < 0.5, set escalation_flag=true so a human reviews it.
- reasoning must be kind, professional, and in both languages.
- Never invent details not in the customer's reason.

Return ONLY this JSON:
{
  "success": true,
  "confidence": 0.92,
  "null_reason": null,
  "decision": "Exchange",
  "reasoning_en": "Customer received the wrong size. An exchange is the appropriate resolution.",
  "reasoning_ar": "استلمت العميلة المقاس الخطأ. التبديل هو الحل المناسب.",
  "escalation_flag": false
}
"""


def run_returns(user_message: str, lang: str) -> dict:
    lang_instruction = get_response_language_instruction(lang)
    full_message = f"{lang_instruction}\n\nCustomer's return reason: {user_message}"

    raw = call_llm(system_prompt=SYSTEM_PROMPT, user_message=full_message)
    result = parse_llm_json(raw, ReturnResponse)

    if result is None:
        return {
            "success": False,
            "confidence": 0.0,
            "null_reason": "Could not classify this return reason.",
            "escalation_flag": True,
            "module": "returns",
        }

    return {**result.model_dump(), "module": "returns"}