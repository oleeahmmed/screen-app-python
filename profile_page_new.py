# profile_page_new.py - Complete Profile Page with API Integration

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont
from ui_components import GradientWidget, GlassCard, HeaderWidget, C


class ProfileLoadThread(QThread):
    """Thread to load profile data from API"""
    finished = pyqtSignal(bool, dict)
    
    def __init__(self, auth):
        super().__init__()
        self.auth = auth
    
    def run(self):
        """Load profile in background"""
        try:
            ok, data = self.auth.get_user_profile()
            self.finished.emit(ok, data if data else {})
        except Exception as e:
            print(f"Profile load thread error: {e}")
            self.finished.emit(False, {})


class ProfileUpdateThread(QThread):
    """Thread to update profile via API"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, auth, email, first_name, last_name):
        super().__init__()
        self.auth = auth
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
    
    def run(self):
        """Update profile in background"""
        try:
            ok, msg = self.auth.update_user_profile(self.email, self.first_name, self.last_name)
            self.finished.emit(ok, msg)
        except Exception as e:
            print(f"Profile update thread error: {e}")
            self.finished.emit(False, str(e))


class PasswordChangeThread(QThread):
    """Thread to change password via API"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, auth, current_pwd, new_pwd):
        super().__init__()
        self.auth = auth
        self.current_pwd = current_pwd
        self.new_pwd = new_pwd
    
    def run(self):
        """Change password in background"""
        try:
            ok, msg = self.auth.change_password(self.current_pwd, self.new_pwd)
            self.finished.emit(ok, msg)
        except Exception as e:
            print(f"Password change thread error: {e}")
            self.finished.emit(False, str(e))


