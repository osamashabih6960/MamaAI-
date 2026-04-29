from src.utils.llm_client import call_llm
from src.utils.language_detect import detect_language

ROUTER_SYSTEM_PROMPT = """
You are an intent classifier for MamaAI, an AI assistant for mothers on Mumzworld.

Given a user message, classify it into EXACTLY one of these intents:
- shopping    : User wants to buy something, needs a product list, or asks for recommendations
- health      : User asks about pregnancy, baby symptoms, pediatric health, or maternal wellness
- verdict     : User wants a summary or review analysis of a specific product
- returns     : User wants to return a product and explains why

Respond with ONLY a single word — one of: shopping, health, verdict, returns
If you cannot classify clearly, respond with: unknown
"""


def route_intent(user_message: str) -> str:
    """
    Detect intent from user message.
    Returns one of: shopping | health | verdict | returns | unknown
    """
    result = call_llm(
        system_prompt=ROUTER_SYSTEM_PROMPT,
        user_message=user_message,
        temperature=0.0,
    )
    intent = result.strip().lower()
    valid = {"shopping", "health", "verdict", "returns"}
    if intent not in valid:
        print(f"[router] Unknown intent: '{intent}' — defaulting to unknown")
        return "unknown"
    return intent


def handle(user_message: str):
    """
    Main entry point. Routes message to correct module and returns structured response.
    """
    lang = detect_language(user_message)
    intent = route_intent(user_message)

    print(f"[router] lang={lang} | intent={intent}")

    if intent == "shopping":
        from src.modules.shopper import run_shopper
        return run_shopper(user_message, lang)

    elif intent == "health":
        from src.modules.health import run_health
        return run_health(user_message, lang)

    elif intent == "verdict":
        from src.modules.verdict import run_verdict
        return run_verdict(user_message, lang)

    elif intent == "returns":
        from src.modules.returns import run_returns
        return run_returns(user_message, lang)

    else:
        return {
            "success": False,
            "confidence": 0.0,
            "null_reason": "Could not understand the request. Please rephrase.",
            "intent": "unknown",
        }