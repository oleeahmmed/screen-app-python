# Setup Small Notification Sound

## Quick Setup (Recommended)

### Option 1: Download from Freesound
```bash
cd sounds/
# Download a short notification sound (you'll need to find a suitable one)
# Example: https://freesound.org/people/InspectorJ/sounds/411459/
```

### Option 2: Use System Sound (Linux)
```bash
cd sounds/
# Copy a system notification sound
cp /usr/share/sounds/freedesktop/stereo/message-new-instant.oga notification-small.oga

# Or if you have sox installed, convert to WAV:
sox /usr/share/sounds/freedesktop/stereo/message-new-instant.oga notification-small.wav
```

### Option 3: Create with Python (requires scipy)
```bash
# Install scipy
pip install scipy numpy

# Run the script
python3 create_small_sound.py
```

### Option 4: Manual Download
1. Go to https://mixkit.co/free-sound-effects/notification/
2. Download "Notification tone" or similar short sound
3. Rename to `notification-small.wav`
4. Place in `sounds/` folder

## Verify
```bash
ls -lh sounds/
# Should see both:
# - mixkit-happy-bells-notification-937.wav (big sound)
# - notification-small.wav (small sound)
```

## Test Sound
```bash
# Play the sound (Linux with aplay)
aplay sounds/notification-small.wav

# Or with ffplay
ffplay -nodisp -autoexit sounds/notification-small.wav
```

## Sound Requirements
- **Format**: WAV (preferred) or MP3
- **Duration**: < 1 second (300-500ms ideal)
- **Type**: Short "ding", "pop", or "beep"
- **Volume**: Quiet (will be played at 50% in app)

## Fallback
If `notification-small.wav` is missing, the app will use system beep sound.
