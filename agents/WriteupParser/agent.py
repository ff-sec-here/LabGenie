"""
WriteupParser (Vulnerability Information Builder) Agent
"""

from pathlib import Path
from typing import Dict, Any

from ..base_agent import BaseAgent, GenerationConfig


class WriteupParserAgent(BaseAgent):
    """
    WriteupParser (Vulnerability Information Builder) Agent
    """

    def __init__(
            self,
            api_key: str | None = None,
            provider: str | None = None,
            model: str | None = None):
        # Use default claude-opus-4-8 if not specified
        model = model or "claude-opus-4-8"
        prompt_path = Path(__file__).parent / "prompt.md"
        super().__init__(
            api_key,
            model=model,
            prompt_file_path=prompt_path,
            provider=provider)

        # Optimized config for precise information extraction
        if self.provider in ("claude", "claude-code"):
            self.generation_config = {
                "temperature": 0.2,
                "max_tokens": 8192,
            }
        elif self.provider == "vertex" and GenerationConfig is not None:
            self.generation_config = GenerationConfig(
                temperature=0.2,
                top_p=0.9,
                top_k=20,
                max_output_tokens=8192,
            )
        else:  # gemini — always use plain dict
            self.generation_config = {
                "temperature": 0.2,
                "top_p": 0.9,
                "top_k": 20,
                "max_output_tokens": 8192,
            }

    async def parse(self, markdown_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse vulnerability information from markdown

        System instruction from prompt.md contains all instructions.
        User prompt contains only the markdown content.
        """
        markdown_content = markdown_data.get("markdown", "")

        # Pass only the markdown content - prompt.md has all instructions
        prompt = markdown_content[:8000]

        try:
            return await self.generate_json(prompt, retries=3)
        except Exception as e:
            return {
                "status": "error",
                "error": True,
                "reason": f"Agent processing failed: {str(e)}"
            }
