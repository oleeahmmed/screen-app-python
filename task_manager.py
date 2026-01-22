# task_manager.py - Attendance & Task Manager

import requests
from config import API_CHECKIN_URL, API_CHECKOUT_URL, API_TASKS_URL


class TaskManager:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.current_attendance = None
        self.on_access_denied = None  # Callback when 403/401 received

    def _handle_403(self, response):
        """Handle 403 response - update auth and notify"""
        try:
            data = response.json()
            print(f"403 Response data: {data}")  # Debug
            error_code = data.get('error_code', 'ACCESS_DENIED')
            message = data.get('message', 'Access denied')
            self.auth_manager.handle_access_denied(data)
            if self.on_access_denied:
                self.on_access_denied(error_code, message)
            return error_code, message
        except Exception as e:
            print(f"Error parsing 403 response: {e}")
            return 'ACCESS_DENIED', 'Access denied'

    def _handle_401(self):
        """Handle 401 Unauthorized - token expired"""
        error_code = 'TOKEN_EXPIRED'
        message = 'Session expired. Please login again.'
        self.auth_manager.update_access_from_error(error_code, message)
        if self.on_access_denied:
            self.on_access_denied(error_code, message)
        return error_code, message

    def check_in(self):
        """Check in when user logs in"""
        headers = self.auth_manager.get_auth_header()
        if not headers:
            return False, "Not authenticated"
        
        try:
            response = requests.post(API_CHECKIN_URL, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                data = response.json()
                self.current_attendance = data.get('attendance')
                return True, data.get('message', 'Checked in')
            elif response.status_code == 401:
                error_code, message = self._handle_401()
                return False, message
            elif response.status_code == 403:
                error_code, message = self._handle_403(response)
                return False, message
            return False, "Check-in failed"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except Exception as e:
            return False, str(e)

    def check_out(self):
        """Check out when user logs out"""
        headers = self.auth_manager.get_auth_header()
        if not headers:
            return False, "Not authenticated"
        
        try:
            response = requests.post(API_CHECKOUT_URL, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.current_attendance = None
                return True, data.get('message', 'Checked out')
            elif response.status_code == 401:
                error_code, message = self._handle_401()
                return False, message
            elif response.status_code == 403:
                error_code, message = self._handle_403(response)
                return False, message
            return False, "Check-out failed"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except Exception as e:
            return False, str(e)

    def add_task(self, name, description="", task_date=None):
        """Add a new task with optional date"""
        headers = self.auth_manager.get_auth_header()
        if not headers:
            return False, "Not authenticated", None
        
        try:
            data = {'name': name, 'description': description}
            if task_date:
                data['date'] = task_date
            
            response = requests.post(
                API_TASKS_URL,
                headers=headers,
                json=data,
                timeout=10
            )
            if response.status_code == 201:
                return True, "Task added", response.json()
            elif response.status_code == 403:
                error_code, message = self._handle_403(response)
                return False, message, None
            return False, "Failed to add task", None
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server", None
        except Exception as e:
            return False, str(e), None

    def get_tasks(self):
        """Get list of tasks"""
        headers = self.auth_manager.get_auth_header()
        if not headers:
            return []
        
        try:
            response = requests.get(API_TASKS_URL, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                self._handle_403(response)
            return []
        except:
            return []

    def complete_task(self, task_id):
        """Mark task as completed"""
        headers = self.auth_manager.get_auth_header()
        if not headers:
            return False
        
        try:
            response = requests.patch(
                f"{API_TASKS_URL}{task_id}/",
                headers=headers,
                json={'completed': True},
                timeout=10
            )
            if response.status_code == 403:
                self._handle_403(response)
            return response.status_code == 200
        except:
            return False

    def toggle_task(self, task_id):
        """Toggle task completed status"""
        headers = self.auth_manager.get_auth_header()
        if not headers:
            return False, None
        
        try:
            response = requests.post(
                f"{API_TASKS_URL}{task_id}/toggle/",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            elif response.status_code == 403:
                self._handle_403(response)
            return False, None
        except:
            return False, None

    def delete_task(self, task_id):
        """Delete a task"""
        headers = self.auth_manager.get_auth_header()
        if not headers:
            return False
        
        try:
            response = requests.delete(
                f"{API_TASKS_URL}{task_id}/",
                headers=headers,
                timeout=10
            )
            if response.status_code == 403:
                self._handle_403(response)
            return response.status_code == 204
        except:
            return False
