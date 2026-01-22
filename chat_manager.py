# chat_manager.py - WebSocket Chat Manager

import json
import threading
import time
from datetime import datetime
import websocket
from PyQt5.QtCore import QObject, pyqtSignal


class ChatManager(QObject):
    """Manage WebSocket connection for real-time chat"""
    
    # Signals
    message_received = pyqtSignal(dict)
    user_status_changed = pyqtSignal(dict)
    messages_read = pyqtSignal(dict)
    typing_indicator = pyqtSignal(dict)
    connection_status = pyqtSignal(bool, str)
    
    def __init__(self, auth):
        super().__init__()
        self.auth = auth
        self.ws = None
        self.connected = False
        self.running = False
        self.thread = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
    
    def connect(self):
        """Connect to WebSocket server"""
        if self.connected:
            return
        
        try:
            token = self.auth.get_valid_token()
            if not token:
                self.connection_status.emit(False, "No auth token")
                return
            
            # WebSocket URL with token in query parameter (more reliable for WebSocket)
            ws_url = f"wss://att.igenhr.com/ws/chat/?token={token}"
            
            # Create WebSocket connection
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Run in separate thread
            self.running = True
            self.thread = threading.Thread(target=self._run_websocket, daemon=True)
            self.thread.start()
            
        except Exception as e:
            print(f"WebSocket connection error: {e}")
            self.connection_status.emit(False, str(e))
    
    def _run_websocket(self):
        """Run WebSocket in thread"""
        try:
            self.ws.run_forever()
        except Exception as e:
            print(f"WebSocket run error: {e}")
    
    def disconnect(self):
        """Disconnect from WebSocket"""
        self.running = False
        if self.ws:
            self.ws.close()
        self.connected = False
    
    def on_open(self, ws):
        """WebSocket connection opened"""
        print("WebSocket connected")
        self.connected = True
        self.reconnect_attempts = 0
        self.connection_status.emit(True, "Connected")
    
    def on_message(self, ws, message):
        """Receive message from WebSocket"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'chat_message':
                self.message_received.emit(data)
            elif msg_type == 'user_status':
                self.user_status_changed.emit(data)
            elif msg_type == 'messages_read':
                self.messages_read.emit(data)
            elif msg_type == 'typing_indicator':
                self.typing_indicator.emit(data)
                
        except Exception as e:
            print(f"Message parse error: {e}")
    
    def on_error(self, ws, error):
        """WebSocket error"""
        print(f"WebSocket error: {error}")
        self.connection_status.emit(False, str(error))
    
    def on_close(self, ws, close_status_code, close_msg):
        """WebSocket connection closed"""
        print(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.connected = False
        self.connection_status.emit(False, "Disconnected")
        
        # Auto reconnect
        if self.running and self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            print(f"Reconnecting... Attempt {self.reconnect_attempts}")
            time.sleep(2)
            self.connect()
    
    def send_message(self, receiver_id, message):
        """Send chat message"""
        if not self.connected:
            return False
        
        try:
            data = {
                'type': 'chat_message',
                'receiver_id': receiver_id,
                'message': message
            }
            self.ws.send(json.dumps(data))
            return True
        except Exception as e:
            print(f"Send message error: {e}")
            return False
    
    def mark_as_read(self, sender_id):
        """Mark messages as read"""
        if not self.connected:
            return
        
        try:
            data = {
                'type': 'mark_read',
                'sender_id': sender_id
            }
            self.ws.send(json.dumps(data))
        except Exception as e:
            print(f"Mark read error: {e}")
    
    def send_typing(self, receiver_id, is_typing):
        """Send typing indicator"""
        if not self.connected:
            return
        
        try:
            data = {
                'type': 'typing',
                'receiver_id': receiver_id,
                'is_typing': is_typing
            }
            self.ws.send(json.dumps(data))
        except Exception as e:
            print(f"Typing indicator error: {e}")
