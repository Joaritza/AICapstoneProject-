"""Response synthesis and formatting for Plant Based Assistant."""

import logging
from typing import Dict, List, Any, Optional

from utils.formatting import (
    format_ingredient_analysis,
    format_recipe_result,
    format_error_message,
    format_source_attribution,
)

logger = logging.getLogger(__name__)


class ResponseSynthesizer:
    """Synthesizes tool outputs into coherent, multi-source responses."""

    def __init__(self):
        """Initialize response synthesizer."""
        self.include_sources = True
        self.explain_reasoning = True
        self.provide_alternatives = True
        self.suggest_recipes = True
        self.cite_nutrition = True

    def synthesize_ingredient_analysis(
        self,
        ingredient: str,
        vegan_status: Dict,
        alternatives: Optional[List[Dict]] = None,
        recipes: Optional[List[Dict]] = None,
    ) -> str:
        """
        Synthesize ingredient analysis from multiple tool outputs.

        Args:
            ingredient: Ingredient name
            vegan_status: Output from check_ingredient_vegan_status()
            alternatives: Output from get_vegan_alternatives()
            recipes: List of recipes using alternative

        Returns:
            Formatted response string
        """
        response_parts = []

        # 1. Vegan status with reasoning
        vegan_status_text = format_ingredient_analysis(
            ingredient=vegan_status.get("name", ingredient),
            vegan=vegan_status.get("vegan", False),
            reason=vegan_status.get("reason", ""),
            alternatives=vegan_status.get("alternatives", []),
            sources=vegan_status.get("sources", []) if self.include_sources else None,
        )
        response_parts.append(vegan_status_text)

        # 2. Detailed alternatives if available
        if alternatives and self.provide_alternatives:
            response_parts.append("\n### Vegan Alternatives\n")

            for i, alt in enumerate(alternatives[:3], 1):
                alt_text = f"{i}. **{alt.get('alternative', '')}**"

                if alt.get("reason"):
                    alt_text += f"\n   - {alt['reason']}"

                if alt.get("nutritional_match") and self.cite_nutrition:
                    match = alt.get("nutritional_match", 0)
                    alt_text += f"\n   - Nutritional match: {match:.0%}"

                response_parts.append(alt_text)

        # 3. Recipe suggestions if available
        if recipes and self.suggest_recipes:
            response_parts.append("\n### Recipe Ideas with Alternatives\n")

            for recipe in recipes[:2]:
                recipe_title = recipe.get("title", "Recipe")
                response_parts.append(f"- {recipe_title}")

                if recipe.get("diets"):
                    response_parts.append(f"  *{', '.join(recipe['diets'])}*")

        # 4. Source attribution
        all_sources = set()
        if vegan_status.get("sources"):
            all_sources.update(vegan_status["sources"])

        if all_sources and self.include_sources:
            response_parts.append(f"\n{format_source_attribution(*all_sources)}")

        return "".join(response_parts)

    def synthesize_recipe_recommendation(
        self,
        query: str,
        recipes: List[Dict],
        nutrition_analysis: Optional[Dict] = None,
    ) -> str:
        """
        Synthesize recipe recommendations.

        Args:
            query: User's search query
            recipes: List of recipe dicts
            nutrition_analysis: Nutritional analysis if available

        Returns:
            Formatted recommendation text
        """
        response_parts = [f"## Recipes for: {query}\n"]

        if not recipes:
            return "No recipes found matching your criteria."

        # Display top recipes
        for i, recipe in enumerate(recipes[:3], 1):
            diets = recipe.get("diets", [])
            title = recipe.get("title", "Recipe")

            response_parts.append(f"### {i}. {title}")

            if diets:
                response_parts.append(f"**Dietary Tags:** {', '.join(diets)}\n")

            used_count = recipe.get("usedIngredientCount", 0)
            missed_count = recipe.get("missedIngredientCount", 0)

            if used_count:
                response_parts.append(f"- Uses {used_count} ingredients you have")

            if missed_count:
                response_parts.append(f"- Missing {missed_count} ingredients")

            response_parts.append("")

        # Add nutritional summary if available
        if nutrition_analysis:
            response_parts.append("### Nutritional Summary")
            response_parts.append(f"Average calories: {nutrition_analysis.get('avg_calories', 'N/A')}\n")

        return "\n".join(response_parts)

    def synthesize_nutrition_comparison(
        self,
        ingredient1: str,
        ingredient2: str,
        nutrition1: Dict,
        nutrition2: Dict,
        recommendation: Optional[str] = None,
    ) -> str:
        """
        Synthesize nutritional comparison.

        Args:
            ingredient1: First ingredient
            ingredient2: Second ingredient
            nutrition1: Nutrition facts for ingredient1
            nutrition2: Nutrition facts for ingredient2
            recommendation: Optional recommendation

        Returns:
            Formatted comparison
        """
        response = f"## Nutritional Comparison\n\n"
        response += f"**{ingredient1.title()}** vs **{ingredient2.title()}**\n\n"

        # Create comparison table
        response += "| Nutrient | " + ingredient1.title() + " | " + ingredient2.title() + " |\n"
        response += "|----------|" + "-" * (len(ingredient1) + 2) + "|" + "-" * (len(ingredient2) + 2) + "|\n"

        nutrients = ["calories", "protein", "carbs", "fat", "fiber"]
        units = {"calories": "kcal", "protein": "g", "carbs": "g", "fat": "g", "fiber": "g"}

        for nutrient in nutrients:
            val1 = nutrition1.get(nutrient, 0)
            val2 = nutrition2.get(nutrient, 0)
            unit = units.get(nutrient, "")

            response += f"| {nutrient.title()} | {val1:.1f}{unit} | {val2:.1f}{unit} |\n"

        # Add recommendation
        if recommendation:
            response += f"\n**Recommendation:** {recommendation}"

        # Add analysis
        protein_diff = nutrition2.get("protein", 0) - nutrition1.get("protein", 0)

        if abs(protein_diff) > 2:
            direction = "more" if protein_diff > 0 else "less"
            response += f"\n\n**Note:** {ingredient2.title()} has {abs(protein_diff):.1f}g {direction} protein per serving."

        return response

    def synthesize_meal_plan(
        self,
        recipes: List[Dict],
        shopping_list: Optional[Dict] = None,
    ) -> str:
        """
        Synthesize meal plan recommendations.

        Args:
            recipes: List of recipes
            shopping_list: Shopping list dict

        Returns:
            Formatted meal plan
        """
        response = f"## Meal Plan\n\n"

        # List recipes
        response += "**Recipes included:**\n"

        for i, recipe in enumerate(recipes[:7], 1):
            title = recipe.get("title", "Recipe")
            response += f"{i}. {title}\n"

        # Shopping list summary
        if shopping_list:
            ingredient_count = shopping_list.get("ingredient_count", 0)
            response += f"\n**Shopping List:** {ingredient_count} unique ingredients needed\n"

            # List first 10 ingredients
            ingredients = shopping_list.get("total_ingredients", [])[:10]

            if ingredients:
                response += "\nKey ingredients:\n"

                for ing in ingredients:
                    name = ing.get("name", "")
                    amount = ing.get("amount", 0)
                    unit = ing.get("unit", "")

                    response += f"- {amount} {unit} {name}\n"

        return response

    def synthesize_error_response(self, error: Exception) -> str:
        """
        Synthesize user-friendly error message.

        Args:
            error: Exception that occurred

        Returns:
            User-friendly error message
        """
        user_message = format_error_message(error)

        # Add helpful suggestions
        error_type = type(error).__name__

        suggestions = {
            "IngredientNotFoundError": "Try asking about common ingredients like milk, eggs, honey, or butter.",
            "RecipeNotFoundError": "Try a different search term or specific ingredient.",
            "APIRateLimitError": "Please wait a few moments and try again.",
            "APITimeoutError": "The request took too long. Please try a simpler query.",
        }

        suggestion = suggestions.get(error_type, "")

        if suggestion:
            user_message += f"\n\n💡 {suggestion}"

        return user_message

    def format_multi_source_response(
        self,
        tool_results: Dict[str, Any],
    ) -> str:
        """
        Format response combining multiple tool results.

        Args:
            tool_results: Dictionary with tool outputs

        Returns:
            Synthesized response
        """
        response = ""

        # Determine what kind of response to build
        if "vegan_status" in tool_results:
            response = self.synthesize_ingredient_analysis(
                ingredient=tool_results.get("ingredient", ""),
                vegan_status=tool_results["vegan_status"],
                alternatives=tool_results.get("alternatives"),
                recipes=tool_results.get("recipes"),
            )

        elif "recipes" in tool_results:
            response = self.synthesize_recipe_recommendation(
                query=tool_results.get("query", ""),
                recipes=tool_results["recipes"],
                nutrition_analysis=tool_results.get("nutrition"),
            )

        elif "nutrition_comparison" in tool_results:
            response = self.synthesize_nutrition_comparison(
                ingredient1=tool_results.get("ingredient1", ""),
                ingredient2=tool_results.get("ingredient2", ""),
                nutrition1=tool_results.get("nutrition1", {}),
                nutrition2=tool_results.get("nutrition2", {}),
            )

        return response if response else "Unable to generate response from available data."
