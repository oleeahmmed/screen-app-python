# screenshot_service.py - Screenshot Capture Service

import os
import datetime
import threading
import time
from mss import mss
from mss.exception import ScreenShotError
from PIL import Image
from config import SCREENSHOTS_DIR, SCREENSHOT_INTERVAL, IMAGE_QUALITY, IMAGE_FORMAT


class ScreenshotService:
    def __init__(self, on_capture_callback=None):
        self.is_running = False
        self.thread = None
        self.screen_map = {}
        self.on_capture_callback = on_capture_callback
        self.captured_files = []  # Track captured files for upload queue

    def start(self):
        """Start the screenshot capture loop"""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the screenshot capture loop"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None

    def _capture_loop(self):
        """Main capture loop running in background thread"""
        with mss() as sct:
            while self.is_running:
                try:
                    self._capture_screens(sct)
                except Exception as e:
                    print(f"Capture error: {e}")
                
                # Sleep in small intervals to allow quick stop
                for _ in range(SCREENSHOT_INTERVAL):
                    if not self.is_running:
                        break
                    time.sleep(1)

    def _capture_screens(self, sct):
        """Capture all screens"""
        today = datetime.date.today().isoformat()
        date_folder = os.path.join(SCREENSHOTS_DIR, today)
        os.makedirs(date_folder, exist_ok=True)

        monitors = sct.monitors[1:]  # Skip the "all monitors" entry
        current_hashes = [hash(frozenset(mon.items())) for mon in monitors]

        # Detect new screens
        for idx, mon_hash in enumerate(current_hashes, 1):
            if mon_hash not in self.screen_map:
                folder_name = f"screen{len(self.screen_map) + 1}"
                self.screen_map[mon_hash] = folder_name

        # Remove disconnected screens
        removed_hashes = [h for h in self.screen_map if h not in current_hashes]
        for h in removed_hashes:
            del self.screen_map[h]

        # Capture each screen
        captured_this_round = []
        for mon, mon_hash in zip(monitors, current_hashes):
            folder_name = self.screen_map[mon_hash]
            screen_folder = os.path.join(date_folder, folder_name)
            os.makedirs(screen_folder, exist_ok=True)

            try:
                shot = sct.grab(mon)
                img = Image.frombytes("RGB", shot.size, shot.rgb)
                timestamp = datetime.datetime.now().strftime("%H-%M-%S")
                file_path = os.path.join(screen_folder, f"{timestamp}.webp")
                img.save(file_path, IMAGE_FORMAT, quality=IMAGE_QUALITY, method=6)
                
                captured_this_round.append(file_path)
                self.captured_files.append(file_path)
                
            except ScreenShotError as e:
                print(f"Could not capture {folder_name}: {e}")

        # Notify callback
        if self.on_capture_callback and captured_this_round:
            self.on_capture_callback(captured_this_round)

    def get_pending_files(self):
        """Get list of files pending upload"""
        return self.captured_files.copy()

    def mark_uploaded(self, file_path):
        """Mark a file as uploaded"""
        if file_path in self.captured_files:
            self.captured_files.remove(file_path)
