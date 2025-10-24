"""
WriteUpToMarkdown Agent - Converts write-up URLs to markdown using Jina.ai
Model: gemini-2.5-flash
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import httpx

from ..base_agent import BaseAgent, GenerationConfig


class WriteUpToMarkdownAgent(BaseAgent):
    """
    WriteUpToMarkdown Agent - Converts write-up URLs to markdown using Jina.ai
    """

    def __init__(
            self,
            api_key: str | None = None,
            provider: str | None = None,
            model: str | None = None):
        # Use default gemini-2.5-flash because this a lightweight task
        model = model or "gemini-2.5-flash"
        prompt_path = Path(__file__).parent / "prompt.md"
        super().__init__(
            api_key,
            model=model,
            prompt_file_path=prompt_path,
            provider=provider)

        # Override generation config - lower temperature for consistent
        # validation decisions
        if GenerationConfig is not None:
            self.generation_config = GenerationConfig(
                temperature=0.4,
                top_p=0.9,
                top_k=40,
                max_output_tokens=15000,
            )
        else:
            self.generation_config = {
                "temperature": 0.4,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 15000,
            }

    async def convert(self, url: str) -> Dict[str, Any]:
        """Convert write-up URL to structured markdown"""
        jina_url = f"https://r.jina.ai/{url}"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(jina_url)
                response.raise_for_status()
                markdown_content = response.text
        except Exception:
            return {
                "error": True,
                "status": "error"
            }

        # The system instruction from prompt.txt is already loaded
        # Pass the actual data as the user prompt
        prompt = (
            f"Analyze this URL and determine if it's a vulnerability "
            f"write-up or security blog post.\n\n"
            f"URL: {url}\n\n"
            f"Markdown content:\n{markdown_content[:8000]}\n"
        )

        try:
            result = await self.generate_json(prompt, retries=3)

            # Add fetch metadata
            if "input" not in result:
                result["input"] = {}
            result["input"]["url"] = url
            result["input"]["fetch_time"] = datetime.utcnow().isoformat() + "Z"

            # Store full markdown if successful
            if result.get("status") == "ok":
                result["markdown"] = markdown_content

            return result

        except Exception as e:
            error_msg = str(e)
            return {
                "error": True,
                "reason": (
                    f"Agent processing failed: {error_msg}. "
                    f"Check logs/agent_errors/ for details."
                ),
                "status": "error"
            }
