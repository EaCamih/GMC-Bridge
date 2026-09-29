# Media Bridge Architecture

## Overview

Media Bridge is a cross-platform desktop application that exposes media playback information via a REST API. It runs as a system tray application and provides endpoints for querying current media state.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Media Bridge Application                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  System Tray │    │ Flask Server │    │ Media Engine │   │
│  │   Interface  │◄──►│   (API)      │◄──►│   (SMTC/     │   │
│  │              │    │              │    │   MPRIS)     │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│         │                   │                   │           │
│         └───────────────────┴───────────────────┘           │
│                             │                               │
│                             ▼                               │
│                    ┌──────────────┐                         │
│                    │   Cache &    │                         │
│                    │  Rate Limit  │                         │
│                    └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. System Tray Interface

**Purpose**: Provides user interaction and application lifecycle management

**Responsibilities**:
- Display application icon in system tray
- Provide context menu for user actions
- Handle application quit/exit
- Manage startup configuration

**Implementation**:
- Uses `pystray` library for cross-platform tray support
- Platform-specific icons (.ico for Windows, .png for Linux)
- Menu items include:
  - View API endpoints (opens browser)
  - Toggle startup with system
  - Quit application

### 2. Flask Server

**Purpose**: HTTP API for querying media state

**Responsibilities**:
- Handle HTTP requests on configured port
- Serve JSON responses for media data
- Serve HTML responses for session lists
- Enable CORS for cross-origin requests

**Endpoints**:
- `GET /now-playing` - Returns current media state as JSON
- `GET /sessions` - Returns list of active media sessions (HTML)

**Configuration**:
- Host: Configurable (default: 127.0.0.1)
- Port: Configurable (default: 5000)
- Threaded: Yes (for concurrent requests)
- Reloader: Disabled (prevents duplicate processes)

### 3. Media Engine

**Purpose**: Abstract interface to platform-specific media APIs

**Design Pattern**: Strategy Pattern

**Windows Implementation (SMTC)**:
```python
class WindowsMediaEngine:
    async def get_media_info():
        manager = await SMTC.request_async()
        sessions = manager.get_sessions()
        # Extract playback, timeline, and media properties
```

**Linux Implementation (MPRIS)**:
```python
class LinuxMediaEngine:
    def get_media_info():
        bus = dbus.SessionBus()
        players = discover_mpris_players(bus)
        # Query each player via D-Bus
```

**Unified Interface**:
```python
async def get_all_media_info():
    if IS_WINDOWS:
        return await get_windows_media_info()
    elif IS_LINUX:
        return get_linux_media_info()
```

### 4. Cache & Rate Limiting

**Purpose**: Optimize performance and prevent excessive CPU usage

**Caching Strategy**:
- Response cache: 0.5 second TTL
- Thumbnail cache: LRU with max 50 items
- MD5 hashing for thumbnail deduplication

**Rate Limiting**:
```python
if (current_time - last_execution_time) < 0.5 and last_payload:
    return last_payload  # Return cached response
```

**Thumbnail Cache**:
```python
thumb_cache = OrderedDict()  # LRU cache
MAX_CACHE_SIZE = 50

# Cache lookup
if img_hash in thumb_cache:
    thumb_cache.move_to_end(img_hash)  # Mark as recently used
    return thumb_cache[img_hash]

# Cache insertion
thumb_cache[img_hash] = thumb_url
if len(thumb_cache) > MAX_CACHE_SIZE:
    thumb_cache.popitem(last=False)  # Evict oldest
```

## Data Flow

### Request Flow

```
Client Request
    │
    ▼
Flask Server (/now-playing)
    │
    ▼
Rate Limit Check (cached?)
    │
    ├─ Yes ──► Return Cached Response
    │
    └─ No ──► Media Engine
                  │
                  ├─ Windows ──► SMTC API
                  │               │
                  │               └─ Sessions → Properties → Thumbnail
                  │
                  └─ Linux ──► D-Bus
                                  │
                                  └─ MPRIS Players → Properties → Artwork
    │
    ▼
Process & Cache Response
    │
    ▼
Return JSON to Client
```

### Thumbnail Processing Flow

```
Media API Returns Thumbnail
    │
    ▼
Read Raw Bytes
    │
    ▼
Compute MD5 Hash
    │
    ▼
Check Cache (hash exists?)
    │
    ├─ Yes ──► Return Cached Base64
    │
    └─ No ──► Convert to Base64
                  │
                  ▼
                  Store in Cache
                  │
                  ▼
                  Evict if > 50 items
                  │
                  ▼
                  Return Base64
```

## Platform-Specific Details

### Windows (SMTC)

