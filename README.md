# MamaAI — يا ماما
> One AI assistant for every Mumzworld mom — shopping, health, reviews, returns. Bilingual EN + AR.

---

## Setup & Run:-

```bash
# 1. Clone the repo
git clone https://github.com/osamashabih6960/MamaAI-.git
cd mamaai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up API key
cp .env.example .env
# Open .env and add your free OpenRouter API key from https://openrouter.ai

# 5. Run the app
uvicorn main:app --reload --port 8000

# 6. Test it
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a shopping list for my newborn"}'
```

---

## What it does

MamaAI is a single AI system with 4 modules, unified by an intent router:

| Module | Trigger | Output |
|---|---|---|
| Smart Shopper | Shopping query | Bilingual list + product recs |
| Health Assistant | Pregnancy / baby health | Advice + doctor referral if needed |
| Moms Verdict | Product review request | RAG-based bilingual verdict |
| Return Classifier | Return reason | Decision + confidence + reasoning |

All outputs are schema-validated JSON. If the model cannot answer, it returns `success: false` and a `null_reason` — it never hallucinates.

---

## Evals

Run the full eval suite:

```bash
python evals/run_evals.py
```

**10 test cases** — 5 easy, 5 adversarial. Results saved to `evals/eval_results.json`.
Failures logged to `evals/failures.md`.

### Scores

| Module | Tests | Passed | Notes |
|---|---|---|---|
| Router | 10 | X/10 | Fill after running |
| Shopper | 3 | X/3 | |
| Health | 2 | X/2 | |
| Verdict | 1 | X/1 | |
| Returns | 3 | X/3 | |

*(Update this table after running evals — be honest about failures)*

### Known failures / limitations

- Verdict module accuracy depends on how many reviews are in `data/sample_reviews.json`
- Arabic detection can fail on very short inputs (< 3 words)
- Model may over-defer to doctor on mild health queries (conservative by design)

---

## Tradeoffs

**Why this problem:** Returns and reviews are real Mumzworld operations pain points. Combining them with mom-facing shopping + health creates a system with both internal value (ops efficiency) and external value (mom experience). Neither problem alone would justify the AI complexity.

**Model choice:** Used free open-weight models via OpenRouter (Llama 3.1 8B). Small models struggle with native Arabic quality — a tradeoff I accepted to stay within the free tier. With a budget, Claude or GPT-4 would improve Arabic output significantly.

**Architecture tradeoff:** The intent router adds one LLM call per request. I accepted this latency cost because it keeps modules cleanly separated and testable. Alternative was regex-based routing — faster but brittle.

**What I cut:** Embeddings-based RAG (replaced with keyword retrieval), voice input transcription (would need Whisper API), full UI (kept to API only).

**What I would build next:** Vector embeddings for Verdict module, Whisper-based voice input for Shopper, streaming responses via SSE.

---

## Tooling

| Tool | Used for |
|---|---|
| OpenRouter + Llama 3.1 8B | All LLM calls — free tier |
| KiloCode (VS Code) | Pair-coding and refactoring modules |
| Pydantic v2 | Schema validation and null handling |
| FastAPI | API layer |
| pytest | Unit tests |

**How AI tools were used:**
- KiloCode: Used for generating boilerplate schemas and refactoring prompt strings. I reviewed and rewrote all system prompts manually.
- LLM for evals: Used the model itself to generate 30 synthetic review samples in `data/sample_reviews.json`. No scraping.

**What I had to override:**
- AI-generated Arabic prompts had literal translation quality — rewrote all Arabic instructions manually.
- Auto-generated router prompt was too permissive — added stricter `unknown` fallback by hand.

---

## Data

All data in `/data` is self-generated — no scraping of any retailer site.
See `data/data_generation.md` for how each file was created.