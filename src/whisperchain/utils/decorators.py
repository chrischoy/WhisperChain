from whisperchain.utils.logger import get_logger

logger = get_logger(__name__)


def handle_exceptions(func):
    """Decorator to handle exceptions in a function."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise e

    return wrapper
