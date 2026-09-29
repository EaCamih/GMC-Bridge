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
        
        # Determine the executable/script directory
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Go up to the project root
        project_root = os.path.dirname(os.path.dirname(exe_dir))
        ini_path = os.path.join(project_root, 'settings.ini')
        
        if os.path.exists(ini_path):
            config.read(ini_path)
        else:
            with open(ini_path, 'w') as f:
                config.write(f)
        
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
