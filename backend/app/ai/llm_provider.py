"""
ai/llm_provider.py

Abstract interface for any LLM provider. Qwen is the only implementation
right now, but every service in this app depends on THIS interface, not
on QwenClient directly — swapping providers later (or adding a second
one) means writing one new class, not touching services/routers.

Two methods map directly to the two AI pipelines from the architecture:
- extract_structured(): unstructured text -> structured JSON facts
- generate(): structured context -> natural-language reasoning output
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def extract_structured(self, system_prompt: str, user_content: str) -> dict:
        """
        Send text to the model with instructions to return ONLY JSON.
        Returns a parsed dict. Raises ValueError if the model's response
        isn't valid JSON (callers should handle this — extraction is not
        guaranteed to always succeed against a live model).
        """
        raise NotImplementedError

    @abstractmethod
    def generate(self, system_prompt: str, user_content: str, temperature: float = 0.7) -> str:
        """Send text to the model for open-ended reasoning; returns raw text."""
        raise NotImplementedError

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text, same order."""
        raise NotImplementedError
