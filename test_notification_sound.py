#!/usr/bin/env python3
"""
Test notification sound playback
"""

import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
import os

class SoundTester(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notification Sound Tester")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # Info label
        self.info_label = QLabel("Click buttons to test notification sounds")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Sound file path
        self.sound_file = os.path.join(os.path.dirname(__file__), "sounds", "mixkit-happy-bells-notification-937.wav")
        
        # File exists label
        exists = os.path.exists(self.sound_file)
        exists_label = QLabel(f"Sound file exists: {'✅ YES' if exists else '❌ NO'}")
        exists_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(exists_label)
        
        # File path label
        path_label = QLabel(f"Path: {self.sound_file}")
        path_label.setWordWrap(True)
        path_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(path_label)
        
        # Media player
        self.player = QMediaPlayer()
        
        # Test button 1: QMediaPlayer
        btn1 = QPushButton("🔊 Test with QMediaPlayer (80% volume)")
        btn1.clicked.connect(self.test_qmediaplayer)
        layout.addWidget(btn1)
        
        # Test button 2: System beep
        btn2 = QPushButton("🔔 Test System Beep")
        btn2.clicked.connect(self.test_system_beep)
        layout.addWidget(btn2)
        
        # Test button 3: aplay
        btn3 = QPushButton("🎵 Test with aplay (Linux)")
        btn3.clicked.connect(self.test_aplay)
        layout.addWidget(btn3)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def test_qmediaplayer(self):
        """Test with QMediaPlayer"""
        try:
            print(f"Testing QMediaPlayer...")
            print(f"Sound file: {self.sound_file}")
            print(f"File exists: {os.path.exists(self.sound_file)}")
            
            if os.path.exists(self.sound_file):
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.sound_file)))
                self.player.setVolume(80)
                self.player.play()
                self.status_label.setText("✅ Playing with QMediaPlayer...")
                print("✅ QMediaPlayer.play() called")
            else:
                self.status_label.setText("❌ Sound file not found!")
                print("❌ Sound file not found")
        except Exception as e:
            self.status_label.setText(f"❌ Error: {e}")
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def test_system_beep(self):
        """Test system beep"""
        try:
            print("Testing system beep...")
            QApplication.beep()
            self.status_label.setText("✅ System beep played")
            print("✅ System beep called")
        except Exception as e:
            self.status_label.setText(f"❌ Error: {e}")
            print(f"❌ Error: {e}")
    
    def test_aplay(self):
        """Test with aplay command"""
        try:
            print("Testing aplay...")
            import subprocess
            subprocess.Popen(['aplay', self.sound_file], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            self.status_label.setText("✅ Playing with aplay...")
            print("✅ aplay started")
        except Exception as e:
            self.status_label.setText(f"❌ Error: {e}")
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    tester = SoundTester()
    tester.show()
    sys.exit(app.exec_())
