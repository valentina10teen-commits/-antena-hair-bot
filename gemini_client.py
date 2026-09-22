"""Integração opcional com a Gemini API.

O bot continua funcionando sem esta integração. Para ativá-la, defina
GEMINI_API_KEY e instale google-genai.
"""
from __future__ import annotations

import os
from pathlib import Path


class GeminiClient:
    def __init__(self) -> None:
        from google import genai  # import opcional

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Defina GEMINI_API_KEY para ativar o Gemini.")
        self.client = genai.Client(api_key=api_key)
        self.model = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
        self.system_prompt = Path(__file__).with_name("prompt_gemini.txt").read_text(encoding="utf-8")

    def answer(self, user_text: str) -> str:
        prompt = f"{self.system_prompt}\n\nMensagem da cliente:\n{user_text}"
        interaction = self.client.interactions.create(model=self.model, input=prompt)
        return interaction.output_text.strip()
