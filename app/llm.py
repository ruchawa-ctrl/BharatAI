import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini-3.8-flash")


class GeminiWrapper:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self.client = None
        if GEMINI_API_KEY:
            try:
                from google import genai
                self.client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception as e:
                print(f"[LLM] Warning: Could not initialize Google GenAI client: {e}")
                self.client = None

    def is_available(self) -> bool:
        return self.client is not None and bool(GEMINI_API_KEY)

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Generate grounded text using Gemini. Falls back to deterministic synthesis if unavailable.
        """
        if self.is_available():
            try:
                full_input = prompt
                if system_instruction:
                    full_input = f"{system_instruction}\n\nUser Question:\n{prompt}"
                
                interaction = self.client.interactions.create(
                    model=self.model_name,
                    input=full_input
                )
                if interaction and hasattr(interaction, "output_text") and interaction.output_text:
                    return interaction.output_text.strip()
            except Exception as e:
                print(f"[LLM] Gemini call failed, falling back to local synthesizer: {e}")

        # Local deterministic synthesis
        return ""


# Singleton instance
llm_client = GeminiWrapper()
