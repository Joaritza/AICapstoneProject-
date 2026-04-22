"""Nutrition analysis tools for Plant Based Assistant."""

import logging
from typing import Dict, Optional

from data_sources.usda_client import USDAFoodClient
from data_sources.cache_manager import CacheManager
from utils.exceptions import IngredientNotFoundError, ValidationError
from utils.validators import validate_ingredient_name, validate_serving_size
from utils.logging_util import log_tool_execution

logger = logging.getLogger(__name__)

# Initialize clients
usda_client = USDAFoodClient()
cache = CacheManager()


def get_ingredient_nutrition(
    ingredient: str,
    serving_size: float = 100,
    serving_unit: str = "grams",
) -> Dict[str, float]:
    """
    Get nutritional information for an ingredient.

    Returns nutrition facts for a specific serving size,
    with data sourced primarily from USDA API.

    Args:
        ingredient: Name of the ingredient
        serving_size: Amount (default 100)
        serving_unit: Unit of measurement (default 'grams')

    Returns:
        Dictionary with nutrition facts:
        {
            'ingredient': str,
            'serving_size': float,
            'serving_unit': str,
            'calories': float,
            'protein': float (grams),
            'carbs': float (grams),
            'fat': float (grams),
            'fiber': float (grams),
            'source': str
        }

    Raises:
        ValidationError: If inputs are invalid
        IngredientNotFoundError: If ingredient not found

    Example:
        >>> nutrition = get_ingredient_nutrition('milk', 240, 'milliliters')
        >>> nutrition['calories']
        152.0
        >>> nutrition['protein']
        7.7
    """
    try:
        # Validate inputs
        ingredient = validate_ingredient_name(ingredient)
        serving_size = validate_serving_size(serving_size)
        logger.debug(f"Getting nutrition for: {ingredient} ({serving_size}g)")

        # Check cache
        cache_key = f"{ingredient}_{serving_size}"
        cached = cache.get_nutrition(cache_key)
        if cached:
            logger.debug(f"Cache hit for nutrition: {cache_key}")
            return cached

        # Get ingredient info from USDA
        ingredient_info = usda_client.get_ingredient_info(ingredient)

        if not ingredient_info:
            raise IngredientNotFoundError(ingredient)

        food_data, nutrition_per_100g = ingredient_info

        # Scale nutrition for serving size
        scale_factor = serving_size / 100.0

        result = {
            "ingredient": ingredient.title(),
            "serving_size": serving_size,
            "serving_unit": serving_unit,
            "calories": nutrition_per_100g["calories"] * scale_factor,
            "protein": nutrition_per_100g["protein"] * scale_factor,
            "carbs": nutrition_per_100g["carbs"] * scale_factor,
            "fat": nutrition_per_100g["fat"] * scale_factor,
            "fiber": nutrition_per_100g["fiber"] * scale_factor,
            "source": "USDA FoodData Central",
        }

        # Cache result
        cache.cache_nutrition(cache_key, result)

        logger.info(f"Retrieved nutrition for: {ingredient}")

        log_tool_execution(
            logger,
            "get_ingredient_nutrition",
            {"ingredient": ingredient, "serving_size": serving_size},
            result,
        )

        return result

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        log_tool_execution(
            logger,
            "get_ingredient_nutrition",
            {"ingredient": ingredient, "serving_size": serving_size},
            error=str(e),
        )
        raise
    except IngredientNotFoundError as e:
        logger.warning(f"Ingredient not found: {e}")
        log_tool_execution(
            logger,
            "get_ingredient_nutrition",
            {"ingredient": ingredient},
            error=str(e),
        )
        raise


