"""
LLM interface: abstraction for language model interactions.
"""

import json
import os
from typing import Any, Dict, Optional


class LLMInterface:
    """
    Interface to LLM for workflow generation.
    Supports multiple backends: OpenAI, Anthropic, local models via vLLM/ollama.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.provider = provider or os.getenv("AI4S_LLM_PROVIDER", "openai")
        self.model = model or os.getenv("AI4S_LLM_MODEL", "gpt-4o")
        self.api_key = api_key or os.getenv("AI4S_LLM_API_KEY")
        self.base_url = base_url or os.getenv("AI4S_LLM_BASE_URL")

        self._client = None

    def _get_client(self):
        """Lazy-load the appropriate client."""
        if self._client is not None:
            return self._client

        if self.provider == "openai":
            try:
                import openai
                self._client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )
            except ImportError:
                raise ImportError("Install openai: pip install openai")

        elif self.provider == "anthropic":
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("Install anthropic: pip install anthropic")

        elif self.provider == "ollama":
            # Ollama uses OpenAI-compatible API
            try:
                import openai
                base = self.base_url or "http://localhost:11434/v1"
                self._client = openai.OpenAI(
                    api_key="ollama",  # required but unused
                    base_url=base,
                )
            except ImportError:
                raise ImportError("Install openai for ollama support: pip install openai")

        elif self.provider == "vllm":
            try:
                import openai
                base = self.base_url or "http://localhost:8000/v1"
                self._client = openai.OpenAI(
                    api_key=self.api_key or "vllm",
                    base_url=base,
                )
            except ImportError:
                raise ImportError("Install openai for vLLM support: pip install openai")

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        return self._client

    def complete(self, prompt: str, temperature: float = 0.1, max_tokens: int = 500) -> str:
        """Get a text completion from the LLM."""
        client = self._get_client()

        if self.provider == "openai":
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""

        elif self.provider == "anthropic":
            response = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text if response.content else ""

        return ""

    def generate_plan(self, query: str, domain_context: str) -> Dict[str, Any]:
        """
        Generate a structured workflow plan from a query and domain context.

        Returns a dict with:
        - steps: list of {tool, command, inputs, outputs, dependencies, description}
        - estimated_compute: str
        - required_software: list of str
        - validation_checks: list of str
        """
        prompt = f"""You are an expert computational scientist. Given a research query and domain context, generate a detailed, executable workflow plan.

Domain Context:
{domain_context}

Research Query:
{query}

Generate a JSON workflow plan with this exact structure:
{{
    "steps": [
        {{
            "tool": "software tool name",
            "command": "exact shell command or script call",
            "inputs": {{"param_name": "value_or_path"}},
            "outputs": {{"output_name": "path_or_description"}},
            "dependencies": ["0", "1"],
            "description": "what this step does"
        }}
    ],
    "estimated_compute": "e.g., 4 hours on 8 CPU cores + 1 GPU",
    "required_software": ["tool1", "tool2"],
    "validation_checks": ["check1", "check2"]
}}

Rules:
1. Commands must be executable (no placeholders like <input>)
2. Use realistic file names and paths
3. Dependencies reference step indices as strings
4. Include all necessary setup/preparation steps
5. Consider data validation and error checking

Output ONLY valid JSON. No markdown, no explanations."""

        response = self.complete(prompt, temperature=0.2, max_tokens=4000)

        # Extract JSON from response
        try:
            # Try direct parse first
            plan = json.loads(response)
        except json.JSONDecodeError:
            # Try extracting from markdown code block
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                plan = json.loads(json_str)
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
                plan = json.loads(json_str)
            else:
                # Fallback: wrap in minimal structure
                plan = {
                    "steps": [],
                    "estimated_compute": "unknown",
                    "required_software": [],
                    "validation_checks": [],
                    "raw_response": response,
                }

        return plan
