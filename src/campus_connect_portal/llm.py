"""LLM client with an offline-friendly fallback."""

from __future__ import annotations

import logging
import os
import textwrap
from typing import Any

from .config import DEFAULT_CHAT_MODEL

LOGGER = logging.getLogger(__name__)


class LLMClient:
    """Thin wrapper around OpenAI's Responses API with a heuristic fallback."""

    def __init__(self, model: str | None = None):
        self.model = model or DEFAULT_CHAT_MODEL
        self.api_key = os.getenv("OPENAI_API_KEY")
        self._client = self._build_openai_client()

    def _build_openai_client(self):
        if not self.api_key:
            return None
        try:
            from openai import OpenAI  # type: ignore

            return OpenAI(api_key=self.api_key)
        except Exception as exc:  # pragma: no cover - optional dependency
            LOGGER.warning("Unable to initialize OpenAI client: %s", exc)
            return None

    def respond(self, system_prompt: str, user_prompt: str) -> str:
        if self._client:
            try:
                response = self._client.responses.create(
                    model=self.model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                )
                return self._extract_text(response)
            except Exception as exc:  # pragma: no cover - network failure
                LOGGER.warning("OpenAI request failed, falling back to heuristic mode: %s", exc)
        return self._fallback_response(user_prompt)

    def _extract_text(self, response: Any) -> str:
        """Handle OpenAI Responses output shape."""
        try:
            first_output = response.output[0]
            if hasattr(first_output, "content"):
                content = first_output.content[0]
                return content.text
        except Exception:
            pass
        try:
            return response.output_text
        except AttributeError:
            return "Unable to parse model output."

    def _fallback_response(self, user_prompt: str) -> str:
        """Produce a deterministic, explainable summary when no LLM is available."""
        summary_lines = []
        knowledge, tasks = self._extract_sections(user_prompt)
        if knowledge:
            summary_lines.append(f"Knowledge insights: {', '.join(knowledge[:2])}.")
        if tasks:
            summary_lines.append(f"Suggested tasks: {', '.join(tasks[:2])}.")
        if not summary_lines:
            summary_lines.append("No stored knowledge or tasks yet—add notes with `add-note`.")
        return " ".join(summary_lines)

    def _extract_sections(self, prompt: str) -> tuple[list[str], list[str]]:
        knowledge_items: list[str] = []
        task_items: list[str] = []
        current = None
        for line in prompt.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith("knowledge entries"):
                current = "knowledge"
                continue
            if line.lower().startswith("tasks:"):
                current = "tasks"
                continue
            if line.startswith("- "):
                content = line[2:]
                if current == "knowledge":
                    knowledge_items.append(textwrap.shorten(content, width=120))
                elif current == "tasks":
                    task_items.append(textwrap.shorten(content, width=120))
        return knowledge_items, task_items
