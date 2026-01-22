# main.py - Quimo Style Dark Theme UI

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QStackedWidget, QFrame,
    QMessageBox, QScrollArea, QGraphicsDropShadowEffect, QSizePolicy,
    QCheckBox, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QBrush, QLinearGradient, QPainterPath, QPen, QPixmap

from auth import AuthManager
from screenshot_service import ScreenshotService
from sync_manager import SyncManager
from cleanup import CleanupManager
from task_manager import TaskManager
from config import SCREENSHOTS_DIR
from ui_components import GradientWidget, GlassCard, HeaderWidget, BottomNavBar, C
from pages import DashboardPage, TasksPage, ProfilePage
from chat_manager import ChatManager
from chat_api import ChatAPI
from chat_page import ChatPage


class SignalEmitter(QObject):
    capture_signal = pyqtSignal(list)
    sync_signal = pyqtSignal(str, bool)
    task_refresh_signal = pyqtSignal()


class LoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor('#2563eb'))  # Bright blue at top
        gradient.setColorAt(0.3, QColor('#1e40af'))  # Medium blue
        gradient.setColorAt(0.6, QColor('#1e3a5f'))  # Dark blue
        gradient.setColorAt(1.0, QColor('#0f172a'))  # Very dark at bottom
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 25, 25)
        painter.fillPath(path, QBrush(gradient))


class GlassCard(QWidget):
    """Glass morphism card effect"""
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Glass background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(255, 255, 255, 18))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 8))
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        painter.fillPath(path, QBrush(gradient))
        
        # Border
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1.5))
        painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 20, 20)


class BottomNavBar(QFrame):
    """Modern sleek bottom navigation with floating pill design"""
    nav_clicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_index = 0
        self.setFixedHeight(75)
        
        # Modern dark background with subtle gradient
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(15, 23, 42, 0.98),
                    stop:1 rgba(10, 18, 35, 1));
                border-top: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """)
        
        # Main layout with padding
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 10, 20, 10)
        main_layout.setSpacing(0)
        
        # Floating pill container
        pill_container = QFrame()
        pill_container.setFixedHeight(55)
        pill_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.8),
                    stop:1 rgba(25, 35, 50, 0.8));
                border-radius: 27px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        
        layout = QHBoxLayout(pill_container)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(4)
        
        # Navigation items with better icons and proper text
        self.nav_buttons = []
        nav_items = [
            ("🏢", "Work", "#10B981"),      # Green - Work/Attendance
            ("📋", "Tasks", "#F59E0B"),     # Orange - Tasks
            ("💬", "Chat", "#3B82F6")       # Blue - Chat
        ]
        
        for i, (icon, label, color) in enumerate(nav_items):
            # Create button
            btn = QPushButton()
            btn.setFixedSize(100, 45)  # Slightly smaller for better fit
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty('nav_index', i)
            btn.setProperty('nav_color', color)
            
            # Button content
            btn_layout = QHBoxLayout(btn)
            btn_layout.setContentsMargins(12, 0, 12, 0)
            btn_layout.setSpacing(8)
            btn_layout.setAlignment(Qt.AlignCenter)
            
            # Icon
            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("background: transparent; border: none; font-size: 18px;")
            btn_layout.addWidget(icon_label)
            
            # Label
            text_label = QLabel(label)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setStyleSheet("background: transparent; border: none; font-size: 10px; font-weight: 600;")
            btn_layout.addWidget(text_label)
            
            # Inactive style - transparent
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 22px;
                }}
                QPushButton:hover {{
                    background: rgba(255, 255, 255, 0.05);
                }}
            """)
            
            btn.clicked.connect(lambda checked, idx=i: self.on_nav_click(idx))
            self.nav_buttons.append((btn, icon_label, text_label, color))
            layout.addWidget(btn)
        
        main_layout.addWidget(pill_container)
        
        # Set first button as active
        self.set_active(0)
    
    def on_nav_click(self, idx):
        self.current_index = idx
        self.set_active(idx)
        self.nav_clicked.emit(idx)
    
    def set_active(self, idx):
        """Set active navigation button with modern pill style"""
        for i, (btn, icon_label, text_label, color) in enumerate(self.nav_buttons):
            if i == idx:
                # Active state - colored pill with glow
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 {color}, stop:1 {self.darken_color(color)});
                        border: none;
                        border-radius: 22px;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 {self.lighten_color(color)}, stop:1 {color});
                    }}
                """)
                icon_label.setStyleSheet("background: transparent; border: none; font-size: 18px; color: white;")
                text_label.setStyleSheet("background: transparent; border: none; font-size: 10px; font-weight: 700; color: white; letter-spacing: 0.3px;")
            else:
                # Inactive state - transparent
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        border: none;
                        border-radius: 22px;
                    }}
                    QPushButton:hover {{
                        background: rgba(255, 255, 255, 0.05);
                    }}
                """)
                icon_label.setStyleSheet("background: transparent; border: none; font-size: 18px; color: rgba(255, 255, 255, 0.5);")
                text_label.setStyleSheet("background: transparent; border: none; font-size: 10px; font-weight: 600; color: rgba(255, 255, 255, 0.5);")
    
    def lighten_color(self, hex_color):
        """Lighten a hex color"""
        # Simple lighten by increasing RGB values
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def darken_color(self, hex_color):
        """Darken a hex color"""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        
        return f"#{r:02x}{g:02x}{b:02x}"

class TaskCard(QFrame):
    clicked = pyqtSignal(dict)
    
    def __init__(self, data, color):
        super().__init__()
        self.data = data
        self.color = color
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(70)
        self.setStyleSheet(f"background: {color}; border-radius: 15px;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 20, 10)
        layout.setSpacing(15)
        
        # Date badge
        date_widget = QWidget()
        date_widget.setFixedSize(50, 50)
        date_layout = QVBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(0)
        date_layout.setAlignment(Qt.AlignCenter)
        
        task_date = data.get('date', '')
        day_abbr, day_num = "MO", "20"
        if task_date:
            try:
                dt = datetime.strptime(task_date, "%Y-%m-%d")
                day_abbr = dt.strftime("%a").upper()[:2]
                day_num = dt.strftime("%d")
            except:
                pass
        
        day_label = QLabel(day_abbr)
        day_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        day_label.setAlignment(Qt.AlignCenter)
        date_layout.addWidget(day_label)
        
        num_label = QLabel(day_num)
        num_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        num_label.setAlignment(Qt.AlignCenter)
        date_layout.addWidget(num_label)
        layout.addWidget(date_widget)
        
        # Task info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        name = QLabel(data.get('name', 'Task'))
        name.setStyleSheet("color: white; font-size: 15px; font-weight: 600;")
        info_layout.addWidget(name)
        due_time = data.get('due_time', '12:24 PM')
        due_label = QLabel(f"Due: {due_time}")
        due_label.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 12px;")
        info_layout.addWidget(due_label)
        layout.addLayout(info_layout, 1)
        
        # Priority
        priority = data.get('priority', 'High')
        priority_label = QLabel(f"Priority: {priority}")
        priority_label.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 12px;")
        layout.addWidget(priority_label)
    
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.data)


class HeaderWidget(QWidget):
    menu_clicked = pyqtSignal()
    subscription_clicked = pyqtSignal()
    notification_clicked = pyqtSignal()
    
    def __init__(self, username="User", days_remaining=0):
        super().__init__()
        self.username = username
        self.days_remaining = days_remaining
        self.setFixedHeight(80)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 10)
        
        greeting = QLabel(f"Hi, {username}")
        greeting.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 24px; font-style: italic; font-weight: 500;")
        layout.addWidget(greeting)
        layout.addStretch()
        
        # Subscription status indicator
        if days_remaining <= 7 and days_remaining > 0:
            sub_btn = QPushButton(f"⚠️ {days_remaining}d")
            sub_btn.setFixedSize(60, 30)
            sub_btn.setCursor(Qt.PointingHandCursor)
            sub_btn.setStyleSheet(f"QPushButton {{background: {C['orange']}; color: white; border: none; border-radius: 15px; font-size: 12px; font-weight: bold;}} QPushButton:hover {{background: #F5B043;}}")
            sub_btn.clicked.connect(self.subscription_clicked.emit)
            layout.addWidget(sub_btn)
        
        # Notification bell (animated)
        from notification_bell import NotificationBellWithBadge
        self.notification_bell = NotificationBellWithBadge()
        self.notification_bell.clicked_signal.connect(self.notification_clicked.emit)
        layout.addWidget(self.notification_bell)
        
        menu_btn = QPushButton("☰")
        menu_btn.setFixedSize(40, 40)
        menu_btn.setCursor(Qt.PointingHandCursor)
        menu_btn.setStyleSheet(f"QPushButton {{background: transparent; color: {C['text_white']}; border: none; font-size: 24px;}}")
        menu_btn.clicked.connect(self.menu_clicked.emit)
        layout.addWidget(menu_btn)



