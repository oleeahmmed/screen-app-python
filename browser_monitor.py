"""
Browser Window Title Monitor - Simple approach
Just gets the window title from browser windows
"""

import re

try:
    from debug_logger import log_browser
except ImportError:
    def log_browser(msg, level='info'):
        print(f"[BROWSER] {msg}")


class BrowserMonitor:
    """Monitor browser window titles to extract website names"""
    
    def __init__(self):
        self.browser_processes = [
            'chrome', 'firefox', 'msedge', 'brave', 'opera', 
            'chromium', 'vivaldi', 'safari'
        ]
    
    def get_active_browser_url(self, window_title, process_name):
        """Extract website info from browser window title"""
        if not window_title or not process_name:
            return None
        
        # Check if it's a browser
        process_lower = process_name.lower()
        is_browser = any(browser in process_lower for browser in self.browser_processes)
        
        if not is_browser:
            return None
        
        log_browser(f"Browser detected: {process_name} - {window_title}")
        
        # Extract website name from title
        website_name = self._extract_website_from_title(window_title)
        
        if website_name:
            log_browser(f"✅ Website extracted: {website_name}")
            return {
                'url': website_name,
                'title': window_title,
                'browser': self._get_browser_name(process_name),
                'domain': website_name
            }
        
        return None
    
    def _extract_website_from_title(self, title):
        """Extract website name from window title"""
        if not title:
            return None
        
        # Common patterns in browser titles:
        # "Page Title - Google Chrome"
        # "Page Title - Mozilla Firefox"
        # "YouTube" 
        # "Facebook - Mozilla Firefox"
        
        # Remove browser name from end
        title = re.sub(r'\s*-\s*(Google Chrome|Mozilla Firefox|Microsoft Edge|Brave|Opera).*$', '', title, flags=re.IGNORECASE)
        
        # If title contains " - ", take the last part (usually site name)
        if ' - ' in title:
            parts = title.split(' - ')
            # Last part is usually the site name
            site_name = parts[-1].strip()
        else:
            site_name = title.strip()
        
        # Clean up
        site_name = site_name.strip()
        
        # Ignore empty or very short titles
        if len(site_name) < 2:
            return None
        
        # Ignore common non-website titles
        ignore_list = ['new tab', 'about:blank', 'settings', 'extensions', 'downloads']
        if site_name.lower() in ignore_list:
            return None
        
        return site_name
    
    def _get_browser_name(self, process_name):
        """Get friendly browser name from process name"""
        process_lower = process_name.lower()
        
        if 'chrome' in process_lower:
            return 'Chrome'
        elif 'firefox' in process_lower:
            return 'Firefox'
        elif 'edge' in process_lower or 'msedge' in process_lower:
            return 'Edge'
        elif 'brave' in process_lower:
            return 'Brave'
        elif 'opera' in process_lower:
            return 'Opera'
        elif 'safari' in process_lower:
            return 'Safari'
        else:
            return process_name


# Singleton instance
_browser_monitor = None

def get_browser_monitor():
    """Get or create browser monitor instance"""
    global _browser_monitor
    if _browser_monitor is None:
        _browser_monitor = BrowserMonitor()
    return _browser_monitor
