#!/usr/bin/env python3
"""
Media Bridge - Main entry point

Cross-platform system tray application that exposes media controls
as a REST API.
"""

import sys
import os
import datetime
import traceback
import threading
import tempfile
import atexit
import psutil

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import Config
from src.core.server import APIServer
from src.ui.tray import TrayIcon
from src.utils.startup import StartupManager
from plyer import notification


def log_crash(e):
    """Log crash information to file"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    filename = os.path.join(log_dir, f"crash_{timestamp}.txt")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("--- CRASH DETECTED ---\n")
        f.write(f"Time: {timestamp}\n")
        f.write(f"Platform: {sys.platform}\n")
        f.write(str(e) + "\n\n")
        f.write(traceback.format_exc())
    
    # Keep only the 10 most recent logs
    files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith(".txt")]
    files.sort(key=os.path.getmtime)
    
    while len(files) > 10:
        oldest_file = files.pop(0)
        try:
            os.remove(oldest_file)
        except OSError:
            pass


def is_already_running():
    """Check if another instance is already running"""
    lockfile = os.path.join(tempfile.gettempdir(), 'media_bridge.lock')
    
    if os.path.exists(lockfile):
        try:
            with open(lockfile, 'r') as f:
                pid = int(f.read())
            if psutil.pid_exists(pid):
                return True
            else:
                os.remove(lockfile)
        except (ValueError, PermissionError):
            os.remove(lockfile)
    
    try:
        with open(lockfile, 'w') as f:
            f.write(str(os.getpid()))
    except IOError:
        pass
    
    atexit.register(lambda: os.remove(lockfile) if os.path.exists(lockfile) else None)
    return False


def on_quit(icon, item):
    """Handle quit action"""
    icon.stop()
    os._exit(0)


def toggle_startup(icon, item):
    """Toggle startup with system"""
    startup_manager.set_enabled(not startup_manager.is_enabled())


def run_flask_server(config: Config):
    """Run the Flask server in a separate thread"""
    # Disable Flask startup messages
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    def send_notification():
        """Send startup notification"""
        icon_path = config.get_resource_path('media-bridge.ico') if sys.platform == 'win32' else config.get_resource_path('media-bridge.png')
        notification.notify(
            title='Media Bridge v1.0.0',
            message=f'Server successfully started on port {config.port}',
            app_icon=icon_path if os.path.exists(icon_path) else None,
            timeout=5,
        )
    
    send_notification()
    
    # Create and run the server
    server = APIServer(config.host, config.port)
    server.run()


def main():
    """Main application entry point"""
    try:
        # Single instance check
        if is_already_running():
            print("Another instance is already running. Exiting...")
            sys.exit()
        
        # Initialize configuration
        config = Config()
        
        # Initialize startup manager
        global startup_manager
        startup_manager = StartupManager(config)
        
        # Start Flask server in background thread
        flask_thread = threading.Thread(target=run_flask_server, args=(config,), daemon=True)
        flask_thread.start()
        
        # Setup and run system tray
        tray = TrayIcon(config, on_quit, toggle_startup)
        tray.setup()
        
    except Exception as e:
        log_crash(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
