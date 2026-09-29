"""Flask API server"""

import asyncio
import platform
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from typing import Dict, Any
from ..media.windows import WindowsMediaEngine
from ..media.linux import LinuxMediaEngine


class APIServer:
    """Flask API server for media endpoints"""
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize media engine based on platform
        if platform.system() == "Windows":
            self.media_engine = WindowsMediaEngine()
        elif platform.system() == "Linux":
            self.media_engine = LinuxMediaEngine()
        else:
            # Fallback for unsupported platforms
            self.media_engine = None
        
        self._setup_routes()
        self._setup_logging()
    
    def _setup_logging(self):
        """Disable Flask startup messages"""
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    
    def _setup_routes(self):
        """Setup API routes"""
        @self.app.route('/now-playing')
        def now_playing():
            return self._handle_now_playing()
        
        @self.app.route('/sessions', methods=['GET'])
        def get_sessions():
            return self._handle_get_sessions()
    
    def _handle_now_playing(self):
        """Handle /now-playing endpoint"""
        if not self.media_engine:
            return jsonify({
                "current_session_id": None,
                "sessions": [],
                "error": "Unsupported platform"
            })
        
        if platform.system() == "Windows":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.media_engine.get_media_info())
                return jsonify(result)
            finally:
                loop.close()
        else:
            return jsonify(self.media_engine.get_media_info())
    
    def _handle_get_sessions(self):
        """Handle /sessions endpoint"""
        if platform.system() == "Windows" and self.media_engine and self.media_engine.available:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def fetch():
                from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as SMTC
                manager = await SMTC.request_async()
                if not manager:
                    return []
                return list(set([s.source_app_user_model_id for s in manager.get_sessions()]))
            
            try:
                sessions = loop.run_until_complete(fetch())
            except Exception as e:
                sessions = []
            finally:
                loop.close()
        elif platform.system() == "Linux" and self.media_engine and self.media_engine.available:
            try:
                from dbus.mainloop.glib import DBusGMainLoop
                import dbus
                DBusGMainLoop(set_as_default=True)
                bus = dbus.SessionBus()
                sessions = [name for name in bus.list_names() if name.startswith('org.mpris.MediaPlayer2.')]
            except Exception as e:
                sessions = []
        else:
            sessions = []
        
        html_list = """
        <body style='background-color: #121212; color: white; font-family: sans-serif; padding: 20px;'>
            <h3 style='margin-top: 0;'>Active Audio Sources:</h3>
            <ul>
        """
        
        if not sessions:
            html_list += "<li style='color: #888;'>No active audio sources found.</li>"
        else:
            for s in sessions:
                html_list += f"<li style='margin-bottom: 8px; font-size: 1.1em;'>{s}</li>"
        
        html_list += "</ul></body>"
        return html_list
    
    def run(self):
        """Run the Flask server"""
        try:
            self.app.run(
                host=self.host,
                port=self.port,
                threaded=True,
                use_reloader=False
            )
        except Exception as e:
            with open("error.txt", "w") as f:
                f.write(str(e))
