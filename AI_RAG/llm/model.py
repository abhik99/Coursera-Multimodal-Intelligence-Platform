import os
from dotenv import load_dotenv

from google import genai
from google.genai import types

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


class GeminiModel:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    attempts=1,
                    http_status_codes=[429, 500, 502, 503, 504]
                )
            )
        )

    def generate(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        # Attempt with primary model, then fallback to current stable models
        candidate_models = [MODEL_NAME, "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-3.8-flash"]
        models_to_try = []
        for m in candidate_models:
            if m and m not in models_to_try:
                models_to_try.append(m)
        last_error = None

        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response and hasattr(response, "text") and response.text:
                    return response.text
            except Exception as exc:
                last_error = exc
                continue

        # If all model attempts failed, inspect the last error
        if last_error:
            error_message = str(last_error).lower()
            if "429" in error_message or "quota" in error_message or "resource exhausted" in error_message:
                raise RuntimeError("Gemini API rate limit or quota was reached. Please check the Gemini API usage.") from last_error
            if "503" in error_message or "service unavailable" in error_message:
                raise RuntimeError(f"Gemini API returned HTTP 503 service unavailable: {last_error}") from last_error
            raise RuntimeError(f"LLM generation failed on models {models_to_try}: {last_error}") from last_error

        raise RuntimeError("LLM generation returned an empty response.")