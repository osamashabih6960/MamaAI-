"""
test_schemas.py
Tests for all Pydantic schemas — validates field types, null handling, and defaults.
Run: pytest tests/test_schemas.py -v

NOTE: Field names match the ACTUAL schema definitions (verified from error logs):
  HealthResponse  → advice_en, advice_ar, week, symptoms_flagged, defer_to_doctor,
                    doctor_message_en, doctor_message_ar
  VerdictResponse → verdict_badge_en, verdict_badge_ar, pros_en, pros_ar,
                    cons_en, cons_ar, summary_en, summary_ar, review_count_used
  ReturnResponse  → decision, reasoning_en, reasoning_ar, escalation_flag
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.schemas.base_schema import BaseResponse
from src.schemas.shopper_schema import ShoppingListResponse, ProductRec
from src.schemas.health_schema import HealthResponse
from src.schemas.verdict_schema import VerdictResponse
from src.schemas.returns_schema import ReturnResponse
import json


# ── BaseResponse ──────────────────────────────────────────────────────────────

class TestBaseResponse:

    def test_defaults_are_success(self):
        b = BaseResponse()
        assert b.success is True
        assert b.confidence == 1.0
        assert b.null_reason is None

    def test_failure_case(self):
        b = BaseResponse(success=False, confidence=0.0, null_reason="Out of scope")
        assert b.success is False
        assert b.null_reason == "Out of scope"

    def test_confidence_range(self):
        b = BaseResponse(confidence=0.85)
        assert 0.0 <= b.confidence <= 1.0


# ── ShoppingListResponse ──────────────────────────────────────────────────────

class TestShoppingSchema:

    def test_full_valid_response(self):
        data = {
            "success": True,
            "confidence": 0.9,
            "null_reason": None,
            "items_en": ["Diapers", "Baby wipes"],
            "items_ar": ["حفاضات", "مناديل مبللة"],
            "recommendations": [{
                "name_en": "Pampers New Baby",
                "name_ar": "بامبرز نيو بيبي",
                "reason_en": "Soft for newborns",
                "reason_ar": "ناعم للمولود",
                "price_range": "25-40 AED"
            }],
            "summary_en": "Here is your list.",
            "summary_ar": "إليكِ القائمة."
        }
        r = ShoppingListResponse(**data)
        assert r.success is True
        assert len(r.items_en) == 2
        assert len(r.recommendations) == 1
        assert r.recommendations[0].price_range == "25-40 AED"

    def test_minimal_response(self):
        r = ShoppingListResponse(success=True, confidence=0.7)
        assert r.items_en is None
        assert r.recommendations is None

    def test_null_reason_on_failure(self):
        r = ShoppingListResponse(success=False, confidence=0.0, null_reason="Not a shopping query")
        assert r.null_reason == "Not a shopping query"

    def test_items_bilingual(self):
        r = ShoppingListResponse(
            success=True,
            confidence=0.88,
            items_en=["Baby bottle"],
            items_ar=["زجاجة الرضاعة"]
        )
        assert r.items_en[0] == "Baby bottle"
        assert r.items_ar[0] == "زجاجة الرضاعة"


# ── HealthResponse ────────────────────────────────────────────────────────────

class TestHealthSchema:

    def test_valid_health_response(self):
        """Uses actual field names: advice_en, advice_ar (not answer_en)"""
        r = HealthResponse(
            success=True,
            confidence=0.88,
            week=20,
            advice_en="At week 20, your baby is the size of a banana.",
            advice_ar="في الأسبوع العشرين، طفلك بحجم الموزة.",
            defer_to_doctor=False
        )
        assert r.success is True
        assert "week 20" in r.advice_en
        assert r.week == 20

    def test_health_null_when_out_of_scope(self):
        r = HealthResponse(success=False, confidence=0.0, null_reason="Not a health question")
        assert r.null_reason is not None
        assert r.advice_en is None

    def test_disclaimer_via_doctor_message(self):
        """Schema uses doctor_message_en instead of disclaimer_en"""
        r = HealthResponse(
            success=True,
            confidence=0.9,
            advice_en="Fever in babies is common.",
            doctor_message_en="Always consult a pediatrician.",
            defer_to_doctor=True
        )
        assert r.doctor_message_en is not None
        assert r.defer_to_doctor is True

    def test_minimal_fields(self):
        r = HealthResponse(success=True, confidence=0.5)
        assert r.advice_en is None
        assert r.symptoms_flagged is None
        assert r.week is None

    def test_symptoms_flagged(self):
        r = HealthResponse(
            success=True,
            confidence=0.75,
            symptoms_flagged=["fever", "cough"],
            advice_en="Monitor the baby.",
            advice_ar="راقبي الطفل."
        )
        assert "fever" in r.symptoms_flagged

    def test_arabic_advice_present(self):
        r = HealthResponse(
            success=True,
            confidence=0.8,
            advice_en="Take iron supplements.",
            advice_ar="تناولي مكملات الحديد."
        )
        assert r.advice_ar is not None


# ── VerdictResponse ───────────────────────────────────────────────────────────

class TestVerdictSchema:

    def test_full_verdict(self):
        """Uses actual fields: verdict_badge_en, review_count_used (not avg_rating, verdict_en)"""
        r = VerdictResponse(
            success=True,
            confidence=0.92,
            product_name="Chicco Fast2Fix Car Seat",
            pros_en=["Easy to install", "Comfortable padding"],
            pros_ar=["سهل التركيب", "وسادة مريحة"],
            cons_en=["Slightly heavy"],
            cons_ar=["ثقيل قليلاً"],
            verdict_badge_en="Highly recommended by moms.",
            verdict_badge_ar="موصى به بشدة من الأمهات.",
            review_count_used=128
        )
        assert r.product_name == "Chicco Fast2Fix Car Seat"
        assert len(r.pros_en) == 2
        assert r.review_count_used == 128

    def test_verdict_null_no_reviews(self):
        r = VerdictResponse(success=False, confidence=0.0, null_reason="No reviews found")
        assert r.pros_en is None
        assert r.verdict_badge_en is None

    def test_review_count_optional(self):
        """Actual field name is review_count_used"""
        r = VerdictResponse(success=True, confidence=0.8)
        assert r.review_count_used is None

    def test_summary_bilingual(self):
        r = VerdictResponse(
            success=True,
            confidence=0.85,
            product_name="Baby Monitor X",
            summary_en="Great value for money.",
            summary_ar="قيمة رائعة مقابل السعر."
        )
        assert r.summary_en is not None
        assert r.summary_ar is not None

    def test_cons_optional(self):
        r = VerdictResponse(
            success=True,
            confidence=0.9,
            product_name="Pampers Premium",
            pros_en=["Super soft", "Long-lasting"],
            pros_ar=["ناعم جداً", "طويل الأمد"]
        )
        assert r.cons_en is None


# ── ReturnResponse ────────────────────────────────────────────────────────────

class TestReturnSchema:

    def test_refund_classification(self):
        """Actual field name is 'decision' not 'classification'"""
        r = ReturnResponse(
            success=True,
            confidence=0.95,
            decision="REFUND",
            reasoning_en="Product arrived damaged",
            reasoning_ar="وصل المنتج تالفاً",
            escalation_flag=True
        )
        assert r.decision == "REFUND"
        assert r.escalation_flag is True

    def test_exchange_classification(self):
        r = ReturnResponse(
            success=True,
            confidence=0.85,
            decision="EXCHANGE"
        )
        assert r.decision == "EXCHANGE"

    def test_null_reason_on_failure(self):
        r = ReturnResponse(success=False, confidence=0.0, null_reason="Unrelated query")
        assert r.null_reason == "Unrelated query"
        assert r.decision is None

    def test_escalation_flag_default_false(self):
        r = ReturnResponse(success=True, confidence=0.8, decision="STORE_CREDIT")
        assert r.escalation_flag is False

    def test_reasoning_bilingual(self):
        r = ReturnResponse(
            success=True,
            confidence=0.9,
            decision="REFUND",
            reasoning_en="Wrong item delivered.",
            reasoning_ar="تم تسليم منتج خاطئ."
        )
        assert r.reasoning_en is not None
        assert r.reasoning_ar is not None