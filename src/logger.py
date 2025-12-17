import logging
import sys
import os
from .utils import Colors
from .display import display

class DisplayHandler(logging.Handler):
    """Custom handler to route logs to DisplayManager"""
    def emit(self, record):
        try:
            msg = record.getMessage()
            display.add_log(msg, record.levelname)
        except Exception:
            self.handleError(record)

def setup_logger(name="MacroTool", log_file="macro.log", level=logging.INFO):
    """Setup the logger with display and file handlers"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent adding handlers multiple times
    if logger.hasHandlers():
        return logger

    # Display Handler (replaces Console Handler)
    display_handler = DisplayHandler()
    logger.addHandler(display_handler)

    # File Handler
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Fallback if file logging fails, though display might not be ready
        pass

    return logger

# Create a default logger instance
logger = setup_logger()
