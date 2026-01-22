"""
Window Monitor - Get active window title and process name
Simple cross-platform solution
"""

from debug_logger import log_browser

# Platform-specific imports
try:
    import platform
    system = platform.system()
    
    if system == 'Windows':
        import win32gui
        import win32process
        import psutil
        PLATFORM = 'windows'
    elif system == 'Linux':
        # Linux: Use xdotool or wmctrl
        import subprocess
        PLATFORM = 'linux'
    elif system == 'Darwin':
        # macOS: Use AppKit
        from AppKit import NSWorkspace
        PLATFORM = 'macos'
    else:
        PLATFORM = 'unknown'
    
    log_browser(f"✅ Window Monitor initialized for {PLATFORM}")
except Exception as e:
    PLATFORM = 'unknown'
    log_browser(f"⚠️ Window Monitor initialization error: {e}", 'warning')


class WindowMonitor:
    """Monitor active window to get title and process name"""
    
    def __init__(self):
        pass
    
    def get_active_window_info(self):
        """Get active window title and process name"""
        if PLATFORM == 'windows':
            return self._get_windows_active_window()
        elif PLATFORM == 'linux':
            return self._get_linux_active_window()
        elif PLATFORM == 'macos':
            return self._get_macos_active_window()
        return None
    
    def _get_windows_active_window(self):
        """Get active window on Windows"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            
            # Get process name
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid).name()
            
            return {'title': title, 'process': process}
        except Exception as e:
            log_browser(f"Windows window detection error: {e}", 'error')
            return None
    
    def _get_linux_active_window(self):
        """Get active window on Linux"""
        try:
            # Try xdotool first
            result = subprocess.run(
                ['xdotool', 'getactivewindow', 'getwindowname'],
                capture_output=True,
                text=True,
                timeout=1
            )
            
            if result.returncode == 0:
                title = result.stdout.strip()
                
                # Get process name
                pid_result = subprocess.run(
                    ['xdotool', 'getactivewindow', 'getwindowpid'],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                
                if pid_result.returncode == 0:
                    pid = int(pid_result.stdout.strip())
                    try:
                        import psutil
                        process = psutil.Process(pid).name()
                    except:
                        process = 'unknown'
                else:
                    process = 'unknown'
                
                return {'title': title, 'process': process}
        except FileNotFoundError:
            log_browser("xdotool not installed, trying wmctrl...", 'warning')
            
            # Try wmctrl as fallback
            try:
                result = subprocess.run(
                    ['wmctrl', '-l', '-p'],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    # Get first window (usually active)
                    if lines:
                        parts = lines[0].split(None, 4)
                        if len(parts) >= 5:
                            title = parts[4]
                            return {'title': title, 'process': 'unknown'}
            except:
                pass
        except Exception as e:
            log_browser(f"Linux window detection error: {e}", 'error')
        
        return None
    
    def _get_macos_active_window(self):
        """Get active window on macOS"""
        try:
            active_app = NSWorkspace.sharedWorkspace().activeApplication()
            app_name = active_app['NSApplicationName']
            
            # macOS doesn't easily give window title, use app name
            return {'title': app_name, 'process': app_name}
        except Exception as e:
            log_browser(f"macOS window detection error: {e}", 'error')
            return None


# Singleton instance
_window_monitor = None

def get_window_monitor():
    """Get or create window monitor instance"""
    global _window_monitor
    if _window_monitor is None:
        _window_monitor = WindowMonitor()
    return _window_monitor
