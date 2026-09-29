<div align="center">
  <img src="GMC-Bridge.png" alt="GMC-Bridge Logo" width="256"/>
  
  # GMC-Bridge
  
  **Global Media Control - Cross-platform Media Bridge**
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
  [![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/GMC-Bridge)
  [![Semantic Release](https://img.shields.io/badge/semantic--release-auto.svg)](https://github.com/semantic-release/semantic-release)
</div>

---

**GMC-Bridge** is a cross-platform system tray application that exposes media controls as a clean REST API. Originally based on [smtc-bridge](https://github.com/nuttylmao/smtc-bridge), this version adds Linux support via MPRIS and automates releases with semantic versioning.

## Features

- **Cross-Platform**: Works on both Windows (SMTC) and Linux (MPRIS)
- **System Tray Integration**: Runs silently in your system tray
- **REST API**: Simple HTTP endpoints for media information
- **Album Artwork**: Base64-encoded thumbnails in API responses
- **Rate Limiting**: Built-in caching to prevent excessive CPU usage
- **Auto-Startup**: Configure to start with your system
- **Automated Releases**: Semantic versioning with GitHub Actions

## What It Does

Media Bridge runs in the background and provides a simple HTTP API to query currently playing media information:

- **Windows**: Uses the System Media Transport Controls (SMTC) API
- **Linux**: Uses the MPRIS (Media Player Remote Interfacing Specification) via D-Bus

This allows developers to create "Now Playing" widgets that work with any media player, bypassing complex API limitations from streaming platforms.

## Quick Start

### Download

Download the latest executable from the [Releases page](https://github.com/yourusername/GMC-Bridge/releases):
- **Windows**: `Media-Bridge-windows.exe`
- **Linux**: `Media-Bridge-linux`

### Run

1. Run the executable — a tray icon will appear in your system tray
2. Right-click the icon to access the API endpoints
3. By default, the API is available at `http://127.0.0.1:5000/now-playing`

### API Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/now-playing` | Returns current media state as JSON |
| `GET` | `/sessions` | Returns list of active media sessions (HTML) |

## API Response

The `/now-playing` endpoint provides a real-time snapshot of your active media sessions. This allows developers to create custom "Now Playing" widgets, overlays, or integrations with any media player that supports standard media controls.

```json
{
  "app_version": "1.0.0",
  "os": "Windows 10" or "Linux 5.15",
  "current_session_id": "string",
  "sessions": [
    {
      "source_app_id": "string",
      "media_properties": {
        "Title": "string",
        "Artist": "string",
        "AlbumTitle": "string",
        "AlbumArtist": "string",
        "Thumbnail": "string (base64 data URI)",
        "AlbumTrackCount": "integer",
        "TrackNumber": "integer",
        "Genres": "array of strings",
        "Subtitle": "string"
      },
      "playback_info": {
        "PlaybackStatus": "integer",
        "PlaybackType": "integer",
        "PlaybackRate": "number or null",
        "IsShuffleActive": "boolean",
        "AutoRepeatMode": "integer"
      },
      "timeline_properties": {
        "Position": "integer (ms)",
        "StartTime": "integer (ms)",
        "EndTime": "integer (ms)",
        "MinSeekTime": "integer (ms)",
        "MaxSeekTime": "integer (ms)",
        "LastUpdatedTime": "string (ISO 8601)"
      }
    }
  ]
}
```

```json
{
  "app_version": "1.0.0",
  "os": "Windows 10" or "Linux 5.15",
  "current_session_id": "string",
  "sessions": [
    {
      "source_app_id": "string",
      "media_properties": {
        "Title": "string",
        "Artist": "string",
        "AlbumTitle": "string",
        "AlbumArtist": "string",
        "Thumbnail": "string (base64 data URI)",
        "AlbumTrackCount": "integer",
        "TrackNumber": "integer",
        "Genres": "array of strings",
        "Subtitle": "string"
      },
      "playback_info": {
        "PlaybackStatus": "integer",
        "PlaybackType": "integer",
        "PlaybackRate": "number or null",
        "IsShuffleActive": "boolean",
        "AutoRepeatMode": "integer"
      },
      "timeline_properties": {
        "Position": "integer (ms)",
        "StartTime": "integer (ms)",
        "EndTime": "integer (ms)",
        "MinSeekTime": "integer (ms)",
        "MaxSeekTime": "integer (ms)",
        "LastUpdatedTime": "string (ISO 8601)"
      }
    }
  ]
}
```

## Enum Reference

### Playback Status

| Value | Status | Description |
| :--- | :--- | :--- |
| `0` | `CLOSED` | Engine uninitialized or empty |
| `1` | `OPENED` | Pipeline loaded but idling |
| `2` | `CHANGING` | Buffering, track skipping, or seeking |
| `3` | `STOPPED` | Track queued but fully stopped |
| `4` | `PLAYING` | Audio actively streaming |
| `5` | `PAUSED` | Audio frozen |

### Playback Type

| Value | Type | Description |
| :--- | :--- | :--- |
| `0` | `UNKNOWN` | Generic audio wrapper |
| `1` | `MUSIC` | Pure audio pipeline (Spotify, iTunes, etc.) |
| `2` | `VIDEO` | Visual media feed (YouTube, Twitch, etc.) |
| `3` | `IMAGE` | Static slideshow presentation hook |

### Auto Repeat Mode

| Value | Mode | Description |
| :--- | :--- | :--- |
| `0` | `NONE` | Plays queue through and terminates |
| `1` | `TRACK` | Single active song looping |
| `2` | `LIST` | Parent playlist/album looping |

## How It Works

### Architecture Overview

Media Bridge consists of several key components:

1. **Single Instance Check**: Prevents multiple instances from running simultaneously
2. **Platform Detection**: Automatically detects Windows vs Linux and loads appropriate libraries
3. **Media API Interface**: Abstracts platform-specific media APIs (SMTC for Windows, MPRIS for Linux)
4. **Flask Web Server**: Provides HTTP endpoints for querying media state
5. **System Tray Integration**: Provides a GUI for user interaction
6. **Startup Management**: Allows users to auto-start the application on system boot

### Windows Implementation (SMTC)

#### Step 1: Initialization
```python
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as SMTC
smtc_manager = await SMTC.request_async()
```

The application requests access to Windows' SMTC API, which provides system-wide media information.

#### Step 2: Session Discovery
```python
current_focused = manager.get_current_session()
all_sessions = manager.get_sessions()
```

SMTC maintains a list of all active media sessions (Spotify, VLC, browser, etc.) and identifies which one is currently focused.

#### Step 3: Data Extraction
For each session, the application extracts:

**Playback Info:**
- AutoRepeatMode: Loop behavior (none, track, list)
- IsShuffleActive: Whether shuffle is enabled
- PlaybackRate: Playback speed (1.0 = normal)
- PlaybackStatus: Current state (playing, paused, stopped)
- PlaybackType: Content type (music, video, image)

**Timeline Properties:**
- Position: Current playback position in milliseconds
- StartTime/EndTime: Track boundaries
- MinSeekTime/MaxSeekTime: Seekable range
- LastUpdatedTime: When the timeline was last refreshed

**Media Properties:**
- Title, Artist, AlbumTitle, AlbumArtist
- TrackNumber, AlbumTrackCount
- Genres array
- Thumbnail artwork

#### Step 4: Thumbnail Processing
```python
stream = await stream_ref.open_read_async()
reader = DataReader(stream.get_input_stream_at(0))
await reader.load_async(stream.size)
buffer = bytearray(stream.size)
reader.read_bytes(buffer)
```

Windows provides artwork as a byte stream. The application:
1. Reads the raw bytes
2. Computes an MD5 hash for caching
3. Converts to Base64 data URI
4. Caches up to 50 unique artworks using LRU eviction

### Linux Implementation (MPRIS)

#### Step 1: D-Bus Connection
```python
DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
```

Linux uses D-Bus for inter-process communication. The application connects to the session bus.

#### Step 2: Player Discovery
```python
mpris_names = [name for name in bus.list_names() if name.startswith('org.mpris.MediaPlayer2.')]
```

MPIS-compliant players register with names like `org.mpris.MediaPlayer2.spotify`. The application discovers all active players.

#### Step 3: Property Retrieval
For each player, the application queries D-Bus properties:

```python
player_properties = dbus.Interface(player_object, 'org.freedesktop.DBus.Properties')
playback_status = player_properties.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
metadata = player_properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
```

**Playback Status Mapping:**
- 'Stopped' → 3
- 'Playing' → 4
- 'Paused' → 5

**Metadata Extraction:**
- `xesam:title` → Title
- `xesam:artist` → Artist (array)
- `xesam:album` → AlbumTitle
- `xesam:albumArtist` → AlbumArtist
- `xesam:trackNumber` → TrackNumber
- `xesam:genre` → Genres
- `mpris:artUrl` → Thumbnail URL

#### Step 4: Artwork Handling
```python
if artwork_url.startswith('file://'):
    artwork_path = artwork_url[7:]
    with open(artwork_path, 'rb') as f:
        img_data = f.read()
```

MPRIS provides artwork as file:// URLs. The application:
1. Converts URL to filesystem path
2. Reads the image file
3. Computes MD5 hash for caching
4. Converts to Base64 data URI
5. Caches using the same LRU strategy as Windows

### Cross-Platform Abstraction

The application uses a unified interface:

```python
async def get_all_media_info():
    if IS_WINDOWS:
        return await get_windows_media_info()
    elif IS_LINUX:
        return get_linux_media_info()
```

This allows the Flask endpoints to work identically on both platforms:

```python
@app.route('/now-playing')
def now_playing():
    if IS_WINDOWS:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return jsonify(loop.run_until_complete(get_all_media_info()))
        finally:
            loop.close()
    else:
        return jsonify(get_all_media_info())
```

### Rate Limiting and Caching

To prevent excessive CPU usage from rapid API calls:

```python
if (current_time - last_execution_time) < 0.5 and last_payload:
    return last_payload
```

The application caches responses for 0.5 seconds and reuses them if multiple requests arrive in quick succession.

### System Tray Integration

#### Windows
```python
import pystray
from PIL import Image

image = Image.open(get_resource_path("media-bridge.ico"))
menu = pystray.Menu(
    pystray.MenuItem("View Data (JSON)", lambda: webbrowser.open(...)),
    pystray.MenuItem("Start with Windows", toggle_startup),
    pystray.MenuItem("Quit", on_quit)
)
icon = pystray.Icon("MediaBridge", image, "Media Bridge", menu=menu)
icon.run()
```

#### Linux
Uses the same `pystray` library but with a PNG icon instead of ICO.

### Startup Management

#### Windows
Creates a `.lnk` shortcut in the Startup folder using PowerShell:
```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('path/to/shortcut.lnk')
$Shortcut.TargetPath = 'path/to/exe'
$Shortcut.Save()
```

#### Linux
Creates a `.desktop` file in `~/.config/autostart/`:
```ini
[Desktop Entry]
Type=Application
Name=Media Bridge
Exec=/path/to/executable
Icon=/path/to/icon.png
X-GNOME-Autostart-enabled=true
```

## Project Structure

```
GMC-Bridge/
├── .github/
│   └── workflows/
│       └── release.yml          # GitHub Actions workflow for automated releases
├── src/                         # Source code
│   ├── __init__.py
│   ├── core/                    # Core application components
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   └── server.py            # Flask API server
│   ├── media/                   # Media detection engines
│   │   ├── __init__.py
│   │   ├── base.py              # Base media interface
│   │   ├── windows.py           # Windows SMTC engine
│   │   └── linux.py             # Linux MPRIS engine
│   ├── ui/                      # User interface components
│   │   ├── __init__.py
│   │   └── tray.py              # System tray interface
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── startup.py           # Startup management
├── main.py                      # Application entry point
├── media-bridge.spec            # PyInstaller build configuration
├── requirements.txt             # Python dependencies
├── settings.ini                 # Default configuration
├── media-bridge.png             # Source icon file (256x256, resized from your image)
├── media-bridge.ico             # Generated Windows icon (multi-size, from PNG)
├── build.sh                     # Linux build script
├── build.bat                    # Windows build script
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_basic.py            # Basic functionality tests
├── scripts/                     # Utility scripts
│   └── create_icons.py          # Icon generation script (PNG → ICO)
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md          # Technical architecture
│   ├── DEVELOPMENT.md           # Development guide
│   ├── CHANGELOG.md             # Version history
│   └── REFACTORING.md           # Reorganization guide
├── README.md                    # User documentation
├── .releaserc.json              # Semantic release configuration
├── .gitignore                   # Git ignore rules
└── package.json                 # Project metadata
```

## Development

### Prerequisites

- Python 3.11+
- Platform-specific dependencies:
  - Windows: 
    - Basic: No additional system dependencies required
    - Full media support: `winsdk` (requires Visual Studio build tools)
  - Linux: `libgirepository1.0-dev`, `gir1.2-gtk-3.0`

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/GMC-Bridge.git
cd GMC-Bridge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your icon file
# The project requires a source PNG file (any size, will be resized to 256x256)
# The script will resize it to 256x256 and generate the Windows .ico file
# For example: python scripts/create_icons.py your-icon.png

# Generate icons (resizes to 256x256 and creates multi-size Windows .ico)
python scripts/create_icons.py your-icon.png
```

### Running from Source

```bash
python main.py
```

### Building Executables

```bash
# Install PyInstaller
pip install pyinstaller

# Build
pyinstaller --noconfirm media-bridge.spec
```

The executable will be in the `dist/` directory.

## Configuration

Edit `settings.ini` to change the server configuration:

```ini
[SERVER]
Host = 127.0.0.1
Port = 5000
```

- Set `Host = 0.0.0.0` to make the server accessible from other devices on your network
- Change `Port` if you need to use a different port

## Documentation

For more detailed information, see:
- [Architecture Documentation](docs/ARCHITECTURE.md) - Technical architecture and system design
- [Development Guide](docs/DEVELOPMENT.md) - Development workflow and contribution guide
- [Changelog](docs/CHANGELOG.md) - Version history and changes
- [Reorganization Guide](docs/REFACTORING.md) - Information about the project structure reorganization

## Semantic Release

This project uses semantic release to automate versioning and publishing:

### How It Works

1. **Commit Analysis**: Commits are analyzed following [Conventional Commits](https://www.conventionalcommits.org/)
   - `feat:` → Minor version bump (1.0.0 → 1.1.0)
   - `fix:` → Patch version bump (1.0.0 → 1.0.1)
   - `BREAKING CHANGE:` → Major version bump (1.0.0 → 2.0.0)

2. **Changelog Generation**: Automatic CHANGELOG.md updates

3. **Git Tagging**: Creates Git tags for new versions

4. **GitHub Release**: Creates GitHub releases with built executables

### Commit Examples

```bash
# Feature addition
git commit -m "feat: add support for custom thumbnail sizes"

# Bug fix
git commit -m "fix: resolve memory leak in thumbnail cache"

# Breaking change
git commit -m "feat: redesign API response structure

BREAKING CHANGE: sessions array now uses snake_case keys"
```

### Release Workflow

When you push to `main`:

1. GitHub Actions triggers the release workflow
2. Builds executables for Windows and Linux
3. Runs semantic release to determine version
4. Creates GitHub release with assets
5. Updates CHANGELOG.md

## Troubleshooting

### Windows

**Issue: Application won't start**
- Check that no other instance is running (see lockfile in temp directory)
- Review crash logs in the `logs/` folder

**Issue: No media sessions detected**
- Ensure media players are actually playing something
- Some players may not support SMTC (check player documentation)
- If you see "winsdk not available" warning, install it for full functionality:
  ```bash
  pip install winsdk
  ```
  Note: This requires Visual Studio build tools to compile

**Issue: winsdk installation fails**
- Install Visual Studio Build Tools (C++ build tools)
- Or use the application without winsdk (limited functionality)

### Linux

**Issue: Application won't start**
- Install required system dependencies:
  ```bash
  sudo apt-get install libgirepository1.0-dev gir1.2-gtk-3.0
  ```
- Check that D-Bus session is running

**Issue: No media sessions detected**
- Ensure your media player supports MPRIS (most modern Linux players do)
- Check that the player is actually running and playing media
- Verify D-Bus communication: `dbus-send --session --dest=org.freedesktop.DBus --type=method_call --print-reply /org/freedesktop/DBus org.freedesktop.DBus.ListNames`

## License

This project is based on [smtc-bridge](https://github.com/nuttylmao/smtc-bridge) and maintains compatibility with its API while adding cross-platform support.

## Credits

- Original project: [nuttylmao/smtc-bridge](https://github.com/nuttylmao/smtc-bridge)
- Cross-platform enhancements for Linux support
- Automated release workflow with semantic versioning

---

Developed with love by [Camilla Viana](https://github.com/EaCamih) 💜
