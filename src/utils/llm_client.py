import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = os.getenv("MODEL_NAME", "meta-llama/llama-3.1-8b-instruct:free")


def call_llm(system_prompt: str, user_message: str, temperature: float = 0.3) -> str:
    """
    Call the LLM via OpenRouter.
    Returns the response text, or empty string on failure.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[llm_client] Error: {e}")
        return ""