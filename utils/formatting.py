"""Response formatting utilities for Plant Based Assistant."""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


def format_ingredient_analysis(
    ingredient: str,
    vegan: bool,
    reason: str,
    alternatives: Optional[List[str]] = None,
    sources: Optional[List[str]] = None,
) -> str:
    """
    Format ingredient analysis into a readable response.

    Args:
        ingredient: Ingredient name
        vegan: Whether ingredient is vegan
        reason: Explanation for vegan status
        alternatives: List of vegan alternatives
        sources: List of data sources used

    Returns:
        Formatted response string
    """
    vegan_status = "✓ Vegan" if vegan else "✗ Not Vegan"
    response = f"**{ingredient.title()}**: {vegan_status}\n\n"
    response += f"**Why**: {reason}\n"

    if alternatives:
        response += f"\n**Vegan Alternatives**:\n"
        for i, alt in enumerate(alternatives[:5], 1):
            response += f"{i}. {alt}\n"

    if sources:
        response += f"\n*Data sources: {', '.join(sources)}*"

    return response


def format_recipe_result(
    title: str,
    diets: List[str],
    image_url: Optional[str] = None,
    nutrition: Optional[Dict[str, float]] = None,
    source_url: Optional[str] = None,
) -> str:
    """
    Format recipe information into a readable response.

    Args:
        title: Recipe title
        diets: List of diet tags (e.g., ['vegan', 'vegetarian'])
        image_url: URL to recipe image
        nutrition: Nutrition facts
        source_url: URL to full recipe

    Returns:
        Formatted response string
    """
    response = f"**{title}**\n"

    if diets:
        diet_badges = ", ".join([f"🌱 {d}" for d in diets])
        response += f"{diet_badges}\n"

    if nutrition:
        response += f"\n**Nutrition (per serving)**:\n"
        if "calories" in nutrition:
            response += f"- Calories: {nutrition['calories']:.0f} kcal\n"
        if "protein" in nutrition:
            response += f"- Protein: {nutrition['protein']:.1f}g\n"
        if "carbs" in nutrition:
            response += f"- Carbs: {nutrition['carbs']:.1f}g\n"
        if "fat" in nutrition:
            response += f"- Fat: {nutrition['fat']:.1f}g\n"

    if source_url:
        response += f"\n[View Full Recipe]({source_url})"

    return response


def format_nutrition_comparison(
    ingredient1: str,
    nutrition1: Dict[str, float],
    ingredient2: str,
    nutrition2: Dict[str, float],
) -> str:
    """
    Format nutritional comparison between two ingredients.

    Args:
        ingredient1: First ingredient name
        nutrition1: Nutrition facts for first ingredient
        ingredient2: Second ingredient name
        nutrition2: Nutrition facts for second ingredient

    Returns:
        Formatted comparison string
    """
    response = f"**Nutritional Comparison** (per 100g)\n\n"
    response += f"| Nutrient | {ingredient1.title()} | {ingredient2.title()} |\n"
    response += f"|----------|{'|'.join(['-----' for _ in range(2)])}\n"

    nutrients = ["calories", "protein", "carbs", "fat", "fiber"]
    for nutrient in nutrients:
        val1 = nutrition1.get(nutrient, 0)
        val2 = nutrition2.get(nutrient, 0)
        unit = "kcal" if nutrient == "calories" else "g"
        response += f"| {nutrient.title()} | {val1:.1f} {unit} | {val2:.1f} {unit} |\n"

    return response


def format_error_message(error: Exception) -> str:
    """
    Convert technical error to user-friendly message.

    Args:
        error: Exception object

    Returns:
        User-friendly error message
    """
    error_name = type(error).__name__

    # Map error types to friendly messages
    error_messages = {
        "IngredientNotFoundError": "I couldn't find information about that ingredient. Try asking about a different one or I can suggest popular vegan ingredients.",
        "APIRateLimitError": "I'm getting a lot of requests right now. Please wait a moment and try again.",
        "APITimeoutError": "I'm having trouble reaching my data sources. Please try again in a moment.",
        "APIConnectionError": "Connection issue with my data sources. I can help with general vegan knowledge.",
        "ValidationError": "Please rephrase your question. Make sure ingredient names are clear and complete.",
        "DataSourceError": "I'm experiencing technical difficulties. Please try a simpler query.",
    }

    return error_messages.get(error_name, f"Something went wrong: {str(error)}")


def format_source_attribution(*sources: str) -> str:
    """
    Format data source attribution.

    Args:
        *sources: Variable number of source names

    Returns:
        Formatted attribution string
    """
    unique_sources = list(dict.fromkeys(sources))  # Remove duplicates, preserve order
    if not unique_sources:
        return ""

    if len(unique_sources) == 1:
        return f"*Source: {unique_sources[0]}*"

    source_list = ", ".join(unique_sources)
    return f"*Sources: {source_list}*"


def format_conversation_summary(
    messages: List[Dict[str, str]],
    max_messages: int = 5,
) -> str:
    """
    Format conversation summary for context.

    Args:
        messages: List of message dicts with 'role' and 'content'
        max_messages: Maximum messages to include

    Returns:
        Formatted conversation summary
    """
    recent = messages[-max_messages:]
    summary = "**Recent Conversation**:\n"

    for msg in recent:
        role = "You" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "")[:100]  # Truncate long messages
        summary += f"- **{role}**: {content}...\n"

    return summary
