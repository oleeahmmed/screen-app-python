# Tesseract OCR Installation Guide

## ⚠️ Important
Tesseract OCR is required for URL detection from screenshots. You need to install it on your system (not just Python library).

## 🪟 Windows Installation

### Method 1: Using Chocolatey (Recommended)
```bash
# Install Chocolatey first if not installed
# Then run:
choco install tesseract
```

### Method 2: Manual Installation
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (tesseract-ocr-w64-setup-v5.x.x.exe)
3. During installation, note the installation path (usually `C:\Program Files\Tesseract-OCR`)
4. Add to PATH:
   - Right-click "This PC" → Properties
   - Advanced system settings → Environment Variables
   - Edit "Path" variable
   - Add: `C:\Program Files\Tesseract-OCR`
   - Click OK

### Method 3: Using Scoop
```bash
scoop install tesseract
```

## 🐧 Ubuntu/Linux Installation

```bash
# Update package list
sudo apt update

# Install Tesseract OCR
sudo apt install tesseract-ocr

# Install development files (optional, for pytesseract)
sudo apt install libtesseract-dev

# Install additional language data (optional)
sudo apt install tesseract-ocr-eng  # English
sudo apt install tesseract-ocr-ben  # Bengali
```

## 🍎 macOS Installation

```bash
# Using Homebrew
brew install tesseract

# Or using MacPorts
sudo port install tesseract
```

## ✅ Verify Installation

After installation, verify it's working:

```bash
# Check version
tesseract --version

# Should output something like:
# tesseract 5.3.0
#  leptonica-1.82.0
#  ...
```

## 🔧 Troubleshooting

### Error: "tesseract is not installed or it's not in your PATH"

**Windows:**
1. Check if tesseract.exe exists in installation folder
2. Add installation folder to PATH
3. Restart terminal/command prompt
4. Restart desktop app

**Linux/macOS:**
1. Run: `which tesseract`
2. If not found, reinstall: `sudo apt install tesseract-ocr`
3. Check PATH: `echo $PATH`

### Error: "Failed to load language data"

Install language data:
```bash
# Ubuntu/Linux
sudo apt install tesseract-ocr-eng

# Windows - included in installer
# macOS
brew install tesseract-lang
```

## 📦 Python Library (Already in requirements.txt)

The Python wrapper is already included:
```
pytesseract>=0.3.10
```

This is installed with:
```bash
pip install -r requirements.txt
```

## 🎯 What Tesseract Does in This App

- Detects URLs from screenshots
- Extracts browser address bar text
- Identifies domain names
- Extracts page titles
- Provides OCR confidence scores

## 🚀 Quick Start

### Windows:
```bash
# 1. Install Tesseract
choco install tesseract

# 2. Verify
tesseract --version

# 3. Run app
python main.py
```

### Ubuntu:
```bash
# 1. Install Tesseract
sudo apt install tesseract-ocr

# 2. Verify
tesseract --version

# 3. Run app
python main.py
```

## 📝 Notes

- Tesseract is a system-level dependency
- Must be installed separately from Python packages
- Required for URL detection feature
- App will work without it, but URL detection will be disabled
- Installation is one-time only

## 🔗 Official Resources

- Tesseract GitHub: https://github.com/tesseract-ocr/tesseract
- Windows Installer: https://github.com/UB-Mannheim/tesseract/wiki
- Documentation: https://tesseract-ocr.github.io/

## ✨ After Installation

Once installed:
1. Restart your terminal/command prompt
2. Restart the desktop app
3. URL detection will work automatically
4. Check admin panel to see detected URLs
