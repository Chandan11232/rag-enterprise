import json
from collections.abc import AsyncGenerator

import httpx
from google import genai

from app.core.config import settings


class OllamaClient:
    @staticmethod
    async def generate_stream(
        prompt: str, system_prompt: str | None = None
    ) -> AsyncGenerator[str, None]:
        if settings.LLM_PROVIDER.lower() == "gemini":
            if not settings.GEMINI_API_KEY:
                yield "Error: GEMINI_API_KEY is not configured in .env or environment variables."
                return
            try:
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                full_prompt = (
                    f"System Instructions: {system_prompt}\n\n{prompt}"
                    if system_prompt
                    else prompt
                )
                response = client.models.generate_content_stream(
                    model=settings.GEMINI_MODEL,
                    contents=full_prompt,
                )
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            except Exception as e:  # noqa: BLE001
                yield f"Gemini API Error: {e!s}"
            return

        # Default Ollama Streaming
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": True,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=120.0) as client, client.stream(
                "POST", url, json=payload
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        yield data.get("response", "")
                        if data.get("done", False):
                            break
        except Exception as e:  # noqa: BLE001
            yield f"Ollama Connection Error: {e!s}"
