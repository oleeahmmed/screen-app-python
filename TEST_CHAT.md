# Chat Feature - Testing Guide

## ✅ Pre-requisites

### Server Side:
1. **Redis Running:**
   ```bash
   sudo systemctl status redis
   # Should show "active (running)"
   ```

2. **Server Running with Daphne:**
   ```bash
   cd server-api
   daphne -b 0.0.0.0 -p 8000 config.asgi:application
   # Or use: ./deploy_daphne.sh
   ```

### Desktop App:
1. **Dependencies Installed:**
   ```bash
   cd desktop-app
   source venv/bin/activate
   pip install websocket-client
   ```

2. **Two User Accounts:**
   - User 1: username/password (same company)
   - User 2: username/password (same company)

---

## 🧪 Test Scenarios

### Test 1: Navigation Check ✓

**Steps:**
1. Login to desktop app
2. Check bottom navigation bar

**Expected:**
- ✅ 4 buttons visible: 📊 Attendance, ✓ Tasks, 💬 Chat, ⚙️ Settings
- ✅ Chat button is 3rd from left
- ✅ Settings button is 4th (rightmost)

**Result:** [ ] Pass [ ] Fail

---

### Test 2: Menu Options Check ✓

**Steps:**
1. Click the ☰ (menu) button in top-right
2. Check menu items

**Expected:**
- ✅ User profile card at top
- ✅ 👤 Profile button
- ✅ 💬 Chat button
- ✅ 📋 Subscription Info button
- ✅ 🚪 Logout button

**Result:** [ ] Pass [ ] Fail

---

### Test 3: Chat Page UI - Light Theme ✓

**Steps:**
1. Click 💬 Chat button in bottom nav
2. Observe the UI

**Expected:**
- ✅ Light/white background (not dark)
- ✅ White user list panel on left
- ✅ Light gray chat area on right
- ✅ White header with "Hi, [username]"
- ✅ Search box with light gray background
- ✅ Connection status indicator

**Result:** [ ] Pass [ ] Fail

---

### Test 4: Menu Navigation to Chat ✓

**Steps:**
1. Click ☰ menu button
2. Click 💬 Chat option in menu
3. Menu should close and chat page should open

**Expected:**
- ✅ Menu closes
- ✅ Chat page opens
- ✅ Same as clicking bottom nav chat button

**Result:** [ ] Pass [ ] Fail

---

### Test 5: Menu Navigation to Profile ✓

**Steps:**
1. Click ☰ menu button
2. Click 👤 Profile option in menu
3. Menu should close and profile/settings page should open

**Expected:**
- ✅ Menu closes
- ✅ Profile page opens
- ✅ Shows profile information

**Result:** [ ] Pass [ ] Fail

---

### Test 6: Settings Button Navigation ✓

**Steps:**
1. Click ⚙️ Settings button in bottom nav
2. Profile/settings page should open

**Expected:**
- ✅ Profile page opens
- ✅ Shows user profile info
- ✅ Can edit profile
- ✅ Can change password

**Result:** [ ] Pass [ ] Fail

---

### Test 7: WebSocket Connection ✓

**Steps:**
1. Open chat page
2. Check connection status (top of user list)

**Expected:**
- ✅ Shows "🟢 Connected" (green) if WebSocket works
- ✅ Shows "🔴 Disconnected" (red) if WebSocket fails
- ✅ Connection happens automatically

**Result:** [ ] Pass [ ] Fail

---

### Test 8: User List Display ✓

**Steps:**
1. Open chat page
2. Wait for users to load

**Expected:**
- ✅ List of company employees shown
- ✅ Each user has avatar (👤)
- ✅ User name displayed
- ✅ Online status shown (🟢 Online / ⚫ Offline)
- ✅ Light gray background for user items
- ✅ White background on hover

**Result:** [ ] Pass [ ] Fail

---

### Test 9: User Search ✓

**Steps:**
1. Open chat page
2. Type in search box
3. User list should filter

**Expected:**
- ✅ Search box works
- ✅ Users filtered by name
- ✅ Shows "No users found" if no match

**Result:** [ ] Pass [ ] Fail

---

### Test 10: Select User to Chat ✓

**Steps:**
1. Click on a user in the list
2. Chat area should update

**Expected:**
- ✅ User name shown in chat header
- ✅ Online status shown
- ✅ Message input enabled
- ✅ Send button enabled
- ✅ Previous messages loaded (if any)

**Result:** [ ] Pass [ ] Fail

---

### Test 11: Send Message ✓

**Steps:**
1. Select a user
2. Type a message
3. Press Enter or click Send

**Expected:**
- ✅ Message appears in chat area
- ✅ Message bubble is blue (sent)
- ✅ Message has white text
- ✅ Timestamp shown
- ✅ Input box clears after sending

**Result:** [ ] Pass [ ] Fail

---

### Test 12: Receive Message (Two Instances) ✓

**Steps:**
1. Open app with User 1
2. Open another instance with User 2 (same company)
3. User 1 sends message to User 2
4. Check User 2's app

**Expected:**
- ✅ Message appears instantly in User 2's chat
- ✅ Message bubble is white (received)
- ✅ Message has dark text
- ✅ Sender name shown in blue
- ✅ Timestamp shown

**Result:** [ ] Pass [ ] Fail

---

### Test 13: Online Status Update ✓

**Steps:**
1. User 1 logged in
2. User 2 logs in
3. Check User 1's user list

**Expected:**
- ✅ User 2 status changes to 🟢 Online
- ✅ Update happens automatically
- ✅ No page refresh needed

