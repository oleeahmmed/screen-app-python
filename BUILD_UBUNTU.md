# 🐧 Screen Monitor - Ubuntu/Linux Build Guide (AppImage - Zero Dependency)

## Prerequisites (Build Machine Only)

### 1. System Dependencies Install করুন
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-dev
sudo apt install libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0 fuse libfuse2
```

### 2. Verify Installation
```bash
python3 --version
pip3 --version
```

---

## Build Steps (AppImage)

### Step 1: Project Folder এ যান
```bash
cd /path/to/ScreenMonitor
```

### Step 2: Virtual Environment তৈরি করুন
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Dependencies Install করুন
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### Step 4: প্রথমে Normal Build করুন
```bash
pyinstaller --onedir --noconsole --name=ScreenMonitor main.py
```

### Step 5: AppImage Structure তৈরি করুন
```bash
mkdir -p ScreenMonitor.AppDir/usr/bin
mkdir -p ScreenMonitor.AppDir/usr/share/icons/hicolor/256x256/apps

# Files copy করুন
cp -r dist/ScreenMonitor/* ScreenMonitor.AppDir/usr/bin/
cp IBIT-Logo-V3.png ScreenMonitor.AppDir/usr/share/icons/hicolor/256x256/apps/screenmonitor.png
cp IBIT-Logo-V3.png ScreenMonitor.AppDir/screenmonitor.png
```

### Step 6: Desktop File তৈরি করুন
```bash
cat > ScreenMonitor.AppDir/screenmonitor.desktop << EOF
[Desktop Entry]
Name=Screen Monitor
Exec=ScreenMonitor
Icon=screenmonitor
Type=Application
Categories=Utility;
EOF
```

### Step 7: AppRun Script তৈরি করুন
```bash
cat > ScreenMonitor.AppDir/AppRun << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/bin:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/ScreenMonitor" "$@"
EOF
chmod +x ScreenMonitor.AppDir/AppRun
```

### Step 8: AppImage Tool Download ও Build করুন
```bash
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
./appimagetool-x86_64.AppImage ScreenMonitor.AppDir ScreenMonitor-x86_64.AppImage
```

---

## Build Output

Build সফল হলে:
- `ScreenMonitor-x86_64.AppImage` - এটাই আপনার final file

---

## 🎉 Client এর জন্য (Zero Dependency!)

Client কে শুধু এই file টা দিন। তারা:
```bash
chmod +x ScreenMonitor-x86_64.AppImage
./ScreenMonitor-x86_64.AppImage
```

**কোনো কিছু install করতে হবে না!**

---

## Quick Build Script

সব একসাথে করতে `build_appimage.sh` run করুন:
```bash
chmod +x build_appimage.sh
./build_appimage.sh
```

---

## Troubleshooting

| সমস্যা | সমাধান |
|--------|--------|
| FUSE error | `sudo apt install fuse libfuse2` |
| AppImage won't run | `chmod +x ScreenMonitor-x86_64.AppImage` |
| No display | `export DISPLAY=:0` |

---

## Clean Build

```bash
rm -rf build dist __pycache__ ScreenMonitor.AppDir *.AppImage
```