class DashboardPage(QWidget):
    subscription_clicked = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__()
        self.p = parent
        self.work_seconds = 0
        self.is_clocked_in = False
        self.username = "User"
        self.days_remaining = 0
        self.access_granted = True
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
        
        # Date and Time row
        datetime_widget = QWidget()
        datetime_widget.setStyleSheet("background: transparent;")
        datetime_layout = QVBoxLayout(datetime_widget)
        datetime_layout.setContentsMargins(25, 0, 25, 0)
        datetime_layout.setSpacing(15)
        
        # Date display - modern design
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
        
        # Clocks row - Company Time and User Time side by side with glass cards
        clocks_row = QWidget()
        clocks_row.setStyleSheet("background: transparent;")
        clocks_layout = QHBoxLayout(clocks_row)
        clocks_layout.setContentsMargins(0, 10, 0, 0)
        clocks_layout.setSpacing(20)
        clocks_layout.setAlignment(Qt.AlignCenter)
        
        # Company Time Clock - Glass Card
        company_clock_card = GlassCard()
        company_clock_card.setFixedSize(160, 110)
        company_layout = QVBoxLayout(company_clock_card)
        company_layout.setContentsMargins(15, 12, 15, 12)
        company_layout.setSpacing(5)
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
        
        # User Local Time Clock - Glass Card
        user_clock_card = GlassCard()
        user_clock_card.setFixedSize(160, 110)
        user_layout = QVBoxLayout(user_clock_card)
        user_layout.setContentsMargins(15, 12, 15, 12)
        user_layout.setSpacing(5)
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
        
        # Work timer and today's work duration
        timer_container = QVBoxLayout()
        timer_container.setAlignment(Qt.AlignCenter)
        
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 72px; font-weight: bold; letter-spacing: 4px;")
        timer_container.addWidget(self.timer_label)
        
        # Today's total work duration
        self.today_work_label = QLabel("Today Work: 0h 0m")
        self.today_work_label.setAlignment(Qt.AlignCenter)
        self.today_work_label.setStyleSheet(f"background: transparent; color: {C['green']}; font-size: 18px; font-weight: 600; margin-top: 10px;")
        timer_container.addWidget(self.today_work_label)
        
        container_layout.addLayout(timer_container)
        
        # Access denied message (hidden by default)
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
        
        # Store company timezone
        self.company_timezone = 'UTC'
        self.today_work_seconds = 0
    
    def set_username(self, name, days_remaining=0, access_granted=True, access_message=""):
        self.username = name
        self.days_remaining = days_remaining
        self.access_granted = access_granted
        
        # Rebuild header
        old_header = self.header
        self.header = HeaderWidget(name, days_remaining)
        self.header.menu_clicked.connect(self.p.show_menu)
        self.header.subscription_clicked.connect(self.subscription_clicked.emit)
        self.container.layout().replaceWidget(old_header, self.header)
        old_header.deleteLater()
        
        # Show/hide clock button based on access
        if access_granted:
            self.btn_container.show()
            self.access_msg.hide()
        else:
            self.btn_container.hide()
            self.access_msg.setText(access_message or "⚠️ Subscription expired or access denied")
            self.access_msg.show()
    
    def update_clock(self):
        from datetime import datetime
        import pytz
        
        # Local time
        now = datetime.now()
        self.time_label.setText(now.strftime("%I:%M").lstrip('0') or '12')
        self.ampm_label.setText(now.strftime("%p"))
        self.day_label.setText(now.strftime("%A").upper())
        self.date_label.setText(now.strftime("%d %B %Y"))
        
        # Company timezone time
        try:
            company_tz = pytz.timezone(self.company_timezone)
            company_now = datetime.now(company_tz)
            self.company_time_label.setText(company_now.strftime("%I:%M").lstrip('0') or '12')
            self.company_ampm_label.setText(company_now.strftime("%p"))
            self.company_tz_detail.setText(self.company_timezone)
        except:
            # Fallback to UTC if timezone is invalid
            self.company_time_label.setText(now.strftime("%I:%M").lstrip('0') or '12')
            self.company_ampm_label.setText(now.strftime("%p"))
            self.company_tz_detail.setText("UTC")
    
    def update_today_work_duration(self, total_seconds):
        """Update today's total work duration"""
        self.today_work_seconds = total_seconds
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        self.today_work_label.setText(f"Today Work: {hours}h {minutes}m")
    
    def set_company_timezone(self, timezone_str):
        """Set company timezone"""
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
        # Try to start work - check for errors
        ok, msg = self.p.start_work()
        if not ok:
            # Show error - access denied or other issue
            from PyQt5.QtWidgets import QMessageBox
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
        
        # Title row
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
        old_header = self.header
        self.header = HeaderWidget(name, days_remaining)
        if self.parent_dash:
            self.header.menu_clicked.connect(self.parent_dash.show_menu)
            self.header.subscription_clicked.connect(self.subscription_clicked.emit)
        self.container.layout().replaceWidget(old_header, self.header)
        old_header.deleteLater()
    
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
        colors = [C['card_green'], C['card_orange'], C['card_red'], C['card_purple']]
        
        if not filtered:
            empty = QLabel("No tasks" if self.show_pending else "No completed tasks")
            empty.setStyleSheet(f"color: {C['text_gray']}; font-size: 16px; padding: 40px;")
            empty.setAlignment(Qt.AlignCenter)
            self.list_layout.insertWidget(0, empty)
        else:
            for i, task in enumerate(filtered):
                card = TaskCard(task, colors[i % len(colors)])
                card.clicked.connect(self.toggle_task)
                self.list_layout.insertWidget(self.list_layout.count() - 1, card)
    
    def toggle_task(self, data):
        if data.get('id'):
            ok, _ = self.task_mgr.toggle_task(data['id'])
            if ok:
                self.refresh()
    
    def showEvent(self, e):
        super().showEvent(e)
        self.refresh()



