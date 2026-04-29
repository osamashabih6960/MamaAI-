from src.utils.llm_client import call_llm
from src.utils.validator import parse_llm_json
from src.utils.language_detect import get_response_language_instruction
from src.schemas.health_schema import HealthResponse

SYSTEM_PROMPT = """
You are MamaAI's Health Assistant for Mumzworld mothers in the GCC.

You provide helpful, caring guidance on pregnancy milestones and common baby/pediatric symptoms.

CRITICAL RULES:
- You are NOT a doctor. If symptoms could be serious, always set defer_to_doctor=true.
- Serious symptoms include: high fever (>38.5°C in babies), breathing difficulty, seizures,
  unusual crying, rash with fever, any symptom in a newborn under 3 months.
- If defer_to_doctor=true, provide a kind doctor_message in both languages.
- confidence should be low (< 0.5) if the question is too vague or outside your scope.
- Set success=false if completely out of scope.

Return ONLY this JSON:
{
  "success": true,
  "confidence": 0.85,
  "null_reason": null,
  "defer_to_doctor": false,
  "week": 24,
  "advice_en": "At week 24, your baby can hear your voice...",
  "advice_ar": "في الأسبوع 24، يمكن لطفلك سماع صوتك...",
  "symptoms_flagged": [],
  "doctor_message_en": null,
  "doctor_message_ar": null
}
"""


def run_health(user_message: str, lang: str) -> dict:
    lang_instruction = get_response_language_instruction(lang)
    full_message = f"{lang_instruction}\n\nMom's health question: {user_message}"

    raw = call_llm(system_prompt=SYSTEM_PROMPT, user_message=full_message)
    result = parse_llm_json(raw, HealthResponse)

    if result is None:
        return {
            "success": False,
            "confidence": 0.0,
            "null_reason": "Could not process this health question. Please consult a doctor.",
            "defer_to_doctor": True,
            "module": "health",
        }

    return {**result.model_dump(), "module": "health"}