"""Streamlit UI for Plant Based Assistant."""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from config.logger_config import logger
from agents.router_agent import RouterAgent
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Plant Based Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Nature-themed custom styling
st.markdown(
    """
    <style>
    /* Main background - soft green */
    .main {
        background-color: #f0f8f4;
        color: #2d5016;
    }
    
    /* Header styling */
    h1 {
        color: #1b5e20;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    h2 {
        color: #2d5016;
        border-bottom: 2px solid #81c784;
        padding-bottom: 10px;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: linear-gradient(135deg, #ffffff 0%, #f1f8f6 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #81c784;
    }
    
    /* Input area */
    .stChatInputContainer {
        border-top: 2px solid #81c784;
        padding-top: 10px;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #2d5016;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #1b5e20;
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #e8f5e9;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #c8e6c9;
        border-left: 4px solid #2d5016;
    }
    
    /* Dividers */
    hr {
        border: 1px solid #81c784;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "agent" not in st.session_state:
    try:
        st.session_state.agent = RouterAgent()
        st.session_state.conversation_state = st.session_state.agent.get_conversation_state()
        st.session_state.show_intro = True
        logger.info("Initialized RouterAgent in session state")
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        logger.error(f"Agent initialization error: {e}")
        st.session_state.agent = None

# Suggested prompts for quick start
SUGGESTED_PROMPTS = [
    "🥛 Is milk vegan?",
    "🧈 What are vegan alternatives for butter?",
    "🥗 Give me a recipe using spinach and chickpeas",
    "📊 How much protein is in soy milk?",
    "🛒 Create a vegan shopping list for the week",
    "🍽️ Suggest a meal plan for 3 days",
    "🌾 What can I substitute for eggs in baking?",
    "🥜 Find recipes with only 5 ingredients",
]

# Page title with subtitle
st.title("🌱 Plant Based Assistant")
st.markdown("*Your friendly guide to plant-based living*")

# Show intro on first load
if st.session_state.show_intro:
    with st.expander("👋 Welcome! Click to learn more", expanded=True):
        st.markdown("""
        Welcome to the **Plant Based Assistant**! I'm here to help you with:
        
        - ✓ **Ingredient Analysis** - Check if ingredients are vegan
        - 🔄 **Vegan Alternatives** - Find substitutions for non-vegan ingredients
        - 🍽️ **Recipe Recommendations** - Discover recipes based on your ingredients
        - 📊 **Nutrition Information** - Get detailed nutritional data and comparisons
        - 📝 **Meal Planning** - Create shopping lists and meal plans
        
        ### Quick Start:
        Click one of the suggested prompts below, or ask me anything about plant-based eating!
        """)
    st.session_state.show_intro = False

# Suggested prompts section
st.markdown("### 💡 Quick Start Prompts")
cols = st.columns(4)
for i, prompt in enumerate(SUGGESTED_PROMPTS):
    with cols[i % 4]:
        if st.button(prompt, use_container_width=True, key=f"prompt_{i}"):
            st.session_state.quick_prompt = prompt

# Sidebar - Settings & History
with st.sidebar:
    st.header("⚙️ Settings & History")
    
    # Tabs for sidebar organization
    sidebar_tab1, sidebar_tab2, sidebar_tab3 = st.tabs(["Preferences", "History", "About"])
    
    with sidebar_tab1:
        st.subheader("👤 User Preferences")
        
        # Dietary restrictions
        dietary_restrictions = st.multiselect(
            "Dietary Restrictions",
            ["None", "Gluten-free", "Nut allergy", "Soy allergy"],
            default=["None"],
            key="dietary_restrictions",
        )
        
        # Cuisine preferences
        cuisines = st.multiselect(
            "Favorite Cuisines",
            ["Italian", "Asian", "Mexican", "Indian", "Mediterranean"],
            default=[],
            key="cuisines_pref",
        )
        
        # Protein goal
        protein_goal = st.slider(
            "Daily Protein Goal (grams)", 
            30, 200, 50, 
            step=10,
            key="protein_goal_slider"
        )
        
        # Budget slider
        budget = st.slider(
            "Weekly Budget ($)",
            10, 100, 40,
            step=5,
            key="budget_slider"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Preferences", use_container_width=True):
                if st.session_state.agent:
                    st.session_state.agent.memory.user_profile.dietary_restrictions = dietary_restrictions
                    st.session_state.agent.memory.user_profile.cuisine_preferences = cuisines
                    st.session_state.agent.memory.user_profile.protein_goal_grams = float(protein_goal)
                    st.session_state.agent.memory.user_profile.budget = float(budget)
                    st.success("✓ Preferences saved!")
                    logger.info(f"User preferences updated: {dietary_restrictions}, {cuisines}")
        
        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.show_intro = True
                st.rerun()
    
    with sidebar_tab2:
        st.subheader("📝 Conversation History")
        
        if st.session_state.agent:
            messages = st.session_state.agent.memory.get_messages_for_llm()
            
            if messages:
                st.success(f"📊 {len(messages)} messages in this conversation")
                
                # Display conversation preview
                with st.expander("View Conversation", expanded=False):
                    for i, msg in enumerate(messages[-6:], 1):  # Show last 3 exchanges
                        role = "👤" if msg["role"] == "user" else "🤖"
                        preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                        st.markdown(f"**{role}:** {preview}")
                
                # Export/Import buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Export", use_container_width=True):
                        state = st.session_state.agent.memory.export_state()
                        st.download_button(
                            label="Download JSON",
                            data=json.dumps(state, indent=2),
                            file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                        )
                with col2:
                    if st.button("🔄 Clear", use_container_width=True):
                        st.session_state.agent.memory.conversation.messages.clear()
                        st.success("✓ Conversation cleared!")
                        st.rerun()
            else:
                st.info("No messages yet. Start chatting!")
    
    with sidebar_tab3:
        st.subheader("ℹ️ About")
        st.info(
            """**Plant Based Assistant v1.0**
            
Built with ❤️ using:
- 🔗 LangChain 1.2.15
- 🎨 Streamlit 1.30+
- 🤖 GPT-4o via GitHub Models
- 🥬 USDA FoodData
- 🍽️ Spoonacular API

**Status:** ✅ All systems active
            """
        )

    # Clear conversation button
    if st.button("�️ Clear All"):
        st.session_state.agent.memory.conversation.messages.clear()
        st.success("✓ Conversation cleared!")
        st.rerun()

# Main chat area
st.divider()
st.header("💬 Chat")

if st.session_state.agent:
    # Display conversation history
    messages = st.session_state.agent.memory.get_messages_for_llm()
    
    # Display all messages in a container
    chat_container = st.container()
    
    with chat_container:
        if not messages:
            st.info("👋 No messages yet. Start by clicking a suggested prompt or typing your question!")
        else:
            for msg in messages:
                if msg["role"] == "user":
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(msg["content"])
                elif msg["role"] == "assistant":
                    with st.chat_message("assistant", avatar="🌱"):
                        st.markdown(msg["content"])
    
    # Chat input and processing
    st.divider()
    
    # Handle quick prompt selection
    user_input = None
    if "quick_prompt" in st.session_state:
        user_input = st.session_state.quick_prompt
        del st.session_state.quick_prompt
    
    # Regular chat input
    if user_input is None:
        user_input = st.chat_input(
            "Ask about ingredients, recipes, nutrition, or meal planning...",
            key="user_input",
        )
    
    if user_input:
        # Display user message immediately
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        
        # Add user message to memory
        st.session_state.agent.memory.add_user_message(user_input)
        
        # Process response with streaming effect
        with st.chat_message("assistant", avatar="🌱"):
            message_placeholder = st.empty()
            status_placeholder = st.empty()
            
            # Show loading indicator
            with status_placeholder.container():
                st.spinner("🤔 Thinking...")
            
            try:
                # Get response from agent
                response = st.session_state.agent.process_query(user_input)
                
                # Clear status and display response
                status_placeholder.empty()
                message_placeholder.markdown(response)
                
                # Update conversation state
                st.session_state.conversation_state = st.session_state.agent.get_conversation_state()
                
                logger.info(f"Query processed successfully. Response length: {len(response)}")
                
            except Exception as e:
                status_placeholder.empty()
                error_msg = f"❌ Error processing query: {str(e)}"
                message_placeholder.error(error_msg)
                logger.error(f"Error processing query: {e}", exc_info=True)
        
        # Rerun to show new message in history
        st.rerun()

else:
    st.error(
        "⚠️ Agent failed to initialize. Please check:\n"
        "- `.env` file exists with API keys\n"
        "- GITHUB_TOKEN is valid\n"
        "- Internet connection is active"
    )

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 20px;">
    <small>🌍 Plant Based Assistant | Powered by LangChain + GPT-4o | Data from USDA & Spoonacular</small>
    </div>
    """,
    unsafe_allow_html=True,
)

logger.info("Streamlit UI loaded successfully")


