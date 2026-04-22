"""Custom exception hierarchy for Plant Based Assistant."""


class PlanBasedAssistantError(Exception):
    """Base exception for all application errors."""

    pass


class APIError(PlanBasedAssistantError):
    """Base exception for API-related errors."""

    pass


class APIRateLimitError(APIError):
    """Exception raised when API rate limit is exceeded."""

    def __init__(self, retry_after: int = 60):
        """
        Initialize APIRateLimitError.

        Args:
            retry_after: Number of seconds to wait before retrying
        """
        self.retry_after = retry_after
        super().__init__(f"API rate limit exceeded. Retry after {retry_after} seconds.")


class APITimeoutError(APIError):
    """Exception raised when API request times out."""

    def __init__(self, api_name: str = "Unknown API"):
        """
        Initialize APITimeoutError.

        Args:
            api_name: Name of the API that timed out
        """
        super().__init__(f"{api_name} request timed out.")


class APIConnectionError(APIError):
    """Exception raised when unable to connect to API."""

    def __init__(self, api_name: str = "Unknown API", details: str = ""):
        """
        Initialize APIConnectionError.

        Args:
            api_name: Name of the API
            details: Additional error details
        """
        message = f"Failed to connect to {api_name}"
        if details:
            message += f": {details}"
        super().__init__(message)


class DataSourceError(PlanBasedAssistantError):
    """Exception raised when data source is unavailable."""

    pass


class IngredientNotFoundError(PlanBasedAssistantError):
    """Exception raised when ingredient is not found in any database."""

    def __init__(self, ingredient: str):
        """
        Initialize IngredientNotFoundError.

        Args:
            ingredient: The ingredient that was not found
        """
        super().__init__(f"Ingredient '{ingredient}' not found in any data source.")


class RecipeNotFoundError(PlanBasedAssistantError):
    """Exception raised when recipe matching criteria is not found."""

    pass


class ConfigurationError(PlanBasedAssistantError):
    """Exception raised when configuration is invalid or incomplete."""

    pass


class ValidationError(PlanBasedAssistantError):
    """Exception raised when input validation fails."""

    def __init__(self, field: str, message: str):
        """
        Initialize ValidationError.

        Args:
            field: Name of the field that failed validation
            message: Validation error message
        """
        super().__init__(f"Validation error for '{field}': {message}")


class CacheError(PlanBasedAssistantError):
    """Exception raised when cache operations fail."""

    pass
