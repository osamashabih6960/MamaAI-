import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import json
from unittest.mock import patch


def make_mock_llm(response_dict):
    def _mock(*args, **kwargs):
        return json.dumps(response_dict)
    return _mock


NULL_RESPONSE = {
    "success": False,
    "confidence": 0.0,
    "null_reason": "This query is outside my scope."
}

SHOPPER_RESPONSE = {
    "success": True,
    "confidence": 0.92,
    "null_reason": None,
    "items_en": ["Newborn diapers", "Baby wipes", "Baby lotion"],
    "items_ar": ["حفاضات المولود", "مناديل مبللة", "لوشن الأطفال"],
    "recommendations": [
        {
            "name_en": "Pampers New Baby",
            "name_ar": "بامبرز نيو بيبي",
            "reason_en": "Best for sensitive newborn skin",
            "reason_ar": "الأفضل لبشرة المولود الحساسة",
            "price_range": "25-40 AED"
        }
    ],
    "summary_en": "Here are essentials for your newborn.",
    "summary_ar": "إليكِ المستلزمات الأساسية لمولودك."
}

HEALTH_RESPONSE = {
    "success": True,
    "confidence": 0.88,
    "null_reason": None,
    "week": 20,
    "advice_en": "At week 20, your baby is the size of a banana.",
    "advice_ar": "في الأسبوع العشرين، طفلك بحجم الموزة.",
    "symptoms_flagged": [],
    "defer_to_doctor": False,
    "doctor_message_en": "Always consult your OB-GYN for personalized advice.",
    "doctor_message_ar": "استشيري طبيبكِ دائماً."
}

VERDICT_RESPONSE = {
    "success": True,
    "confidence": 0.91,
    "null_reason": None,
    "product_name": "Chicco Fast2Fix Car Seat",
    "verdict_badge_en": "Highly recommended by moms",
    "verdict_badge_ar": "موصى به بشدة من الأمهات",
    "pros_en": ["Easy to install", "Comfortable padding"],
    "pros_ar": ["سهل التركيب", "وسادة مريحة"],
    "cons_en": ["Slightly expensive"],
    "cons_ar": ["غالي قليلاً"],
    "summary_en": "Great car seat.",
    "summary_ar": "مقعد رائع.",
    "review_count_used": 128
}

RETURNS_RESPONSE = {
    "success": True,
    "confidence": 0.95,
    "null_reason": None,
    "decision": "REFUND",
    "reasoning_en": "Product arrived damaged.",
    "reasoning_ar": "وصل المنتج تالفاً.",
    "escalation_flag": False
}


class TestShopperModule:

    @patch("src.modules.shopper.call_llm", side_effect=make_mock_llm(SHOPPER_RESPONSE))
    def test_run_shopper_english(self, mock):
        from src.modules.shopper import run_shopper
        result = run_shopper("I need things for my newborn baby", "en")
        assert result["success"] is True
        assert result["module"] == "shopping"

    @patch("src.modules.shopper.call_llm", side_effect=make_mock_llm(SHOPPER_RESPONSE))
    def test_run_shopper_arabic(self, mock):
        from src.modules.shopper import run_shopper
        result = run_shopper("أحتاج لوازم للمولود الجديد", "ar")
        assert result["success"] is True

    @patch("src.modules.shopper.call_llm", side_effect=make_mock_llm(SHOPPER_RESPONSE))
    def test_shopper_has_recommendations(self, mock):
        from src.modules.shopper import run_shopper
        result = run_shopper("Recommend diapers please", "en")
        data = result.get("data", result)
        items = data.get("items_en") or result.get("items_en")
        assert items is not None
        assert len(items) > 0

    @patch("src.modules.shopper.call_llm", side_effect=make_mock_llm(NULL_RESPONSE))
    def test_shopper_null_on_ambiguous(self, mock):
        from src.modules.shopper import run_shopper
        result = run_shopper("xyz ambiguous query", "en")
        assert result["success"] is False
        assert result.get("null_reason") is not None

    @patch("src.modules.shopper.call_llm", side_effect=make_mock_llm(SHOPPER_RESPONSE))
    def test_shopper_returns_module_key(self, mock):
        from src.modules.shopper import run_shopper
        result = run_shopper("I need baby products", "en")
        assert result.get("module") == "shopping"


