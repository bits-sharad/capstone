from __future__ import annotations

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional at import time
    genai = None


class GeminiService:
    """
    Thin wrapper around Google Gemini for structured analysis.

    For this capstone, agents are written so they can also fall back
    to simple heuristic logic when the SDK or API key is not available.
    """

    def __init__(self, model_name: str = "gemini-1.5-flash"):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        self._enabled = bool(api_key and genai is not None)

        self._model_name = model_name
        self._client: Optional[genai.GenerativeModel] = None

        if self._enabled:
            genai.configure(api_key=api_key)
            self._client = genai.GenerativeModel(model_name)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def generate_json(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ask Gemini for a JSON response following a simple schema description.
        Falls back to an empty dict when Gemini is not configured.
        """
        if not self._enabled or self._client is None:
            # In local/offline mode, callers must handle this gracefully.
            return {}

        # We keep this intentionally simple; a production version might use
        # strict JSON mode or function calling style.
        full_prompt = (
            "You are an e-commerce product quality analyzer.\n"
            "Return ONLY valid JSON matching this schema description:\n"
            f"{schema}\n\n"
            "Task:\n"
            f"{prompt}"
        )
        response = self._client.generate_content(full_prompt)
        try:
            # Newer Gemini SDKs expose .parsed or similar helpers; to keep
            # this generic we just eval JSON from text.
            import json

            return json.loads(response.text)
        except Exception:
            return {}