class ProfilePage(QWidget):
    """Complete Profile Page with API Integration"""
    subscription_clicked = pyqtSignal()
    profile_updated = pyqtSignal()
    
    def __init__(self, auth, parent=None):
        super().__init__()
        self.auth = auth
        self.parent_dash = parent
        self.username = "User"
        self.days_remaining = 0
        self.profile_data = {}
        self.is_loading = False
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Container
        self.container = GradientWidget()
        self.container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Header
        self.header = HeaderWidget(self.username, self.days_remaining)
        if self.parent_dash:
            self.header.menu_clicked.connect(self.parent_dash.show_menu)
            self.header.subscription_clicked.connect(self.subscription_clicked.emit)
        container_layout.addWidget(self.header)
        
        # Title
        title_widget = QWidget()
        title_widget.setStyleSheet("background: transparent;")
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(25, 10, 25, 15)
        
        profile_title = QLabel("PROFILE")
        profile_title.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 28px; font-weight: bold;")
        title_layout.addWidget(profile_title)
        title_layout.addStretch()
        container_layout.addWidget(title_widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255,255,255,0.3);
                border-radius: 3px;
            }
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(25, 10, 25, 20)
        self.content_layout.setSpacing(15)
        
        # Avatar
        avatar_container = QWidget()
        avatar_container.setStyleSheet("background: transparent;")
        avatar_layout = QVBoxLayout(avatar_container)
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar_layout.setSpacing(10)
        
        avatar_label = QLabel("👤")
        avatar_label.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {C['header_blue']}, stop:1 {C['green']});
            color: white;
            font-size: 48px;
            border-radius: 50px;
        """)
        avatar_label.setFixedSize(100, 100)
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_layout.addWidget(avatar_label)
        
        self.username_display = QLabel(self.username)
        self.username_display.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 18px; font-weight: 600;")
        self.username_display.setAlignment(Qt.AlignCenter)
        avatar_layout.addWidget(self.username_display)
        
        self.content_layout.addWidget(avatar_container)
        
        # Loading indicator
        self.loading_label = QLabel("Loading profile...")
        self.loading_label.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 14px;")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        self.content_layout.addWidget(self.loading_label)
        
        # Profile Info Card
        self.create_profile_card()
        
        # Password Change Card
        self.create_password_card()
        
        self.content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        container_layout.addWidget(scroll, 1)
        layout.addWidget(self.container)
    
    def create_profile_card(self):
        """Create profile information card"""
        self.info_card = GlassCard()
        info_layout = QVBoxLayout(self.info_card)
        info_layout.setContentsMargins(18, 15, 18, 15)
        info_layout.setSpacing(12)
        
        info_title = QLabel("📋 Profile Information")
        info_title.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 15px; font-weight: 600;")
        info_layout.addWidget(info_title)
        
        # Email
        self.email_input = self.create_input("📧 Email", "email@example.com")
        info_layout.addWidget(self.email_input)
        
        # First Name
        self.fname_input = self.create_input("👤 First Name", "John")
        info_layout.addWidget(self.fname_input)
        
        # Last Name
        self.lname_input = self.create_input("👤 Last Name", "Doe")
        info_layout.addWidget(self.lname_input)
        
        # Update button
        self.update_btn = QPushButton("💾 Update Profile")
        self.update_btn.setFixedHeight(42)
        self.update_btn.setCursor(Qt.PointingHandCursor)
        self.update_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C['header_blue']}, stop:1 #1976D2);
                color: white;
                border: none;
                border-radius: 21px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1976D2, stop:1 {C['header_blue']});
            }}
            QPushButton:disabled {{
                background: rgba(255,255,255,0.1);
                color: rgba(255,255,255,0.5);
            }}
        """)
        self.update_btn.clicked.connect(self.update_profile)
        info_layout.addWidget(self.update_btn)
        
        self.content_layout.addWidget(self.info_card)
    
    def create_password_card(self):
        """Create password change card"""
        self.pwd_card = GlassCard()
        pwd_layout = QVBoxLayout(self.pwd_card)
        pwd_layout.setContentsMargins(18, 15, 18, 15)
        pwd_layout.setSpacing(12)
        
        pwd_title = QLabel("🔐 Change Password")
        pwd_title.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 15px; font-weight: 600;")
        pwd_layout.addWidget(pwd_title)
        
        # Current Password
        self.current_pwd = self.create_input("🔒 Current Password", "Enter current password", password=True)
        pwd_layout.addWidget(self.current_pwd)
        
        # New Password
        self.new_pwd = self.create_input("🔑 New Password", "Enter new password", password=True)
        pwd_layout.addWidget(self.new_pwd)
        
        # Confirm Password
        self.confirm_pwd = self.create_input("🔑 Confirm Password", "Confirm new password", password=True)
        pwd_layout.addWidget(self.confirm_pwd)
        
        # Change Password button
        self.change_pwd_btn = QPushButton("🔐 Change Password")
        self.change_pwd_btn.setFixedHeight(42)
        self.change_pwd_btn.setCursor(Qt.PointingHandCursor)
        self.change_pwd_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C['orange']}, stop:1 #F5B043);
                color: white;
                border: none;
                border-radius: 21px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F5B043, stop:1 {C['orange']});
            }}
            QPushButton:disabled {{
                background: rgba(255,255,255,0.1);
                color: rgba(255,255,255,0.5);
            }}
        """)
        self.change_pwd_btn.clicked.connect(self.change_password)
        pwd_layout.addWidget(self.change_pwd_btn)
        
        self.content_layout.addWidget(self.pwd_card)
    
    def create_input(self, placeholder, default="", password=False):
        """Create styled input field"""
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        if password:
            input_field.setEchoMode(QLineEdit.Password)
        input_field.setFixedHeight(40)
        input_field.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0,0,0,0.3);
                color: {C['text_white']};
                border: 1.5px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 0 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {C['header_blue'] if not password else C['orange']};
                background: rgba(0,0,0,0.4);
            }}
        """)
        return input_field
    
    def set_username(self, name, days_remaining=0):
        """Set username and subscription info"""
        self.username = name
        self.days_remaining = days_remaining
        self.username_display.setText(name)
        if hasattr(self, 'header'):
            self.header.set_username(name, days_remaining)
    
    def showEvent(self, event):
        """Load profile when page is shown"""
        super().showEvent(event)
        if not self.profile_data:
            self.load_profile()
    
    def load_profile(self):
        """Load profile data from API"""
        if self.is_loading:
            return
        
        self.is_loading = True
        self.loading_label.show()
        self.update_btn.setEnabled(False)
        self.change_pwd_btn.setEnabled(False)
        
        # Load in background thread
        self.load_thread = ProfileLoadThread(self.auth)
        self.load_thread.finished.connect(self.on_profile_loaded)
        self.load_thread.start()
    
    def on_profile_loaded(self, success, data):
        """Handle profile load result"""
        self.is_loading = False
        self.loading_label.hide()
        self.update_btn.setEnabled(True)
        self.change_pwd_btn.setEnabled(True)
        
        if success and data:
            self.profile_data = data
            self.email_input.setText(data.get('email', ''))
            self.fname_input.setText(data.get('first_name', ''))
            self.lname_input.setText(data.get('last_name', ''))
            print("✅ Profile loaded successfully")
        else:
            print("⚠️ Failed to load profile, using cached data")
            # Try to load from user_info
            if self.auth.user_info:
                self.email_input.setText(self.auth.user_info.get('email', ''))
                self.fname_input.setText(self.auth.user_info.get('first_name', ''))
                self.lname_input.setText(self.auth.user_info.get('last_name', ''))
    
    def update_profile(self):
        """Update profile information"""
        email = self.email_input.text().strip()
        first_name = self.fname_input.text().strip()
        last_name = self.lname_input.text().strip()
        
        # Validation
        if not email:
            QMessageBox.warning(self, "Validation Error", "Email is required")
            return
        
        if '@' not in email or '.' not in email:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid email address")
            return
        
        # Disable button during update
        self.update_btn.setEnabled(False)
        self.update_btn.setText("Updating...")
        
        # Update in background thread
        self.update_thread = ProfileUpdateThread(self.auth, email, first_name, last_name)
        self.update_thread.finished.connect(self.on_profile_updated)
        self.update_thread.start()
    
    def on_profile_updated(self, success, message):
        """Handle profile update result"""
        self.update_btn.setEnabled(True)
        self.update_btn.setText("💾 Update Profile")
        
        if success:
            QMessageBox.information(self, "Success", "Profile updated successfully!")
            self.profile_updated.emit()
            # Reload profile to get latest data
            self.profile_data = {}
            self.load_profile()
        else:
            QMessageBox.warning(self, "Update Failed", message or "Failed to update profile")
    
    def change_password(self):
        """Change user password"""
        current = self.current_pwd.text()
        new = self.new_pwd.text()
        confirm = self.confirm_pwd.text()
        
        # Validation
        if not current or not new or not confirm:
            QMessageBox.warning(self, "Validation Error", "All password fields are required")
            return
        
        if new != confirm:
            QMessageBox.warning(self, "Validation Error", "New passwords do not match")
            return
        
        if len(new) < 6:
            QMessageBox.warning(self, "Validation Error", "Password must be at least 6 characters")
            return
        
        # Disable button during change
        self.change_pwd_btn.setEnabled(False)
        self.change_pwd_btn.setText("Changing...")
        
        # Change in background thread
        self.pwd_thread = PasswordChangeThread(self.auth, current, new)
        self.pwd_thread.finished.connect(self.on_password_changed)
        self.pwd_thread.start()
    
    def on_password_changed(self, success, message):
        """Handle password change result"""
        self.change_pwd_btn.setEnabled(True)
        self.change_pwd_btn.setText("🔐 Change Password")
        
        if success:
            QMessageBox.information(self, "Success", "Password changed successfully!")
            # Clear password fields
            self.current_pwd.clear()
            self.new_pwd.clear()
            self.confirm_pwd.clear()
        else:
            QMessageBox.warning(self, "Change Failed", message or "Failed to change password")
