import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load .env BEFORE any OpenAI client is created
load_dotenv()


@dataclass
class LLMClient:
    """
    Thin wrapper around the OpenAI chat completions API.

    This client centralizes configuration and provides a small helper
    for JSON-only completions used by the Planner and Verifier agents.
    """

    def __post_init__(self) -> None:
        # Explicitly read and validate API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is missing. Ensure .env is present and loaded."
            )
        
        # Pass api_key explicitly to AsyncOpenAI
        self._client = AsyncOpenAI(api_key=api_key)

    async def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        """
        Request a JSON-only response from the model. The underlying API
        enforces JSON via response_format.
        """
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        response = await self._client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            temperature=0.1,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        message = response.choices[0].message
        content = message.content or "{}"
        return content


llm_client = LLMClient()

