# chat_page.py - Simple Clean Chat (Matching Tasks Style)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from datetime import datetime

from ui_components import GradientWidget, HeaderWidget, C


class SimpleMessageBubble(QFrame):
    """Simple message bubble like TaskCard"""
    def __init__(self, message_data, is_sent=False):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(60)
        
        # Use task card colors
        if is_sent:
            color = C['card_green']
        else:
            color = C['card_purple']
        
        self.setStyleSheet(f"background: {color}; border-radius: 15px;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # Message text
        message_text = message_data.get('message', '')
        text_label = QLabel(message_text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: white; font-size: 14px; font-weight: 500;")
        layout.addWidget(text_label, 1)
        
        # Time
        created_at = message_data.get('created_at', '')
        if created_at:
            try:
                if 'T' in created_at:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    time_str = dt.strftime('%I:%M %p')
                else:
                    time_str = created_at
            except:
                time_str = created_at
        else:
            time_str = datetime.now().strftime('%I:%M %p')
        
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 11px;")
        layout.addWidget(time_label)


class CleanUserCard(QFrame):
    """Ultra clean user card - minimal design"""
    clicked = pyqtSignal(dict)
    
    def __init__(self, user_data, is_active=False):
        super().__init__()
        self.user_data = user_data
        self.is_active = is_active
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)
        
        # Clean transparent background with subtle hover
        if is_active:
            bg_color = "rgba(255,255,255,0.12)"
        else:
            bg_color = "transparent"
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border-radius: 10px;
            }}
            QFrame:hover {{
                background: rgba(255,255,255,0.08);
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        
        # Online indicator (dot)
        is_online = user_data.get('is_online', False)
        online_dot = QLabel("●")
        online_dot.setFixedSize(12, 12)
        online_dot.setAlignment(Qt.AlignCenter)
        if is_online:
            online_dot.setStyleSheet(f"color: {C['green']}; font-size: 16px; background: transparent;")
        else:
            online_dot.setStyleSheet("color: rgba(255,255,255,0.3); font-size: 16px; background: transparent;")
        layout.addWidget(online_dot)
        
        # User name (clean)
        name = user_data.get('full_name', user_data.get('username', 'User'))
        if len(name) > 14:
            name = name[:14] + "..."
        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: {C['text_white']}; font-size: 13px; font-weight: 500; background: transparent;")
        layout.addWidget(name_label, 1)
        
        # Unread badge (minimal)
        unread_count = user_data.get('unread_count', 0)
        if unread_count > 0:
            badge = QLabel(str(unread_count))
            badge.setFixedSize(20, 20)
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(f"background: {C['green']}; color: white; border-radius: 10px; font-size: 10px; font-weight: bold;")
            layout.addWidget(badge)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.user_data)


class ChatPage(QWidget):
    """Simple clean chat page"""
    subscription_clicked = pyqtSignal()
    
    def __init__(self, chat_manager, chat_api, parent=None):
        super().__init__()
        self.chat_manager = chat_manager
        self.chat_api = chat_api
        self.parent_dash = parent
        self.username = "User"
        self.days_remaining = 0
        self.current_user_id = None
        self.current_user_data = None
        self.users = []
        self.messages = []
        self.typing_timer = None
        
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.container = GradientWidget()
        self.container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 20)
        container_layout.setSpacing(10)
        
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
        
        chat_title = QLabel("CHAT")
        chat_title.setStyleSheet(f"background: transparent; color: {C['text_white']}; font-size: 28px; font-weight: bold;")
        title_layout.addWidget(chat_title)
        title_layout.addStretch()
        
        # Connection status
        self.connection_status = QLabel("🔴 Disconnected")
        self.connection_status.setStyleSheet(f"color: {C['text_gray']}; font-size: 12px; background: transparent;")
        title_layout.addWidget(self.connection_status)
        
        container_layout.addWidget(title_widget)
        
        # Content
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # User list
        self.user_list_container = self.create_user_list()
        content_layout.addWidget(self.user_list_container)
        
        # Chat area
        self.chat_container = self.create_chat_area()
        content_layout.addWidget(self.chat_container, 1)
        
        container_layout.addWidget(content_widget, 1)
        layout.addWidget(self.container)
    
    def create_user_list(self):
        """Create clean minimal user list - no search, just users"""
        panel = QWidget()
        panel.setFixedWidth(160)
        panel.setStyleSheet("background: transparent;")
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(15, 0, 5, 0)
        panel_layout.setSpacing(0)
        
        # User list scroll - clean, no search
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea {background: transparent; border: none;} QScrollBar:vertical {background: transparent; width: 4px;} QScrollBar::handle:vertical {background: rgba(255,255,255,0.2); border-radius: 2px;}")
        
        self.user_list_widget = QWidget()
        self.user_list_widget.setStyleSheet("background: transparent;")
        self.user_list_layout = QVBoxLayout(self.user_list_widget)
        self.user_list_layout.setContentsMargins(0, 0, 0, 0)
        self.user_list_layout.setSpacing(8)
        self.user_list_layout.addStretch()
        
        scroll.setWidget(self.user_list_widget)
        panel_layout.addWidget(scroll, 1)
        
        return panel
    
    def create_chat_area(self):
        """Create simple chat area"""
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(10, 0, 20, 0)
        panel_layout.setSpacing(10)
        
        # Chat header - simple
        self.chat_header = QFrame()
        self.chat_header.setFixedHeight(60)
        self.chat_header.setStyleSheet(f"background: rgba(255,255,255,0.08); border-radius: 15px;")
        
        header_layout = QHBoxLayout(self.chat_header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        self.chat_user_name = QLabel("Select a user")
        self.chat_user_name.setStyleSheet(f"color: {C['text_white']}; font-size: 16px; font-weight: 600; background: transparent;")
        header_layout.addWidget(self.chat_user_name)
        
        self.chat_user_status = QLabel("")
        self.chat_user_status.setStyleSheet(f"color: {C['text_gray']}; font-size: 12px; background: transparent;")
        header_layout.addWidget(self.chat_user_status)
        header_layout.addStretch()
        
        panel_layout.addWidget(self.chat_header)
        
        # Messages scroll
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.messages_scroll.setStyleSheet("QScrollArea {background: transparent; border: none;} QScrollBar:vertical {background: transparent; width: 6px;} QScrollBar::handle:vertical {background: rgba(255,255,255,0.3); border-radius: 3px;}")
        
        self.messages_widget = QWidget()
        self.messages_widget.setStyleSheet("background: transparent;")
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)
        self.messages_layout.setSpacing(12)
        self.messages_layout.addStretch()
        
        self.messages_scroll.setWidget(self.messages_widget)
        panel_layout.addWidget(self.messages_scroll, 1)
        
        # Typing
        self.typing_indicator = QLabel("")
        self.typing_indicator.setStyleSheet(f"color: {C['text_gray']}; font-size: 11px; font-style: italic; background: transparent;")
        self.typing_indicator.hide()
        panel_layout.addWidget(self.typing_indicator)
        
        # Input - simple
        input_container = QFrame()
        input_container.setFixedHeight(60)
        input_container.setStyleSheet(f"background: rgba(255,255,255,0.08); border-radius: 15px;")
        
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(15, 10, 15, 10)
        input_layout.setSpacing(10)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message...")
        self.message_input.setFixedHeight(40)
        self.message_input.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0,0,0,0.3);
                color: {C['text_white']};
                border: none;
                border-radius: 20px;
                padding: 0 15px;
                font-size: 14px;
            }}
        """)
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.textChanged.connect(self.on_typing)
        input_layout.addWidget(self.message_input, 1)
        
        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(70, 40)
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background: {C['green']};
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #5FE076;
            }}
            QPushButton:disabled {{
                background: rgba(255,255,255,0.1);
                color: rgba(255,255,255,0.3);
            }}
        """)
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setEnabled(False)
        input_layout.addWidget(self.send_button)
        
        panel_layout.addWidget(input_container)
        
        return panel
    
    def connect_signals(self):
        self.chat_manager.message_received.connect(self.on_message_received)
        self.chat_manager.user_status_changed.connect(self.on_user_status_changed)
        self.chat_manager.typing_indicator.connect(self.on_typing_indicator)
        self.chat_manager.connection_status.connect(self.on_connection_status)
    
    def set_username(self, name, days_remaining=0):
        self.username = name
        self.days_remaining = days_remaining
    
    def load_users(self):
        print("🔄 Loading users from API...")
        ok, users = self.chat_api.get_company_users()
        print(f"📊 API Response: ok={ok}, users={len(users) if users else 0}")
        if ok and users:
            self.users = users
            print(f"✅ Successfully loaded {len(self.users)} users")
            self.display_users()
        else:
            print(f"❌ Failed to load users: ok={ok}")
            self.users = []
            self.display_users()
    
    def display_users(self, filter_text=""):
        while self.user_list_layout.count() > 1:
            item = self.user_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        filtered_users = self.users
        if filter_text:
            filter_text = filter_text.lower()
            filtered_users = [u for u in self.users if filter_text in u.get('username', '').lower() or filter_text in u.get('full_name', '').lower()]
        
        if not filtered_users:
            empty = QLabel("No users")
            empty.setStyleSheet(f"color: {C['text_gray']}; font-size: 12px; padding: 20px; background: transparent;")
            empty.setAlignment(Qt.AlignCenter)
            self.user_list_layout.insertWidget(0, empty)
        else:
            for user in filtered_users:
                is_active = user.get('id') == self.current_user_id
                card = CleanUserCard(user, is_active)
                card.clicked.connect(self.select_user)
                self.user_list_layout.insertWidget(self.user_list_layout.count() - 1, card)
    
    def select_user(self, user_data):
        self.current_user_id = user_data.get('id')
        self.current_user_data = user_data
        
        name = user_data.get('full_name', user_data.get('username', 'User'))
        self.chat_user_name.setText(name)
        
        is_online = user_data.get('is_online', False)
        status_text = "🟢 Online" if is_online else "⚫ Offline"
        self.chat_user_status.setText(status_text)
        
        self.send_button.setEnabled(True)
        self.load_conversation()
        
        # Refresh user list to show active state
        self.display_users()
        
        if self.chat_manager.connected:
            self.chat_manager.mark_as_read(self.current_user_id)
    
    def load_conversation(self):
        if not self.current_user_id:
            return
        
        ok, messages = self.chat_api.get_conversation(self.current_user_id)
        if ok:
            self.messages = messages
            self.display_messages()
    
    def display_messages(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.messages:
            empty = QLabel("No messages\nStart chatting!")
            empty.setStyleSheet(f"color: {C['text_gray']}; font-size: 14px; background: transparent;")
            empty.setAlignment(Qt.AlignCenter)
            self.messages_layout.insertWidget(0, empty)
        else:
            from auth import AuthManager
            auth = AuthManager()
            current_username = auth.get_username()
            
            for msg in self.messages:
                is_sent = msg.get('sender_username') == current_username
                bubble = SimpleMessageBubble(msg, is_sent)
                self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
        
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        scrollbar = self.messages_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        if not self.current_user_id:
            return
        
        message_text = self.message_input.text().strip()
        if not message_text:
            return
        
        if self.chat_manager.connected:
            success = self.chat_manager.send_message(self.current_user_id, message_text)
            if success:
                self.message_input.clear()
        else:
            ok, result = self.chat_api.send_message(self.current_user_id, message_text)
            if ok:
                self.message_input.clear()
                self.load_conversation()
    
    def on_typing(self, text):
        if not self.current_user_id or not self.chat_manager.connected:
            return
        
        is_typing = len(text) > 0
        self.chat_manager.send_typing(self.current_user_id, is_typing)
        
        if self.typing_timer:
            self.typing_timer.stop()
        
        if is_typing:
            self.typing_timer = QTimer()
            self.typing_timer.setSingleShot(True)
            self.typing_timer.timeout.connect(lambda: self.chat_manager.send_typing(self.current_user_id, False))
            self.typing_timer.start(2000)
    
    def on_message_received(self, data):
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        
        from auth import AuthManager
        auth = AuthManager()
        # Get user_id from user_info
        current_user_id = None
        if auth.user_info:
            current_user_id = auth.user_info.get('id')
        
        if (sender_id == self.current_user_id and receiver_id == current_user_id) or (sender_id == current_user_id and receiver_id == self.current_user_id):
            self.messages.append(data)
            is_sent = sender_id == current_user_id
            bubble = SimpleMessageBubble(data, is_sent)
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
            self.scroll_to_bottom()
            
            if receiver_id == current_user_id and self.chat_manager.connected:
                self.chat_manager.mark_as_read(sender_id)
        
        self.load_users()
    
    def on_user_status_changed(self, data):
        user_id = data.get('user_id')
        is_online = data.get('is_online')
        
        for user in self.users:
            if user.get('id') == user_id:
                user['is_online'] = is_online
                break
        
        if self.current_user_id == user_id:
            status_text = "🟢 Online" if is_online else "⚫ Offline"
            self.chat_user_status.setText(status_text)
        
        self.display_users()
    
    def on_typing_indicator(self, data):
        sender_id = data.get('sender_id')
        is_typing = data.get('is_typing')
        
        if sender_id == self.current_user_id:
            if is_typing:
                sender_name = data.get('sender_username', 'User')
                self.typing_indicator.setText(f"{sender_name} is typing...")
                self.typing_indicator.show()
            else:
                self.typing_indicator.hide()
    
    def on_connection_status(self, connected, message):
        if connected:
            self.connection_status.setText("🟢 Connected")
            self.connection_status.setStyleSheet(f"color: {C['green']}; font-size: 12px; background: transparent;")
        else:
            self.connection_status.setText(f"🔴 {message}")
            self.connection_status.setStyleSheet(f"color: {C['red']}; font-size: 12px; background: transparent;")
    
    def showEvent(self, event):
        super().showEvent(event)
        self.load_users()
        
        if not self.chat_manager.connected:
            self.chat_manager.connect()