class LoginWidget(QWidget):
    login_success = pyqtSignal(str, dict)  # username, access_data

    def __init__(self, auth):
        super().__init__()
        self.auth = auth
        self.init_ui()

    def init_ui(self):
        self.container = GradientWidget()
        self.container.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setContentsMargins(25, 20, 25, 20)
        
        container_layout.addStretch()
        
        # IBIT Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("IBIT-Logo-V3.png")
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("IBIT")
            logo_label.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 36px; font-weight: bold;")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background: transparent;")
        container_layout.addWidget(logo_label)
        
        container_layout.addSpacing(10)
        
        # App Title
        title = QLabel("Quimo")
        title.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 38px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title)
        
        subtitle = QLabel("Screen Monitor")
        subtitle.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 13px;")
        subtitle.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(subtitle)
        container_layout.addSpacing(20)
        
        # Glass Form Card
        form_card = GlassCard()
        form_card.setFixedSize(360, 300)
        
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(25, 22, 25, 22)
        form_layout.setSpacing(5)
        
        # Welcome text
        welcome = QLabel("Welcome Back!")
        welcome.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 18px; font-weight: bold;")
        welcome.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(welcome)
        
        welcome_sub = QLabel("Sign in to continue")
        welcome_sub.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 11px;")
        welcome_sub.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(welcome_sub)
        
        form_layout.addSpacing(15)
        
        # Username field - clean design
        self.user = QLineEdit()
        self.user.setPlaceholderText("  👤  Username")
        self.user.setFixedHeight(50)
        self.user.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0,0,0,0.3);
                color: {C['text_white']};
                border: 2px solid rgba(255,255,255,0.1);
                border-radius: 14px;
                padding: 0 20px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {C['green']};
                background: rgba(0,0,0,0.4);
            }}
            QLineEdit::placeholder {{
                color: rgba(255,255,255,0.5);
            }}
        """)
        form_layout.addWidget(self.user)
        
        form_layout.addSpacing(10)
        
        # Password field - clean design
        self.pwd = QLineEdit()
        self.pwd.setPlaceholderText("  🔒  Password")
        self.pwd.setEchoMode(QLineEdit.Password)
        self.pwd.setFixedHeight(50)
        self.pwd.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0,0,0,0.3);
                color: {C['text_white']};
                border: 2px solid rgba(255,255,255,0.1);
                border-radius: 14px;
                padding: 0 20px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {C['green']};
                background: rgba(0,0,0,0.4);
            }}
            QLineEdit::placeholder {{
                color: rgba(255,255,255,0.5);
            }}
        """)
        self.pwd.returnPressed.connect(self.login)
        form_layout.addWidget(self.pwd)
        
        # Error label
        self.err = QLabel("")
        self.err.setStyleSheet(f"background: transparent; color: {C['red']}; font-size: 11px;")
        self.err.setAlignment(Qt.AlignCenter)
        self.err.setFixedHeight(16)
        self.err.setWordWrap(True)
        form_layout.addWidget(self.err)
        
        form_layout.addSpacing(5)
        
        # Sign In button
        self.btn = QPushButton("Sign In  →")
        self.btn.setFixedHeight(48)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['green']};
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #5FE076;
            }}
            QPushButton:pressed {{
                background: #3CB850;
            }}
            QPushButton:disabled {{
                background: rgba(255,255,255,0.15);
                color: rgba(255,255,255,0.5);
            }}
        """)
        self.btn.clicked.connect(self.login)
        form_layout.addWidget(self.btn)
        
        container_layout.addWidget(form_card, alignment=Qt.AlignCenter)
        
        container_layout.addStretch()
        
        # Version info at bottom
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 10px;")
        version_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(version_label)
        
        container_layout.addSpacing(5)
        
        main_layout.addWidget(self.container)

    def login(self):
        u = self.user.text().strip()
        p = self.pwd.text()
        if not u or not p:
            self.err.setText("Enter username and password")
            return
        self.btn.setEnabled(False)
        self.btn.setText("Signing in...")
        ok, msg, data = self.auth.login(u, p)
        self.btn.setEnabled(True)
        self.btn.setText("Sign In  →")
        if ok:
            self.err.setText("")
            self.login_success.emit(u, data or {})
        else:
            self.err.setText(msg)



class GradientMenuPanel(QWidget):
    """Menu panel with gradient background"""
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor('#2563eb'))
        gradient.setColorAt(0.4, QColor('#1e40af'))
        gradient.setColorAt(0.7, QColor('#1e3a5f'))
        gradient.setColorAt(1.0, QColor('#0f172a'))
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 0, 0)
        painter.fillPath(path, QBrush(gradient))


class MenuOverlay(QFrame):
    logout_clicked = pyqtSignal()
    close_clicked = pyqtSignal()
    subscription_clicked = pyqtSignal()
    profile_clicked = pyqtSignal()
    chat_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: rgba(0,0,0,0.6);")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Menu panel with gradient
        self.menu = GradientMenuPanel()
        self.menu.setFixedWidth(280)
        
        menu_layout = QVBoxLayout(self.menu)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)
        
        # Header section
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header.setFixedHeight(120)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        # Close button row
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(36, 36)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.1);
                color: {C['text_white']};
                border: none;
                border-radius: 18px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.2);
            }}
        """)
        close_btn.clicked.connect(self.close_clicked.emit)
        close_row.addWidget(close_btn)
        header_layout.addLayout(close_row)
        
        # Menu title
        menu_title = QLabel("Menu")
        menu_title.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 28px; font-weight: bold;")
        header_layout.addWidget(menu_title)
        
        menu_layout.addWidget(header)
        
        # Menu items section
        items_container = QWidget()
        items_container.setStyleSheet("background: transparent;")
        items_layout = QVBoxLayout(items_container)
        items_layout.setContentsMargins(20, 10, 20, 20)
        items_layout.setSpacing(12)
        
        # Profile info (optional)
        profile_widget = QWidget()
        profile_widget.setStyleSheet("background: rgba(255,255,255,0.08); border-radius: 15px;")
        profile_widget.setFixedHeight(70)
        profile_layout = QHBoxLayout(profile_widget)
        profile_layout.setContentsMargins(15, 10, 15, 10)
        
        avatar = QLabel("👤")
        avatar.setStyleSheet("background: transparent; font-size: 28px;")
        avatar.setFixedSize(45, 45)
        avatar.setAlignment(Qt.AlignCenter)
        profile_layout.addWidget(avatar)
        
        profile_info = QVBoxLayout()
        profile_info.setSpacing(2)
        profile_name = QLabel("User")
        profile_name.setObjectName("profile_name")
        profile_name.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 16px; font-weight: 600;")
        profile_info.addWidget(profile_name)
        profile_status = QLabel("Online")
        profile_status.setStyleSheet(f"background: transparent; color: {C['green']}; font-size: 12px;")
        profile_info.addWidget(profile_status)
        profile_layout.addLayout(profile_info)
        profile_layout.addStretch()
        
        items_layout.addWidget(profile_widget)
        items_layout.addSpacing(10)
        
        # Profile button
        profile_btn = QPushButton("  👤  Profile")
        profile_btn.setFixedHeight(50)
        profile_btn.setCursor(Qt.PointingHandCursor)
        profile_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.08);
                color: {C['text_white']};
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 500;
                text-align: left;
                padding-left: 15px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.15);
            }}
        """)
        profile_btn.clicked.connect(self.profile_clicked.emit)
        items_layout.addWidget(profile_btn)
        
        # Chat button
        chat_btn = QPushButton("  💬  Chat")
        chat_btn.setFixedHeight(50)
        chat_btn.setCursor(Qt.PointingHandCursor)
        chat_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.08);
                color: {C['text_white']};
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 500;
                text-align: left;
                padding-left: 15px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.15);
            }}
        """)
        chat_btn.clicked.connect(self.chat_clicked.emit)
        items_layout.addWidget(chat_btn)
        
        # Subscription Info button
        sub_btn = QPushButton("  📋  Subscription Info")
        sub_btn.setFixedHeight(50)
        sub_btn.setCursor(Qt.PointingHandCursor)
        sub_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.08);
                color: {C['text_white']};
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 500;
                text-align: left;
                padding-left: 15px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.15);
            }}
        """)
        sub_btn.clicked.connect(self.subscription_clicked.emit)
        items_layout.addWidget(sub_btn)
        
        items_layout.addSpacing(10)
        
        # Logout button
        logout_btn = QPushButton("  Logout")
        logout_btn.setFixedHeight(55)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['red']};
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 17px;
                font-weight: 600;
                text-align: center;
            }}
            QPushButton:hover {{
                background: #FF5252;
            }}
        """)
        logout_btn.clicked.connect(self.logout_clicked.emit)
        items_layout.addWidget(logout_btn)
        
        items_layout.addStretch()
        
        # Version info at bottom
        version = QLabel("Quimo v1.0")
        version.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 11px;")
        version.setAlignment(Qt.AlignCenter)
        items_layout.addWidget(version)
        
        menu_layout.addWidget(items_container, 1)
        
        layout.addWidget(self.menu)
        layout.addStretch()
    
    def set_username(self, name):
        profile_name = self.menu.findChild(QLabel, "profile_name")
        if profile_name:
            profile_name.setText(name)


