#!/usr/bin/env python3
"""Test script to verify LLM integration works."""

import sys
sys.path.insert(0, 'src')

from text2sql_agent.config import settings
from text2sql_agent.agent import AgentConfig, Text2SQLAgent

def test_llm_integration():
    print("=" * 60)
    print("Testing LLM Integration")
    print("=" * 60)
    
    # Check configuration
    print(f"\n✓ Configuration loaded:")
    print(f"  - Generator mode: {settings.generator_mode}")
    print(f"  - LLM model: {settings.llm_model}")
    print(f"  - API key present: {settings.openai_api_key is not None}")
    
    # Initialize agent
    config = AgentConfig(
        db_url=settings.db_url,
        generator_mode=settings.generator_mode,
        openai_api_key=settings.openai_api_key,
        llm_model=settings.llm_model,
        llm_temperature=settings.llm_temperature,
    )
    agent = Text2SQLAgent(config)
    print(f"\n✓ Agent initialized with hybrid mode")
    
    # Test 1: Rule-based match (should use rules, not LLM)
    print(f"\n{'=' * 60}")
    print("Test 1: Rule-based question (exact match)")
    print("=" * 60)
    question1 = "order fill rate last 30 days"
    result1 = agent.ask(question1)
    print(f"Question: {question1}")
    print(f"Outcome: {result1['outcome_type']}")
    print(f"SQL: {result1.get('sql', 'None')[:80]}...")
    
    # Test 2: Natural language variation (should fall back to LLM)
    print(f"\n{'=' * 60}")
    print("Test 2: Natural language variation (LLM fallback)")
    print("=" * 60)
    question2 = "what was the fill rate for orders in the past month?"
    result2 = agent.ask(question2)
    print(f"Question: {question2}")
    print(f"Outcome: {result2['outcome_type']}")
    print(f"SQL: {result2.get('sql', 'None')[:80] if result2.get('sql') else 'None'}...")
    print(f"Rationale: {result2.get('rationale', 'None')[:100]}...")
    
    # Test 3: Unsafe query (should be blocked)
    print(f"\n{'=' * 60}")
    print("Test 3: Unsafe query (validation should block)")
    print("=" * 60)
    question3 = "delete all orders"
    result3 = agent.ask(question3)
    print(f"Question: {question3}")
    print(f"Outcome: {result3['outcome_type']}")
    print(f"Message: {result3.get('message', 'None')}")
    
    print(f"\n{'=' * 60}")
    print("✓ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_llm_integration()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
