import os
import sys
from dotenv import load_dotenv

sys.path.append(".")
from ai_tools.tools import LLMQuery


def test_real_piping():
    load_dotenv(override=True)

    print("Initializing LLMQueries...")
    # Use cheap/fast models for testing
    q_gemini = LLMQuery(
        model="gemini-2.5-flash-lite",
        system_prompt="You are a helpful assistant. Keep your answers to one short sentence maximum.",
    )
    q_gpt = LLMQuery(
        model="gpt-4o-mini",
        system_prompt="You are a translator. Translate the given text to French. Only output the translation, nothing else.",
    )

    print("\n--- Test 1: Simple execution pipeline ---")
    pipe1 = "What is the capital of Japan?" | q_gemini | print

    print("\n--- Test 2: Chained LLM pipeline ---")
    pipe2 = "Tell me a fun fact about pandas." | q_gemini | q_gpt | print

    print("\n--- Test 3: kwargs overriding ---")
    pipe3 = "How do you say hello in French?" | q_gpt(temperature=0.0) | print


if __name__ == "__main__":
    test_real_piping()
