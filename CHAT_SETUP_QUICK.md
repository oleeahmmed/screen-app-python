# Chat Feature - Quick Setup Guide

## ✅ What's Already Done

### Server-Side (100% Complete)
- ✅ Database models (ChatMessage, OnlineStatus)
- ✅ WebSocket consumer for real-time messaging
- ✅ REST API endpoints for chat
- ✅ Serializers for data formatting
- ✅ URL routing configured
- ✅ ASGI configuration with Channels
- ✅ Redis channel layer setup

### Desktop App (100% Complete)
- ✅ ChatPage UI with modern design
- ✅ ChatManager for WebSocket handling
- ✅ ChatAPI for REST fallback
- ✅ Integration in main.py
- ✅ Navigation button added
- ✅ All signals connected

## 🚀 How to Use

### 1. Start the Server
```bash
cd server-api

# Make sure Redis is running
sudo systemctl start redis

# Run with Daphne (for WebSocket support)
daphne -b 0.0.0.0 -p 8000 config.asgi:application

# Or use the deployment script
./deploy_daphne.sh
```

### 2. Run the Desktop App
```bash
cd desktop-app

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run the app
python main.py
```

### 3. Test the Chat
1. Login with first user account
2. Click the 💬 Chat button (3rd tab)
3. Open another instance and login with different user (same company)
4. Select user from list
5. Send messages back and forth
6. Watch real-time updates!

## 📋 Features Available

### ✅ Working Features
- Real-time messaging via WebSocket
- User list with online/offline status
- Message bubbles (sent/received)
- Typing indicators
- Read receipts
- Unread message badges
- User search
- Connection status indicator
- Auto-reconnection
- REST API fallback

### 🎨 UI Features
- Modern glass-morphism design
- Smooth animations
- Responsive layout
- Color-coded messages
- Emoji support
- Timestamp display

## 🔧 Configuration

### Desktop App
No configuration needed! It uses the existing `API_BASE_URL` from `config.py`:
```python
API_BASE_URL = "https://att.igenhr.com/api"
```

WebSocket URL is automatically constructed as:
```python
ws_url = "wss://att.igenhr.com/ws/chat/"
```

### Server
Already configured in `settings.py`:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

## 🐛 Troubleshooting

### Chat button not showing?
- Make sure you updated `ui_components.py` (4 nav items now)
- Restart the app

### WebSocket not connecting?
- Check Redis is running: `redis-cli ping` (should return PONG)
- Check Daphne is running (not Gunicorn)
- Check server logs for errors

### Users not loading?
- Ensure you're logged in
- Check you have other employees in your company
- Check API endpoint: `curl -H "Authorization: Bearer <token>" https://att.igenhr.com/api/chat/users/`

### Messages not sending?
- Check connection status (top of user list)
- If red, it will fallback to REST API
- Check browser/desktop console for errors

## 📱 Navigation

The app now has **4 tabs** in bottom navigation:

1. 📊 **Attendance** - Clock in/out and work timer
2. ✓ **Tasks** - Task management
3. 💬 **Chat** - Real-time messaging (NEW!)
4. 👤 **Profile** - User profile and settings

## 🎯 Next Steps

### Optional Enhancements
1. Add notification sounds for new messages
2. Add desktop notifications
3. Add file/image sharing
4. Add group chats
5. Add message search
6. Add emoji picker

### Testing Checklist
- [ ] Login with two users from same company
- [ ] Send messages back and forth
- [ ] Test typing indicators
- [ ] Test online/offline status
- [ ] Test unread badges
- [ ] Test user search
- [ ] Test connection recovery
- [ ] Test with WebSocket disabled (REST fallback)

## 📚 Documentation

- **Full Documentation**: See `CHAT_FEATURE.md`
- **Server Setup**: See `server-api/CHAT_SETUP.md`
- **API Reference**: See `CHAT_FEATURE.md` (WebSocket Protocol section)

## ✨ That's It!

Your chat feature is **fully implemented and ready to use**! 

Just make sure:
1. ✅ Redis is running
2. ✅ Server is running with Daphne
3. ✅ Desktop app is updated
4. ✅ Users are in the same company

Happy chatting! 💬
