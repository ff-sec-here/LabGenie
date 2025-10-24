"""
Base Agent class for all LabGenie agents
Provides common AI backend setup and utilities.

Backends supported:
- vertex: Google Cloud Vertex AI (Gemini via google-cloud-aiplatform)
- gemini: Google Gemini API (via google-generativeai)
"""

import asyncio
import json
import re
import os
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Lazy imports: we import SDKs only when used
try:
    # Suppress Vertex AI deprecation warnings (deprecated June 2025, removed
    # June 2026)
    warnings.filterwarnings(
        'ignore',
        category=UserWarning,
        module='vertexai.generative_models._generative_models')
    from vertexai.generative_models import GenerativeModel, GenerationConfig  # type: ignore
    import vertexai  # type: ignore
except Exception:  # SDK might not be installed if using Gemini API
    GenerativeModel = None  # type: ignore
    GenerationConfig = None  # type: ignore
    vertexai = None  # type: ignore

try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None  # type: ignore


class BaseAgent:
    """Base class for all agents with pluggable AI backend"""

    def __init__(
            self,
            api_key: Optional[str],
            model: str,
            prompt_file_path: Optional[Path] = None,
            provider: Optional[str] = None):
        """
        Initialize agent with selected backend.

        Args:
            api_key: API key for Gemini API (ignored for Vertex). If None, read from env.
            model: Model identifier (Gemini model name)
            prompt_file_path: Optional path to the agent's prompt file
            provider: 'vertex' or 'gemini'. If None, uses LABGENIE_PROVIDER env (default 'gemini').
        """
        self.provider = (
            provider or os.getenv(
                "LABGENIE_PROVIDER",
                "gemini")).lower()
        if self.provider not in ("vertex", "gemini"):
            self.provider = "gemini"

        self.model_name = model
        self.prompt_file_path = prompt_file_path

        # Load system prompt from file if provided
        self.system_instruction = self._load_prompt() if prompt_file_path else ""
        self.prompt_template = self.system_instruction

        # Configure backend
        if self.provider == "vertex":
            if vertexai is None or GenerativeModel is None:
                raise RuntimeError(
                    "google-cloud-aiplatform is required for provider "
                    "'vertex'. Install it or switch provider.")
            project_id = os.getenv(
                "GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
            location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
            if not project_id:
                raise ValueError(
                    "Vertex AI requires GOOGLE_CLOUD_PROJECT environment variable. "
                    "Set it with: export GOOGLE_CLOUD_PROJECT='your-project-id'")
            vertexai.init(project=project_id, location=location)

            # Default Generation Config for Vertex (can be overridden by
            # subclasses)
            self.generation_config = GenerationConfig(
                temperature=0.4,
                top_p=0.9,
                top_k=40,
                max_output_tokens=8192,
                candidate_count=1,
            )

        else:  # gemini API
            if genai is None:
                raise RuntimeError(
                    "google-generativeai is required for provider "
                    "'gemini'. Install it or switch provider.")
            api_key = api_key or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "Gemini API requires GOOGLE_API_KEY. "
                    "Set it with: export GOOGLE_API_KEY='your-key'")
            genai.configure(api_key=api_key)

            # Simple dict to mirror GenerationConfig fields we use
            self.generation_config = {
                "temperature": 0.4,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 8192,
            }

    def _load_prompt(self) -> str:
        """Load agent prompt from the specified prompt file"""
        if not self.prompt_file_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {
                    self.prompt_file_path}")

        with open(self.prompt_file_path, 'r', encoding='utf-8') as f:
            return f.read()

    async def generate(self, prompt: str) -> str:
        """Generate response text from the configured backend"""
        if self.provider == "vertex":
            # Vertex AI doesn't have native async support, so we use
            # asyncio.to_thread
            def _generate_sync_vertex():
                model = GenerativeModel(
                    self.model_name,
                    system_instruction=self.system_instruction
                )
                try:
                    response = model.generate_content(
                        prompt,
                        generation_config=self.generation_config
                    )
                    if hasattr(response, 'text'):
                        return response.text
                    elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content'):
                            content = candidate.content
                            if hasattr(
                                    content, 'parts') and len(
                                    content.parts) > 0:
                                return content.parts[0].text
                    return str(response)
                except Exception as e:
                    raise ValueError(
                        f"Vertex AI generation failed: {
                            str(e)}\nPrompt length: {
                            len(prompt)} chars")

            return await asyncio.to_thread(_generate_sync_vertex)

        # Gemini API path
        def _generate_sync_gemini():
            # Build model with optional system_instruction
            # Note: genai.GenerativeModel supports safety_settings and
            # system_instruction
            model = genai.GenerativeModel(
                self.model_name, system_instruction=self.system_instruction)
            try:
                response = model.generate_content(
                    prompt, generation_config=self.generation_config)
                # google-generativeai returns response.text for most cases
                return getattr(response, 'text', str(response))
            except Exception as e:
                raise ValueError(
                    f"Gemini API generation failed: {
                        str(e)}\nPrompt length: {
                        len(prompt)} chars")

        return await asyncio.to_thread(_generate_sync_gemini)

    async def generate_json(
            self, prompt: str, retries: int = 1) -> Dict[str, Any]:
        """Generate and parse JSON with retries and repair fallback."""
        # 0) First attempt: instruct for strict JSON
        strict_prompt = (
            f"{prompt}\n\n"
            "STRICT OUTPUT REQUIREMENTS:\n"
            "- Return valid JSON only.\n"
            "- Do not include any markdown code fences.\n"
            "- No commentary or explanations, JSON only.\n"
        )

        try:
            response_text = await self.generate(strict_prompt)
        except Exception as e:
            # Log generation error
            self._log_error(f"Generation failed: {str(e)}")
            raise ValueError(f"Failed to generate response: {str(e)}")

        try:
            return self.parse_json_response(response_text)
        except ValueError as e:
            self._log_error(
                f"First parse failed: {str(e)}\nResponse: {response_text[:500]}")

        # 1) Retry loop with a repair prompt using the previous output
        last_text = response_text
        for retry_idx in range(max(0, retries)):
            repair_prompt = (
                "You previously produced invalid JSON. Convert the following into valid JSON only, "
                "matching the schema described in the system instruction. If fields are missing, "
                "use null, empty arrays, or empty strings. Do not include markdown or prose.\n\n"
                f"Input:\n{last_text}"
            )

            try:
                last_text = await self.generate(repair_prompt)
            except Exception as e:
                self._log_error(
                    f"Retry {
                        retry_idx +
                        1} generation failed: {
                        str(e)}")
                continue

            try:
                return self.parse_json_response(last_text)
            except ValueError as e:
                self._log_error(
                    f"Retry {retry_idx + 1} parse failed: {str(e)}\nResponse: {last_text[:500]}")
                continue

        # 2) Final failure: save the problematic response for debugging
        self._log_error(f"All retries exhausted. Last response:\n{last_text}")
        raise ValueError(
            f"Failed to parse JSON response from LLM after {retries} retries.\n"
            f"Last response preview: {last_text[:1000]}\n"
            f"See logs for full response."
        )

    def _log_error(self, message: str):
        """Log error to file for debugging"""
        log_dir = Path("logs") / "agent_errors"
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"error_{timestamp}.log"

        with open(log_file, "a") as f:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"Time: {datetime.now().isoformat()}\n")
            f.write(f"Agent: {self.__class__.__name__}\n")
            f.write(f"Model: {self.model_name}\n")
            f.write(f"{message}\n")
            f.write(f"{'=' * 80}\n")

    @staticmethod
    def clean_json_response(response_text: str) -> str:
        """Clean JSON response from markdown code blocks"""
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        return response_text.strip()

    @staticmethod
    def repair_json_text(text: str) -> str:
        """Attempt lightweight repairs on common JSON errors."""
        s = text
        # Normalize smart quotes to straight quotes
        s = s.replace(
            "“",
            '"').replace(
            "”",
            '"').replace(
            "‘",
            "'").replace(
                "’",
            "'")
        # Remove trailing commas before object/array closers
        s = re.sub(r",\s*(?=[}\]])", "", s)
        # Ensure keys are quoted (very conservative: only for simple word keys)
        s = re.sub(r'(?m)^(\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', s)
        # Strip stray backticks
        s = s.replace("```", "")
        return s.strip()

    @staticmethod
    def parse_json_response(response_text: str) -> Dict[str, Any]:
        """
        Parse JSON response with better error handling

        Args:
            response_text: Raw response text from LLM

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If JSON cannot be parsed with details about the error
        """
        cleaned_text = BaseAgent.clean_json_response(response_text)

        # 1) Try direct parse
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            pass

        # 2) Try lightweight repairs
        repaired = BaseAgent.repair_json_text(cleaned_text)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

        # 3) Try extracting the largest JSON object substring
        m = re.search(r"\{[\s\S]*\}", repaired)
        if m:
            candidate = m.group(0)
            # Remove trailing commas again in case extraction changed context
            candidate2 = re.sub(r",\s*(?=[}\]])", "", candidate)
            try:
                return json.loads(candidate2)
            except json.JSONDecodeError:
                # One last attempt with original cleaned substring
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError as e:
                    # Fall through to detailed error
                    final_text = candidate
                    error = e
        else:
            # Try array extraction as top-level JSON
            m_arr = re.search(r"\[[\s\S]*\]", repaired)
            if m_arr:
                candidate = m_arr.group(0)
                candidate2 = re.sub(r",\s*(?=[}\]])", "", candidate)
                try:
                    return json.loads(candidate2)
                except json.JSONDecodeError:
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError as e:
                        final_text = candidate
                        error = e
            else:
                final_text = repaired
                error = None

        # Detailed error report
        try:
            # Re-raise using the most recent error context if available
            if 'error' in locals() and error is not None:
                raise error
            else:
                json.loads(final_text)  # Will raise
        except json.JSONDecodeError as e:
            error_context = final_text[max(
                0, e.pos - 100):min(len(final_text), e.pos + 100)]
            error_msg = (
                f"Failed to parse JSON response from LLM.\n"
                f"Error: {e.msg} at line {e.lineno}, column {e.colno} (char {e.pos})\n"
                f"Context around error:\n...{error_context}...\n\n"
                f"First 500 chars of response:\n{final_text[:500]}\n\n"
                f"Last 500 chars of response:\n{final_text[-500:]}"
            )
            raise ValueError(error_msg) from e
