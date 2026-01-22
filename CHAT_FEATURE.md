# Chat Feature Documentation

## Overview
The desktop application now includes a **real-time chat feature** that allows employees within the same company to communicate with each other instantly using WebSocket technology.

## Features

### ✅ Real-time Messaging
- Instant message delivery via WebSocket
- Message bubbles with sender info and timestamps
- Sent/received message differentiation
- Auto-scroll to latest messages

### ✅ User Management
- List of all company employees
- Online/offline status indicators (🟢/⚫)
- User search functionality
- Unread message badges

### ✅ Connection Status
- Real-time connection indicator
- Auto-reconnection on disconnect
- Fallback to REST API if WebSocket fails

### ✅ Typing Indicators
- Shows when other user is typing
- Auto-hides after 2 seconds of inactivity

### ✅ Read Receipts
- Messages marked as read automatically
- Unread count per conversation

## Architecture

### Desktop App Components

#### 1. **chat_page.py** - Main Chat UI
- `ChatPage`: Main chat interface widget
- `MessageBubble`: Individual message display
- `UserListItem`: User list item with status
- Modern glass-morphism design matching app theme

#### 2. **chat_manager.py** - WebSocket Handler
- `ChatManager`: Manages WebSocket connection
- Handles: messages, status updates, typing, read receipts
- Auto-reconnection with exponential backoff
- Thread-safe WebSocket operations

#### 3. **chat_api.py** - REST API Helper
- `ChatAPI`: REST API fallback methods
- Get users, conversations, send messages
- Unread counts and mark as read

### Server Components

#### 1. **Models** (models.py)
- `ChatMessage`: Message storage with company scope
- `OnlineStatus`: User online/offline tracking

#### 2. **WebSocket Consumer** (consumers.py)
- `ChatConsumer`: Real-time message handling
- Company-scoped rooms (users only see company members)
- Typing indicators and read receipts

#### 3. **REST API** (chat_views.py)
- User list endpoint
- Conversation history
- Send message (fallback)
- Unread counts

## Usage

### For Users

1. **Access Chat**
   - Click the 💬 Chat button in bottom navigation
   - Chat is the 3rd tab (between Tasks and Profile)

2. **Start Conversation**
   - Select a user from the left panel
   - Type message in the input box
   - Press Enter or click Send button

3. **View Status**
   - 🟢 Green dot = User is online
   - ⚫ Gray dot = User is offline
   - Red badge = Unread message count

4. **Search Users**
   - Use search box at top of user list
   - Filters by name or username

### For Developers

#### Initialize Chat
```python
# In Dashboard.__init__
self.chat_manager = ChatManager(self.auth)
self.chat_api = ChatAPI(self.auth)

# Create chat page
self.chat_page = ChatPage(self.chat_manager, self.chat_api, self)
self.pages.addWidget(self.chat_page)
```

#### Connect WebSocket
```python
# On login/dashboard show
self.chat_manager.connect()

# On logout
self.chat_manager.disconnect()
```

#### Handle Messages
```python
# Signals are automatically connected in ChatPage
self.chat_manager.message_received.connect(self.on_message_received)
self.chat_manager.user_status_changed.connect(self.on_user_status_changed)
self.chat_manager.typing_indicator.connect(self.on_typing_indicator)
self.chat_manager.connection_status.connect(self.on_connection_status)
```

## WebSocket Protocol

### Connection
```
URL: wss://att.igenhr.com/ws/chat/
Headers: Authorization: Bearer <token>
```

### Message Types

#### 1. Chat Message
```json
{
  "type": "chat_message",
  "receiver_id": 123,
  "message": "Hello!"
}
```

#### 2. Mark as Read
```json
{
  "type": "mark_read",
  "sender_id": 123
}
```

#### 3. Typing Indicator
```json
{
  "type": "typing",
  "receiver_id": 123,
  "is_typing": true
}
```

### Received Events

#### 1. New Message
```json
{
  "type": "chat_message",
  "message_id": 456,
  "sender_id": 123,
  "sender_username": "john",
  "receiver_id": 789,
  "message": "Hello!",
  "created_at": "2024-01-20T10:30:00Z",
  "is_read": false
}
```

#### 2. User Status
```json
{
  "type": "user_status",
  "user_id": 123,
  "username": "john",
  "is_online": true
}
```

#### 3. Messages Read
```json
{
  "type": "messages_read",
  "reader_id": 789,
  "sender_id": 123
}
```

#### 4. Typing Indicator
```json
{
  "type": "typing_indicator",
  "sender_id": 123,
  "sender_username": "john",
  "receiver_id": 789,
  "is_typing": true
}
```

