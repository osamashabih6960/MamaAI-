# MamaAI Eval Failures

Total failures: 1 / 10

## E01 (easy)
**Input:** I need a shopping list for my newborn baby

**Notes:** Basic English shopping query — should return bilingual list

**Failed checks:**
- `field_items_en` FAILED
- `field_items_ar` FAILED

**Actual result:** `{
  "success": true,
  "confidence": 1.0,
  "null_reason": null,
  "items_en": [],
  "items_ar": [],
  "recommendations": [
    {
      "name_en": "Newborn essentials",
      "name_ar": "مستلزمات مولود جديد",
      "reason_en": "To ensure a smooth transition for you and your baby",
      "reason_ar": "لضمان انتقال سلس للولادة",
      "price_range": "100-200 AED"
    },
    {
      "name_en": "Diapers and wipes",
      "name_ar": "حفاضات ومندلات",
      "reason_en": "For daily use and convenience",
      "reason_ar": "للاستخدام اليومي والراحة",
      "price_range": "50-100 AED"
    }
  ],
  "summary_en": "Here is a suggested shopping list for your newborn baby.",
  "summary_ar": "إليكِ قائمة تسوق مقترحة للمولود الجديد.",
  "module": "shopper"
}`

---

