import json
import numpy as np
from pathlib import Path
from src.utils.llm_client import call_llm


def load_reviews(filepath: str = "data/sample_reviews.json") -> list[dict]:
    """Load product reviews from JSON file."""
    path = Path(filepath)
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def simple_keyword_retrieval(query: str, reviews: list[dict], top_k: int = 20) -> list[str]:
    """
    Lightweight retrieval: score reviews by keyword overlap with query.
    No embedding API needed — free and fast.
    """
    query_words = set(query.lower().split())
    scored = []
    for r in reviews:
        text = r.get("text", "")
        review_words = set(text.lower().split())
        overlap = len(query_words & review_words)
        scored.append((overlap, text))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in scored[:top_k]]


def retrieve_relevant_reviews(product_name: str, filepath: str = "data/sample_reviews.json") -> str:
    """
    Retrieve top reviews for a product and return as a joined string for the prompt.
    """
    reviews = load_reviews(filepath)
    if not reviews:
        return ""

    # Filter by product name if field exists
    product_reviews = [
        r for r in reviews
        if product_name.lower() in r.get("product", "").lower()
    ]
    if not product_reviews:
        product_reviews = reviews  # fallback: use all

    top = simple_keyword_retrieval(product_name, product_reviews, top_k=15)
    return "\n---\n".join(top)