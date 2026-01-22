# chat_api.py - Chat REST API Helper

import requests
from config import API_BASE_URL


class ChatAPI:
    """REST API helper for chat"""
    
    def __init__(self, auth):
        self.auth = auth
    
    def get_company_users(self):
        """Get list of users in company"""
        headers = self.auth.get_auth_header()
        print(f"🔑 Auth headers: {headers is not None}")
        
        if not headers:
            print("❌ No auth headers - user not logged in")
            return False, []
        
        try:
            url = f"{API_BASE_URL}/chat/users/"
            print(f"📡 Calling API: {url}")
            
            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )
            
            print(f"📊 API Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Got {len(data)} users")
                return True, data
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return False, []
        except Exception as e:
            print(f"❌ Get users error: {e}")
            return False, []
    
    def get_conversation(self, user_id):
        """Get conversation with a user"""
        headers = self.auth.get_auth_header()
        if not headers:
            return False, []
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/chat/conversation/{user_id}/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            return False, []
        except Exception as e:
            print(f"Get conversation error: {e}")
            return False, []
    
    def send_message(self, receiver_id, message):
        """Send message via REST API (fallback)"""
        headers = self.auth.get_auth_header()
        if not headers:
            return False, "Not authenticated"
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat/send/",
                headers=headers,
                json={
                    'receiver_id': receiver_id,
                    'message': message
                },
                timeout=10
            )
            
            if response.status_code == 201:
                return True, response.json()
            return False, "Failed to send"
        except Exception as e:
            print(f"Send message error: {e}")
            return False, str(e)
    
    def get_unread_count(self):
        """Get unread messages count"""
        headers = self.auth.get_auth_header()
        if not headers:
            return 0
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/chat/unread/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('total_unread', 0)
            return 0
        except Exception as e:
            print(f"Get unread error: {e}")
            return 0
