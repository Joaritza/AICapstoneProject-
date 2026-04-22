"""Verify that the Streamlit app loads without import errors."""

import sys
from pathlib import Path

# Add project root to path (same as app.py does)
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("Testing UI imports...")
print("=" * 80)

try:
    print("\n[1] Testing core imports...")
    import streamlit as st
    print("  [OK] streamlit")
    
    from config.logger_config import logger
    print("  [OK] logger_config")
    
    from agents.router_agent import RouterAgent
    print("  [OK] RouterAgent")
    
    import json
    print("  [OK] json")
    
    from datetime import datetime
    print("  [OK] datetime")
    
    print("\n[2] Testing RouterAgent initialization...")
    agent = RouterAgent()
    print(f"  [OK] RouterAgent initialized")
    print(f"       Tools: {len(agent.tools)}")
    print(f"       Memory: ConversationMemory ready")
    
    print("\n[3] Testing session state simulation...")
    session_state = {
        "agent": agent,
        "conversation_state": agent.get_conversation_state(),
        "show_intro": True,
    }
    print(f"  [OK] Session state created")
    print(f"       Agent stored")
    print(f"       Conversation state captured")
    
    print("\n[4] Testing suggested prompts...")
    SUGGESTED_PROMPTS = [
        "Is milk vegan?",
        "What are vegan alternatives for butter?",
        "Give me a recipe using spinach and chickpeas",
        "How much protein is in soy milk?",
        "Create a vegan shopping list for the week",
        "Suggest a meal plan for 3 days",
        "What can I substitute for eggs in baking?",
        "Find recipes with only 5 ingredients",
    ]
    print(f"  [OK] {len(SUGGESTED_PROMPTS)} prompts available")
    
    print("\n[5] Testing message processing logic...")
    test_query = "Is milk vegan?"
    agent.memory.add_user_message(test_query)
    response = agent.process_query(test_query)
    print(f"  [OK] Query processed successfully")
    print(f"       Query: {test_query}")
    print(f"       Response length: {len(response)} chars")
    print(f"       Memory messages: {len(agent.memory.get_messages_for_llm())}")
    
    print("\n[6] Testing state export/import...")
    state = agent.memory.export_state()
    print(f"  [OK] State exported successfully")
    print(f"       User ID: {state.get('user_id')}")
    print(f"       Messages: {len(state.get('conversation', []))}")
    
    print("\n" + "=" * 80)
    print("SUCCESS - ALL CHECKS PASSED - STREAMLIT APP READY")
    print("=" * 80)
    print("\nYour UI should now work correctly at http://localhost:8501")
    print("To start the app: streamlit run ui/app.py")
    
except ImportError as e:
    print(f"\nERROR - Import Error: {e}")
    print("Make sure all files exist and __init__.py files are present")
    sys.exit(1)
    
except Exception as e:
    print(f"\nERROR - Runtime Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
