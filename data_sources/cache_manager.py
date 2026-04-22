"""Cache management for Plant Based Assistant."""

import json
import logging
import time
from pathlib import Path
from typing import Any, Optional
from config.constants import CACHE_TTL_INGREDIENT, CACHE_TTL_RECIPE, CACHE_TTL_NUTRITION

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path(__file__).parent.parent / "cache"


class CacheManager:
    """
    File-based cache manager with TTL support.

    Caches API responses to reduce redundant requests.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory for cache files
        """
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str, category: str = "default") -> Path:
        """
        Get cache file path for a key.

        Args:
            key: Cache key
            category: Cache category (ingredient, recipe, nutrition)

        Returns:
            Path to cache file
        """
        # Sanitize key for filesystem
        safe_key = "".join(c if c.isalnum() or c in "._-" else "_" for c in key)
        return self.cache_dir / category / f"{safe_key}.json"

    def _ensure_category_dir(self, category: str) -> None:
        """Ensure category directory exists."""
        (self.cache_dir / category).mkdir(parents=True, exist_ok=True)

    def get(self, key: str, category: str = "default") -> Optional[Any]:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key
            category: Cache category

        Returns:
            Cached value if found and not expired, None otherwise
        """
        cache_path = self._get_cache_path(key, category)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Check if expired
            if cache_data["expires_at"] < time.time():
                logger.debug(f"Cache expired for: {key}")
                cache_path.unlink()  # Delete expired cache
                return None

            logger.debug(f"Cache hit for: {key}")

            return cache_data["value"]

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Cache read error for {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int,
        category: str = "default",
    ) -> bool:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds
            category: Cache category

        Returns:
            True if successful, False otherwise
        """
        try:
            self._ensure_category_dir(category)
            cache_path = self._get_cache_path(key, category)

            cache_data = {
                "key": key,
                "value": value,
                "expires_at": time.time() + ttl_seconds,
                "created_at": time.time(),
            }

            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, default=str)

            logger.debug(f"Cache set for: {key} (TTL: {ttl_seconds}s)")

            return True

        except Exception as e:
            logger.error(f"Cache write error for {key}: {e}")
            return False

    def invalidate(self, key: str, category: str = "default") -> bool:
        """
        Invalidate a cache entry.

        Args:
            key: Cache key
            category: Cache category

        Returns:
            True if successful, False otherwise
        """
        cache_path = self._get_cache_path(key, category)

        if not cache_path.exists():
            return True

        try:
            cache_path.unlink()
            logger.debug(f"Cache invalidated for: {key}")
            return True

        except Exception as e:
            logger.error(f"Cache invalidation error for {key}: {e}")
            return False

    def clear_category(self, category: str = "default") -> bool:
        """
        Clear all cache for a category.

        Args:
            category: Cache category

        Returns:
            True if successful
        """
        category_dir = self.cache_dir / category

        if not category_dir.exists():
            return True

        try:
            for cache_file in category_dir.glob("*.json"):
                cache_file.unlink()

            logger.info(f"Cleared cache for category: {category}")
            return True

        except Exception as e:
            logger.error(f"Cache clear error for {category}: {e}")
            return False

    def clear_all(self) -> bool:
        """
        Clear all cache.

        Returns:
            True if successful
        """
        try:
            for cache_file in self.cache_dir.rglob("*.json"):
                cache_file.unlink()

            logger.info("Cleared all cache")
            return True

        except Exception as e:
            logger.error(f"Cache clear all error: {e}")
            return False

    def cache_ingredient(self, ingredient_name: str, data: Any) -> bool:
        """
        Cache ingredient data.

        Args:
            ingredient_name: Ingredient name
            data: Ingredient data

        Returns:
            True if successful
        """
        return self.set(
            key=ingredient_name.lower(),
            value=data,
            ttl_seconds=CACHE_TTL_INGREDIENT,
            category="ingredients",
        )

    def get_ingredient(self, ingredient_name: str) -> Optional[Any]:
        """
        Get cached ingredient data.

        Args:
            ingredient_name: Ingredient name

        Returns:
            Cached data or None
        """
        return self.get(
            key=ingredient_name.lower(),
            category="ingredients",
        )

    def cache_recipe(self, recipe_id: str, data: Any) -> bool:
        """
        Cache recipe data.

        Args:
            recipe_id: Recipe ID
            data: Recipe data

        Returns:
            True if successful
        """
        return self.set(
            key=str(recipe_id),
            value=data,
            ttl_seconds=CACHE_TTL_RECIPE,
            category="recipes",
        )

    def get_recipe(self, recipe_id: str) -> Optional[Any]:
        """
        Get cached recipe data.

        Args:
            recipe_id: Recipe ID

        Returns:
            Cached data or None
        """
        return self.get(
            key=str(recipe_id),
            category="recipes",
        )

    def cache_nutrition(self, key: str, data: Any) -> bool:
        """
        Cache nutrition data.

        Args:
            key: Cache key (e.g., 'milk_100g')
            data: Nutrition data

        Returns:
            True if successful
        """
        return self.set(
            key=key,
            value=data,
            ttl_seconds=CACHE_TTL_NUTRITION,
            category="nutrition",
        )

    def get_nutrition(self, key: str) -> Optional[Any]:
        """
        Get cached nutrition data.

        Args:
            key: Cache key

        Returns:
            Cached data or None
        """
        return self.get(
            key=key,
            category="nutrition",
        )
