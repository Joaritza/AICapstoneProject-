"""
Test script for Phase 4 - RouterAgent verification.

This script tests the RouterAgent's ability to:
1. Process user queries
2. Route to appropriate tools
3. Generate coherent responses
4. Maintain conversation memory
"""

import sys
import logging
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_memory_manager():
    """Test memory manager functionality."""
    print("\n" + "=" * 60)
    print("TEST 1: Memory Manager")
    print("=" * 60)

    from agents.memory_manager import MemoryManager, ConversationMemory, UserProfile

    # Test ConversationMemory
    memory = ConversationMemory(window_size=5)
    memory.add_message("user", "What's in milk?")
    memory.add_message("assistant", "Milk is not vegan...")
    memory.add_message("user", "What about oat milk?")
    memory.add_message("assistant", "Oat milk is vegan...")

    print(f"✓ ConversationMemory: {len(memory.messages)} messages stored")
    print(f"✓ Last user message: {memory.get_last_user_message()}")

    # Test UserProfile
    profile = UserProfile()
    profile.update(
        dietary_restrictions=["gluten-free"],
        protein_goal_grams=75.0,
        cuisine_preferences=["Asian", "Mediterranean"]
    )

    print(f"✓ UserProfile: {profile.dietary_restrictions}")
    print(f"✓ Protein goal: {profile.protein_goal_grams}g")

    # Test MemoryManager
    manager = MemoryManager(user_id="test_user")
    manager.add_user_message("Is tofu vegan?")
    manager.add_assistant_message("Yes, tofu is 100% vegan!")

    messages = manager.get_messages_for_llm()
    print(f"✓ MemoryManager: {len(messages)} messages (including system prompt)")

    # Check message format for LLM
    assert messages[0]["role"] == "system", "First message should be system prompt"
    assert "plant-based" in messages[0]["content"].lower(), "System prompt should mention plant-based"
    
    print("✓ All memory manager tests PASSED")
    return True


def test_response_synthesizer():
    """Test response synthesizer functionality."""
    print("\n" + "=" * 60)
    print("TEST 2: Response Synthesizer")
    print("=" * 60)

    from agents.response_synthesizer import ResponseSynthesizer

    synth = ResponseSynthesizer()

    # Test ingredient analysis synthesis
    vegan_status = {
        "name": "milk",
        "vegan": False,
        "reason": "Animal product from cow lactation",
        "sources": ["local_database"],
        "alternatives": ["Soy Milk", "Oat Milk", "Almond Milk"]
    }

    alternatives = [
        {
            "alternative": "Oat Milk",
            "reason": "Popular non-dairy milk alternative",
            "nutritional_match": 0.85
        },
        {
            "alternative": "Soy Milk",
            "reason": "High in protein",
            "nutritional_match": 0.95
        }
    ]

    response = synth.synthesize_ingredient_analysis(
        ingredient="milk",
        vegan_status=vegan_status,
        alternatives=alternatives
    )

    print(f"✓ Ingredient analysis synthesized ({len(response)} chars)")
    assert "Milk" in response or "milk" in response.lower()
    assert "Oat Milk" in response or "oat" in response.lower()

    # Test error response synthesis
    error = ValueError("Test error")
    error_response = synth.synthesize_error_response(error)
    print(f"✓ Error response synthesized ({len(error_response)} chars)")

    print("✓ All response synthesizer tests PASSED")
    return True


def test_router_agent_tools():
    """Test RouterAgent tool definitions."""
    print("\n" + "=" * 60)
    print("TEST 3: RouterAgent Tool Definitions")
    print("=" * 60)

    try:
        from agents.router_agent import RouterAgent
        
        agent = RouterAgent()
        
        print(f"✓ RouterAgent initialized")
        print(f"✓ LLM Model: {agent.llm.model_name}")
        print(f"✓ Number of tools: {len(agent.tools)}")
        
        # Check tools are defined
        tool_names = [tool.name for tool in agent.tools]
        expected_tools = [
            "check_ingredient_vegan_status",
            "get_vegan_alternatives",
            "search_recipes_by_ingredients",
            "get_recipe_details",
            "get_ingredient_nutrition",
            "generate_shopping_list"
        ]
        
        for expected in expected_tools:
            assert expected in tool_names, f"Tool {expected} not found"
            print(f"  ✓ {expected}")
        
        # Check tool map exists
        assert hasattr(agent, 'tool_map'), "Agent should have tool_map"
        print(f"✓ Tool map created with {len(agent.tool_map)} entries")
        
        # Check memory manager
        assert agent.memory is not None, "Agent should have memory manager"
        print(f"✓ Memory manager configured")
        
        print("✓ All RouterAgent tests PASSED")
        return True
        
    except Exception as e:
        print(f"✗ RouterAgent test failed: {e}")
        logger.error(f"RouterAgent error: {e}", exc_info=True)
        return False


def test_memory_state_export():
    """Test memory state export and import."""
    print("\n" + "=" * 60)
    print("TEST 4: Memory State Export/Import")
    print("=" * 60)

    from agents.memory_manager import MemoryManager

    # Create initial state
    manager1 = MemoryManager(user_id="user123")
    manager1.add_user_message("Is milk vegan?")
    manager1.add_assistant_message("No, milk is not vegan.")
    manager1.update_user_profile(
        dietary_restrictions=["gluten-free"],
        protein_goal_grams=100
    )

    # Export state
    exported = manager1.export_state()
    print(f"✓ Exported state: {len(exported)} keys")
    assert "user_id" in exported
    assert "conversation" in exported
    assert "user_profile" in exported

    # Create new manager and import
    manager2 = MemoryManager(user_id="user456")
    manager2.import_state(exported)

    # Verify state restored
    assert manager2.user_id == "user123", "User ID should match"
    assert len(manager2.conversation.messages) == 2, "Messages should be restored"
    assert "gluten-free" in manager2.user_profile.dietary_restrictions
    assert manager2.user_profile.protein_goal_grams == 100

    print(f"✓ Imported state restored correctly")
    print(f"  - User ID: {manager2.user_id}")
    print(f"  - Messages: {len(manager2.conversation.messages)}")
    print(f"  - Dietary restrictions: {manager2.user_profile.dietary_restrictions}")
    print("✓ All memory state tests PASSED")
    return True


def main():
    """Run all tests."""
    print("\n" + "🧪 PHASE 4 VERIFICATION TEST SUITE".center(60))
    print("=" * 60)

    results = []

    try:
        results.append(("Memory Manager", test_memory_manager()))
        results.append(("Response Synthesizer", test_response_synthesizer()))
        results.append(("RouterAgent Tools", test_router_agent_tools()))
        results.append(("Memory State Export/Import", test_memory_state_export()))
    except Exception as e:
        logger.error(f"Test suite error: {e}", exc_info=True)
        print(f"\n✗ Test suite failed: {e}")
        return False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL PHASE 4 TESTS PASSED!")
        print("RouterAgent, Memory, and Response Synthesizer are ready for integration.")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    import os
    
    # Set dummy API key for testing (RouterAgent init requires key)
    os.environ.setdefault("GITHUB_TOKEN", "test-token-for-verification")
    
    success = main()
    sys.exit(0 if success else 1)
