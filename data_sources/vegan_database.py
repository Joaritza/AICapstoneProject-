"""Vegan ingredients database for Plant Based Assistant."""

import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from utils.exceptions import DataSourceError

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent / "data" / "vegan_ingredients.db"
CSV_PATH = Path(__file__).parent / "data" / "vegan_ingredients.csv"


class VeganDatabaseClient:
    """
    Local SQLite database of vegan/non-vegan ingredients.

    Provides fallback when APIs are unavailable.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize vegan database client.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path or DB_PATH
        self._ensure_database()

    def _ensure_database(self) -> None:
        """Create database if it doesn't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.db_path.exists():
            self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize database with schema."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create ingredients table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ingredients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    vegan INTEGER NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Create alternatives table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS alternatives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ingredient_id INTEGER NOT NULL,
                    alternative_name TEXT NOT NULL,
                    explanation TEXT,
                    FOREIGN KEY(ingredient_id) REFERENCES ingredients(id)
                )
                """
            )

            # Create index for faster lookups
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ingredient_name ON ingredients(name)"
            )

            conn.commit()
            conn.close()

            logger.info(f"Initialized vegan database at {self.db_path}")

            # Load initial data from CSV if it exists
            if CSV_PATH.exists():
                self._load_csv_data()

        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DataSourceError(f"Database initialization failed: {e}")

    def _load_csv_data(self) -> None:
        """Load initial data from CSV file."""
        try:
            import csv

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            with open(CSV_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    ingredient_name = row["ingredient"].strip().lower()
                    vegan = 1 if row["vegan"].lower() == "true" else 0
                    reason = row.get("reason", "")

                    try:
                        cursor.execute(
                            "INSERT INTO ingredients (name, vegan, reason) VALUES (?, ?, ?)",
                            (ingredient_name, vegan, reason),
                        )

                        # Insert alternatives if provided
                        ingredient_id = cursor.lastrowid
                        alternatives = row.get("alternatives", "").split("|")
                        explanations = row.get("alternatives_explained", "").split("|")

                        for alt, exp in zip(alternatives, explanations):
                            if alt.strip():
                                cursor.execute(
                                    "INSERT INTO alternatives (ingredient_id, alternative_name, explanation) VALUES (?, ?, ?)",
                                    (ingredient_id, alt.strip(), exp.strip()),
                                )

                    except sqlite3.IntegrityError:
                        # Skip duplicates
                        pass

            conn.commit()
            conn.close()

            logger.info(f"Loaded vegan database from CSV")

        except Exception as e:
            logger.warning(f"Failed to load CSV data: {e}")

    def get_ingredient(self, ingredient_name: str) -> Optional[Dict]:
        """
        Get ingredient vegan status and information.

        Args:
            ingredient_name: Name of the ingredient

        Returns:
            Dictionary with ingredient info or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, name, vegan, reason FROM ingredients WHERE name = ?",
                (ingredient_name.lower().strip(),),
            )

            row = cursor.fetchone()

            if not row:
                return None

            result = {
                "name": row["name"],
                "vegan": bool(row["vegan"]),
                "reason": row["reason"],
                "alternatives": [],
            }

            # Get alternatives
            cursor.execute(
                "SELECT alternative_name, explanation FROM alternatives WHERE ingredient_id = ?",
                (row["id"],),
            )

            for alt_row in cursor.fetchall():
                result["alternatives"].append(
                    {
                        "name": alt_row["alternative_name"],
                        "explanation": alt_row["explanation"],
                    }
                )

            conn.close()

            return result

        except sqlite3.Error as e:
            logger.error(f"Database error querying ingredient: {e}")
            return None

    def add_ingredient(
        self,
        name: str,
        vegan: bool,
        reason: str = "",
        alternatives: Optional[List[Tuple[str, str]]] = None,
    ) -> bool:
        """
        Add an ingredient to the database.

        Args:
            name: Ingredient name
            vegan: Whether ingredient is vegan
            reason: Explanation
            alternatives: List of (alternative_name, explanation) tuples

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO ingredients (name, vegan, reason) VALUES (?, ?, ?)",
                (name.lower().strip(), 1 if vegan else 0, reason),
            )

            ingredient_id = cursor.lastrowid

            if alternatives:
                for alt_name, alt_exp in alternatives:
                    cursor.execute(
                        "INSERT INTO alternatives (ingredient_id, alternative_name, explanation) VALUES (?, ?, ?)",
                        (ingredient_id, alt_name, alt_exp),
                    )

            conn.commit()
            conn.close()

            logger.info(f"Added ingredient to database: {name}")

            return True

        except sqlite3.Error as e:
            logger.error(f"Failed to add ingredient: {e}")
            return False

    def search_similar(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for ingredients similar to query.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching ingredients
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Search using LIKE pattern
            pattern = f"%{query.lower()}%"
            cursor.execute(
                "SELECT id, name, vegan, reason FROM ingredients WHERE name LIKE ? LIMIT ?",
                (pattern, limit),
            )

            results = []
            for row in cursor.fetchall():
                results.append(
                    {
                        "name": row["name"],
                        "vegan": bool(row["vegan"]),
                        "reason": row["reason"],
                    }
                )

            conn.close()

            return results

        except sqlite3.Error as e:
            logger.error(f"Database error searching: {e}")
            return []

    def get_all_vegan_alternatives(self) -> List[str]:
        """
        Get all known vegan ingredients.

        Returns:
            List of vegan ingredient names
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM ingredients WHERE vegan = 1")
            results = [row[0] for row in cursor.fetchall()]

            conn.close()

            return results

        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return []
