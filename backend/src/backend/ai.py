import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "openai/gpt-oss-120b:free"


def _get_openrouter_headers() -> dict:
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "User-Agent": "ProjectManagementMVP/1.0",
    }


async def call_ai(message: str) -> dict:
    """Call OpenRouter AI with the given message and return full response."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in environment")

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": message}],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            json=payload,
            headers=_get_openrouter_headers(),
            timeout=30.0,
        )
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()


async def call_ai_with_context(board_data: dict, question: str) -> dict:
    """Call AI with Kanban context and return response with optional updates."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in environment")

    prompt = f"""You are a project management assistant. The user has a Kanban board with the following state:

{json.dumps(board_data, indent=2)}

User question: {question}

Respond with ONLY a JSON object (no markdown, no explanations) in this format:
{{
  "response": "Your helpful response to the user",
  "updates": [
    {{"action": "create_card", "columnId": 1, "title": "Card title", "details": "Card details"}},
    {{"action": "edit_card", "cardId": 1, "title": "New title", "details": "New details"}},
    {{"action": "move_card", "cardId": 1, "columnId": 2, "position": 0}},
    {{"action": "delete_card", "cardId": 1}}
  ]
}}

Only include updates if the user's question implies changes. Otherwise, just respond without updates."""

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            json=payload,
            headers=_get_openrouter_headers(),
            timeout=30.0,
        )
        if response.status_code != 200:
            response.raise_for_status()

        openrouter_response = response.json()
        content = openrouter_response["choices"][0]["message"]["content"]

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "response": content,
                "updates": []
            }
