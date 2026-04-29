from src.utils.llm_client import call_llm
from src.utils.validator import parse_llm_json
from src.utils.language_detect import get_response_language_instruction
from src.schemas.shopper_schema import ShoppingListResponse

SYSTEM_PROMPT = """
You are MamaAI's Smart Shopper assistant for Mumzworld — the largest e-commerce platform for mothers in the GCC.

Your job: Convert the mom's request into a structured bilingual shopping list with product recommendations.

Rules:
- Always return valid JSON matching the schema below.
- items_en and items_ar must be native language, not translations of each other.
- If the request is not about shopping, set success=false and explain in null_reason.
- confidence should reflect how clearly you understood the request (0.0 to 1.0).

Return ONLY this JSON — no explanation, no markdown:
{
  "success": true,
  "confidence": 0.9,
  "null_reason": null,
  "items_en": ["Newborn diapers size 1", "Baby wipes unscented"],
  "items_ar": ["حفاضات مولود جديد مقاس 1", "مناديل مبللة للأطفال بدون عطر"],
  "recommendations": [
    {
      "name_en": "Pampers New Baby",
      "name_ar": "بامبرز نيو بيبي",
      "reason_en": "Soft and gentle for newborn skin",
      "reason_ar": "ناعم ولطيف على بشرة المولود",
      "price_range": "25-40 AED"
    }
  ],
  "summary_en": "Here is your newborn shopping list.",
  "summary_ar": "إليكِ قائمة تسوق مولودك الجديد."
}
"""


def run_shopper(user_message: str, lang: str) -> dict:
    lang_instruction = get_response_language_instruction(lang)
    full_message = f"{lang_instruction}\n\nMom's request: {user_message}"

    raw = call_llm(system_prompt=SYSTEM_PROMPT, user_message=full_message)
    result = parse_llm_json(raw, ShoppingListResponse)

    if result is None:
        return {
            "success": False,
            "confidence": 0.0,
            "null_reason": "Could not generate a shopping list. Please try rephrasing.",
            "module": "shopping",
        }

    return {**result.model_dump(), "module": "shopping"}