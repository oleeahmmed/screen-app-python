"""
Debug Logger - Comprehensive logging for troubleshooting
"""

import os
import logging
from datetime import datetime

# Create logs directory
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Log file path
LOG_FILE = os.path.join(LOGS_DIR, f'app_{datetime.now().strftime("%Y%m%d")}.log')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()  # Also print to console
    ]
)

# Create loggers for different modules
auth_logger = logging.getLogger('AUTH')
screenshot_logger = logging.getLogger('SCREENSHOT')
sync_logger = logging.getLogger('SYNC')
task_logger = logging.getLogger('TASK')
browser_logger = logging.getLogger('BROWSER')
main_logger = logging.getLogger('MAIN')

def log_auth(message, level='info'):
    """Log authentication related events"""
    if level == 'error':
        auth_logger.error(message)
    elif level == 'warning':
        auth_logger.warning(message)
    else:
        auth_logger.info(message)

def log_screenshot(message, level='info'):
    """Log screenshot capture events"""
    if level == 'error':
        screenshot_logger.error(message)
    elif level == 'warning':
        screenshot_logger.warning(message)
    else:
        screenshot_logger.info(message)

def log_sync(message, level='info'):
    """Log sync/upload events"""
    if level == 'error':
        sync_logger.error(message)
    elif level == 'warning':
        sync_logger.warning(message)
    else:
        sync_logger.info(message)

def log_task(message, level='info'):
    """Log task/attendance events"""
    if level == 'error':
        task_logger.error(message)
    elif level == 'warning':
        task_logger.warning(message)
    else:
        task_logger.info(message)

def log_browser(message, level='info'):
    """Log browser monitoring events"""
    if level == 'error':
        browser_logger.error(message)
    elif level == 'warning':
        browser_logger.warning(message)
    else:
        browser_logger.info(message)

def log_main(message, level='info'):
    """Log main app events"""
    if level == 'error':
        main_logger.error(message)
    elif level == 'warning':
        main_logger.warning(message)
    else:
        main_logger.info(message)

def get_log_file_path():
    """Get current log file path"""
    return LOG_FILE

print(f"📝 Logging to: {LOG_FILE}")
