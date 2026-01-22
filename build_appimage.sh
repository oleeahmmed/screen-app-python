#!/bin/bash
# AppImage Build Script for Screen Monitor
# Zero-dependency distribution for Linux clients

set -e

echo "🚀 Building Screen Monitor AppImage..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Install PyInstaller
pip install pyinstaller

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist __pycache__ ScreenMonitor.AppDir *.AppImage

# Build with PyInstaller (onedir mode for AppImage)
echo "🔨 Building with PyInstaller..."
pyinstaller --onedir --noconsole --name=ScreenMonitor main.py

# Create AppImage directory structure
echo "📁 Creating AppImage structure..."
mkdir -p ScreenMonitor.AppDir/usr/bin
mkdir -p ScreenMonitor.AppDir/usr/share/icons/hicolor/256x256/apps

# Copy files
cp -r dist/ScreenMonitor/* ScreenMonitor.AppDir/usr/bin/
cp IBIT-Logo-V3.png ScreenMonitor.AppDir/usr/share/icons/hicolor/256x256/apps/screenmonitor.png
cp IBIT-Logo-V3.png ScreenMonitor.AppDir/screenmonitor.png

# Create desktop file
cat > ScreenMonitor.AppDir/screenmonitor.desktop << EOF
[Desktop Entry]
Name=Screen Monitor
Exec=ScreenMonitor
Icon=screenmonitor
Type=Application
Categories=Utility;
EOF

# Create AppRun
cat > ScreenMonitor.AppDir/AppRun << 'APPRUN'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/bin:${LD_LIBRARY_PATH}"
export QT_PLUGIN_PATH="${HERE}/usr/bin/PyQt5/Qt5/plugins"
exec "${HERE}/usr/bin/ScreenMonitor" "$@"
APPRUN
chmod +x ScreenMonitor.AppDir/AppRun

# Download appimagetool if not exists
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "📥 Downloading appimagetool..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Build AppImage
echo "📦 Creating AppImage..."
./appimagetool-x86_64.AppImage ScreenMonitor.AppDir ScreenMonitor-x86_64.AppImage

# Check result
if [ -f "ScreenMonitor-x86_64.AppImage" ]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
    echo ""
    echo "📦 Output: ScreenMonitor-x86_64.AppImage"
    echo "📏 Size: $(du -h ScreenMonitor-x86_64.AppImage | cut -f1)"
    echo ""
    echo "🎉 Client কে এই file দিন - কোনো dependency install করতে হবে না!"
    echo "   chmod +x ScreenMonitor-x86_64.AppImage"
    echo "   ./ScreenMonitor-x86_64.AppImage"
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi
