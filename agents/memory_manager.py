"""Conversation memory and user profile management for Plant-Based Assistant."""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from config.constants import CONVERSATION_WINDOW_SIZE

logger = logging.getLogger(__name__)


class UserProfile:
    """Stores user preferences and dietary information."""

    def __init__(self):
        """Initialize user profile."""
        self.dietary_restrictions: List[str] = []
        self.ingredients_on_hand: List[str] = []
        self.allergies: List[str] = []
        self.protein_goal_grams: float = 50.0
        self.budget: str = "moderate"  # low, moderate, high
        self.cuisine_preferences: List[str] = []
        self.vegan_years: Optional[int] = None
        self.last_updated = datetime.now()

    def update(self, **kwargs) -> None:
        """
        Update user profile attributes.

        Args:
            **kwargs: Profile fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                self.last_updated = datetime.now()
                logger.debug(f"Updated user profile: {key} = {value}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "dietary_restrictions": self.dietary_restrictions,
            "ingredients_on_hand": self.ingredients_on_hand,
            "allergies": self.allergies,
            "protein_goal_grams": self.protein_goal_grams,
            "budget": self.budget,
            "cuisine_preferences": self.cuisine_preferences,
            "vegan_years": self.vegan_years,
            "last_updated": self.last_updated.isoformat(),
        }


class ConversationMemory:
    """Manages conversation history with configurable window size."""

    def __init__(self, window_size: int = CONVERSATION_WINDOW_SIZE):
        """
        Initialize conversation memory.

        Args:
            window_size: Number of exchanges to keep in memory
        """
        self.window_size = window_size
        self.messages: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to conversation history.

        Args:
            role: 'user' or 'assistant'
            content: Message text
        """
        self.messages.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Keep only recent messages
        if len(self.messages) > self.window_size * 2:  # 2 messages per exchange
            self.messages = self.messages[-self.window_size * 2 :]

            logger.debug(f"Trimmed conversation to {len(self.messages)} messages")

    def get_context(self, max_messages: Optional[int] = None) -> List[Dict]:
        """
        Get conversation context for LLM.

        Args:
            max_messages: Maximum messages to return (uses window_size if None)

        Returns:
            List of message dicts in format for LLM
        """
        limit = max_messages or self.window_size * 2
        return self.messages[-limit :]

    def get_context_string(self) -> str:
        """
        Get conversation context as formatted string.

        Returns:
            Formatted conversation history
        """
        context = []
        for msg in self.messages:
            role = "You" if msg["role"] == "user" else "Assistant"
            context.append(f"{role}: {msg['content']}")

        return "\n".join(context) if context else "No prior conversation"

    def clear(self) -> None:
        """Clear conversation history."""
        self.messages = []
        logger.info("Cleared conversation history")

    def get_last_user_message(self) -> Optional[str]:
        """Get the last user message."""
        for msg in reversed(self.messages):
            if msg["role"] == "user":
                return msg["content"]

        return None

    def get_summary(self, max_lines: int = 5) -> str:
        """
        Get a brief summary of recent conversation.

        Args:
            max_lines: Maximum lines to include

        Returns:
            Summary string
        """
        recent = self.messages[-max_lines * 2 :]
        summary = "Recent conversation:\n"

        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"][:80]  # Truncate

            if msg["content"].endswith("..."):
                summary += f"- {role}: {content}...\n"
            else:
                summary += f"- {role}: {content}\n"

        return summary


class MemoryManager:
    """Manages both conversation history and user profile."""

    def __init__(self, user_id: Optional[str] = None):
        """
        Initialize memory manager.

        Args:
            user_id: Optional user ID for session
        """
        self.user_id = user_id or "default_user"
        self.conversation = ConversationMemory()
        self.user_profile = UserProfile()
        logger.info(f"Initialized memory for user: {self.user_id}")

    def add_user_message(self, content: str) -> None:
        """
        Add user message to conversation.

        Args:
            content: User message
        """
        self.conversation.add_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        """
        Add assistant message to conversation.

        Args:
            content: Assistant response
        """
        self.conversation.add_message("assistant", content)

    def get_conversation_context(self) -> str:
        """Get formatted conversation context."""
        return self.conversation.get_context_string()

    def get_last_user_message(self) -> Optional[str]:
        """Get last user message."""
        return self.conversation.get_last_user_message()

    def get_messages_for_llm(self) -> List[Dict]:
        """
        Get messages in format suitable for LLM API.

        Returns:
            List of message dicts with 'role' and 'content'
        """
        messages = []

        # Add system prompt context
        system_context = {
            "role": "system",
            "content": self._get_system_prompt(),
        }
        messages.append(system_context)

        # Add conversation history
        messages.extend(self.conversation.get_context())

        return messages

    def _get_system_prompt(self) -> str:
        """
        Build system prompt with user context.

        Returns:
            System prompt string
        """
        profile = self.user_profile

        prompt = (
            "You are a helpful Plant-Based Assistant chatbot. "
            "Your role is to help users with vegan ingredient analysis, "
            "alternative suggestions, recipe recommendations, and nutrition information.\n\n"
        )

        # Add user context if available
        if profile.dietary_restrictions:
            prompt += f"User's dietary restrictions: {', '.join(profile.dietary_restrictions)}\n"

        if profile.ingredients_on_hand:
            prompt += f"Ingredients on hand: {', '.join(profile.ingredients_on_hand[:5])}\n"

        if profile.allergies:
            prompt += f"Known allergies: {', '.join(profile.allergies)}\n"

        if profile.cuisine_preferences:
            prompt += f"Preferred cuisines: {', '.join(profile.cuisine_preferences)}\n"

        if profile.protein_goal_grams:
            prompt += f"Protein goal: {profile.protein_goal_grams}g per day\n"

        prompt += (
            "\nProvide accurate, helpful responses synthesizing information from "
            "multiple sources (USDA nutrition data, recipe databases, vegan databases). "
            "Always cite sources and explain your reasoning."
        )

        return prompt

    def update_user_profile(self, **kwargs) -> None:
        """
        Update user profile information.

        Args:
            **kwargs: Profile fields to update
        """
        self.user_profile.update(**kwargs)

    def export_state(self) -> Dict[str, Any]:
        """
        Export complete memory state.

        Returns:
            Dictionary with conversation and profile state
        """
        return {
            "user_id": self.user_id,
            "conversation": self.conversation.messages,
            "user_profile": self.user_profile.to_dict(),
        }

    def import_state(self, state: Dict[str, Any]) -> None:
        """
        Import complete memory state.

        Args:
            state: Dictionary with saved state
        """
        # Update user_id if provided in state
        if "user_id" in state:
            self.user_id = state["user_id"]

        if "conversation" in state:
            self.conversation.messages = state["conversation"]

        if "user_profile" in state:
            profile_data = state["user_profile"]
            for key, value in profile_data.items():
                if key != "last_updated":
                    self.user_profile.update(**{key: value})

        logger.info(f"Imported memory state for user: {self.user_id}")