**API**: Windows Runtime (WinRT) via `winsdk` library

**Key Objects**:
- `GlobalSystemMediaTransportControlsSessionManager`
- `GlobalSystemMediaTransportControlsSession`
- `GlobalSystemMediaTransportControlsSessionPlaybackInfo`
- `GlobalSystemMediaTransportControlsSessionTimelineProperties`
- `GlobalSystemMediaTransportControlsSessionMediaProperties`

**Async Pattern**:
```python
manager = await SMTC.request_async()
media_props = await session.try_get_media_properties_async()
stream = await stream_ref.open_read_async()
await reader.load_async(stream.size)
```

**Thumbnail Handling**:
- Windows provides thumbnail as `IRandomAccessStream`
- Read using `DataReader`
- Convert bytes to Base64 data URI

### Linux (MPRIS)

**API**: D-Bus via `dbus-python` library

**Key Interfaces**:
- `org.mpris.MediaPlayer2` - Player control
- `org.mpris.MediaPlayer2.Player` - Playback control
- `org.freedesktop.DBus.Properties` - Property access

**Synchronous Pattern**:
```python
bus = dbus.SessionBus()
player_object = bus.get_object(player_name, '/org/mpris/MediaPlayer2')
properties = dbus.Interface(player_object, 'org.freedesktop.DBus.Properties')
metadata = properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
```

**Thumbnail Handling**:
- MPRIS provides artwork as `mpris:artUrl` (file:// URL)
- Convert URL to filesystem path
- Read file and convert to Base64 data URI

## Error Handling

### Crash Logging

```python
def log_crash(e):
    # Create logs directory
    # Write timestamped crash log
    # Include stack trace
    # Keep only 10 most recent logs
```

### Single Instance Check

```python
def is_already_running():
    # Check for lockfile in temp directory
    # Verify PID is still running
    # Clean up stale locks
    # Register cleanup on exit
```

### Graceful Degradation

- If media API fails, return empty sessions list
- If thumbnail processing fails, return None for thumbnail
- If startup configuration fails, continue without error
- If notification fails, continue without error

## Startup Management

### Windows

**Mechanism**: Shortcut in Startup folder

**Implementation**:
```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut(path)
$Shortcut.TargetPath = executable_path
$Shortcut.WorkingDirectory = working_directory
$Shortcut.Save()
```

**Location**: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`

### Linux

**Mechanism**: .desktop file in autostart directory

**Implementation**:
```ini
[Desktop Entry]
Type=Application
Name=Media Bridge
Exec=/path/to/executable
Icon=/path/to/icon.png
X-GNOME-Autostart-enabled=true
```

**Location**: `~/.config/autostart/`

## Performance Considerations

### CPU Usage

- Rate limiting prevents excessive API calls
- Thumbnail caching avoids repeated image processing
- LRU eviction prevents unbounded memory growth

### Memory Usage

- Thumbnail cache limited to 50 items
- Crash logs limited to 10 files
- No persistent state beyond cache

### Network Usage

- Single HTTP server thread
- No external network calls
- All processing is local

## Security Considerations

### Default Configuration

- Binds to 127.0.0.1 by default (localhost only)
- User must explicitly configure for network access
- No authentication built-in (assumes trusted local network)

### File Access

- Only reads media player-provided artwork
- Only writes to designated temp directories
- No arbitrary file system access

### Process Isolation

- Single instance check prevents conflicts
- Lockfile mechanism ensures clean shutdown
- Daemon threads for background processing

## Build Process

### PyInstaller Configuration

**Windows**:
- Includes `winsdk` and Windows-specific libraries
- Bundles `plyer` Windows platform backend
- Uses .ico icon
- No console window

**Linux**:
- Includes D-Bus and GLib libraries
- Bundles `plyer` Linux platform backend
- Uses .png icon
- No console window

### Dependencies

**Core**:
- Flask - Web server
- Flask-CORS - Cross-origin support
- psutil - Process management
- pystray - System tray
- Pillow - Image processing
- plyer - Cross-platform notifications

**Platform-Specific**:
- Windows: `winsdk`
- Linux: `dbus-python`, `pygobject`

## Future Extensibility

### Adding New Platforms

1. Implement platform detection in initialization
2. Create platform-specific media engine
3. Add platform-specific dependencies to requirements.txt
4. Update PyInstaller spec for new platform
5. Add build matrix in GitHub Actions

### Adding New Endpoints

1. Define Flask route handler
2. Call appropriate media engine function
3. Process and format response
4. Update documentation

### Adding New Media Properties

1. Extract property in media engine
2. Add to response schema
3. Update enum documentation
4. Test with various media players
