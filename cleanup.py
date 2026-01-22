# cleanup.py - Auto Cleanup Old Screenshots

import os
import shutil
import threading
import time
from datetime import datetime, timedelta
from config import SCREENSHOTS_DIR, CLEANUP_DAYS


class CleanupManager:
    def __init__(self):
        self.is_running = False
        self.thread = None

    def start(self):
        """Start weekly cleanup scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop cleanup scheduler"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None

    def _cleanup_loop(self):
        """Background cleanup loop - runs daily check"""
        while self.is_running:
            self.cleanup_old_files()
            # Sleep for 24 hours (check daily)
            for _ in range(86400):  # 24 * 60 * 60 seconds
                if not self.is_running:
                    break
                time.sleep(1)

    def cleanup_old_files(self):
        """Delete screenshot folders older than CLEANUP_DAYS"""
        if not os.path.exists(SCREENSHOTS_DIR):
            return

        cutoff_date = datetime.now() - timedelta(days=CLEANUP_DAYS)
        deleted_count = 0

        for folder_name in os.listdir(SCREENSHOTS_DIR):
            folder_path = os.path.join(SCREENSHOTS_DIR, folder_name)
            
            if not os.path.isdir(folder_path):
                continue

            try:
                # Parse folder name as date (YYYY-MM-DD format)
                folder_date = datetime.strptime(folder_name, "%Y-%m-%d")
                
                if folder_date < cutoff_date:
                    shutil.rmtree(folder_path)
                    deleted_count += 1
                    print(f"Deleted old folder: {folder_name}")
            except ValueError:
                # Folder name is not a valid date, skip it
                continue

        return deleted_count

    def get_storage_info(self):
        """Get storage usage information"""
        total_size = 0
        folder_count = 0
        file_count = 0

        if os.path.exists(SCREENSHOTS_DIR):
            for root, dirs, files in os.walk(SCREENSHOTS_DIR):
                folder_count += len(dirs)
                for f in files:
                    file_count += 1
                    total_size += os.path.getsize(os.path.join(root, f))

        return {
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'folder_count': folder_count,
            'file_count': file_count
        }
