# screenshot_service.py - Screenshot Capture Service with Browser URL Detection

import os
import datetime
import threading
import time
from mss import mss
from mss.exception import ScreenShotError
from PIL import Image
from config import SCREENSHOTS_DIR, SCREENSHOT_INTERVAL, IMAGE_QUALITY, IMAGE_FORMAT
from debug_logger import log_screenshot

# Import lightweight browser monitor (no heavy dependencies!)
try:
    from browser_monitor import get_browser_monitor
    from window_monitor import get_window_monitor
    BROWSER_MONITOR_AVAILABLE = True
    log_screenshot("✅ Browser Monitor initialized - URL tracking enabled")
except ImportError:
    BROWSER_MONITOR_AVAILABLE = False
    log_screenshot("⚠️  Browser Monitor not available", 'warning')


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
            log_screenshot("Screenshot service already running", 'warning')
            return
        
        log_screenshot("🚀 Starting screenshot capture service...")
        log_screenshot(f"Interval: {SCREENSHOT_INTERVAL} seconds")
        log_screenshot(f"Save directory: {SCREENSHOTS_DIR}")
        
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        log_screenshot("✅ Screenshot service started successfully")

    def stop(self):
        """Stop the screenshot capture loop"""
        if not self.is_running:
            log_screenshot("Screenshot service not running", 'warning')
            return
            
        log_screenshot("🛑 Stopping screenshot capture service...")
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None
        log_screenshot("✅ Screenshot service stopped")

    def _capture_loop(self):
        """Main capture loop running in background thread"""
        log_screenshot("📸 Capture loop started")
        capture_count = 0
        
        with mss() as sct:
            while self.is_running:
                try:
                    capture_count += 1
                    log_screenshot(f"Capture #{capture_count} starting...")
                    self._capture_screens(sct)
                    log_screenshot(f"Capture #{capture_count} completed")
                except Exception as e:
                    log_screenshot(f"Capture error: {e}", 'error')
                    import traceback
                    log_screenshot(traceback.format_exc(), 'error')
                
                # Sleep in small intervals to allow quick stop
                for _ in range(SCREENSHOT_INTERVAL):
                    if not self.is_running:
                        break
                    time.sleep(1)
        
        log_screenshot("📸 Capture loop ended")

    def _capture_screens(self, sct):
        """Capture all screens with URL detection"""
        today = datetime.date.today().isoformat()
        date_folder = os.path.join(SCREENSHOTS_DIR, today)
        os.makedirs(date_folder, exist_ok=True)
        log_screenshot(f"Date folder: {date_folder}")

        monitors = sct.monitors[1:]  # Skip the "all monitors" entry
        log_screenshot(f"Found {len(monitors)} monitor(s)")
        
        current_hashes = [hash(frozenset(mon.items())) for mon in monitors]

        # Detect new screens
        for idx, mon_hash in enumerate(current_hashes, 1):
            if mon_hash not in self.screen_map:
                folder_name = f"screen{len(self.screen_map) + 1}"
                self.screen_map[mon_hash] = folder_name
                log_screenshot(f"New screen detected: {folder_name}")

        # Remove disconnected screens
        removed_hashes = [h for h in self.screen_map if h not in current_hashes]
        for h in removed_hashes:
            del self.screen_map[h]

        # Capture each screen
        captured_this_round = []
        for mon_idx, (mon, mon_hash) in enumerate(zip(monitors, current_hashes), 1):
            folder_name = self.screen_map[mon_hash]
            screen_folder = os.path.join(date_folder, folder_name)
            os.makedirs(screen_folder, exist_ok=True)

            try:
                log_screenshot(f"Capturing monitor {mon_idx}/{len(monitors)} ({folder_name})...")
                shot = sct.grab(mon)
                img = Image.frombytes("RGB", shot.size, shot.rgb)
                
                # Detect URL from browser history (lightweight, no OCR!)
                url_data = self._detect_url_from_browser()
                if url_data.get('is_browser_active'):
                    log_screenshot(f"URL detected: {url_data.get('detected_url', 'N/A')}")
                else:
                    log_screenshot("No active browser URL detected")
                
                timestamp = datetime.datetime.now().strftime("%H-%M-%S")
                file_path = os.path.join(screen_folder, f"{timestamp}.webp")
                img.save(file_path, IMAGE_FORMAT, quality=IMAGE_QUALITY, method=6)
                log_screenshot(f"✅ Screenshot saved: {file_path}")
                
                # Store with URL metadata
                captured_this_round.append({
                    'file_path': file_path,
                    'url_data': url_data
                })
                self.captured_files.append({
                    'file_path': file_path,
                    'url_data': url_data
                })
                
            except ScreenShotError as e:
                log_screenshot(f"Could not capture {folder_name}: {e}", 'error')

        # Notify callback
        if self.on_capture_callback and captured_this_round:
            self.on_capture_callback(captured_this_round)
    
    def _detect_url_from_browser(self):
        """Detect current URL from browser window title (lightweight!)"""
        if not BROWSER_MONITOR_AVAILABLE:
            return {'is_browser_active': False}
        
        try:
            # Get active window info
            window_monitor = get_window_monitor()
            window_info = window_monitor.get_active_window_info()
            
            if not window_info:
                return {'is_browser_active': False}
            
            # Pass window title and process to browser monitor
            browser_monitor = get_browser_monitor()
            url_data = browser_monitor.get_active_browser_url(
                window_info.get('title', ''),
                window_info.get('process', '')
            )
            
            if url_data:
                return {
                    'detected_url': url_data['url'],
                    'detected_domain': url_data['domain'],
                    'page_title': url_data['title'],
                    'browser_name': url_data['browser'],
                    'is_browser_active': True,
                    'ocr_confidence': 1.0  # 100% accurate from window title
                }
        except Exception as e:
            log_screenshot(f"Browser URL detection error: {e}", 'error')
        
        return {'is_browser_active': False}

    def get_pending_files(self):
        """Get list of files pending upload"""
        return self.captured_files.copy()

    def mark_uploaded(self, file_path):
        """Mark a file as uploaded"""
        if file_path in self.captured_files:
            self.captured_files.remove(file_path)
