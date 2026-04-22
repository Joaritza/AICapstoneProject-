"""Meal planning and shopping list tools for Plant Based Assistant."""

import logging
from typing import Dict, List, Optional

from tools.recipe_tools import get_recipe_details
from utils.exceptions import RecipeNotFoundError, ValidationError
from utils.validators import validate_recipe_id
from utils.logging_util import log_tool_execution

logger = logging.getLogger(__name__)


def generate_shopping_list(recipe_ids: List[int], servings: int = 1) -> Dict:
    """
    Generate aggregated shopping list from multiple recipes.

    Combines ingredients from multiple recipes into a consolidated list,
    accounting for overlapping ingredients and scaling by servings.

    Args:
        recipe_ids: List of Spoonacular recipe IDs
        servings: Number of servings to prepare

    Returns:
        Dictionary with aggregated ingredients:
        {
            'recipes': list[str],
            'total_ingredients': list[dict],
            'estimated_cost': float (optional),
            'dietary_info': dict
        }

    Raises:
        ValidationError: If recipe IDs are invalid
        RecipeNotFoundError: If any recipe not found

    Example:
        >>> shopping_list = generate_shopping_list([594736, 123456], servings=2)
        >>> shopping_list['total_ingredients'][0]
        {'name': 'Pasta', 'amount': 2, 'unit': 'pounds', 'sources': [0, 1]}
    """
    try:
        logger.debug(f"Generating shopping list for {len(recipe_ids)} recipes")

        # Validate recipe IDs
        validated_ids = []
        for rid in recipe_ids:
            try:
                validated_ids.append(validate_recipe_id(rid))
            except ValidationError as e:
                logger.warning(f"Invalid recipe ID {rid}: {e}")
                raise

        # Get recipes
        recipes = []
        recipe_titles = []

        for recipe_id in validated_ids:
            try:
                recipe = get_recipe_details(recipe_id)
                recipes.append(recipe)
                recipe_titles.append(recipe.get("title", f"Recipe {recipe_id}"))
            except RecipeNotFoundError as e:
                logger.warning(f"Recipe not found: {recipe_id}")
                raise

        # Aggregate ingredients
        ingredient_map = {}  # Normalized name -> {amount, unit, original_names, recipes}

        for recipe_idx, recipe in enumerate(recipes):
            extended_ingredients = recipe.get("extendedIngredients", [])

            for ingredient in extended_ingredients:
                name = ingredient.get("name", "").lower()
                amount = ingredient.get("amount", 0)
                unit = ingredient.get("unit", "")

                # Scale by servings and recipe servings
                recipe_servings = recipe.get("servings", 1)
                scaled_amount = (amount / recipe_servings) * servings

                if name not in ingredient_map:
                    ingredient_map[name] = {
                        "name": ingredient.get("original", name),
                        "amount": scaled_amount,
                        "unit": unit,
                        "sources": [recipe_idx],
                    }
                else:
                    # Aggregate amounts if same unit or no unit
                    if ingredient_map[name]["unit"] == unit or not unit:
                        ingredient_map[name]["amount"] += scaled_amount
                        if recipe_idx not in ingredient_map[name]["sources"]:
                            ingredient_map[name]["sources"].append(recipe_idx)

        # Convert to list
        total_ingredients = [
            {
                "name": ing_data["name"],
                "amount": round(ing_data["amount"], 2),
                "unit": ing_data["unit"],
                "sources": [recipe_titles[i] for i in ing_data["sources"]],
            }
            for ing_data in ingredient_map.values()
        ]

        # Sort by name
        total_ingredients.sort(key=lambda x: x["name"])

        # Get dietary info from recipes
        all_diets = set()
        for recipe in recipes:
            diets = recipe.get("diets", [])
            all_diets.update(diets)

        result = {
            "recipes": recipe_titles,
            "total_ingredients": total_ingredients,
            "ingredient_count": len(total_ingredients),
            "servings": servings,
            "dietary_info": {
                "diets": list(all_diets),
                "is_vegan": "vegan" in all_diets,
                "is_vegetarian": "vegetarian" in all_diets,
            },
        }

        logger.info(f"Generated shopping list with {len(total_ingredients)} items")

        log_tool_execution(
            logger,
            "generate_shopping_list",
            {"recipe_count": len(recipe_ids), "servings": servings},
            result,
        )

        return result

    except (ValidationError, RecipeNotFoundError) as e:
        logger.warning(f"Error generating shopping list: {e}")
        log_tool_execution(
            logger,
            "generate_shopping_list",
            {"recipe_ids": recipe_ids},
            error=str(e),
        )
        raise


