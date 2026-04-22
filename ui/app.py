"""Streamlit UI for Plant Based Assistant."""

import streamlit as st
from config.logger_config import logger
from agents.router_agent import RouterAgent

# Page configuration
st.set_page_config(
    page_title="Plant Based Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f8f4;
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
        logger.info("Initialized RouterAgent in session state")
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        logger.error(f"Agent initialization error: {e}")
        st.session_state.agent = None

# Page title
st.title("🌱 Plant Based Assistant")

st.write(
    """
Welcome to the Plant Based Assistant! I'm here to help you with:

- ✓ **Ingredient Analysis** - Check if ingredients are vegan
- 🔄 **Vegan Alternatives** - Find substitutions for non-vegan ingredients
- 🍽️ **Recipe Recommendations** - Discover recipes based on your ingredients
- 📊 **Nutrition Information** - Get detailed nutritional data and comparisons
- 📝 **Meal Planning** - Create shopping lists and meal plans

### How to use:
Simply type your question below, and I'll help you explore plant-based options!
"""
)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    st.subheader("User Preferences")

    # Dietary restrictions
    dietary_restrictions = st.multiselect(
        "Dietary Restrictions",
        ["None", "Gluten-free", "Nut allergy", "Soy allergy"],
        default=["None"],
    )

    # Cuisine preferences
    cuisines = st.multiselect(
        "Favorite Cuisines",
        ["Italian", "Asian", "Mexican", "Indian", "Mediterranean"],
        default=[],
    )

    # Protein goal
    protein_goal = st.slider("Daily Protein Goal (grams)", 30, 200, 50, step=10)

    # Save preferences
    if st.button("Save Preferences"):
        if st.session_state.agent:
            st.session_state.agent.update_user_profile(
                dietary_restrictions=dietary_restrictions,
                cuisine_preferences=cuisines,
                protein_goal_grams=float(protein_goal),
            )
            st.success("Preferences saved! ✓")

    st.divider()

    st.subheader("About")
    st.info(
        "Plant Based Assistant v0.1.0\n\n"
        "Built with LangChain, Streamlit, and integrated with:\n"
        "- USDA FoodData Central\n"
        "- Spoonacular Recipes\n"
        "- GPT-4o via Copilot"
    )

    # Clear conversation button
    if st.button("🔄 Clear Conversation"):
        st.session_state.agent.memory.conversation.clear()
        st.success("Conversation cleared!")

# Main chat area
st.header("Chat")

# Display conversation history
if st.session_state.agent:
    messages = st.session_state.agent.memory.conversation.get_context()

    chat_container = st.container()

    with chat_container:
        for msg in messages:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(msg["content"])

    # Input area
    st.divider()

    user_input = st.chat_input(
        "Ask about ingredients, recipes, nutrition, or meal planning...",
        key="user_input",
    )

    if user_input:
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    response = st.session_state.agent.process_query(user_input)
                    st.write(response)
                    st.session_state.conversation_state = (
                        st.session_state.agent.get_conversation_state()
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    logger.error(f"Error processing query: {e}")

else:
    st.error("⚠️ Agent failed to initialize. Check your environment variables and API configuration.")

logger.info("Streamlit UI loaded successfully")

