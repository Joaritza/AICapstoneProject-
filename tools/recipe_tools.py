"""Recipe search and management tools for Plant Based Assistant."""

import logging
from typing import Dict, List, Optional

from data_sources.spoonacular_client import SpoonacularRecipeClient
from data_sources.cache_manager import CacheManager
from utils.exceptions import RecipeNotFoundError, ValidationError
from utils.validators import validate_ingredients_list, validate_recipe_id
from utils.logging_util import log_tool_execution

logger = logging.getLogger(__name__)

# Initialize clients
spoonacular_client = SpoonacularRecipeClient()
cache = CacheManager()


def search_recipes_by_ingredients(
    ingredients: List[str],
    dietary_filters: Optional[Dict[str, bool]] = None,
    limit: int = 10,
) -> List[Dict]:
    """
    Search for recipes using available ingredients.

    Finds recipes that can be made with the provided ingredients,
    optionally filtering by dietary preferences.

    Args:
        ingredients: List of available ingredients
        dietary_filters: Optional dict with filters:
            - vegan: bool
            - vegetarian: bool
            - gluten_free: bool
        limit: Maximum recipes to return (max 100)

    Returns:
        List of recipes with structure:
        [
            {
                'id': int,
                'title': str,
                'image': str (URL),
                'diets': list[str],
                'usedIngredients': list[dict],
                'missedIngredients': list[dict],
                'usedIngredientCount': int,
                'url': str
            },
            ...
        ]

    Raises:
        ValidationError: If inputs are invalid
        RecipeNotFoundError: If no recipes found

    Example:
        >>> recipes = search_recipes_by_ingredients(['tofu', 'broccoli'])
        >>> recipes[0]['title']
        'Vegan Tofu Stir Fry'
    """
    try:
        # Validate ingredients
        ingredients = validate_ingredients_list(ingredients)
        logger.debug(f"Searching recipes for ingredients: {ingredients}")

        # Search via Spoonacular
        recipes = spoonacular_client.find_by_ingredients(
            ingredients=ingredients,
            number=limit,
            ranking=1,  # Better matches first
        )

        if not recipes:
            raise RecipeNotFoundError(
                f"No recipes found for ingredients: {', '.join(ingredients)}"
            )

        # Filter by dietary preferences if specified
        if dietary_filters:
            filtered_recipes = []

            for recipe in recipes:
                diets = recipe.get("diets", [])

                if dietary_filters.get("vegan") and "vegan" not in diets:
                    continue
                if dietary_filters.get("vegetarian") and "vegetarian" not in diets:
                    continue
                if (
                    dietary_filters.get("gluten_free")
                    and "gluten free" not in diets
                ):
                    continue

                filtered_recipes.append(recipe)

            recipes = filtered_recipes

            if not recipes:
                raise RecipeNotFoundError(
                    f"No recipes match dietary filters for: {', '.join(ingredients)}"
                )

        logger.info(f"Found {len(recipes)} recipes for ingredients")

        log_tool_execution(
            logger,
            "search_recipes_by_ingredients",
            {
                "ingredients": ingredients,
                "dietary_filters": dietary_filters,
                "limit": limit,
            },
            len(recipes),
        )

        return recipes[:limit]

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        log_tool_execution(
            logger,
            "search_recipes_by_ingredients",
            {"ingredients": ingredients},
            error=str(e),
        )
        raise
    except RecipeNotFoundError as e:
        logger.warning(f"Recipe not found: {e}")
        log_tool_execution(
            logger,
            "search_recipes_by_ingredients",
            {"ingredients": ingredients},
            error=str(e),
        )
        raise