class Dashboard(QWidget):
    logout_signal = pyqtSignal()

    def __init__(self, auth, ss, sync, cleanup, task, signals, notification_manager):
        super().__init__()
        self.auth = auth
        self.ss = ss
        self.sync = sync
        self.cleanup = cleanup
        self.task = task
        self.signals = signals
        self.notification_manager = notification_manager
        self.capturing = False
        self.username = "User"
        self.days_remaining = 0
        self.access_granted = True
        self.access_message = ""
        
        # Initialize chat components
        self.chat_manager = ChatManager(self.auth)
        self.chat_api = ChatAPI(self.auth)
        
        # Connect chat notifications
        self.chat_manager.message_received.connect(self.on_chat_message_received)
        self.chat_manager.task_notification.connect(self.on_task_notification_received)
        
        self.init_ui()
        self.setup()

    def init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        
        # Content area
        self.content = QWidget()
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.pages = QStackedWidget()
        self.dash_page = DashboardPage(self)
        self.dash_page.subscription_clicked.connect(self.show_subscription_info)
        self.pages.addWidget(self.dash_page)
        self.task_page = TasksPage(self.task, self.signals, self)
        self.task_page.subscription_clicked.connect(self.show_subscription_info)
        self.pages.addWidget(self.task_page)
        self.chat_page = ChatPage(self.chat_manager, self.chat_api, self)
        self.chat_page.subscription_clicked.connect(self.show_subscription_info)
        self.pages.addWidget(self.chat_page)
        self.profile_page = ProfilePage(self.auth, self)
        self.profile_page.subscription_clicked.connect(self.show_subscription_info)
        self.pages.addWidget(self.profile_page)
        content_layout.addWidget(self.pages)
        
        # Bottom nav
        self.nav = BottomNavBar()
        self.nav.nav_clicked.connect(self.switch_page)
        content_layout.addWidget(self.nav)
        
        main.addWidget(self.content)
        
        # Menu overlay (hidden by default)
        self.menu_overlay = MenuOverlay(self)
        self.menu_overlay.hide()
        self.menu_overlay.logout_clicked.connect(self.logout)
        self.menu_overlay.close_clicked.connect(self.hide_menu)
        self.menu_overlay.subscription_clicked.connect(self.on_menu_subscription_click)
        self.menu_overlay.profile_clicked.connect(self.on_menu_profile_click)
        self.menu_overlay.chat_clicked.connect(self.on_menu_chat_click)
        
        # Subscription info dialog (hidden by default)
        self.subscription_dialog = SubscriptionInfoDialog(self.auth, self)
        self.subscription_dialog.hide()
        self.subscription_dialog.close_clicked.connect(self.hide_subscription_info)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.menu_overlay.setGeometry(0, 0, self.width(), self.height())
        self.subscription_dialog.setGeometry(0, 0, self.width(), self.height())

    def show_menu(self):
        self.menu_overlay.setGeometry(0, 0, self.width(), self.height())
        self.menu_overlay.show()
        self.menu_overlay.raise_()

    def hide_menu(self):
        self.menu_overlay.hide()
    
    def on_menu_subscription_click(self):
        """Handle subscription click from menu"""
        self.hide_menu()
        self.show_subscription_info()
    
    def on_menu_profile_click(self):
        """Handle profile click from menu"""
        self.hide_menu()
        self.switch_page(3)  # Profile is now at index 3
    
    def on_menu_chat_click(self):
        """Handle chat click from menu"""
        self.hide_menu()
        self.switch_page(2)  # Chat is at index 2

    def show_subscription_info(self):
        """Show subscription info dialog"""
        self.subscription_dialog.update_info()
        self.subscription_dialog.setGeometry(0, 0, self.width(), self.height())
        self.subscription_dialog.show()
        self.subscription_dialog.raise_()
    
    def hide_subscription_info(self):
        self.subscription_dialog.hide()

    def set_username(self, name, days_remaining=0, access_granted=True, access_message=""):
        self.username = name
        self.days_remaining = days_remaining
        self.access_granted = access_granted
        self.access_message = access_message
        
        self.dash_page.set_username(name, days_remaining, access_granted, access_message)
        self.task_page.set_username(name, days_remaining)
        self.chat_page.set_username(name, days_remaining)
        self.profile_page.set_username(name, days_remaining)
        self.menu_overlay.set_username(name)

    def switch_page(self, idx):
        try:
            if idx == 0:
                self.pages.setCurrentIndex(0)
            elif idx == 1:
                self.pages.setCurrentIndex(1)
            elif idx == 2:
                # Chat page
                self.pages.setCurrentIndex(2)
            elif idx == 3:
                # Load profile data when switching to profile page
                try:
                    self.profile_page.load_profile_data()
                except Exception as e:
                    print(f"Error loading profile: {e}")
                self.pages.setCurrentIndex(3)
        except Exception as e:
            print(f"Error switching page: {e}")
            import traceback
            traceback.print_exc()

    def setup(self):
        self.signals.capture_signal.connect(self.on_capture)
        self.signals.sync_signal.connect(self.on_sync)
        
        # Setup access denied callbacks
        self.task.on_access_denied = self.on_access_denied
        self.sync.on_access_denied = self.on_access_denied

    def on_access_denied(self, error_code, message):
        """Handle access denied from server - update UI"""
        self.access_granted = False
        self.access_message = message
        
        # Update dashboard UI
        self.dash_page.set_username(
            self.username, 
            0,  # days remaining = 0
            False,  # access_granted = False
            message
        )
        
        # Stop capturing if running
        if self.capturing:
            self.ss.stop()
            self.capturing = False
            self.dash_page.clock_out()

    def start_auto(self):
        # Only start sync if access granted
        if self.access_granted:
            self.sync.on_sync_callback = lambda f, s: self.signals.sync_signal.emit(f, s)
            self.sync.start_sync()
        self.cleanup.start()
        
        # Connect to chat WebSocket
        try:
            self.chat_manager.connect()
        except Exception as e:
            print(f"Error connecting to chat: {e}")
        
        # Pre-load profile data in background
        self.load_profile_data_async()
    
    def load_profile_data_async(self):
        """Load profile data in background without blocking UI"""
        import threading
        def load():
            try:
                self.profile_page.load_profile_data()
            except Exception as e:
                print(f"Error pre-loading profile: {e}")
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()

    def start_work(self):
        from debug_logger import log_main
        log_main("=" * 50)
        log_main("🚀 START WORK REQUESTED")
        log_main("=" * 50)
        
        # Don't start if no access
        if not self.access_granted:
            log_main("❌ Access denied - cannot start work", 'error')
            return False, "Access denied"
        
        log_main("✅ Access granted - proceeding with check-in")
        ok, msg = self.task.check_in()
        if not ok:
            # Check-in failed - likely access denied
            log_main(f"❌ Check-in failed: {msg}", 'error')
            return False, msg
        
        log_main(f"✅ Check-in successful: {msg}")
        log_main("Starting screenshot service...")
        self.ss.on_capture_callback = lambda f: self.signals.capture_signal.emit(f)
        self.ss.start()
        
        log_main("Starting sync service...")
        self.sync.start_sync()
        
        self.capturing = True
        log_main("✅ Work started successfully!")
        log_main("=" * 50)
        return True, "Started"

    def stop_work(self):
        from debug_logger import log_main
        log_main("=" * 50)
        log_main("🛑 STOP WORK REQUESTED")
        log_main("=" * 50)
        
        log_main("Checking out...")
        ok, msg = self.task.check_out()
        log_main(f"Check-out result: {ok} - {msg}")
        
        log_main("Stopping screenshot service...")
        self.ss.stop()
        
        self.capturing = False
        log_main("✅ Work stopped")
        log_main("=" * 50)
        return ok, msg
    
    def on_chat_message_received(self, data):
        """Handle incoming chat message for notifications"""
        try:
            # Check if chat page is currently active
            is_chat_active = self.pages.currentIndex() == 2  # Chat is index 2
            
            # Get current user info
            current_user_id = None
            if self.auth.user_info:
                current_user_id = self.auth.user_info.get('id')
            
            sender_id = data.get('sender_id')
            receiver_id = data.get('receiver_id')
            
            # Only show notification if message is for current user
            if receiver_id != current_user_id:
                return
            
            # Check if currently chatting with this sender
            is_chatting_with_sender = False
            if is_chat_active and hasattr(self.chat_page, 'current_user_id'):
                is_chatting_with_sender = self.chat_page.current_user_id == sender_id
            
            # Show notification if not actively chatting with sender
            if not is_chatting_with_sender:
                sender_name = data.get('sender_username', 'Someone')
                message = data.get('message', '')
                
                # Show notification
                self.notification_manager.show_chat_notification(sender_name, message)
                
                # Update unread count
                current_count = self.notification_manager.unread_count
                self.notification_manager.update_badge(current_count + 1)
                
                # Update bell icon in header (all pages)
                self.update_notification_bell(current_count + 1)
                
        except Exception as e:
            print(f"Notification error: {e}")
    
    def update_notification_bell(self, count):
        """Update notification bell on all page headers"""
        try:
            # Update dashboard page header
            if hasattr(self.dash_page, 'header') and hasattr(self.dash_page.header, 'notification_bell'):
                self.dash_page.header.notification_bell.set_count(count)
        except Exception as e:
            print(f"Update bell error: {e}")
    
    def on_task_notification_received(self, data):
        """Handle incoming task notification from WebSocket"""
        try:
            print(f"🔔 Task notification received: {data}")  # Debug
            
            # Get current user info
            current_user_id = None
            if self.auth.user_info:
                current_user_id = self.auth.user_info.get('id')
            
            assigned_to_id = data.get('assigned_to_id')
            
            print(f"Current user ID: {current_user_id}, Assigned to: {assigned_to_id}")  # Debug
            
            # Only show notification if task is for current user
            if assigned_to_id != current_user_id:
                print("Task not for current user, skipping notification")
                return
            
            task_name = data.get('task_name', 'New Task')
            task_description = data.get('task_description', '')
            assigned_by = data.get('assigned_by')
            
            print(f"Showing task notification: {task_name} from {assigned_by}")  # Debug
            
            # Show task notification (always uses big sound)
            self.notification_manager.show_task_notification(
                task_name,
                task_description[:100],  # Limit length
                assigned_by
            )
            
            # Refresh task list if on task page
            if self.pages.currentIndex() == 1:  # Task page is index 1
                if hasattr(self.task_page, 'load_tasks'):
                    self.task_page.load_tasks()
                elif hasattr(self.task_page, 'refresh'):
                    self.task_page.refresh()
            
            print(f"✅ Task notification complete")
            
        except Exception as e:
            print(f"❌ Task notification error: {e}")
            import traceback
            traceback.print_exc()
            
            # Update tasks page header
            if hasattr(self.task_page, 'header') and hasattr(self.task_page.header, 'notification_bell'):
                self.task_page.header.notification_bell.set_count(count)
            
            # Update chat page header (if it has one)
            # Chat page doesn't use HeaderWidget, so skip
            
            # Update profile page header
            if hasattr(self.profile_page, 'header') and hasattr(self.profile_page.header, 'notification_bell'):
                self.profile_page.header.notification_bell.set_count(count)
                
        except Exception as e:
            print(f"Bell update error: {e}")
        return ok, msg

    def on_capture(self, files):
        self.sync.add_to_queue(files)

    def on_sync(self, path, ok):
        if ok and path and os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
        self.auto_clean_old_folders()

    def auto_clean_old_folders(self):
        if not os.path.exists(SCREENSHOTS_DIR):
            return
        today = datetime.now().strftime("%Y-%m-%d")
        for folder in os.listdir(SCREENSHOTS_DIR):
            folder_path = os.path.join(SCREENSHOTS_DIR, folder)
            if os.path.isdir(folder_path) and folder != today:
                try:
                    import shutil
                    shutil.rmtree(folder_path)
                except:
                    pass

    def logout(self):
        self.hide_menu()
        if self.capturing:
            self.task.check_out()
            self.dash_page.clock_out()
        self.sync.stop_sync()
        self.cleanup.stop()
        
        # Disconnect chat
        try:
            self.chat_manager.disconnect()
        except Exception as e:
            print(f"Error disconnecting chat: {e}")
        
        self.auth.logout()
        self.logout_signal.emit()



