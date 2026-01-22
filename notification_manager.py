# notification_manager.py - Desktop Notification Manager

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtMultimedia import QSound
import os


class NotificationManager(QObject):
    """Manage desktop notifications for chat and tasks"""
    
    # Signals
    notification_clicked = pyqtSignal(str, dict)  # type, data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.tray_icon = None
        self.unread_count = 0
        self.sound_enabled = True
        self.notifications_enabled = True
        
        # Setup system tray
        self.setup_tray_icon()
    
    def setup_tray_icon(self):
        """Setup system tray icon"""
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self.parent_window)
        
        # Set icon (use app icon or create simple one)
        icon = self.create_app_icon()
        self.tray_icon.setIcon(icon)
        
        # Create context menu
        menu = QMenu()
        
        show_action = QAction("Show App", self.parent_window)
        show_action.triggered.connect(self.show_app)
        menu.addAction(show_action)
        
        menu.addSeparator()
        
        notifications_action = QAction("Notifications", self.parent_window)
        notifications_action.setCheckable(True)
        notifications_action.setChecked(True)
        notifications_action.triggered.connect(self.toggle_notifications)
        menu.addAction(notifications_action)
        
        sound_action = QAction("Sound", self.parent_window)
        sound_action.setCheckable(True)
        sound_action.setChecked(True)
        sound_action.triggered.connect(self.toggle_sound)
        menu.addAction(sound_action)
        
        menu.addSeparator()
        
        exit_action = QAction("Exit", self.parent_window)
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        
        # Connect click signal
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Show tray icon
        self.tray_icon.show()
    
    def create_app_icon(self, badge_count=0):
        """Create app icon with optional badge"""
        # Create a simple icon (you can replace with actual icon file)
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(16, 185, 129))  # Green color
        
        if badge_count > 0:
            # Add badge
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Badge background
            badge_size = 24
            badge_x = pixmap.width() - badge_size - 4
            badge_y = 4
            
            painter.setBrush(QColor(239, 68, 68))  # Red
            painter.setPen(QColor(255, 255, 255))
            painter.drawEllipse(badge_x, badge_y, badge_size, badge_size)
            
            # Badge text
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            badge_text = str(badge_count) if badge_count < 100 else "99+"
            painter.drawText(badge_x, badge_y, badge_size, badge_size, 
                           0x84, badge_text)  # AlignCenter
            
            painter.end()
        
        return QIcon(pixmap)
    
    def update_badge(self, count):
        """Update badge count on tray icon"""
        self.unread_count = count
        icon = self.create_app_icon(count)
        if self.tray_icon:
            self.tray_icon.setIcon(icon)
            
            # Update tooltip
            if count > 0:
                self.tray_icon.setToolTip(f"Quimo - {count} unread")
            else:
                self.tray_icon.setToolTip("Quimo")
    
    def show_notification(self, title, message, notification_type="info", data=None):
        """Show desktop notification"""
        if not self.notifications_enabled:
            return
        
        # Show system tray notification
        if self.tray_icon:
            icon = QSystemTrayIcon.Information
            if notification_type == "chat":
                icon = QSystemTrayIcon.Information
            elif notification_type == "task":
                icon = QSystemTrayIcon.Warning
            
            self.tray_icon.showMessage(
                title,
                message,
                icon,
                5000  # 5 seconds
            )
        
        # Play sound
        if self.sound_enabled:
            self.play_sound(notification_type)
    
    def play_sound(self, notification_type):
        """Play notification sound"""
        try:
            # Simple beep for now (you can add custom sound files)
            # QSound.play("sounds/notification.wav")
            pass  # Placeholder - add sound file later
        except Exception as e:
            print(f"Sound play error: {e}")
    
    def show_chat_notification(self, sender_name, message_preview):
        """Show chat message notification"""
        self.show_notification(
            f"💬 {sender_name}",
            message_preview[:100],  # Limit message length
            "chat",
            {"type": "chat", "sender": sender_name}
        )
    
    def show_task_notification(self, task_name, task_info):
        """Show task notification"""
        self.show_notification(
            f"📋 New Task",
            f"{task_name}\n{task_info}",
            "task",
            {"type": "task", "name": task_name}
        )
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.Trigger:  # Left click
            self.show_app()
        elif reason == QSystemTrayIcon.DoubleClick:  # Double click
            self.show_app()
    
    def show_app(self):
        """Show main application window"""
        if self.parent_window:
            self.parent_window.show()
            self.parent_window.raise_()
            self.parent_window.activateWindow()
    
    def toggle_notifications(self, checked):
        """Toggle notifications on/off"""
        self.notifications_enabled = checked
        print(f"Notifications: {'ON' if checked else 'OFF'}")
    
    def toggle_sound(self, checked):
        """Toggle sound on/off"""
        self.sound_enabled = checked
        print(f"Sound: {'ON' if checked else 'OFF'}")
    
    def exit_app(self):
        """Exit application"""
        if self.parent_window:
            self.parent_window.close()
    
    def hide(self):
        """Hide tray icon"""
        if self.tray_icon:
            self.tray_icon.hide()
    
    def show(self):
        """Show tray icon"""
        if self.tray_icon:
            self.tray_icon.show()
