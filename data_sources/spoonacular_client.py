"""Spoonacular Recipe API client for Plant Based Assistant."""

import logging
import time
from typing import Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import settings
from config.constants import API_TIMEOUT_SECONDS, RETRY_MAX_ATTEMPTS
from utils.exceptions import APITimeoutError, APIRateLimitError, APIConnectionError
from utils.retry_logic import retry_with_backoff
from utils.logging_util import log_api_call

logger = logging.getLogger(__name__)


class SpoonacularRecipeClient:
    """
    Client for Spoonacular Recipe API.

    Provides access to 5+ million recipes with dietary information.
    """

    BASE_URL = "https://api.spoonacular.com/recipes"
    API_KEY = settings.SPOONACULAR_API_KEY

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Spoonacular API client.

        Args:
            api_key: Spoonacular API key (uses settings if not provided)
        """
        self.api_key = api_key or self.API_KEY
        self.session = self._create_session()
        self.last_request_time = 0

    def _create_session(self) -> requests.Session:
        """
        Create requests session with retry strategy.

        Returns:
            Configured requests.Session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=RETRY_MAX_ATTEMPTS,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _rate_limit_wait(self) -> None:
        """Enforce rate limit (150 requests per day for free tier)."""
        # For free tier, be conservative: 150 requests/day = ~0.1736 requests/second
        min_interval = 86400.0 / 150  # ~576 seconds between requests
        elapsed = time.time() - self.last_request_time

        if elapsed < min_interval:
            wait_time = min_interval - elapsed
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)

        self.last_request_time = time.time()

    @retry_with_backoff(
        max_attempts=RETRY_MAX_ATTEMPTS,
        base_delay=1.0,
        exceptions=(APITimeoutError, APIConnectionError),
    )
    def find_by_ingredients(
        self,
        ingredients: List[str],
        number: int = 10,
        ranking: int = 1,
    ) -> List[Dict]:
        """
        Find recipes by ingredients.

        Args:
            ingredients: List of ingredient names
            number: Number of recipes to return (max 100)
            ranking: Ranking type (1=better matches, 2=most matches)

        Returns:
            List of recipe summaries

        Raises:
            APITimeoutError: If request times out
            APIConnectionError: If connection fails
            APIRateLimitError: If rate limit exceeded
        """
        self._rate_limit_wait()

        try:
            url = f"{self.BASE_URL}/findByIngredients"
            params = {
                "ingredients": ",".join(ingredients),
                "number": min(number, 100),
                "ranking": ranking,
                "apiKey": self.api_key,
            }

            start_time = time.time()
            response = self.session.get(
                url,
                params=params,
                timeout=API_TIMEOUT_SECONDS,
            )

            duration_ms = (time.time() - start_time) * 1000
            log_api_call(
                logger,
                "Spoonacular",
                f"/recipes/findByIngredients",
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            if response.status_code == 429:
                raise APIRateLimitError(retry_after=3600)  # 1 hour

            response.raise_for_status()

            return response.json()

        except requests.Timeout as e:
            error_msg = f"Spoonacular request timed out after {API_TIMEOUT_SECONDS}s"
            log_api_call(logger, "Spoonacular", "/recipes/findByIngredients", error=error_msg)
            raise APITimeoutError("Spoonacular Recipe API") from e

        except requests.ConnectionError as e:
            error_msg = "Failed to connect to Spoonacular API"
            log_api_call(logger, "Spoonacular", "/recipes/findByIngredients", error=error_msg)
            raise APIConnectionError("Spoonacular Recipe API", str(e)) from e

    @retry_with_backoff(
        max_attempts=RETRY_MAX_ATTEMPTS,
        base_delay=1.0,
        exceptions=(APITimeoutError, APIConnectionError),
    )
    def get_recipe_information(
        self,
        recipe_id: int,
        include_nutrition: bool = True,
    ) -> Optional[Dict]:
        """
        Get detailed information for a recipe.

        Args:
            recipe_id: Spoonacular recipe ID
            include_nutrition: Include nutrition information

        Returns:
            Detailed recipe information

        Raises:
            APITimeoutError: If request times out
            APIConnectionError: If connection fails
        """
        self._rate_limit_wait()

        try:
            url = f"{self.BASE_URL}/{recipe_id}/information"
            params = {
                "includeNutrition": "true" if include_nutrition else "false",
                "apiKey": self.api_key,
            }

            start_time = time.time()
            response = self.session.get(
                url,
                params=params,
                timeout=API_TIMEOUT_SECONDS,
            )

            duration_ms = (time.time() - start_time) * 1000
            log_api_call(
                logger,
                "Spoonacular",
                f"/recipes/{recipe_id}/information",
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            if response.status_code == 429:
                raise APIRateLimitError(retry_after=3600)

            response.raise_for_status()

            return response.json()

        except requests.Timeout as e:
            error_msg = f"Spoonacular request timed out after {API_TIMEOUT_SECONDS}s"
            log_api_call(logger, "Spoonacular", f"/recipes/{recipe_id}/information", error=error_msg)
            raise APITimeoutError("Spoonacular Recipe API") from e

        except requests.ConnectionError as e:
            error_msg = "Failed to connect to Spoonacular API"
            log_api_call(logger, "Spoonacular", f"/recipes/{recipe_id}/information", error=error_msg)
            raise APIConnectionError("Spoonacular Recipe API", str(e)) from e

    def extract_nutrition(self, recipe_data: Dict) -> Dict[str, float]:
        """
        Extract nutrition information from recipe data.

        Args:
            recipe_data: Recipe data from Spoonacular API

        Returns:
            Dictionary with nutrition facts:
            - calories: Energy in kcal
            - protein: Protein in grams
            - carbs: Carbohydrates in grams
            - fat: Total fat in grams
            - fiber: Dietary fiber in grams
        """
        nutrition = {
            "calories": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0,
            "fiber": 0.0,
        }

        # Try to extract from nutrition object
        if "nutrition" in recipe_data:
            nutrition_obj = recipe_data["nutrition"]
            nutrition["calories"] = float(
                nutrition_obj.get("nutrients", [{}])[0].get("value", 0) 
                if nutrition_obj.get("nutrients") else 0
            )
        
        # Try extended nutrition data
        if "nutrients" in recipe_data:
            for nutrient in recipe_data.get("nutrients", []):
                name = nutrient.get("name", "").lower()
                value = nutrient.get("value", 0)

                if "calories" in name or "energy" in name:
                    nutrition["calories"] = float(value)
                elif "protein" in name:
                    nutrition["protein"] = float(value)
                elif "carbohydrate" in name:
                    nutrition["carbs"] = float(value)
                elif "fat" in name and "total" in name:
                    nutrition["fat"] = float(value)
                elif "fiber" in name:
                    nutrition["fiber"] = float(value)

        return nutrition

    def search_recipes(
        self,
        query: str,
        diet: Optional[str] = None,
        number: int = 10,
    ) -> List[Dict]:
        """
        Search for recipes by name.

        Args:
            query: Recipe search query
            diet: Diet type filter (e.g., 'vegan', 'vegetarian')
            number: Number of results to return

        Returns:
            List of recipe summaries

        Raises:
            APITimeoutError: If request times out
            APIConnectionError: If connection fails
        """
        self._rate_limit_wait()

        try:
            url = f"{self.BASE_URL}/complexSearch"
            params = {
                "query": query,
                "number": min(number, 100),
                "addRecipeInformation": "true",
                "apiKey": self.api_key,
            }

            if diet:
                params["diet"] = diet

            start_time = time.time()
            response = self.session.get(
                url,
                params=params,
                timeout=API_TIMEOUT_SECONDS,
            )

            duration_ms = (time.time() - start_time) * 1000
            log_api_call(
                logger,
                "Spoonacular",
                f"/recipes/complexSearch?query={query}",
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            if response.status_code == 429:
                raise APIRateLimitError(retry_after=3600)

            response.raise_for_status()

            data = response.json()
            return data.get("results", [])

        except requests.Timeout as e:
            error_msg = f"Spoonacular request timed out after {API_TIMEOUT_SECONDS}s"
            log_api_call(logger, "Spoonacular", f"/recipes/complexSearch?query={query}", error=error_msg)
            raise APITimeoutError("Spoonacular Recipe API") from e

        except requests.ConnectionError as e:
            error_msg = "Failed to connect to Spoonacular API"
            log_api_call(logger, "Spoonacular", f"/recipes/complexSearch?query={query}", error=error_msg)
            raise APIConnectionError("Spoonacular Recipe API", str(e)) from e