def create_meal_plan(
    recipes: List[Dict],
    days: int = 7,
    meals_per_day: int = 3,
) -> Dict:
    """
    Create a structured meal plan from recipes.

    Organizes recipes into a daily meal plan structure.

    Args:
        recipes: List of recipe dictionaries
        days: Number of days to plan for
        meals_per_day: Meals per day (breakfast, lunch, dinner)

    Returns:
        Dictionary with meal plan:
        {
            'meal_plan': dict (day_1, day_2, etc.),
            'total_recipes': int,
            'shopping_list': dict,
            'nutritional_summary': dict
        }

    Example:
        >>> plan = create_meal_plan([recipe1, recipe2], days=3)
        >>> plan['meal_plan']['day_1']['lunch']
        'Vegan Pasta'
    """
    try:
        logger.debug(f"Creating meal plan for {days} days")

        if not recipes:
            raise ValidationError("recipes", "Must provide at least one recipe")

        if days < 1 or days > 365:
            raise ValidationError("days", "Days must be between 1 and 365")

        # Create meal plan structure
        meal_plan = {}
        meal_types = ["breakfast", "lunch", "dinner"]

        recipe_idx = 0
        for day in range(1, days + 1):
            meal_plan[f"day_{day}"] = {}

            for meal_idx in range(meals_per_day):
                meal_type = meal_types[meal_idx] if meal_idx < len(meal_types) else f"meal_{meal_idx + 1}"
                recipe = recipes[recipe_idx % len(recipes)]
                meal_plan[f"day_{day}"][meal_type] = recipe.get("title", "Recipe")
                recipe_idx += 1

        result = {
            "meal_plan": meal_plan,
            "total_recipes": len(recipes),
            "days": days,
            "meals_per_day": meals_per_day,
        }

        logger.info(f"Created meal plan for {days} days")

        log_tool_execution(
            logger,
            "create_meal_plan",
            {"recipe_count": len(recipes), "days": days},
            result,
        )

        return result

    except ValidationError as e:
        logger.warning(f"Error creating meal plan: {e}")
        log_tool_execution(
            logger,
            "create_meal_plan",
            {"recipe_count": len(recipes)},
            error=str(e),
        )
        raise


def estimate_prep_time(recipes: List[Dict]) -> Dict:
    """
    Estimate total prep and cook time for recipes.

    Args:
        recipes: List of recipe dictionaries

    Returns:
        Dictionary with time estimates:
        {
            'total_prep_minutes': int,
            'total_cook_minutes': int,
            'total_minutes': int,
            'recipes_breakdown': list
        }

    Example:
        >>> times = estimate_prep_time([recipe1, recipe2])
        >>> times['total_minutes']
        125
    """
    try:
        total_prep = 0
        total_cook = 0
        breakdown = []

        for recipe in recipes:
            prep_time = recipe.get("preparationMinutes", 10)
            cook_time = recipe.get("cookingMinutes", 20)
            total_time = prep_time + cook_time

            total_prep += prep_time
            total_cook += cook_time

            breakdown.append(
                {
                    "recipe": recipe.get("title", "Recipe"),
                    "prep_minutes": prep_time,
                    "cook_minutes": cook_time,
                    "total_minutes": total_time,
                }
            )

        result = {
            "total_prep_minutes": total_prep,
            "total_cook_minutes": total_cook,
            "total_minutes": total_prep + total_cook,
            "recipes_breakdown": breakdown,
        }

        return result

    except Exception as e:
        logger.error(f"Error estimating prep time: {e}")
        raise
