"""Linux MPRIS media engine"""

import os
import datetime
import platform
from typing import Dict, List, Any, Optional
from .base import MediaEngineBase

# Try to import Linux-specific libraries
try:
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk as gtk
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False


class LinuxMediaEngine(MediaEngineBase):
    """Linux MPRIS media detection engine"""
    
    def __init__(self):
        super().__init__()
        self.available = DBUS_AVAILABLE
    
    def get_media_info(self) -> Dict[str, Any]:
        """Get media info from Linux MPRIS via D-Bus"""
        if not self.available:
            return {"current_session_id": None, "sessions": [], "error": "D-Bus not available"}
        
        if self._check_rate_limit() and self.last_payload:
            return self.last_payload
        
        try:
            DBusGMainLoop(set_as_default=True)
            bus = dbus.SessionBus()
            
            mpris_names = self._discover_players(bus)
            if not mpris_names:
                return {"current_session_id": None, "sessions": []}
            
            current_session_id = mpris_names[0] if mpris_names else None
            sessions_list = []
            
            for player_name in mpris_names:
                session_data = self._extract_session_data(bus, player_name)
                if session_data:
                    sessions_list.append(session_data)
            
            payload = self._create_payload(current_session_id, sessions_list)
            self.last_payload = payload
            return payload
            
        except Exception as e:
            print(f"Error in Linux media info: {e}")
            return {"current_session_id": None, "sessions": [], "error": str(e)}
    
    def _discover_players(self, bus) -> List[str]:
        """Discover MPRIS players on D-Bus"""
        return [name for name in bus.list_names() if name.startswith('org.mpris.MediaPlayer2.')]
    
    def _extract_session_data(self, bus, player_name: str) -> Optional[Dict[str, Any]]:
        """Extract data from a single MPRIS player"""
        try:
            player_object = bus.get_object(player_name, '/org/mpris/MediaPlayer2')
            player_properties = dbus.Interface(player_object, 'org.freedesktop.DBus.Properties')
            
            playback_data = self._extract_playback_info(player_properties)
            timeline_data = self._extract_timeline_info(player_properties)
            media_data = self._extract_media_info(player_properties, player_name)
            
            return {
                "source_app_id": player_name,
                "playback_info": playback_data,
                "timeline_properties": timeline_data,
                "media_properties": media_data
            }
            
        except Exception as e:
            print(f"Error getting info from {player_name}: {e}")
            return None
    
    def _extract_playback_info(self, player_properties) -> Dict[str, Any]:
        """Extract playback information from MPRIS"""
        try:
            playback_status = player_properties.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
            playback_status_map = {'Stopped': 3, 'Playing': 4, 'Paused': 5}
            playback_status_value = playback_status_map.get(playback_status, 0)
        except:
            playback_status_value = 0
        
        try:
            rate = player_properties.Get('org.mpris.MediaPlayer2.Player', 'Rate')
        except:
            rate = 1.0
        
        try:
            shuffle = player_properties.Get('org.mpris.MediaPlayer2.Player', 'Shuffle')
        except:
            shuffle = False
        
        try:
            loop_status = player_properties.Get('org.mpris.MediaPlayer2.Player', 'LoopStatus')
            loop_map = {'None': 0, 'Track': 1, 'Playlist': 2}
            auto_repeat_mode = loop_map.get(loop_status, 0)
        except:
            auto_repeat_mode = 0
        
        return {
            "AutoRepeatMode": auto_repeat_mode,
            "IsShuffleActive": bool(shuffle),
            "PlaybackRate": float(rate) if rate else 1.0,
            "PlaybackStatus": playback_status_value,
            "PlaybackType": 1  # Assume music for MPRIS
        }
    
    def _extract_timeline_info(self, player_properties) -> Dict[str, Any]:
        """Extract timeline information from MPRIS"""
        try:
            position = player_properties.Get('org.mpris.MediaPlayer2.Player', 'Position')
            position_ms = int(position / 1000) if position else 0
        except:
            position_ms = 0
        
        return {
            "EndTime": 0,  # MPRIS doesn't always provide this
            "LastUpdatedTime": datetime.datetime.utcnow().isoformat(),
            "MaxSeekTime": 0,
            "MinSeekTime": 0,
            "Position": position_ms,
            "StartTime": 0
        }
    
    def _extract_media_info(self, player_properties, player_name: str) -> Dict[str, Any]:
        """Extract media information from MPRIS"""
        try:
            metadata = player_properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
        except:
            metadata = {}
        
        # Convert metadata to Python dict
        metadata_dict = {}
        for key, value in metadata.items():
            if isinstance(value, dbus.Dictionary):
                metadata_dict[key] = dict(value)
            elif isinstance(value, (dbus.Array, list)):
                metadata_dict[key] = list(value)
            else:
                metadata_dict[key] = str(value) if value is not None else ""
        
        media_data = {
            "Title": metadata_dict.get('xesam:title', 'Unknown'),
            "Artist": metadata_dict.get('xesam:artist', ['Unknown'])[0] if metadata_dict.get('xesam:artist') else 'Unknown',
            "AlbumTitle": metadata_dict.get('xesam:album', 'Unknown'),
            "AlbumArtist": metadata_dict.get('xesam:albumArtist', ['Unknown'])[0] if metadata_dict.get('xesam:albumArtist') else 'Unknown',
            "TrackNumber": int(metadata_dict.get('xesam:trackNumber', 0)),
            "AlbumTrackCount": 0,
            "Genres": metadata_dict.get('xesam:genre', []),
            "Subtitle": "",
            "Thumbnail": None
        }
        
        # Handle artwork
        artwork_url = metadata_dict.get('mpris:artUrl')
        if artwork_url:
            thumb_url = self._process_artwork(artwork_url, media_data)
            media_data["Thumbnail"] = thumb_url
        
        return media_data
    
    def _process_artwork(self, artwork_url: str, media_data: Dict) -> Optional[str]:
        """Process artwork from MPRIS file URL"""
        try:
            if artwork_url.startswith('file://'):
                artwork_path = artwork_url[7:]
                if os.path.exists(artwork_path):
                    with open(artwork_path, 'rb') as f:
                        img_data = f.read()
                    
                    print(f"Processing new artwork for: {media_data['Artist']} - {media_data['Title']}")
                    return self._cache_thumbnail(img_data)
        except Exception as e:
            print(f"Error processing artwork: {e}")
            return None
