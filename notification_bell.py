# notification_bell.py - Animated Notification Bell Icon

from PyQt5.QtWidgets import QPushButton, QLabel
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer, pyqtSignal
from PyQt5.QtGui import QFont


class NotificationBell(QPushButton):
    """Animated notification bell icon with badge"""
    
    clicked_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unread_count = 0
        self.is_animating = False
        
        # Setup button
        self.setFixedSize(40, 40)
        self.setCursor(0x0d)  # PointingHandCursor
        self.update_style()
        
        # Animation
        self.animation = QPropertyAnimation(self, b"rotation")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.OutElastic)
        
        # Click handler
        self.clicked.connect(self.clicked_signal.emit)
    
    def update_style(self):
        """Update button style based on unread count"""
        if self.unread_count > 0:
            # Has notifications - show badge
            badge_text = str(self.unread_count) if self.unread_count < 100 else "99+"
            self.setText(f"🔔")
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    color: #F59E0B;
                    font-size: 22px;
                    position: relative;
                }}
                QPushButton:hover {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                }}
            """)
        else:
            # No notifications
            self.setText("🔔")
            self.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 22px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    color: rgba(255, 255, 255, 0.9);
                }
            """)
    
    def set_count(self, count):
        """Set unread notification count"""
        self.unread_count = count
        self.update_style()
        
        # Animate if count increased
        if count > 0:
            self.animate()
    
    def animate(self):
        """Animate bell (shake effect)"""
        if self.is_animating:
            return
        
        self.is_animating = True
        
        # Create shake animation using QTimer
        self.shake_count = 0
        self.shake_timer = QTimer()
        self.shake_timer.timeout.connect(self._shake_step)
        self.shake_timer.start(50)  # 50ms intervals
    
    def _shake_step(self):
        """Single step of shake animation"""
        if self.shake_count >= 6:  # 3 shakes (left-right-left-right-left-right)
            self.shake_timer.stop()
            self.is_animating = False
            return
        
        # Alternate between rotating left and right
        if self.shake_count % 2 == 0:
            self.setStyleSheet(self.styleSheet() + "transform: rotate(-15deg);")
        else:
            self.setStyleSheet(self.styleSheet() + "transform: rotate(15deg);")
        
        self.shake_count += 1
    
    # Property for animation (not used but kept for future)
    def get_rotation(self):
        return 0
    
    def set_rotation(self, angle):
        pass
    
    rotation = pyqtProperty(int, get_rotation, set_rotation)


class NotificationBellWithBadge(QPushButton):
    """Notification bell with visible badge overlay"""
    
    clicked_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unread_count = 0
        
        # Setup button
        self.setFixedSize(50, 40)
        self.setCursor(0x0d)  # PointingHandCursor
        
        # Bell icon
        self.setText("🔔")
        self.update_style()
        
        # Badge label (overlay)
        self.badge = QLabel(self)
        self.badge.setFixedSize(18, 18)
        self.badge.setAlignment(0x84)  # AlignCenter
        self.badge.move(28, 5)
        self.badge.hide()
        
        # Click handler
        self.clicked.connect(self.clicked_signal.emit)
    
    def update_style(self):
        """Update button style"""
        if self.unread_count > 0:
            # Has notifications
            self.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #F59E0B;
                    font-size: 22px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                }
            """)
        else:
            # No notifications
            self.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 22px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    color: rgba(255, 255, 255, 0.9);
                }
            """)
    
    def set_count(self, count):
        """Set unread notification count"""
        self.unread_count = count
        self.update_style()
        
        if count > 0:
            # Show badge
            badge_text = str(count) if count < 100 else "99+"
            self.badge.setText(badge_text)
            self.badge.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #EF4444, stop:1 #DC2626);
                    color: white;
                    border-radius: 9px;
                    font-size: 10px;
                    font-weight: bold;
                    border: 2px solid #1e3a5f;
                }
            """)
            self.badge.show()
            
            # Animate
            self.animate()
        else:
            # Hide badge
            self.badge.hide()
    
    def animate(self):
        """Animate bell (pulse effect)"""
        # Simple pulse using style changes
        original_style = self.styleSheet()
        
        # Pulse effect
        self.setStyleSheet(original_style + "font-size: 26px;")
        QTimer.singleShot(100, lambda: self.setStyleSheet(original_style + "font-size: 22px;"))
        QTimer.singleShot(200, lambda: self.setStyleSheet(original_style + "font-size: 26px;"))
        QTimer.singleShot(300, lambda: self.setStyleSheet(original_style))
