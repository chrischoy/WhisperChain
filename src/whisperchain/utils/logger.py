import logging
import sys
from pathlib import Path


class ColorFormatter(logging.Formatter):
    """Custom formatter with colors"""

    COLORS = {
        "DEBUG": "\033[37m",  # White
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        # Add color to the level name
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"

        return super().format(record)


def get_logger(name: str = None) -> logging.Logger:
    """
    Create a logger with consistent formatting including filename and line number

    Args:
        name: Logger name, defaults to file name if None

    Returns:
        Configured logger instance
    """
    if name is None:
        # Get the caller's filename if no name provided
        frame = sys._getframe(1)
        name = Path(frame.f_code.co_filename).stem

    # Create logger
    logger = logging.getLogger(name)

    # Only add handler if logger doesn't have one
    if not logger.handlers:
        # Create stderr handler
        handler = logging.StreamHandler(sys.stderr)

        # Format: [LEVEL] filename:line - message
        formatter = ColorFormatter(
            fmt="[%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Set default level to DEBUG to see all messages
        logger.setLevel(logging.DEBUG)

        # Prevent propagation to avoid duplicate logs
        logger.propagate = False

    return logger
