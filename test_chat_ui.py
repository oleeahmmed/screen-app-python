#!/usr/bin/env python3
"""
Test script to verify chat UI components are working
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

# Test imports
print("Testing imports...")
try:
    from ui_components import BottomNavBar, C
    print("✅ ui_components imported successfully")
except Exception as e:
    print(f"❌ Error importing ui_components: {e}")
    sys.exit(1)

try:
    from chat_page import ChatPage
    print("✅ chat_page imported successfully")
except Exception as e:
    print(f"❌ Error importing chat_page: {e}")
    sys.exit(1)

try:
    from chat_manager import ChatManager
    print("✅ chat_manager imported successfully")
except Exception as e:
    print(f"❌ Error importing chat_manager: {e}")
    sys.exit(1)

try:
    from chat_api import ChatAPI
    print("✅ chat_api imported successfully")
except Exception as e:
    print(f"❌ Error importing chat_api: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("All imports successful! Creating test window...")
print("="*50 + "\n")

# Create test window
app = QApplication(sys.argv)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat UI Test")
        self.setFixedSize(420, 620)
        self.setStyleSheet(f"background: {C['bg_dark']};")
        
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Chat Feature Test")
        title.setStyleSheet(f"color: {C['text_white']}; font-size: 24px; font-weight: bold; padding: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info
        info = QLabel("Bottom navigation should show 4 buttons:\n📊 Attendance | ✓ Tasks | 💬 Chat | 👤 Profile")
        info.setStyleSheet(f"color: {C['text_gray']}; font-size: 14px; padding: 20px;")
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        layout.addStretch()
        
        # Bottom navigation
        self.nav = BottomNavBar()
        self.nav.nav_clicked.connect(self.on_nav_clicked)
        layout.addWidget(self.nav)
        
        print("✅ Test window created with bottom navigation")
        print("✅ Navigation has", len(self.nav.buttons), "buttons")
        
        # Print button labels
        for i, btn in enumerate(self.nav.buttons):
            print(f"   Button {i}: {btn.text()}")
    
    def on_nav_clicked(self, idx):
        labels = ["Attendance", "Tasks", "Chat", "Profile"]
        print(f"✅ Clicked: {labels[idx]} (index {idx})")

# Run test
window = TestWindow()
window.show()

print("\n" + "="*50)
print("✅ TEST SUCCESSFUL!")
print("="*50)
print("\nThe window should show:")
print("1. Title at top")
print("2. Info text in middle")
print("3. Bottom navigation with 4 buttons")
print("4. Chat button (💬) should be the 3rd button")
print("\nClick the buttons to test navigation!")
print("Close the window when done.")
print("="*50 + "\n")

sys.exit(app.exec_())
