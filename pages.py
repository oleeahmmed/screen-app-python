# pages.py - Page Components (Dashboard, Tasks, Profile, Chat)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from datetime import datetime
import pytz

from ui_components import GradientWidget, GlassCard, HeaderWidget, C, BottomNavBar

try:
    from config import API_BASE_URL
except ImportError:
    API_BASE_URL = "https://att.igenhr.com/api"

# Import ChatPage
try:
    from chat_page import ChatPage
except ImportError:
    ChatPage = None


class DashboardPage(QWidget):
    """Main dashboard with clock and work timer"""
    subscription_clicked = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__()
        self.p = parent
        self.work_seconds = 0
        self.is_clocked_in = False
        self.username = "User"
        self.days_remaining = 0
        self.access_granted = True
        self.company_timezone = 'UTC'
        self.today_work_seconds = 0
        
        self.init_ui()
        
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        
        self.work_timer = QTimer()
        self.work_timer.timeout.connect(self.update_work_time)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.container = GradientWidget()
        self.container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 20)
        container_layout.setSpacing(10)
        
        self.header = HeaderWidget(self.username, self.days_remaining)
        self.header.menu_clicked.connect(self.p.show_menu)
        self.header.subscription_clicked.connect(self.subscription_clicked.emit)
        container_layout.addWidget(self.header)
        
        # Date and Time display
        datetime_widget = QWidget()
        datetime_widget.setStyleSheet("background: transparent;")
        datetime_layout = QVBoxLayout(datetime_widget)
        datetime_layout.setContentsMargins(25, 0, 25, 0)
        datetime_layout.setSpacing(15)
        
        # Date
        date_container = QWidget()
        date_container.setStyleSheet("background: transparent;")
        date_layout = QHBoxLayout(date_container)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setAlignment(Qt.AlignCenter)
        
        self.day_label = QLabel(datetime.now().strftime("%A").upper())
        self.day_label.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 24px; font-weight: 700; letter-spacing: 3px;")
        date_layout.addWidget(self.day_label)
        
        date_separator = QLabel("•")
        date_separator.setStyleSheet(f"background: transparent; color: {C['green']}; font-size: 22px; margin: 0 12px;")
        date_layout.addWidget(date_separator)
        
        self.date_label = QLabel(datetime.now().strftime("%d %B %Y"))
        self.date_label.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 17px; font-weight: 500;")
        date_layout.addWidget(self.date_label)
        
        datetime_layout.addWidget(date_container)
        
        # Clocks row
        clocks_row = QWidget()
        clocks_row.setStyleSheet("background: transparent;")
        clocks_layout = QHBoxLayout(clocks_row)
        clocks_layout.setContentsMargins(0, 10, 0, 0)
        clocks_layout.setSpacing(20)
        clocks_layout.setAlignment(Qt.AlignCenter)
        
        # Company Time Clock
        company_clock_card = GlassCard()
        company_clock_card.setFixedSize(160, 90)
        company_layout = QVBoxLayout(company_clock_card)
        company_layout.setContentsMargins(15, 10, 15, 10)
        company_layout.setSpacing(4)
        company_layout.setAlignment(Qt.AlignCenter)
        
        self.company_tz_label = QLabel("COMPANY TIME")
        self.company_tz_label.setStyleSheet(f"background: transparent; color: {C['green']}; font-size: 10px; font-weight: 700; letter-spacing: 1px;")
        self.company_tz_label.setAlignment(Qt.AlignCenter)
        company_layout.addWidget(self.company_tz_label)
        
        company_time_row = QHBoxLayout()
        company_time_row.setAlignment(Qt.AlignCenter)
        company_time_row.setSpacing(4)
        self.company_time_label = QLabel("10:50")
        self.company_time_label.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 32px; font-weight: 700; letter-spacing: 1px;")
        company_time_row.addWidget(self.company_time_label)
        self.company_ampm_label = QLabel("PM")
        self.company_ampm_label.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 12px; font-weight: 600; margin-top: 8px;")
        company_time_row.addWidget(self.company_ampm_label)
        company_layout.addLayout(company_time_row)
        
        self.company_tz_detail = QLabel("UTC")
        self.company_tz_detail.setStyleSheet(f"background: transparent; color: rgba(255,255,255,0.7); font-size: 9px; font-weight: 500;")
        self.company_tz_detail.setAlignment(Qt.AlignCenter)
        company_layout.addWidget(self.company_tz_detail)
        
        clocks_layout.addWidget(company_clock_card)
        
        # User Local Time Clock
        user_clock_card = GlassCard()
        user_clock_card.setFixedSize(160, 90)
        user_layout = QVBoxLayout(user_clock_card)
        user_layout.setContentsMargins(15, 10, 15, 10)
        user_layout.setSpacing(4)
        user_layout.setAlignment(Qt.AlignCenter)
        
        self.local_tz_label = QLabel("YOUR TIME")
        self.local_tz_label.setStyleSheet(f"background: transparent; color: {C['header_blue']}; font-size: 10px; font-weight: 700; letter-spacing: 1px;")
        self.local_tz_label.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(self.local_tz_label)
        
        local_time_row = QHBoxLayout()
        local_time_row.setAlignment(Qt.AlignCenter)
        local_time_row.setSpacing(4)
        self.time_label = QLabel("10:50")
        self.time_label.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 32px; font-weight: 700; letter-spacing: 1px;")
        local_time_row.addWidget(self.time_label)
        self.ampm_label = QLabel("PM")
        self.ampm_label.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 12px; font-weight: 600; margin-top: 8px;")
        local_time_row.addWidget(self.ampm_label)
        user_layout.addLayout(local_time_row)
        
        self.local_tz_detail = QLabel("Local")
        self.local_tz_detail.setStyleSheet(f"background: transparent; color: rgba(255,255,255,0.7); font-size: 9px; font-weight: 500;")
        self.local_tz_detail.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(self.local_tz_detail)
        
        clocks_layout.addWidget(user_clock_card)
        
        datetime_layout.addWidget(clocks_row)
        container_layout.addWidget(datetime_widget)
        
        container_layout.addStretch()
        
        # Work timer
        timer_container = QVBoxLayout()
        timer_container.setAlignment(Qt.AlignCenter)
        
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 72px; font-weight: bold; letter-spacing: 4px;")
        timer_container.addWidget(self.timer_label)
        
        self.today_work_label = QLabel("Today Work: 0h 0m")
        self.today_work_label.setAlignment(Qt.AlignCenter)
        self.today_work_label.setStyleSheet(f"background: transparent; color: {C['green']}; font-size: 18px; font-weight: 600; margin-top: 10px;")
        timer_container.addWidget(self.today_work_label)
        
        container_layout.addLayout(timer_container)
        
        self.access_msg = QLabel("")
        self.access_msg.setAlignment(Qt.AlignCenter)
        self.access_msg.setStyleSheet(f"background: transparent; color: {C['orange']}; font-size: 14px; padding: 10px;")
        self.access_msg.setWordWrap(True)
        self.access_msg.hide()
        container_layout.addWidget(self.access_msg)
        
        container_layout.addStretch()
        
        self.btn_container = QWidget()
        self.btn_container.setStyleSheet("background: transparent;")
        btn_layout = QHBoxLayout(self.btn_container)
        btn_layout.setAlignment(Qt.AlignCenter)
        self.clock_btn = QPushButton("Clock In")
        self.clock_btn.setFixedSize(200, 55)
        self.clock_btn.setCursor(Qt.PointingHandCursor)
        self.clock_btn.setStyleSheet(f"QPushButton {{background: {C['green']}; color: white; border: none; border-radius: 27px; font-size: 20px; font-weight: bold;}} QPushButton:hover {{background: #5FE076;}}")
        self.clock_btn.clicked.connect(self.toggle_clock)
        btn_layout.addWidget(self.clock_btn)
        container_layout.addWidget(self.btn_container)
        container_layout.addSpacing(20)
        
        layout.addWidget(self.container)
    
    def set_username(self, name, days_remaining=0, access_granted=True, access_message=""):
        self.username = name
        self.days_remaining = days_remaining
        self.access_granted = access_granted
        
        if access_granted:
            self.btn_container.show()
            self.access_msg.hide()
        else:
            self.btn_container.hide()
            self.access_msg.setText(access_message or "⚠️ Subscription expired or access denied")
            self.access_msg.show()
    
    def update_clock(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%I:%M").lstrip('0') or '12')
        self.ampm_label.setText(now.strftime("%p"))
        self.day_label.setText(now.strftime("%A").upper())
        self.date_label.setText(now.strftime("%d %B %Y"))
        
        try:
            company_tz = pytz.timezone(self.company_timezone)
            company_now = datetime.now(company_tz)
            self.company_time_label.setText(company_now.strftime("%I:%M").lstrip('0') or '12')
            self.company_ampm_label.setText(company_now.strftime("%p"))
            self.company_tz_detail.setText(self.company_timezone)
        except:
            self.company_time_label.setText(now.strftime("%I:%M").lstrip('0') or '12')
            self.company_ampm_label.setText(now.strftime("%p"))
            self.company_tz_detail.setText("UTC")
    
    def update_today_work_duration(self, total_seconds):
        self.today_work_seconds = total_seconds
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        self.today_work_label.setText(f"Today Work: {hours}h {minutes}m")
    
    def set_company_timezone(self, timezone_str):
        self.company_timezone = timezone_str or 'UTC'
    
    def update_work_time(self):
        self.work_seconds += 1
        h = self.work_seconds // 3600
        m = (self.work_seconds % 3600) // 60
        s = self.work_seconds % 60
        self.timer_label.setText(f"{h:02d}:{m:02d}:{s:02d}")
    
    def toggle_clock(self):
        if not self.is_clocked_in:
            self.clock_in()
        else:
            self.clock_out()
    
    def clock_in(self):
        ok, msg = self.p.start_work()
        if not ok:
            QMessageBox.warning(self, "Clock In Failed", msg)
            return
        
        self.is_clocked_in = True
        self.work_seconds = 0
        self.work_timer.start(1000)
        self.clock_btn.setText("Clock Out")
        self.clock_btn.setStyleSheet(f"QPushButton {{background: {C['red']}; color: white; border: none; border-radius: 27px; font-size: 20px; font-weight: bold;}} QPushButton:hover {{background: #F25C4E;}}")
    
    def clock_out(self):
        ok, msg = self.p.stop_work()
        self.is_clocked_in = False
        self.work_timer.stop()
        self.clock_btn.setText("Clock In")
        self.clock_btn.setStyleSheet(f"QPushButton {{background: {C['green']}; color: white; border: none; border-radius: 27px; font-size: 20px; font-weight: bold;}} QPushButton:hover {{background: #5FE076;}}")


class TasksPage(QWidget):
    """Tasks management page"""
    subscription_clicked = pyqtSignal()
    
    def __init__(self, task_mgr, signals, parent=None):
        super().__init__()
        self.task_mgr = task_mgr
        self.signals = signals
        self.parent_dash = parent
        self.tasks = []
        self.show_pending = True
        self.username = "User"
        self.days_remaining = 0
        self.init_ui()
        self.signals.task_refresh_signal.connect(self.refresh)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.container = GradientWidget()
        self.container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
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
        
        tasks_title = QLabel("TASKS")
        tasks_title.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 28px; font-weight: bold;")
        title_layout.addWidget(tasks_title)
        title_layout.addStretch()
        
        self.pending_btn = QPushButton("Pending")
        self.pending_btn.setCursor(Qt.PointingHandCursor)
        self.pending_btn.setStyleSheet(f"QPushButton {{background: transparent; color: {C['text_white']}; border: none; font-size: 16px; font-weight: 500; padding: 5px 15px;}}")
        self.pending_btn.clicked.connect(lambda: self.set_filter(True))
        title_layout.addWidget(self.pending_btn)
        
        self.complete_btn = QPushButton("Complete")
        self.complete_btn.setCursor(Qt.PointingHandCursor)
        self.complete_btn.setStyleSheet(f"QPushButton {{background: transparent; color: {C['text_gray']}; border: none; font-size: 16px; font-weight: 500; padding: 5px 15px;}}")
        self.complete_btn.clicked.connect(lambda: self.set_filter(False))
        title_layout.addWidget(self.complete_btn)
        
        container_layout.addWidget(title_widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea {background: transparent; border: none;} QScrollBar:vertical {background: transparent; width: 6px;} QScrollBar::handle:vertical {background: rgba(255,255,255,0.3); border-radius: 3px;}")
        
        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(20, 0, 20, 20)
        self.list_layout.setSpacing(12)
        self.list_layout.addStretch()
        
        scroll.setWidget(self.list_container)
        container_layout.addWidget(scroll, 1)
        layout.addWidget(self.container)
    
    def set_username(self, name, days_remaining=0):
        self.username = name
        self.days_remaining = days_remaining
    
    def set_filter(self, show_pending):
        self.show_pending = show_pending
        self.pending_btn.setStyleSheet(f"QPushButton {{background: transparent; color: {C['text_white'] if show_pending else C['text_gray']}; border: none; font-size: 16px; font-weight: 500; padding: 5px 15px;}}")
        self.complete_btn.setStyleSheet(f"QPushButton {{background: transparent; color: {C['text_gray'] if show_pending else C['text_white']}; border: none; font-size: 16px; font-weight: 500; padding: 5px 15px;}}")
        self.refresh()
    
    def refresh(self):
        self.tasks = self.task_mgr.get_tasks()
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        filtered = [t for t in self.tasks if t.get('completed', False) != self.show_pending]
        
        if not filtered:
            empty = QLabel("No tasks" if self.show_pending else "No completed tasks")
            empty.setStyleSheet(f"color: {C['text_gray']}; font-size: 16px; padding: 40px;")
            empty.setAlignment(Qt.AlignCenter)
            self.list_layout.insertWidget(0, empty)
    
    def showEvent(self, e):
        super().showEvent(e)
        self.refresh()


class ProfilePage(QWidget):
    """User profile page with settings and password change"""
    subscription_clicked = pyqtSignal()
    profile_updated = pyqtSignal()
    
    def __init__(self, auth, parent=None):
        super().__init__()
        self.auth = auth
        self.parent_dash = parent
        self.username = "User"
        self.days_remaining = 0
        self.profile_loaded = False
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.container = GradientWidget()
        self.container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
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
        scroll.setStyleSheet("QScrollArea {background: transparent; border: none;} QScrollBar:vertical {background: transparent; width: 6px;} QScrollBar::handle:vertical {background: rgba(255,255,255,0.3); border-radius: 3px;}")
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(25, 10, 25, 20)
        content_layout.setSpacing(15)
        
        # Avatar
        avatar_label = QLabel("👤")
        avatar_label.setStyleSheet(f"background: {C['header_blue']}; color: white; font-size: 48px; border-radius: 50px;")
        avatar_label.setFixedSize(100, 100)
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_layout = QVBoxLayout()
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar_layout.addWidget(avatar_label)
        content_layout.addLayout(avatar_layout)
        
        # Username
        self.username_display = QLabel(self.username)
        self.username_display.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 18px; font-weight: 600;")
        self.username_display.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.username_display)
        
        # Profile Info Card
        info_card = GlassCard()
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(18, 15, 18, 15)
        info_layout.setSpacing(10)
        
        info_title = QLabel("Profile Information")
        info_title.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 14px; font-weight: 600;")
        info_layout.addWidget(info_title)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("📧 Email")
        self.email_input.setFixedHeight(40)
        self.email_input.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0,0,0,0.3);
                color: {C['text_white']};
                border: 1.5px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 0 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {C['header_blue']};
            }}
        """)
        info_layout.addWidget(self.email_input)
        
        # First Name
        self.fname_input = QLineEdit()
        self.fname_input.setPlaceholderText("👤 First Name")
        self.fname_input.setFixedHeight(40)
        self.fname_input.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0,0,0,0.3);
                color: {C['text_white']};
                border: 1.5px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 0 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {C['header_blue']};
            }}
        """)
        info_layout.addWidget(self.fname_input)
        
        # Last Name
        self.lname_input = QLineEdit()
        self.lname_input.setPlaceholderText("👤 Last Name")
        self.lname_input.setFixedHeight(40)
        self.lname_input.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0,0,0,0.3);
                color: {C['text_white']};
                border: 1.5px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 0 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {C['header_blue']};
            }}
        """)
        info_layout.addWidget(self.lname_input)
        
        # Update button
        update_btn = QPushButton("💾 Update Profile")
        update_btn.setFixedHeight(42)
        update_btn.setCursor(Qt.PointingHandCursor)
        update_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['header_blue']};
                color: white;
                border: none;
                border-radius: 21px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #1976D2;
            }}
        """)
        update_btn.clicked.connect(self.update_profile)
        info_layout.addWidget(update_btn)
        
        content_layout.addWidget(info_card)
        
        # Password Change Card
        pwd_card = GlassCard()
        pwd_layout = QVBoxLayout(pwd_card)
        pwd_layout.setContentsMargins(18, 15, 18, 15)
        pwd_layout.setSpacing(10)
        
        pwd_title = QLabel("Change Password")
        pwd_title.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 14px; font-weight: 600;")
        pwd_layout.addWidget(pwd_title)
        
        # Current Password
        self.current_pwd = QLineEdit()
        self.current_pwd.setPlaceholderText("🔒 Current Password")
        self.current_pwd.setEchoMode(QLineEdit.Password)
        self.current_pwd.setFixedHeight(40)
        self.current_pwd.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0,0,0,0.3);
                color: {C['text_white']};
                border: 1.5px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 0 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {C['orange']};
            }}
        """)
        pwd_layout.addWidget(self.current_pwd)
        
        # New Password
        self.new_pwd = QLineEdit()
        self.new_pwd.setPlaceholderText("🔑 New Password")
        self.new_pwd.setEchoMode(QLineEdit.Password)
        self.new_pwd.setFixedHeight(40)
        self.new_pwd.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0,0,0,0.3);
                color: {C['text_white']};
                border: 1.5px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 0 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {C['orange']};
            }}
        """)
        pwd_layout.addWidget(self.new_pwd)
        
        # Confirm Password
        self.confirm_pwd = QLineEdit()
        self.confirm_pwd.setPlaceholderText("🔑 Confirm Password")
        self.confirm_pwd.setEchoMode(QLineEdit.Password)
        self.confirm_pwd.setFixedHeight(40)
        self.confirm_pwd.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0,0,0,0.3);
                color: {C['text_white']};
                border: 1.5px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 0 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {C['orange']};
            }}
        """)
        pwd_layout.addWidget(self.confirm_pwd)
        
        # Change Password button
        change_pwd_btn = QPushButton("🔐 Change Password")
        change_pwd_btn.setFixedHeight(42)
        change_pwd_btn.setCursor(Qt.PointingHandCursor)
        change_pwd_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['orange']};
                color: white;
                border: none;
                border-radius: 21px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #F5B043;
            }}
        """)
        change_pwd_btn.clicked.connect(self.change_password)
        pwd_layout.addWidget(change_pwd_btn)
        
        content_layout.addWidget(pwd_card)
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        container_layout.addWidget(scroll, 1)
        layout.addWidget(self.container)
    
    def set_username(self, name, days_remaining=0):
        self.username = name
        self.days_remaining = days_remaining
        self.username_display.setText(name)
    
    def load_profile_data(self):
        """Load profile data from config file"""
        if self.profile_loaded:
            return
        
        try:
            # First try to load from cached profile info
            profile_info = self.auth.load_profile_info()
            if profile_info:
                self.email_input.setText(profile_info.get('email', ''))
                self.fname_input.setText(profile_info.get('first_name', ''))
                self.lname_input.setText(profile_info.get('last_name', ''))
                self.profile_loaded = True
                print("Profile data loaded from cache")
                return
            
            # If no cached data, try to fetch from API
            print("No cached profile, fetching from API...")
            ok, data = self.auth.get_user_profile()
            if ok and data:
                self.email_input.setText(data.get('email', ''))
                self.fname_input.setText(data.get('first_name', ''))
                self.lname_input.setText(data.get('last_name', ''))
                # Save to cache
                self.auth.save_profile_info(data)
                self.profile_loaded = True
                print("Profile data loaded from API")
            else:
                print("Failed to load profile from API")
                # Set default values from user_info if available
                if self.auth.user_info:
                    self.email_input.setText(self.auth.user_info.get('email', ''))
                    self.fname_input.setText(self.auth.user_info.get('first_name', ''))
                    self.lname_input.setText(self.auth.user_info.get('last_name', ''))
                self.profile_loaded = True
        except Exception as e:
            print(f"Error loading profile: {e}")
            import traceback
            traceback.print_exc()
            # Don't crash, just mark as loaded to prevent retry
            self.profile_loaded = True
    
    def update_profile(self):
        email = self.email_input.text().strip()
        first_name = self.fname_input.text().strip()
        last_name = self.lname_input.text().strip()
        
        if not email:
            QMessageBox.warning(self, "Error", "Email is required")
            return
        
        ok, msg = self.auth.update_user_profile(email, first_name, last_name)
        if ok:
            QMessageBox.information(self, "Success", "Profile updated!")
            self.profile_updated.emit()
        else:
            QMessageBox.warning(self, "Error", msg or "Failed to update")
    
    def change_password(self):
        current = self.current_pwd.text()
        new = self.new_pwd.text()
        confirm = self.confirm_pwd.text()
        
        if not current or not new or not confirm:
            QMessageBox.warning(self, "Error", "All password fields are required")
            return
        
        if new != confirm:
            QMessageBox.warning(self, "Error", "New passwords do not match")
            return
        
        if len(new) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return
        
        ok, msg = self.auth.change_password(current, new)
        if ok:
            QMessageBox.information(self, "Success", "Password changed successfully!")
            self.current_pwd.clear()
            self.new_pwd.clear()
            self.confirm_pwd.clear()
        else:
            QMessageBox.warning(self, "Error", msg or "Failed to change password")
    
    def showEvent(self, event):
        """Load profile data when page is shown"""
        super().showEvent(event)
        if not self.profile_loaded:
            # Load profile data directly without QTimer to avoid segfault
            self.load_profile_data()
