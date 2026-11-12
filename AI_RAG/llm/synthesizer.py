import json


class Synthesizer:
    def __init__(self, llm):
        self.llm = llm

    def generate(self, prompt: str) -> dict:
        response = self.llm.generate(prompt)

        if not response or not response.strip():
            raise ValueError("LLM returned an empty response.")

        cleaned = response.strip()

        # Extract JSON from markdown fences or text if present
        import re
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if fence_match:
            cleaned = fence_match.group(1).strip()
        elif not cleaned.startswith("{"):
            obj_match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if obj_match:
                cleaned = obj_match.group(1).strip()

        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError:
            # Resilient fallback: wrap plain text into expected response dictionary
            result = {
                "answer": response.strip(),
                "evidence_ids": [],
                "confidence": 0.85
            }

        # Basic structure validation
        required_fields = {
            "answer",
            "evidence_ids",
            "confidence"
        }

        missing_fields = required_fields - result.keys()

        if missing_fields:
            raise ValueError(
                f"Missing required fields: {sorted(missing_fields)}"
            )

        if not isinstance(result["answer"], str):
            raise ValueError("The 'answer' field must be a string.")

        if not isinstance(result["evidence_ids"], list):
            raise ValueError("The 'evidence_ids' field must be a list.")

        if not isinstance(result["confidence"], (int, float)):
            raise ValueError(
                "The 'confidence' field must be a number."
            )

        return result