## REST API Endpoints

### Get Company Users
```
GET /api/chat/users/
Response: List of users with online status and unread counts
```

### Get Conversation
```
GET /api/chat/conversation/<user_id>/
Response: List of messages between current user and specified user
```

### Send Message (Fallback)
```
POST /api/chat/send/
Body: {"receiver_id": 123, "message": "Hello"}
Response: Created message object
```

### Get Unread Count
```
GET /api/chat/unread/
Response: {"total_unread": 5, "unread_by_sender": [...]}
```

### Mark as Read
```
POST /api/chat/mark-read/
Body: {"sender_id": 123}
Response: Success message
```

## Styling

The chat interface uses the same design system as the rest of the app:

- **Colors**: Defined in `ui_components.py` (C dictionary)
- **Glass Cards**: Transparent backgrounds with blur effect
- **Gradients**: Blue gradient matching app theme
- **Icons**: Emoji-based for consistency

### Message Bubbles
- **Sent**: Blue background (`C['header_blue']`)
- **Received**: Transparent with border
- **Max Width**: 300px for readability
- **Rounded Corners**: 15px border-radius

### User List
- **Height**: 65px per item
- **Hover Effect**: Lighter background
- **Active Border**: Blue border on hover
- **Badge**: Red circle with unread count

## Error Handling

### Connection Failures
- Auto-reconnect up to 5 times
- 2-second delay between attempts
- Falls back to REST API if WebSocket unavailable

### Message Send Failures
- Try WebSocket first
- Fallback to REST API
- Show error if both fail

### Network Issues
- Connection status indicator updates
- Messages queued locally (future enhancement)
- Graceful degradation to REST API

## Security

### Authentication
- JWT token required for WebSocket connection
- Token sent in Authorization header
- Server validates token on connect

### Authorization
- Users can only see company members
- Messages scoped to company
- Cannot access other companies' chats

### Data Privacy
- Messages stored in database
- Only sender and receiver can see messages
- Company admin has no access to message content

## Performance

### Optimizations
- WebSocket for real-time updates (low latency)
- REST API for bulk data (conversations)
- Lazy loading of conversations
- Auto-cleanup of old connections

### Scalability
- Redis channel layer for WebSocket
- Company-scoped rooms reduce broadcast overhead
- Indexed database queries for fast retrieval

## Future Enhancements

### Planned Features
- [ ] File/image sharing
- [ ] Message editing and deletion
- [ ] Group chats
- [ ] Voice messages
- [ ] Video calls
- [ ] Message reactions (emoji)
- [ ] Message search
- [ ] Notification sounds
- [ ] Desktop notifications
- [ ] Message history export

### Technical Improvements
- [ ] Message caching
- [ ] Offline message queue
- [ ] Better error recovery
- [ ] Connection quality indicator
- [ ] Message delivery status
- [ ] End-to-end encryption

## Troubleshooting

### Chat Not Connecting
1. Check internet connection
2. Verify WebSocket URL is correct
3. Check authentication token is valid
4. Ensure Redis is running on server
5. Check server logs for errors

### Messages Not Sending
1. Check connection status indicator
2. Try refreshing user list
3. Check if receiver is in same company
4. Verify REST API fallback works

### Users Not Showing
1. Ensure you're logged in
2. Check company has other employees
3. Refresh the chat page
4. Check API endpoint response

### Status Not Updating
1. Check WebSocket connection
2. Verify other user is logged in
3. Check server-side consumer logs
4. Test with REST API endpoint

## Testing

### Manual Testing
1. Login with two different accounts
2. Open chat on both
3. Send messages back and forth
4. Test typing indicators
5. Test online/offline status
6. Test unread counts
7. Test search functionality

### Server Testing
```bash
# Test WebSocket connection
wscat -c wss://att.igenhr.com/ws/chat/ -H "Authorization: Bearer <token>"

# Test REST API
curl -H "Authorization: Bearer <token>" https://att.igenhr.com/api/chat/users/
```

## Dependencies

### Desktop App
- `websocket-client`: WebSocket client library
- `PyQt5`: UI framework
- `requests`: HTTP client

### Server
- `channels`: Django WebSocket support
- `channels-redis`: Redis channel layer
- `daphne`: ASGI server
- `redis`: In-memory data store

## Configuration

### Desktop App
```python
# config.py
API_BASE_URL = "https://att.igenhr.com/api"
WS_URL = "wss://att.igenhr.com/ws/chat/"
```

### Server
```python
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

## Support

For issues or questions:
1. Check this documentation
2. Review server logs
3. Check browser/desktop console
4. Contact development team

---

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Status**: ✅ Production Ready
