# 🔊 Notification Sounds

## Dual Sound System

This app uses **two different notification sounds**:

### 1. Big Sound (mixkit-happy-bells-notification-937.wav) ✅
- **When**: App is minimized/background OR task notifications
- **Volume**: 80% (loud)
- **Use**: Important notifications, tasks
- **Status**: ✅ Already added

### 2. Small Sound (notification-small.wav) ⚠️
- **When**: App is open but user on different page
- **Volume**: 50% (quiet, WhatsApp style)
- **Use**: Chat messages while app is active
- **Status**: ⚠️ **NEEDS TO BE ADDED**

## How to Add Small Sound

### Option 1: Download from Pixabay
```bash
cd sounds/
wget "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c6fc0e67.mp3?filename=notification-sound-7062.mp3" -O notification-small.mp3
# Then convert to WAV using online converter or ffmpeg
```

### Option 2: Use System Sound
Copy any short notification sound from your system:
```bash
# Example on Linux
cp /usr/share/sounds/freedesktop/stereo/message-new-instant.oga notification-small.wav
```

### Option 3: Create Your Own
- Use Audacity or any audio editor
- Create a short "ding" or "pop" sound (< 1 second)
- Export as WAV format
- Save as `notification-small.wav`

## Sound Behavior

| Situation | Sound Used | Volume |
|-----------|------------|--------|
| App minimized + chat message | Big | 80% |
| App minimized + task | Big | 80% |
| App open, different page + chat | Small | 50% |
| App open, different page + task | Big | 80% |
| App open, same chat + message | None | - |

## Technical Details

- **Format**: WAV (recommended)
- **Big sound duration**: 1-2 seconds
- **Small sound duration**: < 1 second
- **Fallback**: System beep if file missing

## Disable Sounds

Right-click system tray icon → Uncheck "Sound"
