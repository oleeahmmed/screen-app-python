# Screen Monitor - Desktop Client

Employee monitoring desktop application for screenshot tracking, attendance, and task management.

---

## �* Ubuntu/Linux

### 1. Install Python
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

### 2. Clone & Setup
```bash
git clone git@github.com:ibitltd/screen-desktop-client.git
cd screen-desktop-client
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Libraries
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
python main.py
```

### 5. Build Executable
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="ScreenMonitor" main.py
./dist/ScreenMonitor
```

---

## 🪟 Windows

### 1. Install Python
- Download from [python.org](https://www.python.org/downloads/)
- Run installer, check **"Add Python to PATH"**
- Click "Install Now"

### 2. Clone & Setup
```cmd
git clone git@github.com:ibitltd/screen-desktop-client.git
cd screen-desktop-client
python -m venv venv
venv\Scripts\activate
```

### 3. Install Libraries
```cmd
pip install -r requirements.txt
```

### 4. Run Application
```cmd
python main.py
```

### 5. Build Executable
```cmd
pip install pyinstaller
pyinstaller --onefile --windowed --name="ScreenMonitor" main.py
dist\ScreenMonitor.exe
```

---

## 🍎 macOS

### 1. Install Python
```bash
# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11
```

### 2. Clone & Setup
```bash
git clone git@github.com:ibitltd/screen-desktop-client.git
cd screen-desktop-client
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Libraries
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
python main.py
```

### 5. Build Executable
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="ScreenMonitor" main.py
open dist/ScreenMonitor.app
```

---

## ⚙️ Configuration

Edit `config.py` before running:
```python
API_BASE_URL = "https://att.igenhr.com/api"  # Your server URL
SCREENSHOT_INTERVAL = 30  # Screenshot every 30 seconds
```

---

## 📦 Required Libraries

All libraries are in `requirements.txt`:
- requests
- Pillow
- pyscreenshot

Install with: `pip install -r requirements.txt`

---

## 🎯 Usage

1. Run the application
2. Login with your username/password
3. Application will automatically:
   - Capture screenshots
   - Track attendance
   - Sync with server

---

## 📞 Support

Email: support@igenhr.com  
Website: https://igenhr.com

---

**IBIT Ltd © 2026**