def get_recipe_details(recipe_id: int) -> Dict:
    """
    Get detailed information for a specific recipe.

    Includes full ingredients, instructions, nutrition, and metadata.

    Args:
        recipe_id: Spoonacular recipe ID

    Returns:
        Dictionary with complete recipe information:
        {
            'id': int,
            'title': str,
            'image': str,
            'servings': int,
            'readyInMinutes': int,
            'extendedIngredients': list,
            'instructions': str,
            'nutrition': dict,
            'diets': list[str],
            'cuisines': list[str],
            'url': str
        }

    Raises:
        ValidationError: If recipe ID is invalid
        RecipeNotFoundError: If recipe not found

    Example:
        >>> recipe = get_recipe_details(594736)
        >>> recipe['title']
        'Pasta with Garlic, Scallions, and Breadcrumbs'
    """
    try:
        # Validate recipe ID
        recipe_id = validate_recipe_id(recipe_id)
        logger.debug(f"Getting recipe details for ID: {recipe_id}")

        # Check cache first
        cached = cache.get_recipe(str(recipe_id))
        if cached:
            logger.debug(f"Cache hit for recipe: {recipe_id}")
            return cached

        # Fetch from API
        recipe = spoonacular_client.get_recipe_information(
            recipe_id=recipe_id,
            include_nutrition=True,
        )

        if not recipe:
            raise RecipeNotFoundError(f"Recipe {recipe_id} not found")

        # Cache result
        cache.cache_recipe(str(recipe_id), recipe)

        logger.info(f"Retrieved recipe: {recipe.get('title')}")

        log_tool_execution(
            logger,
            "get_recipe_details",
            {"recipe_id": recipe_id},
            recipe.get("title"),
        )

        return recipe

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        log_tool_execution(
            logger,
            "get_recipe_details",
            {"recipe_id": recipe_id},
            error=str(e),
        )
        raise
    except RecipeNotFoundError as e:
        logger.warning(f"Recipe not found: {e}")
        log_tool_execution(
            logger,
            "get_recipe_details",
            {"recipe_id": recipe_id},
            error=str(e),
        )
        raise


def get_recipe_instructions(recipe_id: int) -> Dict:
    """
    Get step-by-step recipe instructions.

    Args:
        recipe_id: Spoonacular recipe ID

    Returns:
        Dictionary with:
        {
            'recipe_id': int,
            'title': str,
            'instructions': str,
            'steps': list[dict] (if available),
            'prep_time': int (minutes),
            'cook_time': int (minutes),
            'servings': int
        }

    Raises:
        ValidationError: If recipe ID is invalid
        RecipeNotFoundError: If recipe not found

    Example:
        >>> instructions = get_recipe_instructions(594736)
        >>> print(instructions['instructions'])
    """
    try:
        # Validate recipe ID
        recipe_id = validate_recipe_id(recipe_id)

        # Get full recipe details
        recipe = get_recipe_details(recipe_id)

        # Extract instruction information
        result = {
            "recipe_id": recipe_id,
            "title": recipe.get("title", ""),
            "instructions": recipe.get("instructions", ""),
            "steps": recipe.get("analyzedInstructions", []),
            "prep_time": recipe.get("preparationMinutes", 0),
            "cook_time": recipe.get("cookingMinutes", 0),
            "servings": recipe.get("servings", 4),
        }

        logger.debug(f"Retrieved instructions for recipe: {recipe_id}")

        log_tool_execution(
            logger,
            "get_recipe_instructions",
            {"recipe_id": recipe_id},
            result["title"],
        )

        return result

    except (ValidationError, RecipeNotFoundError) as e:
        logger.warning(f"Error getting instructions: {e}")
        log_tool_execution(
            logger,
            "get_recipe_instructions",
            {"recipe_id": recipe_id},
            error=str(e),
        )
        raise


def search_recipe_by_query(
    query: str,
    diet: Optional[str] = None,
    limit: int = 10,
) -> List[Dict]:
    """
    Search for recipes by name or keyword.

    Args:
        query: Recipe search query
        diet: Optional diet filter ('vegan', 'vegetarian', 'gluten-free', etc.)
        limit: Maximum recipes to return

    Returns:
        List of recipe summaries

    Raises:
        ValidationError: If query is invalid
        RecipeNotFoundError: If no recipes found

    Example:
        >>> recipes = search_recipe_by_query('pasta vegan', diet='vegan')
        >>> len(recipes)
        10
    """
    try:
        from utils.validators import validate_user_input

        # Validate query
        query = validate_user_input(query, max_length=100)
        logger.debug(f"Searching recipes for: {query}")

        # Search via Spoonacular
        recipes = spoonacular_client.search_recipes(
            query=query,
            diet=diet,
            number=limit,
        )

        if not recipes:
            raise RecipeNotFoundError(f"No recipes found for: {query}")

        logger.info(f"Found {len(recipes)} recipes for query: {query}")

        log_tool_execution(
            logger,
            "search_recipe_by_query",
            {"query": query, "diet": diet, "limit": limit},
            len(recipes),
        )

        return recipes[:limit]

    except (ValidationError, RecipeNotFoundError) as e:
        logger.warning(f"Error searching recipes: {e}")
        log_tool_execution(
            logger,
            "search_recipe_by_query",
            {"query": query},
            error=str(e),
        )
        raise
