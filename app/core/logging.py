import logging
import sys

LOG_FORMAT = '%(levelname)s - %(name)s - %(message)s'


def setup_logging():
    """Basic logging setup."""
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        stream=sys.stdout,
    )
