#!/bin/bash
# Build script for Screen Monitor Desktop App

echo "🚀 Building Screen Monitor Desktop App..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Install PyInstaller if not installed
pip install pyinstaller

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist __pycache__

# Build the application
echo "🔨 Building executable..."
pyinstaller ScreenMonitor.spec

# Check if build was successful
if [ -f "dist/ScreenMonitor" ]; then
    echo "✅ Build successful!"
    echo "📦 Executable location: dist/ScreenMonitor"
    echo ""
    echo "To run: ./dist/ScreenMonitor"
else
    echo "❌ Build failed!"
    exit 1
fi
