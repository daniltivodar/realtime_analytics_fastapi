import logging
import sys


def setup_logging() -> None:
    """Basic logging setup."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(name)s - %(message)s",
        stream=sys.stdout,
    )
