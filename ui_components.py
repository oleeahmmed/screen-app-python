# ui_components.py - Reusable UI Components

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QLinearGradient, QColor, QPainterPath, QPainter, QBrush, QPen

# Color scheme
C = {
    'bg_dark': '#0a1628',
    'header_blue': '#2196F3',
    'text_white': '#FFFFFF',
    'text_gray': '#8899aa',
    'green': '#4CD964',
    'orange': '#F5A623',
    'red': '#E74C3C',
    'purple': '#9B59B6',
    'nav_dark': '#0d1f35',
    'card_green': '#4CD964',
    'card_orange': '#F5A623',
    'card_red': '#E74C3C',
    'card_purple': '#9B59B6',
}


class GradientWidget(QWidget):
    """Gradient background widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor('#2563eb'))
        gradient.setColorAt(0.3, QColor('#1e40af'))
        gradient.setColorAt(0.6, QColor('#1e3a5f'))
        gradient.setColorAt(1.0, QColor('#0f172a'))
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 25, 25)
        painter.fillPath(path, QBrush(gradient))


class GlassCard(QWidget):
    """Glass morphism card effect"""
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(255, 255, 255, 18))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 8))
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        painter.fillPath(path, QBrush(gradient))
        
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1.5))
        painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 20, 20)


class HeaderWidget(QWidget):
    """Top header with user info"""
    menu_clicked = pyqtSignal()
    subscription_clicked = pyqtSignal()
    
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
        
        if days_remaining <= 7 and days_remaining > 0:
            sub_btn = QPushButton(f"⚠️ {days_remaining}d")
            sub_btn.setFixedSize(60, 30)
            sub_btn.setCursor(Qt.PointingHandCursor)
            sub_btn.setStyleSheet(f"QPushButton {{background: {C['orange']}; color: white; border: none; border-radius: 15px; font-size: 12px; font-weight: bold;}} QPushButton:hover {{background: #F5B043;}}")
            sub_btn.clicked.connect(self.subscription_clicked.emit)
            layout.addWidget(sub_btn)
        
        menu_btn = QPushButton("☰")
        menu_btn.setFixedSize(40, 40)
        menu_btn.setCursor(Qt.PointingHandCursor)
        menu_btn.setStyleSheet(f"QPushButton {{background: transparent; color: {C['text_white']}; border: none; font-size: 24px;}}")
        menu_btn.clicked.connect(self.menu_clicked.emit)
        layout.addWidget(menu_btn)
        
        bell_btn = QPushButton("🔔")
        bell_btn.setFixedSize(40, 40)
        bell_btn.setCursor(Qt.PointingHandCursor)
        bell_btn.setStyleSheet(f"QPushButton {{background: transparent; color: {C['text_white']}; border: none; font-size: 22px;}}")
        layout.addWidget(bell_btn)


class BottomNavBar(QFrame):
    """Bottom navigation bar"""
    nav_clicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_index = 0
        self.setFixedHeight(70)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C['nav_dark']};
                border-top: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(0)
        
        nav_items = [
            ("📊", "Attendance"),
            ("✓", "Tasks"),
            ("💬", "Chat"),
            ("👤", "Profile")
        ]
        
        self.buttons = []
        for i, (icon, label) in enumerate(nav_items):
            btn = QPushButton(f"{icon}\n{label}")
            btn.setFixedHeight(60)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {C['text_gray']};
                    border: none;
                    font-size: 11px;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    background: rgba(255, 255, 255, 0.05);
                }}
            """)
            btn.clicked.connect(lambda checked, idx=i: self.switch_to(idx))
            self.buttons.append(btn)
            layout.addWidget(btn)
        
        self.set_active(0)
    
    def switch_to(self, idx):
        if self.current_index == idx:
            return
        self.current_index = idx
        self.set_active(idx)
        self.nav_clicked.emit(idx)
    
    def set_active(self, idx):
        colors = [C['green'], C['orange'], C['purple'], C['header_blue']]
        for i, btn in enumerate(self.buttons):
            if i == idx:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: rgba(255, 255, 255, 0.08);
                        color: {colors[i]};
                        border: none;
                        border-top: 3px solid {colors[i]};
                        font-size: 11px;
                        font-weight: 600;
                        padding: 5px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {C['text_gray']};
                        border: none;
                        border-top: 3px solid transparent;
                        font-size: 11px;
                        padding: 5px;
                    }}
                    QPushButton:hover {{
                        background: rgba(255, 255, 255, 0.05);
                    }}
                """)
