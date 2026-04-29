"""
test_router.py
Tests for intent router — route_intent() and handle()
Run: pytest tests/test_router.py -v
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch


# ── mock_llm accepts **kwargs to match call_llm(system_prompt=, user_message=, temperature=) ──

def mock_llm(*args, **kwargs):
    """
    Flexible mock: reads 'user_message' from kwargs (keyword call)
    or falls back to first positional arg.
    """
    user_message = kwargs.get("user_message") or (args[1] if len(args) > 1 else args[0] if args else "")
    msg = user_message.lower()

    if any(w in msg for w in ["diaper", "stroller", "buy", "shopping", "recommend", "اشتري", "تسوق"]):
        return "shopping"
    if any(w in msg for w in ["pregnant", "week", "symptom", "baby health", "حمل", "أسبوع"]):
        return "health"
    if any(w in msg for w in ["review", "rating", "opinion", "verdict", "تقييم", "رأي"]):
        return "verdict"
    if any(w in msg for w in ["return", "refund", "exchange", "إرجاع", "استرداد"]):
        return "returns"
    return "unknown"


# ── TestRouteIntent ───────────────────────────────────────────────────────────

class TestRouteIntent:

    @patch("router.call_llm", side_effect=mock_llm)
    def test_shopping_english(self, mock):
        from router import route_intent
        assert route_intent("I want to buy diapers for my newborn") == "shopping"

    @patch("router.call_llm", side_effect=mock_llm)
    def test_shopping_arabic(self, mock):
        from router import route_intent
        assert route_intent("أريد اشتري حفاضات للطفل") == "shopping"

    @patch("router.call_llm", side_effect=mock_llm)
    def test_health_english(self, mock):
        from router import route_intent
        assert route_intent("I am 20 weeks pregnant, what should I eat?") == "health"

    @patch("router.call_llm", side_effect=mock_llm)
    def test_health_arabic(self, mock):
        from router import route_intent
        assert route_intent("أنا في الأسبوع العشرين من الحمل") == "health"

    @patch("router.call_llm", side_effect=mock_llm)
    def test_verdict_english(self, mock):
        from router import route_intent
        assert route_intent("What do moms say in reviews about this stroller?") == "verdict"

    @patch("router.call_llm", side_effect=mock_llm)
    def test_verdict_arabic(self, mock):
        from router import route_intent
        assert route_intent("ما هو تقييم هذا المنتج؟") == "verdict"

    @patch("router.call_llm", side_effect=mock_llm)
    def test_returns_english(self, mock):
        from router import route_intent
        assert route_intent("I want to return my order for a refund") == "returns"

    @patch("router.call_llm", side_effect=mock_llm)
    def test_returns_arabic(self, mock):
        from router import route_intent
        assert route_intent("أريد استرداد المبلغ") == "returns"

    @patch("router.call_llm", side_effect=mock_llm)
    def test_unknown_out_of_scope(self, mock):
        from router import route_intent
        assert route_intent("Tell me a joke") == "unknown"

    @patch("router.call_llm", side_effect=mock_llm)
    def test_unknown_empty_string(self, mock):
        from router import route_intent
        assert route_intent("") == "unknown"

    @patch("router.call_llm", side_effect=mock_llm)
    def test_unknown_gibberish(self, mock):
        from router import route_intent
        assert route_intent("asdkjhasd 123 !!!") == "unknown"


# ── TestHandleFunction ────────────────────────────────────────────────────────

class TestHandleFunction:

    @patch("router.call_llm", side_effect=mock_llm)
    def test_handle_returns_dict(self, mock):
        from router import handle
        result = handle("Tell me a joke")
        assert isinstance(result, dict)

    @patch("router.call_llm", side_effect=mock_llm)
    def test_handle_unknown_has_null_reason(self, mock):
        from router import handle
        result = handle("random unrelated query xyz")
        assert result.get("success") is False
        assert result.get("null_reason") is not None

    @patch("router.call_llm", side_effect=mock_llm)
    def test_handle_has_confidence(self, mock):
        from router import handle
        result = handle("Tell me a joke")
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0