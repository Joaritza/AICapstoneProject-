"""
Pytest configuration and shared fixtures for Plant Based Assistant tests.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_env_vars():
    """Fixture to mock environment variables."""
    with patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "test_key",
            "SPOONACULAR_API_KEY": "test_key",
            "USDA_API_KEY": "test_key",
            "GITHUB_TOKEN": "test_token",
            "LLM_MODEL": "gpt-4",
            "DEBUG": "False",
            "LOG_LEVEL": "INFO",
        },
    ):
        yield


@pytest.fixture
def mock_api_response():
    """Fixture to create mock API responses."""

    def _create_response(status_code=200, json_data=None, raise_error=None):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = json_data or {}

        if raise_error:
            response.raise_for_status.side_effect = raise_error

        return response

    return _create_response


@pytest.fixture
def sample_ingredient():
    """Sample ingredient for testing."""
    return {
        "name": "milk",
        "vegan": False,
        "reason": "Animal product - from cow lactation",
        "alternatives": [
            "Oat Milk",
            "Almond Milk",
            "Soy Milk",
        ],
    }


@pytest.fixture
def sample_recipe():
    """Sample recipe for testing."""
    return {
        "id": 594736,
        "title": "Pasta with Garlic and Vegetables",
        "image": "https://example.com/image.jpg",
        "diets": ["vegan", "vegetarian"],
        "extendedIngredients": [
            {
                "id": 20027,
                "name": "pasta",
                "amount": 1,
                "unit": "pound",
            }
        ],
        "nutrition": {
            "calories": 567,
            "protein": 21,
            "carbs": 98,
            "fat": 5,
        },
    }


@pytest.fixture
def sample_nutrition():
    """Sample nutrition data for testing."""
    return {
        "ingredient": "milk",
        "serving_size": 100,
        "unit": "grams",
        "calories": 49,
        "protein": 3.2,
        "carbs": 4.8,
        "fat": 1.6,
        "fiber": 0,
    }
