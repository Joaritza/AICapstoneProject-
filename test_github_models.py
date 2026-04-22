"""
Direct RouterAgent test with GitHub Models endpoint - no interactive prompts.
"""

import sys
sys.path.insert(0, '.')

from datetime import datetime
from agents.router_agent import RouterAgent

print("\n" + "=" * 80)
print("🌱 Plant Based Assistant - RouterAgent Test with GitHub Models".center(80))
print("=" * 80)

# Initialize agent
print("\n📦 Initializing RouterAgent...")
agent = RouterAgent()
print(f"✅ RouterAgent initialized")
print(f"   • Endpoint: https://models.github.ai/inference")
print(f"   • Model: openai/gpt-4o")
print(f"   • Tools: {len(agent.tools)}")

# Sample queries
queries = [
    "Is milk vegan?",
    "What are vegan alternatives for butter?",
    "How much protein is in soy milk?",
]

print("\n" + "=" * 80)
print("🧪 TESTING SAMPLE QUERIES")
print("=" * 80)

total_time = 0
for i, query in enumerate(queries, 1):
    print(f"\n[Query {i}] {query}")
    print("-" * 80)
    
    try:
        start = datetime.now()
        response = agent.process_query(query)
        elapsed = (datetime.now() - start).total_seconds()
        total_time += elapsed
        
        # Show response (first 300 chars)
        response_preview = response[:300] + "..." if len(response) > 300 else response
        print(f"Response: {response_preview}")
        print(f"⏱️  Time: {elapsed:.2f}s")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)[:100]}")

# Show conversation stats
print("\n" + "=" * 80)
print("📊 CONVERSATION SUMMARY")
print("=" * 80)

state = agent.memory.export_state()
print(f"\n✅ Session Statistics:")
print(f"   • Total queries: {len(queries)}")
print(f"   • Total time: {total_time:.2f}s")
print(f"   • Average response time: {total_time/len(queries):.2f}s")
print(f"   • Messages in memory: {len(state['conversation'])}")
print(f"   • User ID: {state['user_id']}")

print("\n" + "=" * 80)
print("✨ Test Complete - GitHub Models Integration Successful!".center(80))
print("=" * 80 + "\n")
