import logging
import sys
from pathlib import Path
from typing import NoReturn

from .error_logger import setup_logger
from .ui import GapDetectorUI


def setup_application() -> None:
    """Initialize application settings and logging"""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Setup logging
    setup_logger()

    logging.info("Application starting...")


def main() -> NoReturn:
    """Main application entrypoint"""
    try:
        # Initialize application
        setup_application()

        # Create and run UI
        app = GapDetectorUI()
        app.run()

        # Clean exit
        logging.info("Application closed normally")
        sys.exit(0)

    except Exception as e:
        # Log any unhandled exceptions
        logging.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