class CustomTitleBar(QFrame):
    """Custom title bar with minimize, maximize and close buttons"""
    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    close_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(40)
        self.setStyleSheet(f"background: {C['bg_dark']}; border: none;")
        self.drag_pos = None
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 10, 5)
        layout.setSpacing(0)
        
        # App title
        title = QLabel("Quimo 1.0")
        title.setStyleSheet(f"color: {C['text_white']}; font-size: 14px; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Minimize button
        self.min_btn = QPushButton("─")
        self.min_btn.setFixedSize(35, 28)
        self.min_btn.setCursor(Qt.PointingHandCursor)
        self.min_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C['text_white']};
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.1);
            }}
        """)
        self.min_btn.clicked.connect(self.minimize_clicked.emit)
        layout.addWidget(self.min_btn)
        
        # Maximize button
        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(35, 28)
        self.max_btn.setCursor(Qt.PointingHandCursor)
        self.max_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C['text_white']};
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.1);
            }}
        """)
        self.max_btn.clicked.connect(self.maximize_clicked.emit)
        layout.addWidget(self.max_btn)
        
        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(35, 28)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C['text_white']};
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {C['red']};
            }}
        """)
        self.close_btn.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self.close_btn)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.parent_window.move(event.globalPos() - self.drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.drag_pos = None


class TermsAndConditionsDialog(QFrame):
    """Terms and Conditions dialog - shown once after login"""
    accepted = pyqtSignal()
    rejected = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: rgba(0,0,0,0.9);")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Dialog box - responsive
        dialog_box = QFrame()
        dialog_box.setMaximumSize(600, 700)
        dialog_box.setMinimumSize(300, 400)
        dialog_box.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(20, 50, 100, 0.95),
                    stop:1 rgba(10, 30, 60, 0.95));
                border: 2px solid rgba(33, 150, 243, 0.3);
                border-radius: 15px;
            }}
        """)
        
        dialog_layout = QVBoxLayout(dialog_box)
        dialog_layout.setContentsMargins(20, 15, 20, 15)
        dialog_layout.setSpacing(12)
        
        # Title
        title = QLabel("Terms & Conditions")
        title.setStyleSheet(f"color: {C['header_blue']}; font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        dialog_layout.addWidget(title)
        
        # T&C Content
        content = QTextEdit()
        content.setReadOnly(True)
        content.setStyleSheet(f"""
            QTextEdit {{
                background: rgba(0,0,0,0.3);
                color: {C['text_white']};
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 8px;
                font-size: 11px;
                line-height: 1.4;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255,255,255,0.3);
                border-radius: 3px;
            }}
        """)
        
        tc_text = """TERMS AND CONDITIONS

1. ACCEPTANCE OF TERMS
By using this application, you agree to comply with these terms and conditions.

2. USER RESPONSIBILITIES
- You are responsible for maintaining the confidentiality of your login credentials
- You agree not to use this application for any unlawful purposes
- You will not attempt to gain unauthorized access to the system

3. MONITORING AND TRACKING
- This application monitors your work activities and takes screenshots
- All data collected is for legitimate business purposes only
- You consent to this monitoring as a condition of employment

4. DATA PRIVACY
- Your personal data will be handled in accordance with privacy laws
- Data will not be shared with unauthorized third parties
- You have the right to access and request deletion of your data

5. LIMITATION OF LIABILITY
- The company is not liable for any indirect or consequential damages
- Use of this application is at your own risk

6. TERMINATION
- The company reserves the right to terminate access at any time
- Upon termination, all access to the application will be revoked

7. MODIFICATIONS
- These terms may be updated at any time
- Continued use implies acceptance of updated terms

By clicking "I Agree", you acknowledge that you have read and understood these terms."""
        
        content.setText(tc_text.strip())
        dialog_layout.addWidget(content, 1)
        
        # Checkbox
        checkbox_layout = QHBoxLayout()
        self.agree_checkbox = QCheckBox("I have read and agree to the Terms & Conditions")
        self.agree_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {C['text_white']};
                font-size: 11px;
                spacing: 5px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox::indicator:unchecked {{
                background: rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background: {C['green']};
                border: 1px solid {C['green']};
                border-radius: 3px;
            }}
        """)
        checkbox_layout.addWidget(self.agree_checkbox)
        dialog_layout.addLayout(checkbox_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        reject_btn = QPushButton("Decline")
        reject_btn.setMinimumHeight(36)
        reject_btn.setCursor(Qt.PointingHandCursor)
        reject_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['red']};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: #F25C4E;
            }}
        """)
        reject_btn.clicked.connect(self.on_reject)
        button_layout.addWidget(reject_btn)
        
        accept_btn = QPushButton("I Agree")
        accept_btn.setMinimumHeight(36)
        accept_btn.setCursor(Qt.PointingHandCursor)
        accept_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['green']};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: #5FE076;
            }}
        """)
        accept_btn.clicked.connect(self.on_accept)
        button_layout.addWidget(accept_btn)
        
        dialog_layout.addLayout(button_layout)
        
        layout.addWidget(dialog_box)
    
    def on_accept(self):
        if self.agree_checkbox.isChecked():
            self.accepted.emit()
        else:
            QMessageBox.warning(self, "Error", "Please check the agreement checkbox")
    
    def on_reject(self):
        self.rejected.emit()


class ConfirmDialog(QFrame):
    """Confirm close dialog with gradient background"""
    confirmed = pyqtSignal()
    cancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: rgba(0,0,0,0.85);")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Dialog box with gradient
        self.dialog = GradientDialogBox()
        self.dialog.setFixedSize(320, 200)
        
        dlg_layout = QVBoxLayout(self.dialog)
        dlg_layout.setContentsMargins(30, 30, 30, 25)
        dlg_layout.setSpacing(12)
        
        # Warning icon
        icon = QLabel("⚠️")
        icon.setStyleSheet("background: transparent; font-size: 36px;")
        icon.setAlignment(Qt.AlignCenter)
        dlg_layout.addWidget(icon)
        
        title = QLabel("Exit Application?")
        title.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        dlg_layout.addWidget(title)
        
        msg = QLabel("Are you sure you want to close Quimo?")
        msg.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 13px;")
        msg.setAlignment(Qt.AlignCenter)
        dlg_layout.addWidget(msg)
        
        dlg_layout.addSpacing(10)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(120, 45)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.15);
                color: {C['text_white']};
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 22px;
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.25);
                border-color: rgba(255,255,255,0.3);
            }}
        """)
        cancel_btn.clicked.connect(self.cancelled.emit)
        btn_layout.addWidget(cancel_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(120, 45)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['red']};
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #FF5252;
            }}
        """)
        close_btn.clicked.connect(self.confirmed.emit)
        btn_layout.addWidget(close_btn)
        
        dlg_layout.addLayout(btn_layout)
        layout.addWidget(self.dialog)


class GradientDialogBox(QWidget):
    """Dialog box with gradient background matching app theme"""
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor('#1e3a5f'))
        gradient.setColorAt(0.5, QColor('#152238'))
        gradient.setColorAt(1.0, QColor('#0f172a'))
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        painter.fillPath(path, QBrush(gradient))
        
        # Add subtle border
        painter.setPen(QColor(255, 255, 255, 30))
        painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 20, 20)


class SubscriptionInfoDialog(QFrame):
    """Subscription information dialog"""
    close_clicked = pyqtSignal()
    
    def __init__(self, auth, parent=None):
        super().__init__(parent)
        self.auth = auth
        self.setStyleSheet("background: rgba(0,0,0,0.85);")
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Dialog box with gradient
        self.dialog = GradientDialogBox()
        self.dialog.setFixedSize(360, 450)
        
        dlg_layout = QVBoxLayout(self.dialog)
        dlg_layout.setContentsMargins(20, 20, 20, 20)
        dlg_layout.setSpacing(12)
        
        # Header with close button
        header_layout = QHBoxLayout()
        title = QLabel("📋 Subscription Info")
        title.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.1);
                color: {C['text_white']};
                border: none;
                border-radius: 15px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.2);
            }}
        """)
        close_btn.clicked.connect(self.close_clicked.emit)
        header_layout.addWidget(close_btn)
        dlg_layout.addLayout(header_layout)
        
        dlg_layout.addSpacing(5)
        
        # Company Info Card
        company_card = QWidget()
        company_card.setFixedHeight(60)
        company_card.setStyleSheet("background: rgba(255,255,255,0.08); border-radius: 12px;")
        company_layout = QVBoxLayout(company_card)
        company_layout.setContentsMargins(15, 10, 15, 10)
        company_layout.setSpacing(3)
        
        company_label = QLabel("🏢 Company")
        company_label.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 11px;")
        company_layout.addWidget(company_label)
        
        self.company_name = QLabel("-")
        self.company_name.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 15px; font-weight: bold;")
        company_layout.addWidget(self.company_name)
        
        dlg_layout.addWidget(company_card)
        
        # Plan Info Card
        plan_card = QWidget()
        plan_card.setFixedHeight(60)
        plan_card.setStyleSheet("background: rgba(255,255,255,0.08); border-radius: 12px;")
        plan_layout = QVBoxLayout(plan_card)
        plan_layout.setContentsMargins(15, 10, 15, 10)
        plan_layout.setSpacing(3)
        
        plan_label = QLabel("📦 Subscription Plan")
        plan_label.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 11px;")
        plan_layout.addWidget(plan_label)
        
        self.plan_name = QLabel("-")
        self.plan_name.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 15px; font-weight: bold;")
        plan_layout.addWidget(self.plan_name)
        
        dlg_layout.addWidget(plan_card)
        
        # Status & Dates Card - Grid style
        status_card = QWidget()
        status_card.setFixedHeight(100)
        status_card.setStyleSheet("background: rgba(255,255,255,0.08); border-radius: 12px;")
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(15, 12, 15, 12)
        status_layout.setSpacing(6)
        
        # Status row
        status_row = QHBoxLayout()
        status_row.setSpacing(10)
        status_lbl = QLabel("Status:")
        status_lbl.setFixedWidth(80)
        status_lbl.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 13px;")
        status_row.addWidget(status_lbl)
        self.status_value = QLabel("Active ✓")
        self.status_value.setStyleSheet(f"background: transparent; color: {C['green']}; font-size: 13px; font-weight: bold;")
        status_row.addWidget(self.status_value)
        status_row.addStretch()
        status_layout.addLayout(status_row)
        
        # Start date row
        start_row = QHBoxLayout()
        start_row.setSpacing(10)
        start_lbl = QLabel("Start Date:")
        start_lbl.setFixedWidth(80)
        start_lbl.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 13px;")
        start_row.addWidget(start_lbl)
        self.start_value = QLabel("-")
        self.start_value.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 13px;")
        start_row.addWidget(self.start_value)
        start_row.addStretch()
        status_layout.addLayout(start_row)
        
        # End date row
        end_row = QHBoxLayout()
        end_row.setSpacing(10)
        end_lbl = QLabel("End Date:")
        end_lbl.setFixedWidth(80)
        end_lbl.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 13px;")
        end_row.addWidget(end_lbl)
        self.end_value = QLabel("-")
        self.end_value.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 13px;")
        end_row.addWidget(self.end_value)
        end_row.addStretch()
        status_layout.addLayout(end_row)
        
        dlg_layout.addWidget(status_card)
        
        # Days Remaining Card
        self.days_card = QWidget()
        self.days_card.setFixedHeight(70)
        self.days_card.setStyleSheet("background: rgba(76, 217, 100, 0.15); border-radius: 12px;")
        days_layout = QHBoxLayout(self.days_card)
        days_layout.setContentsMargins(15, 10, 15, 10)
        
        days_icon = QLabel("⏰")
        days_icon.setStyleSheet("background: transparent; font-size: 26px;")
        days_layout.addWidget(days_icon)
        
        days_info = QVBoxLayout()
        days_info.setSpacing(0)
        days_title = QLabel("Days Remaining")
        days_title.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 11px;")
        days_info.addWidget(days_title)
        self.days_value = QLabel("0")
        self.days_value.setStyleSheet(f"background: transparent; color: {C['green']}; font-size: 26px; font-weight: bold;")
        days_info.addWidget(self.days_value)
        days_layout.addLayout(days_info)
        days_layout.addStretch()
        
        dlg_layout.addWidget(self.days_card)
        
        dlg_layout.addStretch()
        
        # Close button
        ok_btn = QPushButton("Close")
        ok_btn.setFixedHeight(42)
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['header_blue']};
                color: white;
                border: none;
                border-radius: 21px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #42A5F5;
            }}
        """)
        ok_btn.clicked.connect(self.close_clicked.emit)
        dlg_layout.addWidget(ok_btn)
        
        layout.addWidget(self.dialog)
    
    def update_info(self):
        """Update subscription info from auth manager"""
        # Check if superuser
        is_superuser = False
        if self.auth.user_info:
            is_superuser = self.auth.user_info.get('is_superuser', False)
        
        # Superuser - show special info
        if is_superuser:
            self.company_name.setText('Administrator')
            self.plan_name.setText('Superuser Access')
            self.start_value.setText('-')
            self.end_value.setText('-')
            self.days_value.setText('∞')
            self.status_value.setText("Superuser ✓")
            self.status_value.setStyleSheet(f"background: transparent; color: {C['green']}; font-size: 13px; font-weight: bold;")
            self.days_value.setStyleSheet(f"background: transparent; color: {C['green']}; font-size: 26px; font-weight: bold;")
            self.days_card.setStyleSheet("background: rgba(76, 217, 100, 0.15); border-radius: 12px;")
            return
        
        # Company info
        if self.auth.company_info:
            self.company_name.setText(self.auth.company_info.get('name', 'N/A'))
        else:
            self.company_name.setText('N/A')
        
        # Check error code for special statuses
        error_code = self.auth.error_code
        
        # Subscription info
        if self.auth.subscription_info:
            sub = self.auth.subscription_info
            self.plan_name.setText(sub.get('plan', 'N/A'))
            self.start_value.setText(sub.get('start_date', '-'))
            self.end_value.setText(sub.get('end_date', '-'))
            
            days = sub.get('days_remaining', 0)
            self.days_value.setText(str(days))
            
            status = sub.get('status', 'unknown')
            
            # Handle different error codes
            if error_code == 'USER_INACTIVE':
                self.status_value.setText("User Inactive ✗")
                self.status_value.setStyleSheet(f"background: transparent; color: {C['red']}; font-size: 13px; font-weight: bold;")
                self.days_value.setStyleSheet(f"background: transparent; color: {C['red']}; font-size: 26px; font-weight: bold;")
                self.days_card.setStyleSheet("background: rgba(231, 76, 60, 0.15); border-radius: 12px;")
            elif error_code == 'COMPANY_INACTIVE':
                self.status_value.setText("Company Inactive ✗")
                self.status_value.setStyleSheet(f"background: transparent; color: {C['red']}; font-size: 13px; font-weight: bold;")
                self.days_value.setStyleSheet(f"background: transparent; color: {C['red']}; font-size: 26px; font-weight: bold;")
                self.days_card.setStyleSheet("background: rgba(231, 76, 60, 0.15); border-radius: 12px;")
            elif error_code == 'SUBSCRIPTION_EXPIRED' or status == 'expired' or days <= 0:
                self.status_value.setText("Expired ✗")
                self.status_value.setStyleSheet(f"background: transparent; color: {C['red']}; font-size: 13px; font-weight: bold;")
                self.days_value.setStyleSheet(f"background: transparent; color: {C['red']}; font-size: 26px; font-weight: bold;")
                self.days_card.setStyleSheet("background: rgba(231, 76, 60, 0.15); border-radius: 12px;")
            elif status == 'active' and days > 0 and self.auth.access_granted:
                self.status_value.setText("Active ✓")
                self.status_value.setStyleSheet(f"background: transparent; color: {C['green']}; font-size: 13px; font-weight: bold;")
                self.days_value.setStyleSheet(f"background: transparent; color: {C['green']}; font-size: 26px; font-weight: bold;")
                self.days_card.setStyleSheet("background: rgba(76, 217, 100, 0.15); border-radius: 12px;")
                
                # Warning color if days <= 7
                if days <= 7:
                    self.days_value.setStyleSheet(f"background: transparent; color: {C['orange']}; font-size: 26px; font-weight: bold;")
                    self.days_card.setStyleSheet("background: rgba(245, 166, 35, 0.15); border-radius: 12px;")
            else:
                self.status_value.setText("Inactive ✗")
                self.status_value.setStyleSheet(f"background: transparent; color: {C['orange']}; font-size: 13px; font-weight: bold;")
                self.days_value.setStyleSheet(f"background: transparent; color: {C['orange']}; font-size: 26px; font-weight: bold;")
                self.days_card.setStyleSheet("background: rgba(245, 166, 35, 0.15); border-radius: 12px;")
        else:
            # No subscription
            self.plan_name.setText('No Subscription')
            self.start_value.setText('-')
            self.end_value.setText('-')
            self.days_value.setText('0')
            self.status_value.setText("No Subscription")
            self.status_value.setStyleSheet(f"background: transparent; color: {C['red']}; font-size: 13px; font-weight: bold;")
            self.days_value.setStyleSheet(f"background: transparent; color: {C['red']}; font-size: 26px; font-weight: bold;")
            self.days_card.setStyleSheet("background: rgba(231, 76, 60, 0.15); border-radius: 12px;")


class AccessDeniedDialog(QFrame):
    """Access denied dialog for subscription/access issues"""
    logout_clicked = pyqtSignal()
    retry_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: rgba(0,0,0,0.9);")
        self.error_code = None
        self.message = ""
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Dialog box with gradient
        self.dialog = GradientDialogBox()
        self.dialog.setFixedSize(360, 350)
        
        dlg_layout = QVBoxLayout(self.dialog)
        dlg_layout.setContentsMargins(30, 30, 30, 25)
        dlg_layout.setSpacing(15)
        
        # Warning icon
        icon = QLabel("🚫")
        icon.setStyleSheet("background: transparent; font-size: 48px;")
        icon.setAlignment(Qt.AlignCenter)
        dlg_layout.addWidget(icon)
        
        # Title
        self.title_label = QLabel("Access Denied")
        self.title_label.setStyleSheet(f"background: transparent; color: {C['red']}; font-size: 22px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        dlg_layout.addWidget(self.title_label)
        
        # Message
        self.msg_label = QLabel("Your subscription has expired or access is restricted.")
        self.msg_label.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 14px;")
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setWordWrap(True)
        dlg_layout.addWidget(self.msg_label)
        
        # Error code
        self.code_label = QLabel("")
        self.code_label.setStyleSheet(f"background: transparent; color: {C['text_gray']}; font-size: 11px;")
        self.code_label.setAlignment(Qt.AlignCenter)
        dlg_layout.addWidget(self.code_label)
        
        dlg_layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        retry_btn = QPushButton("Retry")
        retry_btn.setFixedSize(130, 45)
        retry_btn.setCursor(Qt.PointingHandCursor)
        retry_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,255,255,0.15);
                color: {C['text_white']};
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 22px;
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.25);
            }}
        """)
        retry_btn.clicked.connect(self.retry_clicked.emit)
        btn_layout.addWidget(retry_btn)
        
        logout_btn = QPushButton("Logout")
        logout_btn.setFixedSize(130, 45)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['red']};
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #FF5252;
            }}
        """)
        logout_btn.clicked.connect(self.logout_clicked.emit)
        btn_layout.addWidget(logout_btn)
        
        dlg_layout.addLayout(btn_layout)
        layout.addWidget(self.dialog)
    
    def set_error(self, error_code, message):
        """Set error details"""
        self.error_code = error_code
        self.message = message
        
        # Set title based on error code
        titles = {
            'SUBSCRIPTION_EXPIRED': 'Subscription Expired',
            'SUBSCRIPTION_NONE': 'No Subscription',
            'USER_INACTIVE': 'Account Deactivated',
            'COMPANY_INACTIVE': 'Company Deactivated',
            'NO_EMPLOYEE_PROFILE': 'Account Not Linked'
        }
        self.title_label.setText(titles.get(error_code, 'Access Denied'))
        self.msg_label.setText(message)
        self.code_label.setText(f"Error: {error_code}" if error_code else "")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Frameless window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setMinimumSize(800, 620)  # Larger minimum for chat
        self.setStyleSheet(f"background: {C['bg_dark']}; border-radius: 15px;")
        
        self.is_maximized = False
        self.normal_geometry = None
        
        # Load saved window size
        self.load_window_size()

        self.auth = AuthManager()
        self.signals = SignalEmitter()
        self.ss = ScreenshotService()
        self.sync = SyncManager(self.auth)
        self.cleanup = CleanupManager()
        self.task = TaskManager(self.auth)
        
        # Notification Manager
        from notification_manager import NotificationManager
        self.notification_manager = NotificationManager(self)

        self.setup_ui()

        if self.auth.is_logged_in():
            # Check access on app start
            self.check_and_show_dash()
    
    def load_window_size(self):
        """Load saved window size from config"""
        from config import DATA_DIR
        import json
        
        settings_file = os.path.join(DATA_DIR, "window_settings.json")
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    width = settings.get('width', 900)
                    height = settings.get('height', 650)
                    x = settings.get('x')
                    y = settings.get('y')
                    
                    self.resize(width, height)
                    
                    if x is not None and y is not None:
                        self.move(x, y)
                    else:
                        # Center on screen
                        screen = QApplication.desktop().screenGeometry()
                        x = (screen.width() - width) // 2
                        y = (screen.height() - height) // 2
                        self.move(x, y)
            else:
                # Default size - wider for chat
                self.resize(900, 650)
                # Center on screen
                screen = QApplication.desktop().screenGeometry()
                x = (screen.width() - 900) // 2
                y = (screen.height() - 650) // 2
                self.move(x, y)
        except Exception as e:
            print(f"Error loading window size: {e}")
            self.resize(900, 650)
    
    def save_window_size(self):
        """Save current window size to config"""
        from config import DATA_DIR
        import json
        
        settings_file = os.path.join(DATA_DIR, "window_settings.json")
        try:
            settings = {
                'width': self.width(),
                'height': self.height(),
                'x': self.x(),
                'y': self.y()
            }
            with open(settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error saving window size: {e}")

    def setup_ui(self):
        # Main container
        central = QWidget()
        central.setStyleSheet(f"background: {C['bg_dark']}; border-radius: 15px;")
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Custom title bar
        self.title_bar = CustomTitleBar(self)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self.toggle_maximize)
        self.title_bar.close_clicked.connect(self.show_close_confirm)
        main_layout.addWidget(self.title_bar)
        
        # Content stack
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self.login = LoginWidget(self.auth)
        self.login.login_success.connect(self.on_login_success)
        self.stack.addWidget(self.login)

        self.dash = Dashboard(self.auth, self.ss, self.sync, self.cleanup, self.task, self.signals, self.notification_manager)
        self.dash.logout_signal.connect(self.show_login)
        self.stack.addWidget(self.dash)
        
        # Setup work duration update callback
        self.task.on_work_duration_update = self.update_work_duration
        
        # Timer to fetch current attendance every 30 seconds
        self.work_duration_timer = QTimer()
        self.work_duration_timer.timeout.connect(self.fetch_work_duration)
        self.work_duration_timer.start(30000)  # 30 seconds
        
        # Confirm dialog (hidden by default)
        self.confirm_dialog = ConfirmDialog(self)
        self.confirm_dialog.hide()
        self.confirm_dialog.confirmed.connect(self.do_close)
        self.confirm_dialog.cancelled.connect(self.hide_confirm)
        
        # Terms and Conditions dialog (hidden by default)
        self.tc_dialog = TermsAndConditionsDialog(self)
        self.tc_dialog.hide()
        self.tc_dialog.accepted.connect(self.on_tc_accepted)
        self.tc_dialog.rejected.connect(self.on_tc_rejected)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.confirm_dialog.setGeometry(0, 0, self.width(), self.height())
        self.tc_dialog.setGeometry(0, 0, self.width(), self.height())
        
        # Save window size when resized (with debounce)
        if hasattr(self, '_resize_timer'):
            self._resize_timer.stop()
        else:
            self._resize_timer = QTimer()
            self._resize_timer.setSingleShot(True)
            self._resize_timer.timeout.connect(self.save_window_size)
        self._resize_timer.start(500)  # Save after 500ms of no resize
    
    def moveEvent(self, event):
        super().moveEvent(event)
        # Save window position when moved (with debounce)
        if hasattr(self, '_move_timer'):
            self._move_timer.stop()
        else:
            self._move_timer = QTimer()
            self._move_timer.setSingleShot(True)
            self._move_timer.timeout.connect(self.save_window_size)
        self._move_timer.start(500)  # Save after 500ms of no move

    def show_close_confirm(self):
        self.confirm_dialog.setGeometry(0, 0, self.width(), self.height())
        self.confirm_dialog.show()
        self.confirm_dialog.raise_()
    
    def toggle_maximize(self):
        """Toggle between maximized and normal window size"""
        if self.is_maximized:
            # Restore to normal size
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            else:
                self.resize(420, 620)
                # Center on screen
                screen = QApplication.desktop().screenGeometry()
                x = (screen.width() - 420) // 2
                y = (screen.height() - 620) // 2
                self.move(x, y)
            self.is_maximized = False
            self.title_bar.max_btn.setText("□")
        else:
            # Save current geometry
            self.normal_geometry = self.geometry()
            # Maximize
            screen = QApplication.desktop().availableGeometry()
            self.setGeometry(screen)
            self.is_maximized = True
            self.title_bar.max_btn.setText("❐")
    
    def hide_confirm(self):
        self.confirm_dialog.hide()
    
    def do_close(self):
        # Save window size before closing
        self.save_window_size()
        
        if self.dash.capturing:
            self.task.check_out()
        self.ss.stop()
        self.sync.stop_sync()
        self.cleanup.stop()
        self.close()

    def check_and_show_dash(self):
        """Show dashboard using cached login data - no API call needed"""
        username = self.auth.get_username()
        days_remaining = self.auth.get_subscription_days_remaining()
        access_granted = self.auth.access_granted
        access_message = self.auth.access_message or ""
        
        self.show_dash(username, days_remaining, access_granted, access_message)

    def on_login_success(self, username, data):
        """Handle login success - use data from login response directly"""
        access_granted = data.get('access_granted', False)
        
        # Get username from response
        user_info = data.get('user', {})
        display_name = user_info.get('full_name') or user_info.get('username') or username
        
        # Get subscription days remaining
        sub_info = data.get('subscription', {})
        days_remaining = sub_info.get('days_remaining', 0) if sub_info else 0
        
        # Get access message
        access_message = data.get('message', '')
        
        self.show_dash(display_name, days_remaining, access_granted, access_message)

    def show_dash(self, username="User", days_remaining=0, access_granted=True, access_message=""):
        # Check if T&C needs to be shown
        if self.should_show_tc():
            self.show_tc_dialog()
        else:
            self._show_dashboard(username, days_remaining, access_granted, access_message)
    
    def _show_dashboard(self, username="User", days_remaining=0, access_granted=True, access_message=""):
        """Internal method to show dashboard"""
        self.dash.set_username(username, days_remaining, access_granted, access_message)
        self.stack.setCurrentWidget(self.dash)
        self.dash.access_granted = access_granted
        self.dash.start_auto()
        
        # Fetch work duration and company timezone immediately after login
        self.fetch_work_duration()
    
    def should_show_tc(self):
        """Check if T&C has been accepted"""
        import json
        from config import TC_ACCEPTANCE_FILE
        
        try:
            if os.path.exists(TC_ACCEPTANCE_FILE):
                with open(TC_ACCEPTANCE_FILE, 'r') as f:
                    data = json.load(f)
                    return not data.get('accepted', False)
        except:
            pass
        return True
    
    def save_tc_acceptance(self):
        """Save T&C acceptance"""
        import json
        from config import TC_ACCEPTANCE_FILE
        
        try:
            data = {'accepted': True}
            with open(TC_ACCEPTANCE_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving T&C acceptance: {e}")
    
    def show_tc_dialog(self):
        """Show T&C dialog"""
        self.tc_dialog.setGeometry(0, 0, self.width(), self.height())
        self.tc_dialog.show()
        self.tc_dialog.raise_()
    
    def on_tc_accepted(self):
        """Handle T&C acceptance"""
        self.save_tc_acceptance()
        self.tc_dialog.hide()
        # Show dashboard
        username = self.auth.get_username()
        days_remaining = self.auth.get_subscription_days_remaining()
        access_granted = self.auth.access_granted
        access_message = self.auth.access_message or ""
        self._show_dashboard(username, days_remaining, access_granted, access_message)
    
    def on_tc_rejected(self):
        """Handle T&C rejection - close app"""
        self.close()

    def show_login(self):
        self.login.user.clear()
        self.login.pwd.clear()
        self.login.err.clear()
        self.stack.setCurrentWidget(self.login)

    def closeEvent(self, e):
        e.accept()
    
    def changeEvent(self, event):
        """Track window state changes (minimize, restore)"""
        if event.type() == event.WindowStateChange:
            # Update notification manager about app focus
            is_minimized = self.isMinimized()
            self.notification_manager.set_app_focused(not is_minimized)
        super().changeEvent(event)
    
    def focusInEvent(self, event):
        """Track when app gains focus"""
        self.notification_manager.set_app_focused(True)
        super().focusInEvent(event)
    
    def focusOutEvent(self, event):
        """Track when app loses focus"""
        self.notification_manager.set_app_focused(False)
        super().focusOutEvent(event)
    
    def fetch_work_duration(self):
        """Fetch current attendance and work duration from API"""
        if self.auth.is_logged_in():
            # Fetch attendance data which includes company timezone
            self.task.get_current_attendance()
    
    def update_work_duration(self, total_seconds, company_timezone):
        """Update work duration display on dashboard"""
        if hasattr(self, 'dash') and hasattr(self.dash, 'dash_page'):
            self.dash.dash_page.update_today_work_duration(total_seconds)
            self.dash.dash_page.set_company_timezone(company_timezone)


def main():
    try:
        print("Starting app...")
        app = QApplication(sys.argv)
        print("QApplication created")
        app.setStyle('Fusion')
        
        p = QPalette()
        p.setColor(QPalette.Window, QColor(C['bg_dark']))
        p.setColor(QPalette.WindowText, QColor(C['text_white']))
        p.setColor(QPalette.Base, QColor(C['bg_dark']))
        p.setColor(QPalette.Text, QColor(C['text_white']))
        app.setPalette(p)
        
        print("Creating MainWindow...")
        w = MainWindow()
        print("MainWindow created")
        w.show()
        print("Window shown, starting event loop...")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
