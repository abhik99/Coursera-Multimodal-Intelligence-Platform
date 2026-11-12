# from AI_RAG.llm.model import GeminiModel


# model = GeminiModel()

# response = model.generate(
#     "In one sentence, explain what data science is."
# )

# print("\nGemini response:")
# print(response)
import os
from dotenv import load_dotenv

load_dotenv()
from google import genai

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not set."
    )

client = genai.Client(api_key=api_key)

print("Testing Gemini...")
print("Model:", MODEL_NAME)

try:
    response = client.interactions.create(
        model=MODEL_NAME,
        input="Say hello in one short sentence."
    )

    print("\nSUCCESS")
    print("Response:")
    print(response.output_text)

except Exception as exc:
    print("\nGEMINI TEST FAILED")
    print(type(exc).__name__)
    print(exc)