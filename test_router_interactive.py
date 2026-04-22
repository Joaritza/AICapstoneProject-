"""
Interactive RouterAgent test script with sample plant-based queries.

This script tests the RouterAgent's ability to handle realistic user queries
about vegan ingredients, recipes, nutrition, and meal planning.
"""

import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup environment
os.environ.setdefault("LOG_LEVEL", "INFO")

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80)


def print_query(index: int, query: str) -> None:
    """Print a formatted query."""
    print(f"\n[Query {index}] 🤔 USER: {query}")
    print("-" * 80)


def print_response(response: str, time_taken: float = None) -> None:
    """Print a formatted response."""
    print(f"\n✨ ASSISTANT:")
    print(response)
    if time_taken:
        print(f"\n⏱️  Response time: {time_taken:.2f}s")


def print_error(error: str) -> None:
    """Print a formatted error."""
    print(f"\n❌ ERROR: {error}")


def test_router_agent():
    """Test RouterAgent with sample queries."""
    print_header("🌱 Plant Based Assistant - RouterAgent Interactive Test")
    
    try:
        # Import after path setup
        from agents.router_agent import RouterAgent
        from agents.memory_manager import MemoryManager
        
        print("\n📦 Initializing RouterAgent...")
        agent = RouterAgent()
        print("✅ RouterAgent initialized successfully!")
        
        print(f"📊 Configuration:")
        print(f"   - Model: {agent.llm.model_name}")
        print(f"   - Temperature: {agent.llm.temperature}")
        print(f"   - Max tokens: {agent.llm.max_tokens}")
        print(f"   - Tools available: {len(agent.tools)}")
        
        # Sample queries covering different use cases
        sample_queries = [
            {
                "category": "Ingredient Analysis",
                "query": "Is milk vegan?",
                "description": "Check vegan status of a basic ingredient"
            },
            {
                "category": "Alternatives",
                "query": "What are some vegan alternatives for butter?",
                "description": "Get substitutes for common non-vegan ingredient"
            },
            {
                "category": "Recipe Search",
                "query": "I have tofu, broccoli, and garlic. Can you suggest a vegan recipe?",
                "description": "Search recipes by available ingredients"
            },
            {
                "category": "Nutrition",
                "query": "How many calories and protein are in a cup of soy milk?",
                "description": "Get nutritional information"
            },
            {
                "category": "Multi-turn Conversation",
                "query": "What about nutritional comparison between soy milk and oat milk?",
                "description": "Use conversation context from previous query"
            },
        ]
        
        print_header("🧪 Sample Query Tests")
        
        for i, test_case in enumerate(sample_queries, 1):
            print(f"\n\n{'━' * 80}")
            print(f"Test {i}: {test_case['category']}")
            print(f"Description: {test_case['description']}")
            print(f"{'━' * 80}")
            
            print_query(i, test_case['query'])
            
            try:
                start_time = datetime.now()
                response = agent.process_query(test_case['query'])
                elapsed = (datetime.now() - start_time).total_seconds()
                
                print_response(response, elapsed)
                
                # Show memory state
                print(f"\n📝 Conversation History:")
                memory = agent.memory.conversation
                print(f"   - Messages stored: {len(memory.messages)}")
                print(f"   - Last user query: {memory.get_last_user_message()[:60]}...")
                
            except Exception as e:
                print_error(f"{type(e).__name__}: {str(e)}")
                logger.error(f"Query failed: {e}", exc_info=True)
        
        # Final conversation summary
        print_header("📊 Conversation Summary")
        
        final_state = agent.memory.export_state()
        print(f"\n✅ Session Statistics:")
        print(f"   - User ID: {final_state['user_id']}")
        print(f"   - Total messages: {len(final_state['conversation'])}")
        print(f"   - Conversation exchanges: {len(final_state['conversation']) // 2}")
        
        user_profile = final_state['user_profile']
        print(f"\n👤 User Profile:")
        print(f"   - Dietary restrictions: {user_profile.get('dietary_restrictions', [])}")
        print(f"   - Allergies: {user_profile.get('allergies', [])}")
        print(f"   - Protein goal: {user_profile.get('protein_goal_grams')}g/day")
        print(f"   - Cuisine preferences: {user_profile.get('cuisine_preferences', [])}")
        
        # Test state persistence
        print_header("💾 State Persistence Test")
        
        print("\n📝 Exporting conversation state...")
        exported_state = agent.memory.export_state()
        print(f"✅ State exported ({len(str(exported_state))} bytes)")
        
        print("\n📝 Creating new agent and importing state...")
        new_agent = RouterAgent()
        new_agent.memory.import_state(exported_state)
        print(f"✅ State imported successfully")
        
        print(f"\n✓ Recovered {len(new_agent.memory.conversation.messages)} messages")
        print(f"✓ User ID: {new_agent.memory.user_id}")
        print(f"✓ Last message: {new_agent.memory.conversation.get_last_user_message()}")
        
        print_header("✨ All Tests Completed Successfully!")
        
        return True
        
    except ImportError as e:
        print_error(f"Import Error: {e}")
        logger.error("Could not import required modules", exc_info=True)
        return False
        
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        logger.error("Test failed with unexpected error", exc_info=True)
        return False


def interactive_mode():
    """Start interactive chat mode."""
    print_header("🌱 Plant Based Assistant - Interactive Chat Mode")
    
    try:
        from agents.router_agent import RouterAgent
        
        print("\n📦 Initializing RouterAgent...")
        agent = RouterAgent()
        print("✅ Ready to chat!\n")
        
        print("💡 Try asking about:")
        print("   • Vegan status of ingredients")
        print("   • Vegan alternatives for cooking")
        print("   • Recipe recommendations")
        print("   • Nutritional information")
        print("   • Meal planning help\n")
        print("Type 'quit' or 'exit' to end the conversation.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for chatting with Plant Based Assistant!")
                    break
                
                print("\n🤔 Thinking...", end="", flush=True)
                start_time = datetime.now()
                response = agent.process_query(user_input)
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"\r✨ Response ({elapsed:.1f}s):\n")
                
                print(response)
                print("\n" + "-" * 80)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat ended.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                logger.error(f"Chat error: {e}", exc_info=True)
        
        return True
        
    except Exception as e:
        print_error(f"Could not start interactive mode: {e}")
        return False


def main():
    """Main entry point."""
    print_header("🌱 Plant Based Assistant - RouterAgent Test Suite")
    
    print("\nChoose test mode:")
    print("  1. Automated tests with sample queries (default)")
    print("  2. Interactive chat mode")
    print("  3. Exit")
    
    choice = input("\nSelect option (1-3) [1]: ").strip() or "1"
    
    if choice == "1":
        success = test_router_agent()
    elif choice == "2":
        success = interactive_mode()
    else:
        print("Exiting...")
        return True
    
    if success:
        print("\n✅ Test completed successfully!")
        return True
    else:
        print("\n❌ Test failed. Check logs for details.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.error("Fatal error", exc_info=True)
        sys.exit(1)
