"""System tray interface"""

import os
import platform
import webbrowser
import pystray
from PIL import Image
from typing import Callable
from ..core.config import Config


class TrayIcon:
    """System tray icon manager"""
    
    def __init__(self, config: Config, on_quit: Callable, toggle_startup: Callable):
        self.config = config
        self.on_quit = on_quit
        self.toggle_startup = toggle_startup
        self.icon = None
    
    def setup(self):
        """Setup and run the system tray icon"""
        image = self._load_icon()
        menu = self._create_menu()
        
        self.icon = pystray.Icon(
            "MediaBridge",
            image,
            "Media Bridge",
            menu=menu
        )
        self.icon.run()
    
    def _load_icon(self):
        """Load platform-specific icon"""
        if platform.system() == "Windows":
            icon_path = self.config.get_resource_path("media-bridge.ico")
        elif platform.system() == "Linux":
            icon_path = self.config.get_resource_path("media-bridge.png")
        else:
            # Fallback to a simple colored square
            return Image.new('RGB', (64, 64), color='blue')
        
        try:
            return Image.open(icon_path)
        except Exception:
            # Fallback if icon not found
            return Image.new('RGB', (64, 64), color='blue')
    
    def _create_menu(self):
        """Create tray icon menu"""
        return pystray.Menu(
            pystray.MenuItem(
                f"Media Bridge v1.0.0 by GMC-Bridge",
                None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "View Data (JSON)",
                lambda: webbrowser.open(f"http://{self.config.display_host}:{self.config.port}/now-playing")
            ),
            pystray.MenuItem(
                "View Active Sessions",
                lambda: webbrowser.open(f"http://{self.config.display_host}:{self.config.port}/sessions")
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Start with system",
                self.toggle_startup,
                checked=lambda item: self._is_startup_enabled()
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.on_quit)
        )
    
    def _is_startup_enabled(self) -> bool:
        """Check if startup is enabled"""
        from ..utils.startup import StartupManager
        startup_manager = StartupManager(self.config)
        return startup_manager.is_enabled()
