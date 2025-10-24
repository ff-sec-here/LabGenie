"""
LabBuilder Agent
Model: models/gemini-2.5-pro
"""

import json
from pathlib import Path
from typing import Dict, Any

from ..base_agent import BaseAgent, GenerationConfig


class LabBuilderAgent(BaseAgent):
    """
    LabBuilder Agent
    Model: models/gemini-2.5-pro
    """

    def __init__(
            self,
            api_key: str | None = None,
            provider: str | None = None,
            model: str | None = None):
        # Use default models/gemini-2.5-pro if not specified
        model = model or "models/gemini-2.5-pro"
        prompt_path = Path(__file__).parent / "prompt.md"
        super().__init__(
            api_key,
            model=model,
            prompt_file_path=prompt_path,
            provider=provider)

        # Override generation config for LabBuilder - needs higher token limit
        # for complete labs
        if GenerationConfig is not None:
            self.generation_config = GenerationConfig(
                temperature=0.3,
                top_p=0.9,
                top_k=30,
                max_output_tokens=65536,
                candidate_count=1,
            )
        else:
            self.generation_config = {
                "temperature": 0.3,
                "top_p": 0.9,
                "top_k": 30,
                "max_output_tokens": 65536,
            }

    async def build(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build complete runnable lab from plan

        System instruction from prompt.md contains all instructions.
        User prompt contains only the plan data JSON.
        """
        # Pass only the plan data - prompt.md has all instructions
        prompt = json.dumps(plan_data, indent=2)

        try:
            return await self.generate_json(prompt, retries=3)
        except Exception as e:
            return {
                "status": "error",
                "error": True,
                "reason": f"Agent processing failed: {str(e)}",
                "files": []
            }
