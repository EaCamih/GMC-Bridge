"""Base media interface and common utilities"""

import abc
import time
import hashlib
import base64
from collections import OrderedDict
from typing import Dict, List, Optional, Any


class MediaEngineBase(abc.ABC):
    """Abstract base class for media engines"""
    
    def __init__(self):
        self.last_execution_time = 0.0
        self.last_payload = None
        self.thumb_cache = OrderedDict()
        self.MAX_CACHE_SIZE = 50
    
    @abc.abstractmethod
    def get_media_info(self) -> Dict[str, Any]:
        """Get current media information"""
        pass
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit allows new request"""
        current_time = time.time()
        if (current_time - self.last_execution_time) < 0.5 and self.last_payload:
            return True
        self.last_execution_time = current_time
        return False
    
    def _cache_thumbnail(self, img_data: bytes) -> str:
        """Cache thumbnail and return base64 data URI"""
        img_hash = hashlib.md5(img_data).hexdigest()
        
        if img_hash in self.thumb_cache:
            self.thumb_cache.move_to_end(img_hash)
            return self.thumb_cache[img_hash]
        
        encoded_img = base64.b64encode(img_data).decode('utf-8')
        thumb_url = f"data:image/jpeg;base64,{encoded_img}"
        self.thumb_cache[img_hash] = thumb_url
        
        if len(self.thumb_cache) > self.MAX_CACHE_SIZE:
            self.thumb_cache.popitem(last=False)
        
        return thumb_url
    
    def _create_payload(self, current_session_id: str, sessions_list: List[Dict]) -> Dict[str, Any]:
        """Create standardized response payload"""
        import platform
        
        return {
            "app_version": "1.0.0",
            "os": f"{platform.system()} {platform.release()}",
            "current_session_id": current_session_id,
            "sessions": sessions_list
        }
