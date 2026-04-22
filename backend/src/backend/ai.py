import os
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "openai/gpt-oss-120b:free"


async def call_ai(message: str) -> dict:
    """Call OpenRouter AI with the given message and return full response."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in environment")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "User-Agent": "ProjectManagementMVP/1.0",
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": message}],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
            timeout=30.0,
        )
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()