def compare_nutrition(
    ingredient1: str,
    ingredient2: str,
    serving_size: float = 100,
) -> Dict:
    """
    Compare nutritional values of two ingredients.

    Args:
        ingredient1: First ingredient
        ingredient2: Second ingredient
        serving_size: Serving size to use for comparison

    Returns:
        Dictionary comparing nutrition:
        {
            'ingredient1': dict (nutrition),
            'ingredient2': dict (nutrition),
            'differences': dict (protein_diff, calories_diff, etc.)
        }

    Raises:
        ValidationError: If inputs are invalid
        IngredientNotFoundError: If ingredients not found

    Example:
        >>> comparison = compare_nutrition('milk', 'soy milk')
        >>> comparison['differences']['protein_diff']
        2.5
    """
    try:
        logger.debug(f"Comparing nutrition: {ingredient1} vs {ingredient2}")

        # Get nutrition for both ingredients
        nutrition1 = get_ingredient_nutrition(ingredient1, serving_size)
        nutrition2 = get_ingredient_nutrition(ingredient2, serving_size)

        # Calculate differences
        differences = {
            "calories_diff": nutrition2["calories"] - nutrition1["calories"],
            "protein_diff": nutrition2["protein"] - nutrition1["protein"],
            "carbs_diff": nutrition2["carbs"] - nutrition1["carbs"],
            "fat_diff": nutrition2["fat"] - nutrition1["fat"],
            "fiber_diff": nutrition2["fiber"] - nutrition1["fiber"],
        }

        result = {
            "ingredient1": nutrition1,
            "ingredient2": nutrition2,
            "differences": differences,
        }

        log_tool_execution(
            logger,
            "compare_nutrition",
            {"ingredient1": ingredient1, "ingredient2": ingredient2},
            result,
        )

        return result

    except (ValidationError, IngredientNotFoundError) as e:
        logger.warning(f"Error comparing nutrition: {e}")
        log_tool_execution(
            logger,
            "compare_nutrition",
            {"ingredient1": ingredient1, "ingredient2": ingredient2},
            error=str(e),
        )
        raise


def analyze_nutrition_profile(nutrition: Dict[str, float]) -> Dict:
    """
    Analyze and categorize nutritional profile.

    Provides analysis of macronutrient composition and dietary characteristics.

    Args:
        nutrition: Nutrition dictionary (from get_ingredient_nutrition)

    Returns:
        Dictionary with analysis:
        {
            'macronutrient_breakdown': dict,
            'protein_per_calorie': float,
            'category': str,
            'health_score': float (0-100)
        }

    Example:
        >>> nutrition = get_ingredient_nutrition('tofu')
        >>> analysis = analyze_nutrition_profile(nutrition)
        >>> analysis['category']
        'High Protein Plant Source'
    """
    try:
        calories = nutrition.get("calories", 1)  # Avoid division by zero
        protein = nutrition.get("protein", 0)
        carbs = nutrition.get("carbs", 0)
        fat = nutrition.get("fat", 0)

        # Calculate macronutrient percentages
        total_macro_calories = (protein * 4) + (carbs * 4) + (fat * 9)

        if total_macro_calories == 0:
            protein_pct = carbs_pct = fat_pct = 0
        else:
            protein_pct = ((protein * 4) / total_macro_calories) * 100
            carbs_pct = ((carbs * 4) / total_macro_calories) * 100
            fat_pct = ((fat * 9) / total_macro_calories) * 100

        # Categorize based on macronutrient profile
        category = "Balanced"

        if protein_pct > 30:
            category = "High Protein"
        elif carbs_pct > 50:
            category = "High Carb"
        elif fat_pct > 40:
            category = "High Fat"

        # Calculate simple health score (simplified metric)
        health_score = min(
            100,
            (protein * 2) + (nutrition.get("fiber", 0) * 3) - (calories / 2),
        )

        result = {
            "macronutrient_breakdown": {
                "protein_percent": round(protein_pct, 1),
                "carbs_percent": round(carbs_pct, 1),
                "fat_percent": round(fat_pct, 1),
            },
            "protein_per_calorie": round(protein / max(calories, 1), 2),
            "category": category,
            "health_score": round(max(0, min(100, health_score)), 1),
        }

        return result

    except Exception as e:
        logger.error(f"Error analyzing nutrition: {e}")
        raise
