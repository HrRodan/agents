import os
from dotenv import load_dotenv

# Set up dummy environment for testing without hitting APIs
# Actually, I'll mock the internal client or just mock the query method to avoid API calls and costs

import sys

sys.path.append(".")
from ai_tools.tools import LLMQuery


class MockLLMQuery(LLMQuery):
    def invoke(self, user_prompt=None, **kwargs):
        return f"[MOCK_RESPONSE to: '{user_prompt}' with kwargs: {kwargs}]"


def test_piping():
    q1 = MockLLMQuery()
    q2 = MockLLMQuery()

    # Test 1: Simple pipe
    print("--- Test 1 ---")
    res1 = "hello" | q1
    print(repr(res1))

    # Test 2: Pipe with kwargs
    print("--- Test 2 ---")
    res2 = "hello" | q1(model="mock-v1", temperature=0.7)
    print(repr(res2))

    # Test 3: Chained pipes
    print("--- Test 3 ---")
    res3 = "hello" | q1 | q2
    print(repr(res3))

    # Test 4: Chained pipes with kwargs
    print("--- Test 4 ---")
    res4 = "hello" | q1(model="m1") | q2(model="m2")
    print(repr(res4))

    # Test 5: Pipe to print (callable)
    print("--- Test 5 ---")
    "This must be printed correctly" | q1 | print

    # Test 6: Pipeline composition
    print("--- Test 6 ---")
    pipeline = q1(model="p1") | q2(model="p2") | print
    "Pipeline input" | pipeline


if __name__ == "__main__":
    test_piping()
