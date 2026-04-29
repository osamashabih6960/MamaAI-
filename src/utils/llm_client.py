import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")


def call_llm(system_prompt: str, user_message: str, temperature: float = 0.3) -> str:
    """
    Call Groq LLM (free, no credit card needed).
    Returns response text or empty string on failure.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=temperature,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[llm_client] Error calling Groq: {e}")
        return ""