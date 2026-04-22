"""USDA FoodData Central API client for Plant Based Assistant."""

import logging
import time
from typing import Dict, List, Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import settings
from config.constants import USDA_RATE_LIMIT, API_TIMEOUT_SECONDS, RETRY_MAX_ATTEMPTS
from utils.exceptions import APITimeoutError, APIRateLimitError, APIConnectionError
from utils.retry_logic import retry_with_backoff
from utils.logging_util import log_api_call

logger = logging.getLogger(__name__)


class USDAFoodClient:
    """
    Client for USDA FoodData Central API.

    Provides access to comprehensive food nutrition and ingredient data.
    """

    BASE_URL = "https://fdc.nal.usda.gov/api/food"
    API_KEY = settings.USDA_API_KEY

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize USDA API client.

        Args:
            api_key: USDA API key (uses settings if not provided)
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
        """Enforce rate limit (120 requests per minute)."""
        min_interval = 60.0 / USDA_RATE_LIMIT
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
    def search_foods(
        self,
        query: str,
        page_size: int = 10,
    ) -> List[Dict]:
        """
        Search for foods by name.

        Args:
            query: Food name to search for
            page_size: Number of results per page (max 100)

        Returns:
            List of food items with basic info

        Raises:
            APITimeoutError: If request times out
            APIConnectionError: If connection fails
            APIRateLimitError: If rate limit exceeded
        """
        self._rate_limit_wait()

        try:
            url = f"{self.BASE_URL}/search"
            params = {
                "query": query,
                "pageSize": min(page_size, 100),
                "api_key": self.api_key,
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
                "USDA",
                f"/food/search?query={query}",
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            if response.status_code == 429:
                raise APIRateLimitError(retry_after=60)

            response.raise_for_status()

            data = response.json()
            return data.get("foods", [])

        except requests.Timeout as e:
            error_msg = f"USDA request timed out after {API_TIMEOUT_SECONDS}s"
            log_api_call(logger, "USDA", f"/food/search?query={query}", error=error_msg)
            raise APITimeoutError("USDA FoodData Central") from e

        except requests.ConnectionError as e:
            error_msg = "Failed to connect to USDA API"
            log_api_call(logger, "USDA", f"/food/search?query={query}", error=error_msg)
            raise APIConnectionError("USDA FoodData Central", str(e)) from e

    @retry_with_backoff(
        max_attempts=RETRY_MAX_ATTEMPTS,
        base_delay=1.0,
        exceptions=(APITimeoutError, APIConnectionError),
    )
    def get_food_details(self, fdc_id: int) -> Optional[Dict]:
        """
        Get detailed information for a specific food item.

        Args:
            fdc_id: FDC ID of the food item

        Returns:
            Detailed food information including nutrition

        Raises:
            APITimeoutError: If request times out
            APIConnectionError: If connection fails
        """
        self._rate_limit_wait()

        try:
            url = f"{self.BASE_URL}/{fdc_id}"
            params = {"api_key": self.api_key}

            start_time = time.time()
            response = self.session.get(
                url,
                params=params,
                timeout=API_TIMEOUT_SECONDS,
            )

            duration_ms = (time.time() - start_time) * 1000
            log_api_call(
                logger,
                "USDA",
                f"/food/{fdc_id}",
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            if response.status_code == 429:
                raise APIRateLimitError(retry_after=60)

            response.raise_for_status()

            return response.json()

        except requests.Timeout as e:
            error_msg = f"USDA request timed out after {API_TIMEOUT_SECONDS}s"
            log_api_call(logger, "USDA", f"/food/{fdc_id}", error=error_msg)
            raise APITimeoutError("USDA FoodData Central") from e

        except requests.ConnectionError as e:
            error_msg = "Failed to connect to USDA API"
            log_api_call(logger, "USDA", f"/food/{fdc_id}", error=error_msg)
            raise APIConnectionError("USDA FoodData Central", str(e)) from e

    def extract_nutrition(self, food_data: Dict) -> Dict[str, float]:
        """
        Extract nutrition information from food data.

        Args:
            food_data: Food data from USDA API

        Returns:
            Dictionary with nutrition facts per 100g:
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

        # Extract nutrients from food_nutrients array
        food_nutrients = food_data.get("foodNutrients", [])

        for nutrient in food_nutrients:
            nutrient_name = nutrient.get("nutrient", {}).get("name", "").lower()
            value = nutrient.get("value", 0)

            # Map USDA nutrient names to our schema
            if "energy" in nutrient_name and "kcal" in nutrient_name:
                nutrition["calories"] = float(value)
            elif "protein" in nutrient_name:
                nutrition["protein"] = float(value)
            elif "carbohydrate" in nutrient_name:
                nutrition["carbs"] = float(value)
            elif "fat" in nutrient_name and "total" in nutrient_name:
                nutrition["fat"] = float(value)
            elif "fiber" in nutrient_name:
                nutrition["fiber"] = float(value)

        return nutrition

    def get_ingredient_info(self, ingredient_name: str) -> Optional[Tuple[Dict, Dict]]:
        """
        Get complete ingredient information including nutrition.

        Args:
            ingredient_name: Name of the ingredient

        Returns:
            Tuple of (food_data, nutrition_data) or None if not found

        Raises:
            APITimeoutError: If request times out
            APIConnectionError: If connection fails
        """
        # Search for food
        foods = self.search_foods(ingredient_name, page_size=1)

        if not foods:
            logger.warning(f"No USDA data found for: {ingredient_name}")
            return None

        # Get first result details
        food = foods[0]
        fdc_id = food.get("fdcId")

        if not fdc_id:
            logger.warning(f"No FDC ID for: {ingredient_name}")
            return None

        # Get full details including nutrition
        food_details = self.get_food_details(fdc_id)

        if not food_details:
            return None

        # Extract nutrition
        nutrition = self.extract_nutrition(food_details)

        return food_details, nutrition
