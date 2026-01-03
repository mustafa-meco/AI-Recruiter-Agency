import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)


class BaseAgent:
    def __init__(self, name: str, instructions: str, provider: str = None, api_key: str = None):
        self.name = name
        self.instructions = instructions
        self.provider = provider or Config.DEFAULT_PROVIDER
        self.api_key = api_key
        
        # Initialize Client based on provider
        if self.provider == "nebius":
            self.client = OpenAI(
                base_url=Config.NEBIUS_BASE_URL,
                api_key=self.api_key or "placeholder", # Requires key
            )
            self.model = Config.NEBIUS_MODEL
        else: # Default to Ollama
            self.client = OpenAI(
                base_url=Config.OLLAMA_BASE_URL,
                api_key="ollama", # Not required for Ollama
            )
            self.model = Config.OLLAMA_MODEL

    async def run(self, messages: list) -> Dict[str, Any]:
        """
        Process messages and return a result.
        Must be implemented by child classes.
        """
        raise NotImplementedError("Subclasses must implement run method")

    def _query_llm(self, prompt: str) -> str:
        """
        Query the LLM using the configured provider.
        """
        try:
            # logger.info(f"[{self.name}] Querying {self.provider} ({self.model})...") # Reduced verbosity
            
            messages = [
                {"role": "system", "content": self.instructions},
                {"role": "user", "content": prompt}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error querying LLM ({self.provider}): {e}")
            return json.dumps({"error": str(e)})

    # Backwards compatibility alias
    def _query_ollama(self, prompt: str) -> str:
        return self._query_llm(prompt)

    def _parse_json_safely(self, text: str) -> Dict[str, Any]:
        """
        Safely parse JSON from LLM response.
        """
        try:
            # Remove any markdown code block indicators
            clean_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON", "raw_text": text}