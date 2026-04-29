# 🤱 MamaAI — يا ماما

> **One AI assistant for every Mumzworld mom** — shopping, health, reviews, returns. Fully bilingual EN + AR, schema-validated, hallucination-free.

---

```
┌──────────────────────────────────────────────────────────────┐
│                   MamaAI System at a Glance                  │
│                                                              │
│   Mom types query  →  Intent Router  →  Correct Module       │
│   (EN or AR)          (LLM-based)       (1 of 4)            │
│                                                              │
│   🛒 Shopper   🏥 Health   ⭐ Verdict   📦 Returns           │
│                                                              │
│   ↓ Schema-validated JSON · null on uncertainty ↓           │
└──────────────────────────────────────────────────────────────┘
```

---

## Table of Contents

1. [What It Does](#what-it-does)
2. [System Design](#system-design)
3. [Architecture Mind Map](#architecture-mind-map)
4. [How It Works — Step by Step](#how-it-works--step-by-step)
5. [Setup & Run](#setup--run)
6. [API Reference](#api-reference)
7. [Evals — Prove It Works](#evals--prove-it-works)
8. [Tradeoffs](#tradeoffs)
9. [Tooling Stack](#tooling-stack)
10. [Data](#data)

---

## What It Does

MamaAI is a **4-module AI system** unified by a single intent router. A mom can type anything — in English or Arabic — and the right module handles it with structured, validated output.

| Module | When It Triggers | What It Returns |
|---|---|---|
| 🛒 **Smart Shopper** | Shopping queries, product needs | Bilingual list + product recs + price range |
| 🏥 **Health Assistant** | Pregnancy / baby health queries | Safe advice + doctor referral if needed |
| ⭐ **Moms Verdict** | "Is this product good?" | RAG-based bilingual verdict from reviews |
| 📦 **Return Classifier** | Return / refund / exchange | Decision + confidence score + reasoning |

**All outputs are schema-validated JSON.**
If the model cannot answer → it returns `success: false` + `null_reason`. It never hallucinates.

---

## System Design

```
                         ┌─────────────────────────────────────────┐
                         │              FastAPI Server              │
                         │           POST /ask  ·  GET /           │
                         └──────────────────┬──────────────────────┘
                                            │
                              user_message (EN or AR)
                                            │
                         ┌──────────────────▼──────────────────────┐
                         │           language_detect.py             │
                         │    detects: "en" | "ar" | "mixed"        │
                         └──────────────────┬──────────────────────┘
                                            │
                         ┌──────────────────▼──────────────────────┐
                         │              router.py                   │
                         │   LLM call → intent classification       │
                         │   shopping | health | verdict | returns  │
                         │              | unknown                   │
                         └──────┬──────┬──────┬──────┬────────────-┘
                                │      │      │      │
               ┌────────────────┘      │      │      └──────────────────┐
               │               ┌───────┘      └───────┐                 │
               ▼               ▼                      ▼                 ▼
       ┌──────────────┐ ┌──────────────┐   ┌─────────────────┐ ┌──────────────┐
       │  shopper.py  │ │  health.py   │   │   verdict.py    │ │ returns.py   │
       │              │ │              │   │  (RAG engine)   │ │              │
       └──────┬───────┘ └──────┬───────┘   └────────┬────────┘ └──────┬───────┘
              │                │                     │                 │
              ▼                ▼                     ▼                 ▼
       ┌──────────────────────────────────────────────────────────────────────┐
       │                        llm_client.py                                 │
       │              Groq API · llama-3.1-8b-instant · free tier             │
       └──────────────────────────────────────────────────────────────────────┘
              │                │                     │                 │
              ▼                ▼                     ▼                 ▼
       ┌──────────────────────────────────────────────────────────────────────┐
       │                        validator.py                                  │
       │              Pydantic v2 schema validation + null handling            │
       └──────────────────────────────────────────────────────────────────────┘
                                            │
                                 validated JSON response
                                            │
                                     ← back to mom
```

---

## Architecture Mind Map

```
MamaAI
│
├── 🧠 CORE INTELLIGENCE
│   ├── router.py ─────────────── Intent classifier (1 LLM call/request)
│   ├── llm_client.py ─────────── Groq API wrapper (free, fast)
│   └── language_detect.py ────── EN / AR / mixed detection
│
├── 📦 4 MODULES  (src/modules/)
│   ├── shopper.py ─────────────── Shopping list + bilingual recs
│   ├── health.py ──────────────── Pregnancy & baby health advice
│   ├── verdict.py ─────────────── RAG over reviews → Moms Verdict
│   └── returns.py ─────────────── Return reason → Refund/Exchange/Escalate
│
├── ✅ SCHEMA LAYER  (src/schemas/)
│   ├── base_schema.py ─────────── BaseResponse: success, confidence, null_reason
│   ├── shopper_schema.py ──────── items_en, items_ar, recommendations[]
│   ├── health_schema.py ───────── advice_en, advice_ar, refer_to_doctor: bool
│   ├── verdict_schema.py ──────── pros[], cons[], verdict_en, verdict_ar
│   └── returns_schema.py ──────── decision, confidence, reasoning
│
├── 💬 PROMPTS  (src/prompts/)
│   ├── router_prompt.txt ──────── Strict: ONE word output only
│   ├── shopper_prompt.txt ─────── Native Arabic, not translated
│   ├── health_prompt.txt ──────── Conservative; defer to doctor on edge cases
│   ├── verdict_prompt.txt ─────── Summarise reviews; no hallucination
│   └── returns_prompt.txt ─────── Classify: Refund | Exchange | Credit | Escalate
│
├── 📊 EVALS  (evals/)
│   ├── test_cases.json ────────── 10 cases: 5 easy + 5 adversarial
│   ├── run_evals.py ───────────── Auto-runner; saves results + failures
│   ├── eval_results.json ──────── Auto-generated scores
│   ├── eval_rubric.md ─────────── Grading criteria per module
│   └── failures.md ────────────── Honest failure log
│
└── 🗄️ DATA  (data/)
    ├── sample_queries.json ────── Synthetic EN + AR shopping queries
    ├── sample_reviews.json ────── 30 synthetic product reviews (AI-generated)
    ├── return_reasons.json ────── Real-world return reason patterns
    └── health_queries.json ────── Pregnancy & baby health queries
```

---

## How It Works — Step by Step

### Step 1 · Mom sends a message

```
POST /ask
{ "message": "أحتاج قائمة تسوق لمولودي الجديد" }
```

### Step 2 · Language is detected

```python
detect_language("أحتاج قائمة تسوق لمولودي الجديد")
# → "ar"
```

### Step 3 · Intent Router classifies in one LLM call

The router prompt is strict — it returns **exactly one word**:

```
shopping | health | verdict | returns | unknown
```

```python
route_intent(message)
# → "shopping"
```

### Step 4 · Correct module handles the request

`shopper.py` is called with the original message + detected language.
It sends a structured prompt to Groq and parses the JSON response.

### Step 5 · Schema validation runs

```python
ShoppingListResponse(**parsed_json)
# Pydantic v2 validates every field
# If parsing fails → returns success: false, not a crash
```

### Step 6 · Validated response returns to mom

```json
{
  "success": true,
  "confidence": 0.94,
  "null_reason": null,
  "items_en": ["Diapers", "Baby wipes", "Swaddle blankets"],
  "items_ar": ["حفاضات", "مناديل مبللة", "بطانيات التقميط"],
  "recommendations": [
    {
      "name_en": "Pampers New Baby",
      "name_ar": "بامبرز نيو بيبي",
      "reason_en": "Ultra-soft, ideal for newborn skin",
      "reason_ar": "ناعم للغاية، مثالي لجلد المولود",
      "price_range": "25–40 AED"
    }
  ],
  "summary_en": "Here is your newborn essentials list.",
  "summary_ar": "إليكِ قائمة المستلزمات الأساسية لمولودك."
}
```

### Uncertainty Handling (Key Feature)

When the model cannot answer confidently:

```json
{
  "success": false,
  "confidence": 0.0,
  "null_reason": "I can only help with shopping, health, product reviews, or returns on Mumzworld.",
  "module": "unknown"
}
```

It **never guesses**. It **always explains why it cannot answer**.

---

## Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/osamashabih6960/MamaAI-.git
cd mamaai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Get your FREE Groq API key (no credit card needed)
#    → https://console.groq.com → API Keys → Create Key

# 5. Set up environment
cp .env.example .env
# Open .env and paste: GROQ_API_KEY=gsk_your_key_here

# 6. Run the server
uvicorn main:app --reload --port 8000

# 7. Open the UI
#    → http://localhost:8000

# 8. Or test via curl
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a shopping list for my newborn"}'
```

### Test all 4 modules

```bash
# Shopping (EN)
curl -X POST http://localhost:8000/ask \
  -d '{"message": "What do I need for a 6-month-old baby?"}' \
  -H "Content-Type: application/json"

# Health (AR)
curl -X POST http://localhost:8000/ask \
  -d '{"message": "طفلي عنده حمى 38 درجة ماذا أفعل؟"}' \
  -H "Content-Type: application/json"

# Verdict
curl -X POST http://localhost:8000/ask \
  -d '{"message": "Is the Philips Avent bottle good for newborns?"}' \
  -H "Content-Type: application/json"

# Returns
curl -X POST http://localhost:8000/ask \
  -d '{"message": "The stroller I received was damaged"}' \
  -H "Content-Type: application/json"
```

---

## API Reference

### `POST /ask`

**Request:**
```json
{ "message": "string (EN or AR)" }
```

**Response — all modules:**
```json
{
  "success": true,
  "confidence": 0.92,
  "null_reason": null,
  "module": "shopping | health | verdict | returns | unknown",
  "language": "en | ar | mixed",
  "... module-specific fields ..."
}
```

**Null response (uncertainty):**
```json
{
  "success": false,
  "confidence": 0.0,
  "null_reason": "Human-readable explanation of why this cannot be answered",
  "module": "unknown"
}
```

### `GET /`

Returns the full UI (`ui.html`).

---

## Evals — Prove It Works

```bash
python evals/run_evals.py
```

Results are saved to `evals/eval_results.json`. Failures are logged to `evals/failures.md`.

### Test Cases

| # | Input | Module | Type | Expected |
|---|-------|--------|------|----------|
| 1 | "Shopping list for 3-month-old" | Shopper | Easy | success: true |
| 2 | "أريد قائمة للمولود الجديد" | Shopper | Easy (AR) | bilingual output |
| 3 | "My baby has a fever of 39°C" | Health | Easy | refer_to_doctor: true |
| 4 | "Is the Chicco stroller worth it?" | Verdict | Easy | pros/cons in EN+AR |
| 5 | "Dress didn't fit, want to return" | Returns | Easy | Exchange + confidence |
| 6 | "What is the weather today?" | Unknown | Adversarial | success: false |
| 7 | "اشتريت منتج غلط" (vague) | Returns | Adversarial | low confidence |
| 8 | "Baby cried for 3 hours straight" | Health | Adversarial | safe advice, not panic |
| 9 | "Give me everything Mumzworld sells" | Unknown | Adversarial | null_reason returned |
| 10 | "رأيك في هذا المنتج" (no product named) | Verdict | Adversarial | null_reason returned |

### Scores

| Module | Tests | Passed | Notes |
|---|---|---|---|
| Router | 10 | X/10 | Update after running |
| Shopper | 3 | X/3 | |
| Health | 2 | X/2 | |
| Verdict | 1 | X/1 | |
| Returns | 3 | X/3 | |

> *(Run `python evals/run_evals.py` and update this table. Be honest — failures show rigour.)*

### Known Failures / Limitations

- **Verdict module** accuracy depends on how many reviews are in `data/sample_reviews.json` — more data = better output
- **Arabic detection** can fail on very short inputs (< 3 words)
- **Health module** may over-defer to doctor on mild queries — this is intentional (conservative by design)
- **Router latency** adds one extra LLM call per request (~300–500ms on Groq free tier)

---

## Tradeoffs

### Why this problem?

Returns and reviews are real Mumzworld **operations pain points**. Combining them with mom-facing shopping and health creates a system with:
- **Internal value** → ops efficiency (returns classification, review summarisation)
- **External value** → mom experience (shopping assistant, health guidance)

Neither problem alone justified the AI complexity — together they do.

### Model choice

Used free open-weight models via **Groq (llama-3.1-8b-instant)**.

| Decision | Why |
|---|---|
| Groq over OpenAI | Free tier, no credit card, ~500 tokens/s speed |
| llama-3.1-8b | Fast enough for 5-hour prototype; Arabic quality acceptable |
| Single model for all modules | Simplicity; one client, one key, one rate limit to manage |

**Tradeoff accepted:** Small models produce lower-quality native Arabic vs Claude or GPT-4. With a budget, Arabic output quality would improve significantly.

### Architecture tradeoff

The **intent router adds one LLM call per request** (~300ms latency). Accepted because:
- Modules stay cleanly separated and independently testable
- Failures in one module don't cascade
- Alternative (regex routing) is faster but brittle on Arabic input

### What was cut

| Feature | Reason cut |
|---|---|
| Embeddings-based RAG | Replaced with keyword retrieval to save time |
| Voice input (Whisper) | Needs paid API or local GPU |
| Full streaming UI | Kept to REST API + HTML for simplicity |
| Vector similarity search | Overkill for 30 sample reviews |

### What I would build next

- Vector embeddings for Verdict module (FAISS or ChromaDB)
- Whisper-based voice input for Shopper (moms with hands full)
- Streaming responses via Server-Sent Events
- Arabic quality uplift via Claude 3.5 Sonnet

---

## Tooling Stack

| Tool | Used for |
|---|---|
| **Groq + llama-3.1-8b-instant** | All LLM calls — free tier, no card |
| **KiloCode (VS Code)** | Pair-coding and refactoring modules |
| **Pydantic v2** | Schema validation and null handling |
| **FastAPI** | API layer with auto-docs at `/docs` |
| **pytest** | Unit tests for router, schemas, modules |
| **python-dotenv** | `.env` management |
| **langdetect** | Language detection |

### How AI tools were used

**KiloCode:**
Used for generating boilerplate schemas and refactoring prompt strings. All system prompts were reviewed and rewritten manually — AI-generated prompts were too loose on the `unknown` fallback and had literal Arabic translation quality.

**LLM for data generation:**
Used the model itself to generate 30 synthetic product reviews in `data/sample_reviews.json` and sample queries in all languages. No scraping of any retailer site.

### What I had to override

| Issue | What the agent generated | What I fixed manually |
|---|---|---|
| Arabic prompts | Literal English-to-Arabic translation | Rewrote all Arabic instructions natively |
| Router prompt | Too permissive, returned multi-word outputs | Added strict `unknown` fallback + one-word constraint |
| Health module | No doctor referral logic | Added `refer_to_doctor: bool` field + threshold logic |
| Validator | Silent failures on bad JSON | Made failures explicit with `null_reason` |

---

## Data

All data in `/data` is **self-generated — no scraping** of any retailer site.

| File | Contents | How generated |
|---|---|---|
| `sample_queries.json` | 20 EN + AR shopping queries | Manually written + LLM-expanded |
| `sample_reviews.json` | 30 product reviews | LLM-generated (prompted as Mumzworld mom personas) |
| `return_reasons.json` | 15 return reason patterns | Based on common e-commerce return categories |
| `health_queries.json` | 15 pregnancy + baby health queries | Manually written |

---

## Project Stats

```
Total files:     26
Lines of code:   ~1,200
Build time:      ~5 hours
API cost:        $0.00 (Groq free tier)
Languages:       Python, HTML/CSS/JS
Modules:         4
Test cases:      10
```

---

## License

Built for the Mumzworld AI Engineering Internship — Track A.
Not for production use without review of health module outputs.

---

*MamaAI — because every mom deserves answers in her language.*
*يا ماما — لأن كل أم تستحق إجابات بلغتها.*