#!/usr/bin/env python3
"""
Create a simple small notification sound using numpy and scipy
This creates a short "ding" sound similar to WhatsApp
"""

import numpy as np
from scipy.io import wavfile
import os

def create_notification_sound():
    """Create a short notification sound"""
    # Parameters
    sample_rate = 44100  # Hz
    duration = 0.3  # seconds (300ms - very short)
    
    # Create time array
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create a pleasant "ding" sound using multiple frequencies
    # Main tone (higher pitch for notification)
    freq1 = 800  # Hz
    freq2 = 1200  # Hz (harmonic)
    
    # Generate tones
    tone1 = np.sin(2 * np.pi * freq1 * t)
    tone2 = np.sin(2 * np.pi * freq2 * t) * 0.5  # Quieter harmonic
    
    # Combine tones
    sound = tone1 + tone2
    
    # Apply envelope (fade in and fade out)
    # Quick attack, longer decay
    attack = int(0.01 * sample_rate)  # 10ms attack
    decay = int(0.25 * sample_rate)   # 250ms decay
    
    envelope = np.ones_like(sound)
    
    # Attack (fade in)
    envelope[:attack] = np.linspace(0, 1, attack)
    
    # Decay (fade out)
    if decay < len(envelope):
        envelope[-decay:] = np.linspace(1, 0, decay)
    
    # Apply envelope
    sound = sound * envelope
    
    # Normalize to 16-bit range (but keep it quiet)
    sound = sound / np.max(np.abs(sound))  # Normalize to -1 to 1
    sound = sound * 0.5  # Reduce volume to 50%
    sound = (sound * 32767).astype(np.int16)
    
    # Save as WAV file
    output_path = os.path.join(os.path.dirname(__file__), 'sounds', 'notification-small.wav')
    wavfile.write(output_path, sample_rate, sound)
    
    print(f"✅ Created notification sound: {output_path}")
    print(f"   Duration: {duration}s")
    print(f"   Sample rate: {sample_rate}Hz")
    print(f"   Frequencies: {freq1}Hz, {freq2}Hz")

if __name__ == "__main__":
    try:
        create_notification_sound()
    except ImportError as e:
        print("❌ Error: scipy is required to create the sound")
        print("   Install it with: pip install scipy")
        print(f"   Error: {e}")
    except Exception as e:
        print(f"❌ Error creating sound: {e}")
