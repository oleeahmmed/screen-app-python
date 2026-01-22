# Screen Monitor - Desktop Client

Employee monitoring desktop application for tracking screenshots, attendance, and tasks.

## Features

- 📸 Automatic screenshot capture at regular intervals
- ⏰ Attendance tracking with check-in/check-out
- ✅ Task management
- 🔄 Auto-sync with server
- 🔐 Secure authentication with JWT
- 📊 Subscription-based access control

## Requirements

- Python 3.8+
- Windows/Linux/macOS
- Active internet connection

## Installation

1. Clone the repository:
```bash
git clone git@github.com:ibitltd/screen-desktop-client.git
cd screen-desktop-client
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API endpoint:
Edit `config.py` and set your API server URL:
```python
API_BASE_URL = "https://your-server.com/api"
```

## Usage

Run the application:
```bash
python main.py
```

### First Time Setup

1. Enter your username and password
2. Click "Login"
3. The app will start monitoring automatically

### Features

- **Screenshot Capture**: Automatically captures screenshots every 30 seconds
- **Attendance**: Auto check-in when you login, check-out when you close
- **Tasks**: Manage your daily tasks
- **Sync**: All data syncs automatically with the server

## Configuration

Edit `config.py` to customize:

- `SCREENSHOT_INTERVAL`: Time between screenshots (seconds)
- `IMAGE_QUALITY`: Screenshot quality (1-100)
- `IMAGE_FORMAT`: Image format (WEBP, JPEG, PNG)
- `CLEANUP_DAYS`: Days to keep local screenshots

## Building Executable

To create a standalone executable:

```bash
pyinstaller --onefile --windowed --name="ScreenMonitor" main.py
```

## Project Structure

```
desktop-app/
├── main.py              # Main application entry
├── auth.py              # Authentication handler
├── config.py            # Configuration settings
├── screenshot_service.py # Screenshot capture service
├── sync_manager.py      # Server sync manager
├── task_manager.py      # Task management
├── cleanup.py           # Old file cleanup
├── requirements.txt     # Python dependencies
├── data/                # Local data storage
└── screenshots/         # Captured screenshots
```

## Security

- All communication uses HTTPS
- JWT tokens for authentication
- Passwords are never stored locally
- Screenshots are encrypted during transfer

## Support

For issues and support, contact: support@igenhr.com

## License

Proprietary - IBIT Ltd © 2026
