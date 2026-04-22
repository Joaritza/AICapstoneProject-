"""Application constants and configuration values."""

# API Rate Limiting
USDA_RATE_LIMIT = 120  # requests per minute
SPOONACULAR_RATE_LIMIT = 150  # requests per day (free tier)

# Caching
CACHE_TTL_INGREDIENT = 86400  # 24 hours for ingredient data
CACHE_TTL_RECIPE = 604800  # 7 days for recipe data (stable)
CACHE_TTL_NUTRITION = 86400  # 24 hours for nutrition data

# API Timeouts
API_TIMEOUT_SECONDS = 10
RETRY_MAX_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2

# Conversation Memory
CONVERSATION_WINDOW_SIZE = 10  # Number of exchanges to remember
MAX_RESPONSE_LENGTH = 2000

# Data Quality
MIN_RECIPE_MATCH_SCORE = 0.5
DEFAULT_SERVING_SIZE = 100  # grams

# UI
SUGGESTED_PROMPTS_COUNT = 5
MAX_RECIPE_SUGGESTIONS = 10
