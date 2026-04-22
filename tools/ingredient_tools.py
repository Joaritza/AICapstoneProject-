"""Ingredient analysis tools for Plant Based Assistant."""

import logging
from typing import Dict, List, Optional, Tuple

from data_sources.usda_client import USDAFoodClient
from data_sources.spoonacular_client import SpoonacularRecipeClient
from data_sources.vegan_database import VeganDatabaseClient
from data_sources.cache_manager import CacheManager
from utils.exceptions import IngredientNotFoundError, ValidationError
from utils.validators import validate_ingredient_name
from utils.logging_util import log_tool_execution

logger = logging.getLogger(__name__)

# Initialize clients
usda_client = USDAFoodClient()
spoonacular_client = SpoonacularRecipeClient()
vegan_db = VeganDatabaseClient()
cache = CacheManager()


def check_ingredient_vegan_status(ingredient: str) -> Dict:
    """
    Check if an ingredient is vegan with detailed explanation.

    Queries multiple data sources (local database, Spoonacular) and synthesizes
    information to provide vegan status and reasoning.

    Args:
        ingredient: Name of the ingredient

    Returns:
        Dictionary with structure:
        {
            'name': str,
            'vegan': bool,
            'reason': str,
            'sources': list[str],
            'alternatives': list[str] (if not vegan)
        }

    Raises:
        ValidationError: If ingredient name is invalid
        IngredientNotFoundError: If ingredient not found in any database

    Example:
        >>> result = check_ingredient_vegan_status('milk')
        >>> result['vegan']
        False
        >>> result['alternatives']
        ['Oat Milk', 'Soy Milk', ...]
    """
    try:
        # Validate input
        ingredient = validate_ingredient_name(ingredient)
        logger.debug(f"Checking vegan status for: {ingredient}")

        # Check cache first
        cached = cache.get_ingredient(ingredient)
        if cached:
            logger.debug(f"Cache hit for: {ingredient}")
            return cached

        result = {
            "name": ingredient.title(),
            "vegan": None,
            "reason": "",
            "sources": [],
            "alternatives": [],
        }

        # Check local vegan database first (fastest, always available)
        local_data = vegan_db.get_ingredient(ingredient)

        if local_data:
            result["vegan"] = local_data["vegan"]
            result["reason"] = local_data.get("reason", "")
            result["sources"].append("Local Vegan Database")

            # Add alternatives if available
            if local_data.get("alternatives"):
                result["alternatives"] = [
                    alt.get("name", alt) 
                    for alt in local_data["alternatives"]
                ]

            # Cache result
            cache.cache_ingredient(ingredient, result)

            log_tool_execution(
                logger,
                "check_ingredient_vegan_status",
                {"ingredient": ingredient},
                result,
            )

            return result

        # Try Spoonacular API for additional info
        try:
            recipes = spoonacular_client.search_recipes(ingredient, number=1)

            if recipes:
                # This ingredient exists in recipe database
                recipe = recipes[0]
                diets = recipe.get("diets", [])

                if "vegan" in diets:
                    result["vegan"] = True
                    result["reason"] = f"Found in vegan recipes on Spoonacular"
                    result["sources"].append("Spoonacular Recipes")
                elif "vegetarian" in diets:
                    result["vegan"] = False
                    result["reason"] = "Found in vegetarian (not vegan) recipes"
                    result["sources"].append("Spoonacular Recipes")
                else:
                    # Unknown from recipes, but ingredient exists
                    result["vegan"] = None
                    result["reason"] = "Ingredient found but vegan status unclear"
                    result["sources"].append("Spoonacular")

                cache.cache_ingredient(ingredient, result)
                log_tool_execution(
                    logger,
                    "check_ingredient_vegan_status",
                    {"ingredient": ingredient},
                    result,
                )

                return result

        except Exception as e:
            logger.debug(f"Spoonacular API error: {e}")

        # If no data found anywhere, suggest similar ingredients
        similar = vegan_db.search_similar(ingredient, limit=3)

        if similar:
            alternatives = [item["name"] for item in similar]
            raise IngredientNotFoundError(ingredient)

        raise IngredientNotFoundError(ingredient)

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        log_tool_execution(
            logger,
            "check_ingredient_vegan_status",
            {"ingredient": ingredient},
            error=str(e),
        )
        raise
    except IngredientNotFoundError as e:
        logger.warning(f"Ingredient not found: {e}")
        log_tool_execution(
            logger,
            "check_ingredient_vegan_status",
            {"ingredient": ingredient},
            error=str(e),
        )
        raise


