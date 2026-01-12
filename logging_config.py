import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """Configure structured logging for production and development."""
    
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_file = os.getenv('LOG_FILE', 'app.log')
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create app logger
    logger = logging.getLogger('suresh_ai_origin')
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # File handler with rotation (10MB max, keep 5 backups)
    if not app.debug:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s [%(pathname)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        app.logger.addHandler(file_handler)
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def log_request_info(logger, request):
    """Log incoming request details for debugging."""
    logger.info(
        f"Request: {request.method} {request.path} "
        f"from {request.remote_addr} "
        f"UA: {request.user_agent.string[:100]}"
    )


def log_error(logger, error, context=None):
    """Log error with context for troubleshooting."""
    msg = f"Error: {str(error)}"
    if context:
        msg += f" | Context: {context}"
    logger.error(msg, exc_info=True)
