# 🖥️ Screen Monitor - Windows Build Guide

## Prerequisites

### 1. Python Install করুন
- [Python Downloads](https://www.python.org/downloads/) থেকে Python 3.10+ ডাউনলোড করুন
- ⚠️ **গুরুত্বপূর্ণ:** Install এর সময় **"Add Python to PATH"** checkbox এ টিক দিন

### 2. Verify Installation
Command Prompt খুলে চেক করুন:
```cmd
python --version
pip --version
```

---

## Build Steps

### Step 1: Project Folder এ যান
```cmd
cd C:\path\to\ScreenMonitor
```

### Step 2: Virtual Environment তৈরি করুন (Recommended)
```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3: Dependencies Install করুন
```cmd
pip install -r requirements.txt
pip install pyinstaller
```

### Step 4: Application Build করুন
```cmd
pyinstaller --onefile --noconsole --name=ScreenMonitor --icon=IBIT-Logo-V3.png main.py
```

অথবা spec file ব্যবহার করে:
```cmd
pyinstaller build.spec
```

---

## Build Output

Build সফল হলে:
- `dist\ScreenMonitor.exe` - এটাই আপনার executable file

---

## Quick Build (One-liner)

Fresh machine এ সব একসাথে:
```cmd
pip install -r requirements.txt pyinstaller && pyinstaller --onefile --noconsole --name=ScreenMonitor main.py
```

---

## Troubleshooting

| সমস্যা | সমাধান |
|--------|--------|
| `python` command not found | Python PATH এ add করুন অথবা reinstall করুন |
| PyQt5 install error | `pip install --upgrade pip` তারপর আবার try করুন |
| Build failed | `pip install pyinstaller --upgrade` করুন |
| Antivirus blocking | Antivirus এ exception add করুন |

---

## Clean Build

আগের build মুছে নতুন করে build করতে:
```cmd
rmdir /s /q build dist __pycache__
pyinstaller build.spec
```
