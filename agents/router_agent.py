"""Router agent for Plant Based Assistant - main orchestrator."""

import logging
import json
from typing import Dict, List, Any, Optional

from langchain_openai import ChatOpenAI
from langchain.tools import tool

from config.settings import settings
from agents.memory_manager import MemoryManager
from agents.response_synthesizer import ResponseSynthesizer

logger = logging.getLogger(__name__)


class RouterAgent:
    """
    Main routing agent for Plant Based Assistant.

    Routes queries to appropriate tools and synthesizes responses.
    """

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        """
        Initialize router agent.

        Args:
            memory_manager: Optional MemoryManager instance (creates new if None)
        """
        self.memory = memory_manager or MemoryManager()
        self.synthesizer = ResponseSynthesizer()

        # Initialize LLM with GitHub token for GPT-4o access via GitHub Models
        # Using GitHub's inference endpoint with GitHub personal access token
        self.llm = ChatOpenAI(
            model="openai/gpt-4o",
            base_url="https://models.github.ai/inference",
            api_key=settings.GITHUB_TOKEN,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )

        # Define tools
        self.tools = self._define_tools()
        self.tool_map = self._create_tool_map()

        logger.info(
            f"Initialized RouterAgent with model: {settings.LLM_MODEL}"
        )

    def _define_tools(self) -> List:
        """
        Define LangChain tools for agent to use.

        Returns:
            List of LangChain tools
        """

        @tool
        def check_ingredient_vegan_status(ingredient: str) -> Dict[str, Any]:
            """
            Check if an ingredient is vegan with detailed explanation.

            Args:
                ingredient: Name of the ingredient

            Returns:
                Dictionary with vegan status, reason, and alternatives
            """
            from tools.ingredient_tools import check_ingredient_vegan_status as check_tool

            try:
                result = check_tool(ingredient)
                return result
            except Exception as e:
                logger.error(f"Tool error: {e}")
                return {"error": str(e), "ingredient": ingredient}

        @tool
        def get_vegan_alternatives(ingredient: str, limit: int = 5) -> List[Dict]:
            """
            Get vegan alternatives for a non-vegan ingredient.

            Args:
                ingredient: Ingredient to replace
                limit: Maximum alternatives to return

            Returns:
                List of vegan alternative suggestions
            """
            from tools.ingredient_tools import get_vegan_alternatives as alt_tool

            try:
                result = alt_tool(ingredient, limit=limit)
                return result
            except Exception as e:
                logger.error(f"Tool error: {e}")
                return {"error": str(e)}

        @tool
        def search_recipes_by_ingredients(
            ingredients: str,
            diet_type: Optional[str] = None,
            limit: int = 10,
        ) -> List[Dict]:
            """
            Search for recipes using available ingredients.

            Args:
                ingredients: Comma-separated list of ingredient names
                diet_type: Optional diet filter (vegan, vegetarian, gluten-free)
                limit: Maximum recipes to return

            Returns:
                List of recipe summaries
            """
            from tools.recipe_tools import search_recipes_by_ingredients as search_tool

            try:
                # Parse comma-separated string
                ingredient_list = [i.strip() for i in ingredients.split(",")]

                dietary_filters = {}
                if diet_type:
                    dietary_filters = {
                        "vegan": "vegan" in diet_type.lower(),
                        "vegetarian": "vegetarian" in diet_type.lower(),
                        "gluten_free": "gluten" in diet_type.lower(),
                    }

                result = search_tool(
                    ingredients=ingredient_list,
                    dietary_filters=dietary_filters if dietary_filters else None,
                    limit=limit,
                )
                return result
            except Exception as e:
                logger.error(f"Tool error: {e}")
                return {"error": str(e)}

        @tool
        def get_recipe_details(recipe_id: int) -> Dict[str, Any]:
            """
            Get detailed information for a specific recipe.

            Args:
                recipe_id: Spoonacular recipe ID

            Returns:
                Complete recipe information
            """
            from tools.recipe_tools import get_recipe_details as detail_tool

            try:
                result = detail_tool(recipe_id)
                return result
            except Exception as e:
                logger.error(f"Tool error: {e}")
                return {"error": str(e)}

        @tool
        def get_ingredient_nutrition(
            ingredient: str,
            serving_size: float = 100,
            serving_unit: str = "grams",
        ) -> Dict[str, float]:
            """
            Get nutritional information for an ingredient.

            Args:
                ingredient: Ingredient name
                serving_size: Serving size (default 100)
                serving_unit: Unit of measurement

            Returns:
                Nutrition facts dictionary
            """
            from tools.nutrition_tools import get_ingredient_nutrition as nutrition_tool

            try:
                result = nutrition_tool(
                    ingredient=ingredient,
                    serving_size=serving_size,
                    serving_unit=serving_unit,
                )
                return result
            except Exception as e:
                logger.error(f"Tool error: {e}")
                return {"error": str(e)}

        @tool
        def generate_shopping_list(
            recipe_ids: str,
            servings: int = 1,
        ) -> Dict[str, Any]:
            """
            Generate shopping list from multiple recipes.

            Args:
                recipe_ids: Comma-separated list of Spoonacular recipe IDs
                servings: Number of servings

            Returns:
                Aggregated shopping list
            """
            from tools.meal_planning_tools import generate_shopping_list as shopping_tool

            try:
                # Parse comma-separated IDs
                ids = [int(id.strip()) for id in recipe_ids.split(",")]

                result = shopping_tool(recipe_ids=ids, servings=servings)
                return result
            except Exception as e:
                logger.error(f"Tool error: {e}")
                return {"error": str(e)}

        return [
            check_ingredient_vegan_status,
            get_vegan_alternatives,
            search_recipes_by_ingredients,
            get_recipe_details,
            get_ingredient_nutrition,
            generate_shopping_list,
        ]

    def _create_tool_map(self) -> Dict[str, callable]:
        """
        Create a mapping of tool names to functions.

        Returns:
            Dictionary mapping tool names to functions
        """
        return {tool.name: tool for tool in self.tools}

    def process_query(self, user_input: str) -> str:
        """
        Process user query and generate response.

        Args:
            user_input: User's message

        Returns:
            Assistant response
        """
        try:
            logger.info(f"Processing query: {user_input[:100]}")

            # Add to conversation memory
            self.memory.add_user_message(user_input)

            # Get messages for LLM (includes system prompt and history)
            messages = self.memory.get_messages_for_llm()

            # Create system prompt with tool definitions
            system_prompt = self._build_system_prompt()

            # Send to LLM
            response_text = self._call_llm_with_tools(user_input, messages, system_prompt)

            # Add to conversation memory
            self.memory.add_assistant_message(response_text)

            logger.info(f"Generated response ({len(response_text)} chars)")

            return response_text

        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)

            error_response = self.synthesizer.synthesize_error_response(e)
            self.memory.add_assistant_message(error_response)

            return error_response

    def _build_system_prompt(self) -> str:
        """
        Build system prompt with tool descriptions.

        Returns:
            System prompt string
        """
        prompt = (
            "You are the Plant Based Assistant, a helpful chatbot specialized in vegan cooking and nutrition.\n\n"
            "Your role is to:\n"
            "1. Analyze ingredients for vegan status and provide detailed explanations\n"
            "2. Suggest vegan alternatives for non-vegan ingredients\n"
            "3. Recommend recipes based on available ingredients or preferences\n"
            "4. Provide nutritional information and comparisons\n"
            "5. Help with meal planning and shopping lists\n\n"
            "When responding:\n"
            "- Use the available tools to gather accurate information\n"
            "- Explain your reasoning clearly\n"
            "- Cite your sources (USDA, Spoonacular, local database)\n"
            "- Consider user preferences from conversation history\n"
            "- Be helpful and encouraging about plant-based eating\n\n"
            "Available tools:\n"
        )

        for tool in self.tools:
            prompt += f"- {tool.name}: {tool.description}\n"

        return prompt

    def _call_llm_with_tools(
        self,
        user_input: str,
        messages: List[Dict],
        system_prompt: str
    ) -> str:
        """
        Call LLM with tool context and generate response.

        Args:
            user_input: User's message
            messages: Conversation history
            system_prompt: System prompt with tool info

        Returns:
            LLM response
        """
        # Format messages for LLM
        formatted_messages = []

        # Add system prompt
        formatted_messages.append({
            "role": "system",
            "content": system_prompt
        })

        # Add conversation history (skip the system message from messages list)
        for msg in messages:
            if msg["role"] != "system":
                formatted_messages.append(msg)

        # For now, use simple LLM call without tool execution
        # In future, can implement more sophisticated tool calling
        response = self.llm.invoke(formatted_messages)

        if hasattr(response, "content"):
            return response.content
        else:
            return str(response)

    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state."""
        return self.memory.export_state()

    def restore_conversation_state(self, state: Dict[str, Any]) -> None:
        """Restore conversation from saved state."""
        self.memory.import_state(state)
        logger.info("Restored conversation state")

    def update_user_profile(self, **kwargs) -> None:
        """Update user profile information."""
        self.memory.update_user_profile(**kwargs)
        logger.info(f"Updated user profile: {list(kwargs.keys())}")

