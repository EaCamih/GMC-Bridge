"""Configuration management for Media Bridge"""

import os
import sys
import configparser
import socket
import platform


class Config:
    """Application configuration manager"""
    
    def __init__(self):
        self.config = self._load_settings()
        self.host = self.config.get('SERVER', 'Host')
        self.port = self.config.getint('SERVER', 'Port')
        self.display_host = self._get_display_host()
    
    def _load_settings(self):
        """Load settings from configuration file"""
        config = configparser.ConfigParser()
        config['SERVER'] = {'Host': '127.0.0.1', 'Port': '5000'}
        
        # Use user's AppData for settings (better for frozen executables)
        # Falls back to project directory for development
        if getattr(sys, 'frozen', False):
            # For frozen executable, use AppData
            config_dir = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), 'GMC-Bridge')
            os.makedirs(config_dir, exist_ok=True)
            ini_path = os.path.join(config_dir, 'settings.ini')
        else:
            # For development, use project directory
            # We're in src/core/config.py, so go up 3 levels to project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            ini_path = os.path.join(project_root, 'settings.ini')
        
        if os.path.exists(ini_path):
            config.read(ini_path)
        else:
            try:
                with open(ini_path, 'w') as f:
                    config.write(f)
            except (PermissionError, IOError) as e:
                # If we can't write to the file, use default settings
                print(f"Warning: Could not write settings file: {e}")
                print("Using default configuration")
        
        return config
    
    def _get_display_host(self):
        """Get the display host for the tray menu"""
        if self.host == "0.0.0.0":
            return self._get_local_ip()
        return self.host
    
    def _get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            # In development, use the project root (parent of src directory)
            # We're in src/core/config.py, so we need to go up 3 levels to reach project root
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_path, relative_path)
