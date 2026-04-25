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

        elif self.provider == "deepseek":
            # DeepSeek uses OpenAI-compatible API
            try:
                import openai
                base = self.base_url or "https://api.deepseek.com"
                self._client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=base,
                )
            except ImportError:
                raise ImportError("Install openai for DeepSeek support: pip install openai")

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

        elif self.provider in ("ollama", "vllm", "deepseek"):
            # All use OpenAI-compatible API
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""

        return ""

    def generate_plan(self, query: str, domain_context: str) -> Dict[str, Any]:
        """
        Generate a structured workflow plan from a query and domain context.
        For models with limited output length, falls back to outline mode if truncated.

        Returns a dict with:
        - steps: list of {tool, command, inputs, outputs, dependencies, description}
        - estimated_compute: str
        - required_software: list of str
        - validation_checks: list of str
        """
        # Try full plan first
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

        # Check if response was truncated (model hit output limit)
        is_truncated = (
            not response.strip().endswith("}") and
            not response.strip().endswith("]") and
            not response.strip().endswith('"')
        )

        # Extract JSON from response
        plan = self._extract_json(response)

        # If truncated or empty steps, fall back to outline mode
        if is_truncated or not plan.get("steps"):
            print("[LLM] Output truncated or empty, falling back to outline mode...")
            plan = self._generate_outline_plan(query, domain_context)

        return plan

    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Extract JSON from LLM response with multiple fallback strategies."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try markdown code block
        if "```json" in response:
            try:
                json_str = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            except (IndexError, json.JSONDecodeError):
                pass

        if "```" in response:
            try:
                json_str = response.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)
            except (IndexError, json.JSONDecodeError):
                pass

        # Try brace-depth matching for partial JSON
        try:
            start = response.index("{")
            depth = 0
            end = start
            for i, c in enumerate(response[start:]):
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        end = start + i + 1
                        break
            if end > start:
                return json.loads(response[start:end])
        except (ValueError, json.JSONDecodeError):
            pass

        # Final fallback
        return {
            "steps": [],
            "estimated_compute": "unknown",
            "required_software": [],
            "validation_checks": [],
            "raw_response": response,
        }

    def _generate_outline_plan(self, query: str, domain_context: str) -> Dict[str, Any]:
        """Fallback: generate a step outline without detailed commands."""
        prompt = f"""You are an expert computational scientist. Given a research query, list the workflow steps.

Domain Context:
{domain_context[:500]}  # Truncate to save tokens

Research Query:
{query}

Output a compact JSON plan. Keep descriptions short (under 100 chars). Use simple placeholder commands like "# see documentation".

{{
    "steps": [
        {{
            "tool": "tool_name",
            "command": "# Step description - see docs for full command",
            "inputs": {{}},
            "outputs": {{}},
            "dependencies": [],
            "description": "short description"
        }}
    ],
    "estimated_compute": "brief estimate",
    "required_software": ["tool1"],
    "validation_checks": ["check1"]
}}

Output ONLY valid JSON."""

        response = self.complete(prompt, temperature=0.2, max_tokens=3000)
        plan = self._extract_json(response)

        # Mark as outline mode
        plan["_mode"] = "outline"
        plan["_note"] = "Detailed commands omitted due to model output limits. Use domain documentation for full parameters."

        return plan
