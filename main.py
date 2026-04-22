"""
Plant Based Assistant Chatbot - Entry Point

Run the Streamlit UI application.
"""

import subprocess
import sys
from pathlib import Path

from config.logger_config import logger


def main():
    """Launch the Streamlit application."""
    try:
        logger.info("Starting Plant Based Assistant UI...")

        # Get the path to the UI app
        ui_app_path = Path(__file__).parent / "ui" / "app.py"

        # Run streamlit
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(ui_app_path)],
            check=True,
        )

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
