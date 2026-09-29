"""Windows SMTC media engine"""

import asyncio
import platform
from typing import Dict, List, Any, Optional
from .base import MediaEngineBase

# Try to import Windows-specific libraries
try:
    from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as SMTC
    from winsdk.windows.storage.streams import DataReader
    import winsdk._winrt as winrt
    WINSDK_AVAILABLE = True
except ImportError:
    WINSDK_AVAILABLE = False


class WindowsMediaEngine(MediaEngineBase):
    """Windows SMTC media detection engine"""
    
    def __init__(self):
        super().__init__()
        self.smtc_manager = None
        self.available = WINSDK_AVAILABLE
    
    async def get_media_info(self) -> Dict[str, Any]:
        """Get media info from Windows SMTC API"""
        if not self.available:
            return {"current_session_id": None, "sessions": [], "error": "Windows SDK not available"}
        
        if self._check_rate_limit() and self.last_payload:
            return self.last_payload
        
        try:
            manager = await self._get_manager()
            if not manager:
                return {"current_session_id": None, "sessions": []}
            
            current_focused = manager.get_current_session()
            all_sessions = manager.get_sessions()
            
            current_session_id = current_focused.source_app_user_model_id if current_focused else None
            sessions_list = []
            
            for session in all_sessions:
                session_data = await self._extract_session_data(session)
                sessions_list.append(session_data)
            
            payload = self._create_payload(current_session_id, sessions_list)
            self.last_payload = payload
            return payload
            
        except Exception as e:
            return {"current_session_id": None, "sessions": [], "error": str(e)}
    
    async def _get_manager(self):
        """Get or create SMTC manager"""
        if not self.smtc_manager:
            print("Instantiating new SMTC manager...")
            self.smtc_manager = await SMTC.request_async()
        
        try:
            # Test if manager is still valid
            self.smtc_manager.get_current_session()
            return self.smtc_manager
        except Exception:
            # Manager is invalid, recreate it
            print("Reinstantiating SMTC manager...")
            self.smtc_manager = await SMTC.request_async()
            return self.smtc_manager
    
    async def _extract_session_data(self, session) -> Dict[str, Any]:
        """Extract data from a single SMTC session"""
        app_id = session.source_app_user_model_id
        raw_playback = session.get_playback_info()
        raw_timeline = session.get_timeline_properties()
        raw_media = await session.try_get_media_properties_async()
        
        playback_data = self._extract_playback_info(raw_playback)
        timeline_data = self._extract_timeline_info(raw_timeline)
        media_data = await self._extract_media_info(raw_media, app_id)
        
        return {
            "source_app_id": app_id,
            "playback_info": playback_data,
            "timeline_properties": timeline_data,
            "media_properties": media_data
        }
    
    def _extract_playback_info(self, raw_playback) -> Dict[str, Any]:
        """Extract playback information"""
        return {
            "AutoRepeatMode": raw_playback.auto_repeat_mode.value if (raw_playback and raw_playback.auto_repeat_mode) else 0,
            "IsShuffleActive": raw_playback.is_shuffle_active if raw_playback else False,
            "PlaybackRate": raw_playback.playback_rate if raw_playback else 1.0,
            "PlaybackStatus": raw_playback.playback_status.value if (raw_playback and raw_playback.playback_status) else 0,
            "PlaybackType": raw_playback.playback_type.value if (raw_playback and raw_playback.playback_type) else 0
        }
    
    def _extract_timeline_info(self, raw_timeline) -> Dict[str, Any]:
        """Extract timeline information"""
        return {
            "EndTime": int(raw_timeline.end_time.total_seconds() * 1000) if raw_timeline.end_time else 0,
            "LastUpdatedTime": str(raw_timeline.last_updated_time) if raw_timeline.last_updated_time else None,
            "MaxSeekTime": int(raw_timeline.max_seek_time.total_seconds() * 1000) if raw_timeline.max_seek_time else 0,
            "MinSeekTime": int(raw_timeline.min_seek_time.total_seconds() * 1000) if raw_timeline.min_seek_time else 0,
            "Position": int(raw_timeline.position.total_seconds() * 1000) if raw_timeline.position else 0,
            "StartTime": int(raw_timeline.start_time.total_seconds() * 1000) if raw_timeline.start_time else 0,
        }
    
    async def _extract_media_info(self, raw_media, app_id: str) -> Dict[str, Any]:
        """Extract media information and thumbnail"""
        media_data = {
            "Title": raw_media.title if raw_media else "Unknown",
            "Artist": raw_media.artist if raw_media else "Unknown",
            "AlbumTitle": raw_media.album_title if raw_media else "Unknown",
            "AlbumArtist": raw_media.album_artist if raw_media else "Unknown",
            "TrackNumber": raw_media.track_number if raw_media else 0,
            "AlbumTrackCount": raw_media.album_track_count if raw_media else 0,
            "Genres": list(raw_media.genres) if raw_media else [],
            "Subtitle": raw_media.subtitle if raw_media else "",
            "Thumbnail": None
        }
        
        if raw_media and raw_media.thumbnail:
            thumb_url = await self._process_thumbnail(raw_media.thumbnail, media_data)
            media_data["Thumbnail"] = thumb_url
        
        return media_data
    
    async def _process_thumbnail(self, thumbnail, media_data: Dict) -> Optional[str]:
        """Process thumbnail and convert to base64"""
        try:
            stream_ref = thumbnail
            stream = await stream_ref.open_read_async()
            
            if stream.size > 0:
                reader = DataReader(stream.get_input_stream_at(0))
                await reader.load_async(stream.size)
                buffer = bytearray(stream.size)
                reader.read_bytes(buffer)
                
                print(f"Processing new artwork for: {media_data['Artist']} - {media_data['Title']}")
                return self._cache_thumbnail(bytes(buffer))
        
        except Exception as e:
            print(f"Error processing thumbnail: {e}")
            return None
