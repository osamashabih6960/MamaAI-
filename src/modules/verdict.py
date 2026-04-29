from src.utils.llm_client import call_llm
from src.utils.validator import parse_llm_json
from src.utils.language_detect import get_response_language_instruction
from src.utils.rag_engine import retrieve_relevant_reviews
from src.schemas.verdict_schema import VerdictResponse

SYSTEM_PROMPT = """
You are MamaAI's Moms Verdict engine for Mumzworld.

You will receive a set of real customer reviews about a product.
Your job: synthesize them into a structured bilingual verdict that helps moms make quick decisions.

Rules:
- Pros and cons must come ONLY from the reviews. Do not invent.
- verdict_badge must be one of: "Highly Recommended" / "موصى به بشدة",
  "Good Choice" / "خيار جيد", "Mixed Reviews" / "آراء متباينة", "Avoid" / "تجنبي"
- Arabic must be native copy, not a translation.
- If reviews are empty or insufficient, set success=false.
- confidence reflects how many reviews you had to work with.

Return ONLY this JSON:
{
  "success": true,
  "confidence": 0.88,
  "null_reason": null,
  "product_name": "Pampers New Baby Size 1",
  "verdict_badge_en": "Highly Recommended",
  "verdict_badge_ar": "موصى به بشدة",
  "pros_en": ["Very soft on newborn skin", "Good absorbency", "No leaks overnight"],
  "pros_ar": ["ناعم جداً على بشرة المولود", "امتصاص جيد", "لا تسريب ليلاً"],
  "cons_en": ["Expensive compared to alternatives", "Tabs can be stiff"],
  "cons_ar": ["غالي مقارنة بالبدائل", "الأشرطة قد تكون متصلبة"],
  "summary_en": "Moms love this product for everyday use...",
  "summary_ar": "تحب الأمهات هذا المنتج للاستخدام اليومي...",
  "review_count_used": 18
}
"""


def extract_product_name(user_message: str) -> str:
    """Simple heuristic to pull product name from user message."""
    stopwords = {"reviews", "verdict", "of", "for", "about", "tell", "me", "the", "a"}
    words = [w for w in user_message.split() if w.lower() not in stopwords]
    return " ".join(words[:5])


def run_verdict(user_message: str, lang: str) -> dict:
    product_name = extract_product_name(user_message)
    reviews_text = retrieve_relevant_reviews(product_name)

    if not reviews_text:
        return {
            "success": False,
            "confidence": 0.0,
            "null_reason": "No reviews found for this product.",
            "module": "verdict",
        }

    lang_instruction = get_response_language_instruction(lang)
    full_message = (
        f"{lang_instruction}\n\n"
        f"Product: {product_name}\n\n"
        f"Customer Reviews:\n{reviews_text}"
    )

    raw = call_llm(system_prompt=SYSTEM_PROMPT, user_message=full_message)
    result = parse_llm_json(raw, VerdictResponse)

    if result is None:
        return {
            "success": False,
            "confidence": 0.0,
            "null_reason": "Could not generate a verdict. Try a more specific product name.",
            "module": "verdict",
        }

    return {**result.model_dump(), "module": "verdict"}