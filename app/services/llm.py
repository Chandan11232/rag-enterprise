import json
from collections.abc import AsyncGenerator

import google.generativeai as genai
import httpx

from app.core.config import settings


class OllamaClient:
    @staticmethod
    async def generate_stream(
        prompt: str, system_prompt: str | None = None
    ) -> AsyncGenerator[str, None]:
        if settings.LLM_PROVIDER.lower() == "gemini":
            if not settings.GEMINI_API_KEY:
                yield "Error: GEMINI_API_KEY is not configured in .env."
                return
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(
                    model_name=settings.GEMINI_MODEL,
                    system_instruction=system_prompt if system_prompt else None,
                )
                response = model.generate_content(prompt, stream=True)
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
