# sync_manager.py - Upload Queue & Sync Manager

import os
import json
import threading
import time
import requests
from config import UPLOAD_QUEUE_FILE, API_SCREENSHOT_UPLOAD_URL, SCREENSHOTS_DIR, API_SYNC_STATUS_URL


class SyncManager:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.upload_queue = []
        self.uploaded_files = set()  # Track already uploaded files
        self.is_syncing = False
        self.sync_thread = None
        self.on_sync_callback = None
        self.on_access_denied = None  # Callback when 403 received
        self.batch_size = 5  # Upload 5 files at a time
        self.batch_delay = 2  # 2 seconds delay between batches
        self.access_denied_flag = False  # Stop syncing if access denied
        self.load_queue()

    def _handle_403(self, response):
        """Handle 403 response - update auth and notify"""
        try:
            data = response.json()
            error_code = data.get('error_code', 'ACCESS_DENIED')
            message = data.get('message', 'Access denied')
            self.auth_manager.handle_access_denied(data)
            self.access_denied_flag = True
            if self.on_access_denied:
                self.on_access_denied(error_code, message)
            return error_code, message
        except:
            self.access_denied_flag = True
            return 'ACCESS_DENIED', 'Access denied'

    def load_queue(self):
        """Load pending uploads from file"""
        if os.path.exists(UPLOAD_QUEUE_FILE):
            try:
                with open(UPLOAD_QUEUE_FILE, 'r') as f:
                    data = json.load(f)
                    # Handle both old (list) and new (dict) format
                    if isinstance(data, list):
                        self.upload_queue = data
                        self.uploaded_files = set()
                    else:
                        self.upload_queue = data.get('pending', [])
                        self.uploaded_files = set(data.get('uploaded', []))
                # Filter out files that no longer exist
                self.upload_queue = [f for f in self.upload_queue if os.path.exists(f)]
                self.save_queue()
            except (json.JSONDecodeError, IOError):
                self.upload_queue = []
                self.uploaded_files = set()

    def save_queue(self):
        """Save pending uploads to file"""
        data = {
            'pending': self.upload_queue,
            'uploaded': list(self.uploaded_files)
        }
        with open(UPLOAD_QUEUE_FILE, 'w') as f:
            json.dump(data, f)

    def scan_local_files(self):
        """Scan local screenshots folder and find files not yet uploaded"""
        if not os.path.exists(SCREENSHOTS_DIR):
            return
        
        for root, dirs, files in os.walk(SCREENSHOTS_DIR):
            for file in files:
                if file.endswith(('.webp', '.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(root, file)
                    if file_path not in self.uploaded_files and file_path not in self.upload_queue:
                        self.upload_queue.append(file_path)
        
        self.save_queue()

    def sync_with_server(self):
        """Sync local state with server to know what's already uploaded"""
        headers = self.auth_manager.get_auth_header()
        if not headers:
            return False
        
        try:
            response = requests.get(API_SYNC_STATUS_URL, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                server_paths = set(data.get('uploaded_paths', []))
                
                # Mark files as uploaded if server has them
                for file_path in list(self.upload_queue):
                    rel_path = os.path.relpath(file_path, SCREENSHOTS_DIR)
                    if rel_path in server_paths:
                        self.uploaded_files.add(file_path)
                        if file_path in self.upload_queue:
                            self.upload_queue.remove(file_path)
                
                self.save_queue()
                return True
        except Exception as e:
            print(f"Sync status error: {e}")
        return False

    def add_to_queue(self, file_paths):
        """Add files to upload queue"""
        for path in file_paths:
            if path not in self.upload_queue and path not in self.uploaded_files and os.path.exists(path):
                self.upload_queue.append(path)
        self.save_queue()

    def start_sync(self):
        """Start background sync process"""
        if self.is_syncing:
            return
        
        self.is_syncing = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()

    def stop_sync(self):
        """Stop background sync process"""
        self.is_syncing = False
        if self.sync_thread:
            self.sync_thread.join(timeout=2)
            self.sync_thread = None

    def _sync_loop(self):
        """Background sync loop"""
        # Initial sync with server
        if self._is_online() and not self.access_denied_flag:
            self.sync_with_server()
            self.scan_local_files()
        
        while self.is_syncing:
            # Stop if access denied
            if self.access_denied_flag:
                time.sleep(10)  # Wait longer if access denied
                continue
            
            if self._is_online() and self.upload_queue:
                self._process_queue_batch()
            time.sleep(5)  # Check every 5 seconds

    def _is_online(self):
        """Check if internet is available"""
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except:
            return False

    def _process_queue_batch(self):
        """Process upload queue in batches to avoid server overload"""
        headers = self.auth_manager.get_auth_header()
        if not headers:
            return

        # Get batch of files to upload
        batch = self.upload_queue[:self.batch_size]
        
        for file_path in batch:
            if not self.is_syncing:
                break
            
            success = self._upload_file(file_path, headers)
            
            if success:
                self.uploaded_files.add(file_path)
                if file_path in self.upload_queue:
                    self.upload_queue.remove(file_path)
                if self.on_sync_callback:
                    self.on_sync_callback(file_path, True)
            else:
                if self.on_sync_callback:
                    self.on_sync_callback(file_path, False)
            
            # Small delay between individual uploads
            time.sleep(0.5)
        
        self.save_queue()
        
        # Delay between batches if more files pending
        if self.upload_queue:
            time.sleep(self.batch_delay)

    def _upload_file(self, file_path, headers):
        """Upload a single file to server"""
        if not os.path.exists(file_path):
            return True  # File doesn't exist, consider it "uploaded"

        try:
            # Extract relative path for server
            rel_path = os.path.relpath(file_path, SCREENSHOTS_DIR)
            
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'image/webp')}
                data = {'relative_path': rel_path}
                
                response = requests.post(
                    API_SCREENSHOT_UPLOAD_URL,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=30
                )
                
                # Handle 401 Unauthorized - token expired or invalid
                if response.status_code == 401:
                    print("401 Unauthorized - token may be expired")
                    self.access_denied_flag = True
                    # Try to get more info from response
                    try:
                        data = response.json()
                        message = data.get('detail', 'Session expired. Please login again.')
                    except:
                        message = 'Session expired. Please login again.'
                    if self.on_access_denied:
                        self.on_access_denied('TOKEN_EXPIRED', message)
                    return False
                
                # Handle subscription/access denied
                if response.status_code == 403:
                    self._handle_403(response)
                    return False
                
                return response.status_code in [200, 201]
        except requests.exceptions.Timeout:
            print(f"Upload timeout for {file_path}")
            return False
        except Exception as e:
            print(f"Upload error for {file_path}: {e}")
            return False

    def reset_access_denied(self):
        """Reset access denied flag - call when user re-authenticates"""
        self.access_denied_flag = False

    def get_queue_count(self):
        """Get number of files pending upload"""
        return len(self.upload_queue)

    def get_uploaded_count(self):
        """Get number of files already uploaded"""
        return len(self.uploaded_files)

    def get_queue_status(self):
        """Get sync status info"""
        return {
            'pending': len(self.upload_queue),
            'uploaded': len(self.uploaded_files),
            'is_syncing': self.is_syncing,
            'is_online': self._is_online()
        }

    def force_rescan(self):
        """Force rescan of local files"""
        self.scan_local_files()
        if self._is_online():
            self.sync_with_server()