def get_vegan_alternatives(ingredient: str, limit: int = 5) -> List[Dict]:
    """
    Get vegan alternatives for an ingredient.

    Returns top alternatives with nutritional matching and explanations.

    Args:
        ingredient: Name of the ingredient to replace
        limit: Maximum number of alternatives to return

    Returns:
        List of alternatives with structure:
        [
            {
                'alternative': str,
                'reason': str,
                'nutritional_match': float (0-1),
                'use_cases': str
            },
            ...
        ]

    Raises:
        ValidationError: If ingredient name is invalid
        IngredientNotFoundError: If ingredient not found

    Example:
        >>> alts = get_vegan_alternatives('milk')
        >>> alts[0]['alternative']
        'Soy Milk'
        >>> alts[0]['nutritional_match']
        0.95
    """
    try:
        # Validate input
        ingredient = validate_ingredient_name(ingredient)
        logger.debug(f"Getting vegan alternatives for: {ingredient}")

        # First check if ingredient is already vegan
        vegan_status = check_ingredient_vegan_status(ingredient)

        if vegan_status.get("vegan"):
            return [
                {
                    "alternative": ingredient.title(),
                    "reason": "Already vegan - no substitution needed",
                    "nutritional_match": 1.0,
                    "use_cases": "Use as-is",
                }
            ]

        # Get alternatives from local database
        local_data = vegan_db.get_ingredient(ingredient)
        alternatives = []

        if local_data and local_data.get("alternatives"):
            for alt in local_data["alternatives"][:limit]:
                alternatives.append(
                    {
                        "alternative": alt.get("name", alt),
                        "reason": alt.get("explanation", "Vegan alternative"),
                        "nutritional_match": 0.8,  # Default estimate
                        "use_cases": "See recipe suggestions",
                    }
                )

        if not alternatives:
            # Fallback: suggest common plant-based alternatives
            fallback_alts = {
                "milk": [
                    "Soy Milk",
                    "Oat Milk",
                    "Almond Milk",
                    "Coconut Milk",
                    "Cashew Milk",
                ],
                "egg": [
                    "Flax Egg",
                    "Aquafaba",
                    "Applesauce",
                    "Mashed Banana",
                ],
                "butter": [
                    "Vegan Butter",
                    "Coconut Oil",
                    "Olive Oil",
                    "Tahini",
                ],
                "cheese": [
                    "Nutritional Yeast",
                    "Cashew Cheese",
                    "Tofu Cheese",
                    "Vegan Mozzarella",
                ],
            }

            for key, alts_list in fallback_alts.items():
                if key in ingredient.lower():
                    for alt_name in alts_list[:limit]:
                        alternatives.append(
                            {
                                "alternative": alt_name,
                                "reason": f"Common vegan alternative to {ingredient}",
                                "nutritional_match": 0.75,
                                "use_cases": "Popular choice",
                            }
                        )
                    break

        log_tool_execution(
            logger,
            "get_vegan_alternatives",
            {"ingredient": ingredient, "limit": limit},
            alternatives,
        )

        return alternatives[:limit]

    except (ValidationError, IngredientNotFoundError) as e:
        logger.warning(f"Error getting alternatives: {e}")
        log_tool_execution(
            logger,
            "get_vegan_alternatives",
            {"ingredient": ingredient},
            error=str(e),
        )
        raise
