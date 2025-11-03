import logging
import sys


def setup_logging():
    """Basic logging setup."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(name)s - %(message)s',
        stream=sys.stdout,
    )
