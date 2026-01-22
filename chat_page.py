# chat_page.py - Exact WhatsApp Clone UI

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from datetime import datetime

from ui_components import GradientWidget, HeaderWidget, C

# WhatsApp Original Colors
WA_BG_DARK = "#0B141A"  # Dark background
WA_PANEL_BG = "#111B21"  # Panel background
WA_SENT_BUBBLE = "#005C4B"  # Sent message (dark green)
WA_RECEIVED_BUBBLE = "#202C33"  # Received message (dark gray)
WA_INPUT_BG = "#2A3942"  # Input background
WA_BORDER = "#2A3942"  # Border color
WA_TEXT_PRIMARY = "#E9EDEF"  # Primary text
WA_TEXT_SECONDARY = "#8696A0"  # Secondary text
WA_ONLINE_GREEN = "#00A884"  # Online indicator
WA_HOVER = "#202C33"  # Hover state


class WhatsAppMessageBubble(QWidget):
    """Exact WhatsApp message bubble"""
    def __init__(self, message_data, is_sent=False):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        
        # Main layout - align left or right
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 2, 10, 2)
        main_layout.setSpacing(0)
        
        if is_sent:
            main_layout.addStretch()  # Push to right
        
        # Bubble container
        bubble = QFrame()
        bubble.setMaximumWidth(400)
        
        if is_sent:
            # Sent message - app green gradient
            bubble.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #10B981, stop:1 #059669);
                    border-radius: 12px;
                    border-top-right-radius: 2px;
                }
            """)
        else:
            # Received message - subtle gray
            bubble.setStyleSheet("""
                QFrame {
                    background: rgba(255, 255, 255, 0.12);
                    border-radius: 12px;
                    border-top-left-radius: 2px;
                }
            """)
        
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(10, 6, 10, 6)
        bubble_layout.setSpacing(4)
        
        # Message text
        message_text = message_data.get('message', '')
        text_label = QLabel(message_text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("color: white; font-size: 14px; background: transparent;")
        bubble_layout.addWidget(text_label)
        
        # Time at bottom right
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
        time_label.setAlignment(Qt.AlignRight)
        time_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 11px; background: transparent;")
        bubble_layout.addWidget(time_label)
        
        main_layout.addWidget(bubble)
        
        if not is_sent:
            main_layout.addStretch()  # Push to left


class WhatsAppUserCard(QFrame):
    """Exact WhatsApp user card"""
    clicked = pyqtSignal(dict)
    
    def __init__(self, user_data, is_active=False):
        super().__init__()
        self.user_data = user_data
        self.is_active = is_active
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(72)
        
        # Modern style background
        if is_active:
            bg_color = "rgba(255, 255, 255, 0.12)"
        else:
            bg_color = "transparent"
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border: none;
            }}
            QFrame:hover {{
                background: rgba(255, 255, 255, 0.08);
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)
        
        # Avatar circle
        avatar = QLabel("👤")
        avatar.setFixedSize(50, 50)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 25px;
                font-size: 24px;
            }
        """)
        layout.addWidget(avatar)
        
        # User info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name = user_data.get('full_name', user_data.get('username', 'User'))
        if len(name) > 20:
            name = name[:20] + "..."
        name_label = QLabel(name)
        name_label.setStyleSheet("color: rgba(255, 255, 255, 0.95); font-size: 16px; font-weight: 400; background: transparent;")
        info_layout.addWidget(name_label)
        
        # Last message or status
        is_online = user_data.get('is_online', False)
        status_text = "Online" if is_online else "Offline"
        status_label = QLabel(status_text)
        status_label.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 14px; background: transparent;")
        info_layout.addWidget(status_label)
        
        layout.addLayout(info_layout, 1)
        
        # Right side - time and unread
        right_layout = QVBoxLayout()
        right_layout.setSpacing(4)
        right_layout.setAlignment(Qt.AlignTop)
        
        # Time placeholder
        time_label = QLabel("")
        time_label.setStyleSheet(f"color: {WA_TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        right_layout.addWidget(time_label)
        
        # Unread badge
        unread_count = user_data.get('unread_count', 0)
        if unread_count > 0:
            badge = QLabel(str(min(unread_count, 99)))
            badge.setFixedSize(22, 22)
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #10B981, stop:1 #059669);
                    color: white;
                    border-radius: 11px;
                    font-size: 12px;
                    font-weight: 600;
                }
            """)
            right_layout.addWidget(badge)
        
        layout.addLayout(right_layout)
    
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
        
        # Use app's gradient background like other pages
        self.container = GradientWidget()
        self.container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Splitter with subtle styling
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: rgba(255, 255, 255, 0.1);
                width: 2px;
            }
            QSplitter::handle:hover {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        
        # User list
        self.user_list_container = self.create_user_list()
        splitter.addWidget(self.user_list_container)
        
        # Chat area
        self.chat_container = self.create_chat_area()
        splitter.addWidget(self.chat_container)
        
        # Set initial sizes
        splitter.setSizes([350, 550])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        container_layout.addWidget(splitter)
        layout.addWidget(self.container)
    
    def create_user_list(self):
        """Modern user list matching app style"""
        panel = QWidget()
        panel.setMinimumWidth(300)
        panel.setMaximumWidth(450)
        panel.setStyleSheet("background: rgba(0, 0, 0, 0.2); border-right: 1px solid rgba(255, 255, 255, 0.1);")
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        
        # Modern header
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("background: rgba(0, 0, 0, 0.3); border-bottom: 1px solid rgba(255, 255, 255, 0.1);")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 10, 16, 10)
        
        chats_label = QLabel("Chats")
        chats_label.setStyleSheet("color: rgba(255, 255, 255, 0.95); font-size: 24px; font-weight: 600; background: transparent;")
        header_layout.addWidget(chats_label)
        header_layout.addStretch()
        
        panel_layout.addWidget(header)
        
        # User list scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.2);
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
            }
        """)
        
        self.user_list_widget = QWidget()
        self.user_list_widget.setStyleSheet("background: transparent;")
        self.user_list_layout = QVBoxLayout(self.user_list_widget)
        self.user_list_layout.setContentsMargins(0, 0, 0, 0)
        self.user_list_layout.setSpacing(0)
        self.user_list_layout.addStretch()
        
        scroll.setWidget(self.user_list_widget)
        panel_layout.addWidget(scroll, 1)
        
        return panel
    
    def create_chat_area(self):
        """Modern chat area matching app style"""
        panel = QWidget()
        panel.setStyleSheet("background: rgba(0, 0, 0, 0.15);")
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        
        # Chat header - modern style
        self.chat_header = QFrame()
        self.chat_header.setFixedHeight(60)
        self.chat_header.setStyleSheet("background: rgba(0, 0, 0, 0.3); border-bottom: 1px solid rgba(255, 255, 255, 0.1);")
        
        header_layout = QHBoxLayout(self.chat_header)
        header_layout.setContentsMargins(16, 10, 16, 10)
        header_layout.setSpacing(12)
        
        # Avatar
        avatar = QLabel("👤")
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("background: rgba(255, 255, 255, 0.1); border-radius: 20px; font-size: 20px;")
        header_layout.addWidget(avatar)
        
        # Name and status
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        self.chat_user_name = QLabel("")
        self.chat_user_name.setStyleSheet("color: rgba(255, 255, 255, 0.95); font-size: 16px; font-weight: 400; background: transparent;")
        info_layout.addWidget(self.chat_user_name)
        
        self.chat_user_status = QLabel("")
        self.chat_user_status.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 13px; background: transparent;")
        info_layout.addWidget(self.chat_user_status)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        panel_layout.addWidget(self.chat_header)
        
        # Messages scroll - modern styling
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.messages_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.2);
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
            }
        """)
        
        self.messages_widget = QWidget()
        self.messages_widget.setStyleSheet("background: transparent;")
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)
        self.messages_layout.setSpacing(2)
        self.messages_layout.addStretch()
        
        self.messages_scroll.setWidget(self.messages_widget)
        panel_layout.addWidget(self.messages_scroll, 1)
        
        # Typing indicator
        self.typing_indicator = QLabel("")
        self.typing_indicator.setStyleSheet("color: #10B981; font-size: 13px; font-style: italic; background: transparent; padding: 5px 16px;")
        self.typing_indicator.hide()
        panel_layout.addWidget(self.typing_indicator)
        
        # Input - modern style
        input_container = QFrame()
        input_container.setFixedHeight(62)
        input_container.setStyleSheet("background: rgba(0, 0, 0, 0.3); border-top: 1px solid rgba(255, 255, 255, 0.1);")
        
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(16, 10, 16, 10)
        input_layout.setSpacing(10)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message")
        self.message_input.setFixedHeight(42)
        self.message_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 21px;
                padding: 0 16px;
                font-size: 15px;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
            QLineEdit:focus {
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.textChanged.connect(self.on_typing)
        input_layout.addWidget(self.message_input, 1)
        
        self.send_button = QPushButton("➤")
        self.send_button.setFixedSize(42, 42)
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #10B981, stop:1 #059669);
                color: white;
                border: none;
                border-radius: 21px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #34D399, stop:1 #10B981);
            }
            QPushButton:disabled {
                background: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.3);
            }
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
            empty.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 14px; padding: 40px; background: transparent;")
            empty.setAlignment(Qt.AlignCenter)
            self.user_list_layout.insertWidget(0, empty)
        else:
            for user in filtered_users:
                is_active = user.get('id') == self.current_user_id
                card = WhatsAppUserCard(user, is_active)
                card.clicked.connect(self.select_user)
                self.user_list_layout.insertWidget(self.user_list_layout.count() - 1, card)
    
    def select_user(self, user_data):
        self.current_user_id = user_data.get('id')
        self.current_user_data = user_data
        
        name = user_data.get('full_name', user_data.get('username', 'User'))
        self.chat_user_name.setText(name)
        
        is_online = user_data.get('is_online', False)
        status_text = "online" if is_online else "offline"
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
                bubble = WhatsAppMessageBubble(msg, is_sent)
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
            bubble = WhatsAppMessageBubble(data, is_sent)
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
            status_text = "online" if is_online else "offline"
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
        # Connection status can be shown in user list header if needed
        pass
    
    def showEvent(self, event):
        super().showEvent(event)
        self.load_users()
        
        if not self.chat_manager.connected:
            self.chat_manager.connect()
