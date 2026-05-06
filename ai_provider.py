"""
AI Provider abstraction.
Чтобы сменить провайдера — меняешь только .env:
  AI_PROVIDER=claude  | openai
  AI_MODEL=claude-sonnet-4-20250514 | gpt-4o | llama3 | ...
"""
from __future__ import annotations
import os
from abc import ABC, abstractmethod
from typing import List, Dict


# ─── Base ─────────────────────────────────────────────────────────────────────

class AIProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        system: str,
        max_tokens: int = 600,
    ) -> str:
        """messages = [{"role": "user"|"assistant", "content": "..."}]"""
        ...


# ─── Claude (Anthropic) ───────────────────────────────────────────────────────

class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        import anthropic
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def complete(self, messages, system, max_tokens=600):
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return response.content[0].text


# ─── OpenAI / GPT-4 / любой OpenAI-совместимый API ───────────────────────────

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1",
        )
        self._model = model

    async def complete(self, messages, system, max_tokens=600):
        full_messages = [{"role": "system", "content": system}] + messages
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=full_messages,
        )
        return response.choices[0].message.content


# ─── Factory ──────────────────────────────────────────────────────────────────

def get_provider() -> AIProvider:
    provider = os.getenv("AI_PROVIDER", "claude").lower()
    model = os.getenv("AI_MODEL", "")

    if provider == "claude":
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY не задан в .env")
        if not model:
            model = "claude-sonnet-4-20250514"
        return ClaudeProvider(api_key=key, model=model)

    elif provider == "openai":
        key = os.getenv("OPENAI_API_KEY", "")
        if not key:
            raise ValueError("OPENAI_API_KEY не задан в .env")
        if not model:
            model = "gpt-4o"
        base_url = os.getenv("OPENAI_BASE_URL")  # None = дефолтный OpenAI
        return OpenAIProvider(api_key=key, model=model, base_url=base_url)

    else:
        raise ValueError(
            f"Неизвестный AI_PROVIDER='{provider}'. Доступны: claude, openai"
        )
