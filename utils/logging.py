import logging
import os
from logging.handlers import RotatingFileHandler

def ensure_logs_dir():
    """Ensure the logs directory exists"""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create logs directory: {e}")
    return log_dir

def setup_logging():
    """
    Configure and setup logging with both console and file handlers.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger('gcp_monitor')
    logger.setLevel(logging.DEBUG)  # Set to lowest level, let handlers filter
    
    # Clear any existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create formatters
    log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    formatter = logging.Formatter(log_format)
    
    # Console handler (INFO level and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # File handler (DEBUG level and above)
    try:
        log_dir = ensure_logs_dir()
        log_file = os.path.join(log_dir, 'gcp_monitor.log')
        
        # Rotating file handler: 5MB per file, keep 5 backup files
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.debug(f"Logging to file: {log_file}")
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")
    
    logger.addHandler(console_handler)
    return logger

# Initialize the logger
logger = setup_logging()
