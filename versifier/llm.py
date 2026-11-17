"""Optional LLM mode: talk to The Versifier using the Claude API.

Requires `pip install anthropic` and the ANTHROPIC_API_KEY environment variable.
Set VERSIFIER_MODEL to override the default model.
"""
from __future__ import annotations

import os
from pathlib import Path

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system_prompt.md"
DEFAULT_MODEL = "claude-sonnet-5-5"


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


class LLMVersifier:
    def __init__(self, model: str | None = None, max_tokens: int = 1024):
        try:
            import anthropic  # noqa: WPS433
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("LLM mode needs `pip install anthropic`.") from exc
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("Set ANTHROPIC_API_KEY to use LLM mode.")
        self.client = anthropic.Anthropic()
        self.model = model or os.environ.get("VERSIFIER_MODEL", DEFAULT_MODEL)
        self.max_tokens = max_tokens
        self.system = load_system_prompt()
        self.history: list[dict] = []

    def say(self, text: str) -> str:
        self.history.append({"role": "user", "content": text})
        resp = self.client.messages.create(
            model=self.model, max_tokens=self.max_tokens,
            system=self.system, messages=self.history,
        )
        reply = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        self.history.append({"role": "assistant", "content": reply})
        return reply
