"""
LabCorePlanner Agent
Model: models/gemini-2.5-pro
"""

import json
from pathlib import Path
from typing import Dict, Any

from ..base_agent import BaseAgent, GenerationConfig


class LabCorePlannerAgent(BaseAgent):
    """
    LabCorePlanner Agent
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

        # Optimized config for structured lab planning
        if GenerationConfig is not None:
            self.generation_config = GenerationConfig(
                temperature=0.5,
                top_p=0.92,
                top_k=40,
                max_output_tokens=16384,
            )
        else:
            self.generation_config = {
                "temperature": 0.5,
                "top_p": 0.92,
                "top_k": 40,
                "max_output_tokens": 16384,
            }

    async def plan(self, vulnerability_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create lab plan from vulnerability data

        System instruction from prompt.md contains all instructions.
        User prompt contains only the vulnerability data JSON.
        """
        # Pass only the vulnerability data - prompt.md has all instructions
        prompt = json.dumps(vulnerability_data, indent=2)

        try:
            return await self.generate_json(prompt, retries=3)
        except Exception as e:
            return {
                "status": "error",
                "error": True,
                "reason": f"Agent processing failed: {str(e)}"
            }
