"""Startup management for auto-launch"""

import os
import sys
import platform
from ..core.config import Config


class StartupManager:
    """Manages application startup configuration"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def get_shortcut_path(self):
        """Get the path to the startup shortcut"""
        if platform.system() == "Windows":
            startup_dir = os.path.join(
                os.environ['APPDATA'],
                r'Microsoft\Windows\Start Menu\Programs\Startup'
            )
            return os.path.join(startup_dir, 'MediaBridge.lnk')
        elif platform.system() == "Linux":
            autostart_dir = os.path.expanduser('~/.config/autostart')
            return os.path.join(autostart_dir, 'media-bridge.desktop')
        return None
    
    def is_enabled(self) -> bool:
        """Check if startup is enabled"""
        shortcut_path = self.get_shortcut_path()
        return shortcut_path and os.path.exists(shortcut_path)
    
    def set_enabled(self, enable: bool):
        """Enable or disable startup"""
        shortcut_path = self.get_shortcut_path()
        
        if not shortcut_path:
            return
        
        if enable:
            self._create_shortcut(shortcut_path)
        else:
            self._remove_shortcut(shortcut_path)
    
    def _create_shortcut(self, shortcut_path: str):
        """Create startup shortcut"""
        if platform.system() == "Windows":
            self._create_windows_shortcut(shortcut_path)
        elif platform.system() == "Linux":
            self._create_linux_shortcut(shortcut_path)
    
    def _create_windows_shortcut(self, shortcut_path: str):
        """Create Windows startup shortcut"""
        if getattr(sys, 'frozen', False):
            target_path = sys.executable
            working_dir = os.path.dirname(sys.executable)
        else:
            target_path = sys.executable
            working_dir = os.path.dirname(os.path.abspath(__file__))
        
        script_args = f"""
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
        $Shortcut.TargetPath = '{target_path}'
        $Shortcut.WorkingDirectory = '{working_dir}'
        $Shortcut.Save()
        """
        
        import subprocess
        subprocess.run(
            ["powershell", "-Command", script_args],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    
    def _create_linux_shortcut(self, shortcut_path: str):
        """Create Linux autostart desktop file"""
        autostart_dir = os.path.dirname(shortcut_path)
        if not os.path.exists(autostart_dir):
            os.makedirs(autostart_dir)
        
        if getattr(sys, 'frozen', False):
            exec_path = sys.executable
        else:
            exec_path = sys.executable
        
        # Get the main script path
        if getattr(sys, 'frozen', False):
            script_path = exec_path
        else:
            # In development, point to the main entry point
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            script_path = os.path.join(project_root, 'main.py')
        
        icon_path = self.config.get_resource_path('media-bridge.png')
        
        desktop_content = f"""[Desktop Entry]
Type=Application
Name=Media Bridge
Exec={exec_path} {script_path}
Icon={icon_path}
X-GNOME-Autostart-enabled=true
StartupNotify=false
"""
        
        with open(shortcut_path, 'w') as f:
            f.write(desktop_content)
    
    def _remove_shortcut(self, shortcut_path: str):
        """Remove startup shortcut"""
        if os.path.exists(shortcut_path):
            try:
                os.remove(shortcut_path)
            except OSError:
                pass
