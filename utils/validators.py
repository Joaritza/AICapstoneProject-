"""Input validation utilities for Plant Based Assistant."""

from typing import List, Optional, Dict, Any
from utils.exceptions import ValidationError


def validate_ingredient_name(ingredient: str) -> str:
    """
    Validate and normalize ingredient name.

    Args:
        ingredient: Raw ingredient input

    Returns:
        Normalized ingredient name

    Raises:
        ValidationError: If ingredient is invalid
    """
    if not isinstance(ingredient, str):
        raise ValidationError("ingredient", "Must be a string")

    ingredient = ingredient.strip().lower()

    if len(ingredient) == 0:
        raise ValidationError("ingredient", "Cannot be empty")

    if len(ingredient) > 100:
        raise ValidationError("ingredient", "Must be less than 100 characters")

    # Allow alphanumeric, spaces, hyphens, and parentheses
    allowed_chars = set("abcdefghijklmnopqrstuvwxyz0123456789 -().,")
    if not all(c in allowed_chars for c in ingredient):
        raise ValidationError(
            "ingredient", f"Contains invalid characters. Only letters, numbers, and basic punctuation allowed"
        )

    return ingredient


def validate_ingredients_list(ingredients: List[str]) -> List[str]:
    """
    Validate a list of ingredients.

    Args:
        ingredients: List of ingredient names

    Returns:
        List of validated, normalized ingredients

    Raises:
        ValidationError: If any ingredient is invalid
    """
    if not isinstance(ingredients, list):
        raise ValidationError("ingredients", "Must be a list")

    if len(ingredients) == 0:
        raise ValidationError("ingredients", "List cannot be empty")

    if len(ingredients) > 20:
        raise ValidationError("ingredients", "Cannot have more than 20 ingredients")

    validated = []
    for ing in ingredients:
        validated.append(validate_ingredient_name(ing))

    return validated


def validate_serving_size(serving_size: float) -> float:
    """
    Validate serving size in grams.

    Args:
        serving_size: Serving size value

    Returns:
        Validated serving size

    Raises:
        ValidationError: If serving size is invalid
    """
    try:
        size = float(serving_size)
    except (TypeError, ValueError):
        raise ValidationError("serving_size", "Must be a number")

    if size <= 0:
        raise ValidationError("serving_size", "Must be greater than 0")

    if size > 10000:
        raise ValidationError("serving_size", "Must be less than 10000 grams")

    return size


def validate_recipe_id(recipe_id: Any) -> int:
    """
    Validate recipe ID.

    Args:
        recipe_id: Recipe ID value

    Returns:
        Validated recipe ID as integer

    Raises:
        ValidationError: If recipe ID is invalid
    """
    try:
        id_int = int(recipe_id)
    except (TypeError, ValueError):
        raise ValidationError("recipe_id", "Must be an integer")

    if id_int <= 0:
        raise ValidationError("recipe_id", "Must be greater than 0")

    return id_int


def validate_user_input(user_input: str, max_length: int = 500) -> str:
    """
    Validate user chat input.

    Args:
        user_input: Raw user input string
        max_length: Maximum allowed length

    Returns:
        Cleaned user input

    Raises:
        ValidationError: If input is invalid
    """
    if not isinstance(user_input, str):
        raise ValidationError("input", "Must be a string")

    cleaned = user_input.strip()

    if len(cleaned) == 0:
        raise ValidationError("input", "Cannot be empty")

    if len(cleaned) > max_length:
        raise ValidationError("input", f"Cannot exceed {max_length} characters")

    return cleaned