class TestHealthModule:

    @patch("src.modules.health.call_llm", side_effect=make_mock_llm(HEALTH_RESPONSE))
    def test_run_health_english(self, mock):
        from src.modules.health import run_health
        result = run_health("I am 20 weeks pregnant", "en")
        assert result["success"] is True
        assert result["module"] == "health"

    @patch("src.modules.health.call_llm", side_effect=make_mock_llm(HEALTH_RESPONSE))
    def test_run_health_arabic(self, mock):
        from src.modules.health import run_health
        result = run_health("أنا في الأسبوع العشرين من الحمل", "ar")
        assert result["success"] is True

    @patch("src.modules.health.call_llm", side_effect=make_mock_llm(HEALTH_RESPONSE))
    def test_health_has_disclaimer(self, mock):
        from src.modules.health import run_health
        result = run_health("My baby has a fever", "en")
        data = result.get("data", result)
        msg = data.get("doctor_message_en") or result.get("doctor_message_en")
        assert msg is not None

    @patch("src.modules.health.call_llm", side_effect=make_mock_llm(NULL_RESPONSE))
    def test_health_null_on_non_medical(self, mock):
        from src.modules.health import run_health
        result = run_health("Tell me about football", "en")
        assert result["success"] is False
        assert result.get("null_reason") is not None

    @patch("src.modules.health.call_llm", side_effect=make_mock_llm(HEALTH_RESPONSE))
    def test_health_returns_module_key(self, mock):
        from src.modules.health import run_health
        result = run_health("Week 30 pregnancy tips", "en")
        assert result.get("module") == "health"


class TestVerdictModule:

    @patch("src.modules.verdict.call_llm", side_effect=make_mock_llm(VERDICT_RESPONSE))
    def test_run_verdict_english(self, mock):
        from src.modules.verdict import run_verdict
        result = run_verdict("What do moms say about Chicco car seat?", "en")
        assert result["success"] is True
        assert result["module"] == "verdict"

    @patch("src.modules.verdict.call_llm", side_effect=make_mock_llm(VERDICT_RESPONSE))
    def test_run_verdict_arabic(self, mock):
        from src.modules.verdict import run_verdict
        result = run_verdict("ما رأي الأمهات في هذا المنتج؟", "ar")
        assert result["success"] is True

    @patch("src.modules.verdict.call_llm", side_effect=make_mock_llm(VERDICT_RESPONSE))
    def test_verdict_has_rating(self, mock):
        from src.modules.verdict import run_verdict
        result = run_verdict("Review summary for stroller", "en")
        data = result.get("data", result)
        count = data.get("review_count_used") or result.get("review_count_used")
        assert count is not None
        assert count > 0

    @patch("src.modules.verdict.call_llm", side_effect=make_mock_llm(NULL_RESPONSE))
    def test_verdict_null_no_reviews(self, mock):
        from src.modules.verdict import run_verdict
        result = run_verdict("XYZ product with no reviews", "en")
        assert result["success"] is False
        assert result.get("null_reason") is not None

    @patch("src.modules.verdict.call_llm", side_effect=make_mock_llm(VERDICT_RESPONSE))
    def test_verdict_returns_module_key(self, mock):
        from src.modules.verdict import run_verdict
        result = run_verdict("What do people say about this bottle?", "en")
        assert result.get("module") == "verdict"


class TestReturnsModule:

    @patch("src.modules.returns.call_llm", side_effect=make_mock_llm(RETURNS_RESPONSE))
    def test_run_returns_refund(self, mock):
        from src.modules.returns import run_returns
        result = run_returns("I want to return my damaged order", "en")
        assert result["success"] is True
        assert result["module"] == "returns"

    @patch("src.modules.returns.call_llm", side_effect=make_mock_llm(RETURNS_RESPONSE))
    def test_run_returns_arabic(self, mock):
        from src.modules.returns import run_returns
        result = run_returns("أريد إرجاع المنتج التالف", "ar")
        assert result["success"] is True

    @patch("src.modules.returns.call_llm", side_effect=make_mock_llm(RETURNS_RESPONSE))
    def test_returns_has_suggested_action(self, mock):
        from src.modules.returns import run_returns
        result = run_returns("I received the wrong item", "en")
        data = result.get("data", result)
        action = data.get("reasoning_en") or result.get("reasoning_en")
        assert action is not None

    @patch("src.modules.returns.call_llm", side_effect=make_mock_llm(NULL_RESPONSE))
    def test_returns_null_on_unrelated(self, mock):
        from src.modules.returns import run_returns
        result = run_returns("What is the weather today?", "en")
        assert result["success"] is False
        assert result.get("null_reason") is not None

    @patch("src.modules.returns.call_llm", side_effect=make_mock_llm(RETURNS_RESPONSE))
    def test_returns_module_key(self, mock):
        from src.modules.returns import run_returns
        result = run_returns("I want a refund for my stroller", "en")
        assert result.get("module") == "returns"