**Result:** [ ] Pass [ ] Fail

---

### Test 14: Typing Indicator ✓

**Steps:**
1. Two users in conversation
2. User 1 starts typing
3. Check User 2's chat

**Expected:**
- ✅ "User 1 is typing..." appears
- ✅ Disappears after 2 seconds of no typing
- ✅ Shows below message area

**Result:** [ ] Pass [ ] Fail

---

### Test 15: Unread Badge ✓

**Steps:**
1. User 2 sends message to User 1
2. User 1 hasn't opened that conversation
3. Check User 1's user list

**Expected:**
- ✅ Red badge with number appears on User 2's item
- ✅ Badge shows unread count
- ✅ Badge disappears when conversation opened

**Result:** [ ] Pass [ ] Fail

---

### Test 16: Message Bubbles Styling ✓

**Steps:**
1. Send and receive several messages
2. Check message appearance

**Expected Sent Messages:**
- ✅ Blue background (#2196F3)
- ✅ White text
- ✅ Aligned to right
- ✅ Rounded corners
- ✅ Timestamp in light color

**Expected Received Messages:**
- ✅ White background
- ✅ Dark text (#1a1a1a)
- ✅ Aligned to left
- ✅ Sender name in blue
- ✅ Border around bubble
- ✅ Timestamp in gray

**Result:** [ ] Pass [ ] Fail

---

### Test 17: Scroll Behavior ✓

**Steps:**
1. Send many messages (10+)
2. Check scrolling

**Expected:**
- ✅ Auto-scrolls to bottom on new message
- ✅ Can scroll up to see old messages
- ✅ Smooth scrolling
- ✅ Scrollbar visible when needed

**Result:** [ ] Pass [ ] Fail

---

### Test 18: Connection Recovery ✓

**Steps:**
1. Chat connected
2. Stop Redis or server
3. Wait a moment
4. Restart Redis/server

**Expected:**
- ✅ Status changes to 🔴 Disconnected
- ✅ Automatically tries to reconnect
- ✅ Status changes back to 🟢 Connected
- ✅ Messages work again

**Result:** [ ] Pass [ ] Fail

---

### Test 19: REST API Fallback ✓

**Steps:**
1. Stop Daphne (WebSocket server)
2. Start Gunicorn (REST only)
3. Try to send message

**Expected:**
- ✅ Shows disconnected status
- ✅ Message still sends via REST API
- ✅ Message appears in chat
- ✅ No real-time updates (need refresh)

**Result:** [ ] Pass [ ] Fail

---

### Test 20: Logout Cleanup ✓

**Steps:**
1. Chat connected
2. Click menu → Logout
3. Login again

**Expected:**
- ✅ WebSocket disconnects on logout
- ✅ No errors in console
- ✅ Reconnects on login
- ✅ Chat works normally after re-login

**Result:** [ ] Pass [ ] Fail

---

## 🎨 Visual Checks

### Color Verification:
- [ ] Background is light/white (not dark)
- [ ] Text is dark and readable
- [ ] Blue accent color (#2196F3) used consistently
- [ ] Borders are light gray (#e0e0e0)
- [ ] Hover effects work (lighter background)
- [ ] No dark theme remnants

### Layout Verification:
- [ ] User list on left (280px width)
- [ ] Chat area on right (flexible width)
- [ ] Header at top (white background)
- [ ] Input at bottom (white background)
- [ ] Proper spacing and padding
- [ ] No overlapping elements

### Responsive Behavior:
- [ ] Works at 420x620 (app size)
- [ ] No horizontal scrolling
- [ ] All elements visible
- [ ] Text doesn't overflow
- [ ] Buttons are clickable

---

## 🐛 Common Issues & Solutions

### Issue 1: Chat button not showing
**Solution:** Check `ui_components.py` - should have 4 nav items

### Issue 2: Menu options missing
**Solution:** Check `main.py` MenuOverlay class - should have profile_clicked and chat_clicked signals

### Issue 3: Dark theme still showing
**Solution:** Check `chat_page.py` - all colors should be light (#f5f7fa, white, etc.)

### Issue 4: WebSocket not connecting
**Solution:** 
- Check Redis: `redis-cli ping`
- Check Daphne is running (not Gunicorn)
- Check WebSocket URL in chat_manager.py

### Issue 5: Users not loading
**Solution:**
- Check authentication token
- Check API endpoint: `/api/chat/users/`
- Ensure users are in same company

### Issue 6: Messages not sending
**Solution:**
- Check WebSocket connection status
- Check REST API fallback
- Check server logs for errors

---

## 📊 Test Results Summary

**Total Tests:** 20

**Passed:** _____ / 20

**Failed:** _____ / 20

**Pass Rate:** _____ %

---

## ✅ Sign-off

**Tested By:** _________________

**Date:** _________________

**Environment:**
- Server: [ ] Local [ ] Production
- Redis: [ ] Running [ ] Not Running
- Desktop App Version: _________________

**Overall Status:** [ ] ✅ All Pass [ ] ⚠️ Some Issues [ ] ❌ Major Issues

**Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

## 🚀 Ready for Production?

**Checklist:**
- [ ] All 20 tests passed
- [ ] No console errors
- [ ] WebSocket stable
- [ ] UI looks good
- [ ] Performance acceptable
- [ ] No memory leaks
- [ ] Works with multiple users
- [ ] Handles disconnections gracefully

**Approval:** [ ] Yes [ ] No

**Approved By:** _________________

**Date:** _________________
