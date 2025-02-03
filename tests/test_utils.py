import pytest

from whisperchain.utils.logger import get_logger


def test_logger(capsys):
    """Test that logger prints to terminal"""
    logger = get_logger("test")

    # Test all log levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Get captured output
    captured = capsys.readouterr()

    # Check that messages appear in stderr
    assert "Debug message" in captured.err
    assert "Info message" in captured.err
    assert "Warning message" in captured.err
    assert "Error message" in captured.err

    # Check formatting with color codes
    assert "\033[37mDEBUG\033[0m" in captured.err  # White DEBUG
    assert "test_utils.py:" in captured.err
