import json
from pydantic import BaseModel, ValidationError
from typing import Type, TypeVar, Optional

T = TypeVar("T", bound=BaseModel)


def parse_llm_json(raw: str, schema: Type[T]) -> Optional[T]:
    """
    Parse raw LLM output string into a Pydantic schema.
    Returns None (explicit null) if parsing fails — never raises silently.
    """
    if not raw:
        print("[validator] Empty response from LLM.")
        return None

    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1])

    try:
        data = json.loads(cleaned)
        return schema(**data)
    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        print(f"[validator] Validation failed: {e}")
        print(f"[validator] Raw output was: {raw[:300]}")
        return None