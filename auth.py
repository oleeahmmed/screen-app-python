# auth.py - JWT Authentication Manager

import json
import os
import requests
from datetime import datetime, timedelta
import jwt
from config import AUTH_TOKEN_FILE, API_TOKEN_URL, API_TOKEN_REFRESH_URL, API_ACCESS_CHECK_URL


class AuthManager:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        # Subscription & Access Info
        self.access_granted = False
        self.error_code = None
        self.user_info = None
        self.employee_info = None
        self.company_info = None
        self.subscription_info = None
        self.access_message = None
        self.access_message_en = None
        self.load_tokens()

    def load_tokens(self):
        """Load tokens from local storage"""
        if os.path.exists(AUTH_TOKEN_FILE):
            try:
                with open(AUTH_TOKEN_FILE, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get('access')
                    self.refresh_token = data.get('refresh')
                    # Load cached access info
                    self.access_granted = data.get('access_granted', False)
                    self.error_code = data.get('error_code')
                    self.user_info = data.get('user')
                    self.employee_info = data.get('employee')
                    self.company_info = data.get('company')
                    self.subscription_info = data.get('subscription')
            except (json.JSONDecodeError, IOError):
                self.access_token = None
                self.refresh_token = None

    def save_tokens(self, extra_data=None):
        """Save tokens to local storage"""
        data = {
            'access': self.access_token,
            'refresh': self.refresh_token,
            'access_granted': self.access_granted,
            'error_code': self.error_code,
            'user': self.user_info,
            'employee': self.employee_info,
            'company': self.company_info,
            'subscription': self.subscription_info
        }
        if extra_data:
            data.update(extra_data)
        with open(AUTH_TOKEN_FILE, 'w') as f:
            json.dump(data, f)

    def login(self, username, password):
        """Login and get JWT tokens with access check"""
        try:
            response = requests.post(API_TOKEN_URL, json={
                'username': username,
                'password': password
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
                
                # Store access info from login response
                self.access_granted = data.get('access_granted', False)
                self.error_code = data.get('error_code')
                self.user_info = data.get('user')
                self.employee_info = data.get('employee')
                self.company_info = data.get('company')
                self.subscription_info = data.get('subscription')
                self.access_message = data.get('message')
                self.access_message_en = data.get('message_en')
                
                self.save_tokens()
                
                # Save profile info to config
                self.save_profile_info(self.user_info)
                
                # Return access status
                if self.access_granted:
                    return True, "Login successful", data
                else:
                    # Login successful but access denied
                    return True, self.access_message or "Access denied", data
            else:
                return False, "Invalid credentials", None
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server", None
        except requests.exceptions.Timeout:
            return False, "Connection timeout", None
        except Exception as e:
            return False, str(e), None

    def check_access(self):
        """Check subscription and access status"""
        headers = self.get_auth_header()
        if not headers:
            return False, "Not authenticated", None
        
        try:
            response = requests.get(API_ACCESS_CHECK_URL, headers=headers, timeout=10)
            data = response.json()
            
            # Update stored info
            self.access_granted = data.get('access_granted', False)
            self.error_code = data.get('error_code')
            self.user_info = data.get('user')
            self.employee_info = data.get('employee')
            self.company_info = data.get('company')
            self.subscription_info = data.get('subscription')
            self.access_message = data.get('message')
            self.access_message_en = data.get('message_en')
            
            self.save_tokens()
            
            return self.access_granted, data.get('message', ''), data
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server", None
        except Exception as e:
            return False, str(e), None

    def can_access(self):
        """Quick check if user has access"""
        return self.access_granted and self.subscription_info is not None

    def get_subscription_days_remaining(self):
        """Get days remaining in subscription"""
        if self.subscription_info:
            return self.subscription_info.get('days_remaining', 0)
        return 0

    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            return False
        
        try:
            response = requests.post(API_TOKEN_REFRESH_URL, json={
                'refresh': self.refresh_token
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access')
                self.save_tokens()
                return True
            elif response.status_code == 401:
                # Refresh token also expired or invalid
                print("Refresh token expired or invalid")
                self.access_granted = False
                self.error_code = 'TOKEN_EXPIRED'
                self.access_message = 'Session expired. Please login again.'
                self.save_tokens()
            return False
        except Exception as e:
            print(f"Token refresh error: {e}")
            return False

    def is_token_expired(self):
        """Check if access token is expired"""
        if not self.access_token:
            return True
        
        try:
            # Decode without verification to check expiry
            decoded = jwt.decode(self.access_token, options={"verify_signature": False})
            exp = datetime.fromtimestamp(decoded['exp'])
            return datetime.now() >= exp
        except:
            return True

    def get_valid_token(self):
        """Get a valid access token, refreshing if necessary"""
        if self.is_token_expired():
            if not self.refresh_access_token():
                return None
        return self.access_token

    def get_auth_header(self):
        """Get authorization header for API requests"""
        token = self.get_valid_token()
        if token:
            return {'Authorization': f'Bearer {token}'}
        return None

    def logout(self):
        """Clear all tokens and access info"""
        self.access_token = None
        self.refresh_token = None
        self.access_granted = False
        self.error_code = None
        self.user_info = None
        self.employee_info = None
        self.company_info = None
        self.subscription_info = None
        if os.path.exists(AUTH_TOKEN_FILE):
            os.remove(AUTH_TOKEN_FILE)

    def is_logged_in(self):
        """Check if user is logged in with valid tokens"""
        return self.get_valid_token() is not None

    def get_username(self):
        """Get current username"""
        if self.user_info:
            return self.user_info.get('full_name') or self.user_info.get('username', 'User')
        return 'User'

    def get_company_name(self):
        """Get company name"""
        if self.company_info:
            return self.company_info.get('name', '')
        return ''

    def get_plan_name(self):
        """Get subscription plan name"""
        if self.subscription_info:
            return self.subscription_info.get('plan', '')
        return ''

    def handle_access_denied(self, response_data):
        """Handle 403 access denied response - update local state"""
        self.access_granted = False
        self.error_code = response_data.get('error_code', 'ACCESS_DENIED')
        self.access_message = response_data.get('message', 'Access denied')
        
        # Update subscription info based on error
        if self.error_code == 'SUBSCRIPTION_EXPIRED':
            if self.subscription_info:
                self.subscription_info['status'] = 'expired'
                self.subscription_info['days_remaining'] = 0
            else:
                self.subscription_info = {'status': 'expired', 'days_remaining': 0, 'plan': 'Expired'}
        elif self.error_code == 'SUBSCRIPTION_NONE':
            self.subscription_info = {'status': 'none', 'days_remaining': 0, 'plan': 'No Subscription'}
        elif self.error_code == 'USER_INACTIVE':
            if self.subscription_info:
                self.subscription_info['status'] = 'user_inactive'
        elif self.error_code == 'COMPANY_INACTIVE':
            if self.subscription_info:
                self.subscription_info['status'] = 'company_inactive'
        
        self.save_tokens()
        return self.error_code, self.access_message

    def update_access_from_error(self, error_code, message):
        """Update access state from error"""
        self.access_granted = False
        self.error_code = error_code
        self.access_message = message
        self.save_tokens()

    def get_user_profile(self):
        """Get user profile data"""
        headers = self.get_auth_header()
        if not headers:
            print("No auth header available")
            return False, None
        
        try:
            from config import API_BASE_URL
            # API_BASE_URL already includes /api, so just add /user/profile/
            url = f"{API_BASE_URL}/user/profile/"
            print(f"Fetching profile from: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Profile response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Profile data received: {data.keys() if data else 'None'}")
                    return True, data
                except ValueError as e:
                    print(f"JSON parse error: {e}")
                    print(f"Response text: {response.text[:200]}")
                    return False, None
            else:
                print(f"Profile fetch failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False, None
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
            return False, None
        except Exception as e:
            print(f"Get profile error: {e}")
            import traceback
            traceback.print_exc()
            return False, None

    def update_user_profile(self, email, first_name, last_name):
        """Update user profile"""
        headers = self.get_auth_header()
        if not headers:
            return False, "Not authenticated"
        
        try:
            from config import API_BASE_URL
            response = requests.put(
                f"{API_BASE_URL}/user/profile/",
                headers=headers,
                json={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name
                },
                timeout=10
            )
            
            if response.status_code == 200:
                # Update cached user info
                if self.user_info:
                    self.user_info['email'] = email
                    self.user_info['first_name'] = first_name
                    self.user_info['last_name'] = last_name
                    self.save_tokens()
                return True, "Profile updated successfully"
            else:
                data = response.json()
                return False, data.get('error', 'Failed to update profile')
        except Exception as e:
            print(f"Update profile error: {e}")
            return False, str(e)

    def change_password(self, current_password, new_password):
        """Change user password"""
        headers = self.get_auth_header()
        if not headers:
            return False, "Not authenticated"
        
        try:
            from config import API_BASE_URL
            response = requests.post(
                f"{API_BASE_URL}/user/change-password/",
                headers=headers,
                json={
                    'current_password': current_password,
                    'new_password': new_password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "Password changed successfully"
            else:
                data = response.json()
                return False, data.get('error', 'Failed to change password')
        except Exception as e:
            print(f"Change password error: {e}")
            return False, str(e)

    def upload_profile_photo(self, file_path):
        """Upload profile photo"""
        headers = self.get_auth_header()
        if not headers:
            print("No auth header for photo upload")
            return False, "Not authenticated"
        
        try:
            from config import API_BASE_URL
            url = f"{API_BASE_URL}/user/upload-photo/"
            print(f"Uploading photo to: {url}")
            print(f"File path: {file_path}")
            
            with open(file_path, 'rb') as f:
                files = {'profile_photo': f}
                print(f"Sending file...")
                response = requests.post(
                    url,
                    headers=headers,
                    files=files,
                    timeout=30
                )
            
            print(f"Upload response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Upload success: {data}")
                    # Update cached user info
                    if self.user_info:
                        self.user_info['profile_photo'] = data.get('profile_photo')
                        self.save_tokens()
                    return True, "Photo uploaded successfully"
                except ValueError as e:
                    print(f"JSON parse error: {e}")
                    print(f"Response text: {response.text[:200]}")
                    return False, "Invalid response from server"
            else:
                print(f"Upload failed: {response.text[:200]}")
                try:
                    data = response.json()
                    return False, data.get('error', 'Failed to upload photo')
                except:
                    return False, f"Upload failed with status {response.status_code}"
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return False, "File not found"
        except Exception as e:
            print(f"Upload photo error: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)

    def save_profile_info(self, user_info):
        """Save profile info to config file"""
        from config import PROFILE_INFO_FILE
        
        try:
            if user_info:
                data = {
                    'id': user_info.get('id'),
                    'username': user_info.get('username'),
                    'email': user_info.get('email'),
                    'first_name': user_info.get('first_name', ''),
                    'last_name': user_info.get('last_name', ''),
                    'full_name': user_info.get('full_name', '')
                }
                with open(PROFILE_INFO_FILE, 'w') as f:
                    json.dump(data, f)
                print("Profile info saved")
        except Exception as e:
            print(f"Error saving profile info: {e}")
    
    def load_profile_info(self):
        """Load profile info from config file"""
        from config import PROFILE_INFO_FILE
        
        try:
            if os.path.exists(PROFILE_INFO_FILE):
                with open(PROFILE_INFO_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading profile info: {e}")
        return None
