"""
ai/qwen_client.py

Concrete LLMProvider implementation for Qwen's OpenAI-compatible endpoint
(DashScope compatible-mode). Uses the official `openai` SDK pointed at
Qwen's base_url — this is what "OpenAI compatible" buys us: no custom
HTTP client needed.

Nothing outside this file (and llm_provider.py's interface) should ever
import the `openai` package directly — that keeps the provider swap-out
promise real, not just aspirational.
"""

import json
import re

from openai import OpenAI

from app.ai.llm_provider import LLMProvider
from app.core.config import get_settings

settings = get_settings()


def _strip_code_fences(text: str) -> str:
    """
    Models frequently wrap JSON in ```json ... ``` even when told not to.
    Strip fences defensively rather than trusting the prompt alone.
    """
    text = text.strip()
    match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    return match.group(1) if match else text


class QwenClient(LLMProvider):
    def __init__(self):
        self._client = OpenAI(api_key=settings.QWEN_API_KEY, base_url=settings.QWEN_BASE_URL)
        self._model = settings.QWEN_MODEL
        self._embedding_model = settings.QWEN_EMBEDDING_MODEL

    def extract_structured(self, system_prompt: str, user_content: str) -> dict:
        response = self._client.chat.completions.create(
            model=self._model,
            temperature=0.1,  # low temperature: extraction should be consistent, not creative
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        raw = response.choices[0].message.content or ""
        cleaned = _strip_code_fences(raw)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Qwen did not return valid JSON: {raw[:200]}") from exc

    def generate(self, system_prompt: str, user_content: str, temperature: float = 0.7) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        return response.choices[0].message.content or ""

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self._client.embeddings.create(model=self._embedding_model, input=texts)
        # API guarantees response order matches input order.
        return [item.embedding for item in response.data]


_qwen_singleton: QwenClient | None = None


def get_llm_provider() -> LLMProvider:
    """
    FastAPI dependency / general accessor. Singleton because constructing
    the OpenAI client is cheap but pointless to repeat per-request, and
    every consumer wants the same configured instance.
    """
    global _qwen_singleton
    if _qwen_singleton is None:
        _qwen_singleton = QwenClient()
    return _qwen_singleton
