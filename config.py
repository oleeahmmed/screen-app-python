# config.py - Application Configuration

import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# API Server Configuration
API_BASE_URL = "https://att.igenhr.com/api"
API_TOKEN_URL = f"{API_BASE_URL}/token/"
API_TOKEN_REFRESH_URL = f"{API_BASE_URL}/token/refresh/"
API_SCREENSHOT_UPLOAD_URL = f"{API_BASE_URL}/screenshots/upload/"
API_SYNC_STATUS_URL = f"{API_BASE_URL}/sync-status/"

# Attendance & Task APIs
API_CHECKIN_URL = f"{API_BASE_URL}/attendance/checkin/"
API_CHECKOUT_URL = f"{API_BASE_URL}/attendance/checkout/"
API_TASKS_URL = f"{API_BASE_URL}/tasks/"

# Subscription & Access APIs
API_ACCESS_CHECK_URL = f"{API_BASE_URL}/access-check/"
API_PROFILE_URL = f"{API_BASE_URL}/profile/"

# Local Storage Paths
DATA_DIR = os.path.join(BASE_DIR, "data")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
AUTH_TOKEN_FILE = os.path.join(DATA_DIR, "auth_token.json")
UPLOAD_QUEUE_FILE = os.path.join(DATA_DIR, "upload_queue.json")
TC_ACCEPTANCE_FILE = os.path.join(DATA_DIR, "tc_accepted.json")
PROFILE_INFO_FILE = os.path.join(DATA_DIR, "profile_info.json")

# Screenshot Settings
SCREENSHOT_INTERVAL = 30  # seconds
IMAGE_QUALITY = 50
IMAGE_FORMAT = "WEBP"

# Cleanup Settings
CLEANUP_DAYS = 7  # Delete files older than 7 days

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
