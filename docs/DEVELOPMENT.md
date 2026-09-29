# Development Guide

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
├── create_icons.py              # Icon generation script
├── build.sh                     # Linux build script
├── build.bat                    # Windows build script
├── test_basic.py                # Basic functionality tests
├── README.md                    # User documentation
├── ARCHITECTURE.md              # Technical architecture documentation
├── DEVELOPMENT.md               # This file
├── CHANGELOG.md                 # Version history
├── .releaserc.json              # Semantic release configuration
├── .gitignore                   # Git ignore rules
└── package.json                 # Project metadata
```

## Development Workflow

### 1. Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/GMC-Bridge.git
cd GMC-Bridge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate icons
python create_icons.py

# Run basic tests
python test_basic.py
```

### 2. Running the Application

```bash
# Run from source
python main.py

# Or build and run the executable
pyinstaller --noconfirm media-bridge.spec
./dist/Media-Bridge  # Linux
dist\Media-Bridge.exe  # Windows
```

### 3. Making Changes

#### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and single-purpose

#### Platform-Specific Code

When adding platform-specific functionality:

```python
import platform

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

if IS_WINDOWS:
    # Windows-specific code
    try:
        import windows_library
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
elif IS_LINUX:
    # Linux-specific code
    try:
        import linux_library
        LINUX_AVAILABLE = True
    except ImportError:
        LINUX_AVAILABLE = False
```

#### Error Handling

Always use graceful degradation:

```python
def platform_specific_function():
    if not PLATFORM_LIBRARY_AVAILABLE:
        return {"error": "Platform library not available"}
    
    try:
        # Attempt operation
        result = perform_operation()
        return result
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
```

### 4. Testing

#### Running Basic Tests

```bash
python test_basic.py
```

#### Manual Testing

1. Start the application
2. Play media in your preferred player
3. Test API endpoints:
   ```bash
   curl http://127.0.0.1:5000/now-playing
   curl http://127.0.0.1:5000/sessions
   ```

#### Platform Testing

- **Windows**: Test with various media players (Spotify, VLC, browser players)
- **Linux**: Test with MPRIS-compliant players (Rhythmbox, VLC, Spotify)

### 5. Building for Distribution

#### Local Build

```bash
# Windows
build.bat

# Linux
chmod +x build.sh
./build.sh
```

#### Manual PyInstaller Build

```bash
pip install pyinstaller
pyinstaller --noconfirm media-bridge.spec
```

### 6. Committing Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```bash
# Feature
git commit -m "feat: add support for custom thumbnail sizes"

# Bug fix
git commit -m "fix: resolve memory leak in thumbnail cache"

# Documentation
git commit -m "docs: update installation instructions"

# Breaking change
git commit -m "feat: redesign API response structure

BREAKING CHANGE: sessions array now uses snake_case keys"
```

### 7. Creating Releases

Releases are automated via semantic release. Just push to main:

```bash
git checkout main
git merge feature-branch
git push origin main
```

The GitHub Actions workflow will:
1. Build executables for Windows and Linux
2. Determine version based on commits
3. Create GitHub release
4. Update CHANGELOG.md

## Architecture Decisions

### Graceful Degradation

The application is designed to work even when platform-specific dependencies are missing:

- **Windows without winsdk**: Application runs but returns empty media data
- **Linux without D-Bus**: Application runs but returns empty media data
- **Missing icons**: Application runs with fallback colored square

This approach ensures:
- Easier development setup
- Broader compatibility
- Clear error messages for users

### Cross-Platform Abstraction

Platform-specific code is isolated in dedicated functions:

```python
async def get_windows_media_info():
    # Windows-specific implementation
    pass

def get_linux_media_info():
    # Linux-specific implementation
    pass

async def get_all_media_info():
    # Unified interface
    if IS_WINDOWS:
        return await get_windows_media_info()
    elif IS_LINUX:
        return get_linux_media_info()
```

### Caching Strategy

- **Response cache**: 0.5 second TTL to prevent excessive API calls
- **Thumbnail cache**: LRU with 50-item limit to manage memory
- **MD5 hashing**: Prevents reprocessing identical artwork

## Adding New Features

### Adding a New API Endpoint

1. Add the route in `media_bridge.py`:
   ```python
   @app.route('/new-endpoint')
   def new_endpoint():
       # Your logic here
       return jsonify({"data": "result"})
   ```

2. Update documentation in `README.md`
3. Add tests in `test_basic.py` if applicable
4. Commit with conventional commit format

### Adding Support for a New Platform

1. Add platform detection in `media_bridge.py`
2. Implement platform-specific media engine
3. Add platform dependencies to `requirements.txt`
4. Update `media-bridge.spec` for the new platform
5. Add build matrix in `.github/workflows/release.yml`
6. Test on the target platform
7. Update documentation

### Adding New Media Properties

1. Extract property in the appropriate media engine function
2. Add to the response schema
3. Update enum documentation in `README.md`
4. Test with various media players
5. Update CHANGELOG.md

## Troubleshooting Development Issues

### winsdk Installation Fails

**Problem**: Cannot install winsdk due to missing build tools

**Solution**: 
- Install Visual Studio Build Tools (C++ build tools)
- Or develop without winsdk (limited functionality)

### PyInstaller Build Fails

**Problem**: PyInstaller cannot find dependencies

**Solution**:
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check PyInstaller spec file for correct configuration
- Try building with `--debug` flag for more information

### D-Bus Issues on Linux

**Problem**: Cannot connect to D-Bus

**Solution**:
- Ensure D-Bus session is running: `dbus-send --session --dest=org.freedesktop.DBus --type=method_call --print-reply /org/freedesktop/DBus org.freedesktop.DBus.ListNames`
- Install required packages: `sudo apt-get install python3-dbus python3-gi`

## Performance Optimization

### Reducing CPU Usage

- Increase cache TTL if acceptable for your use case
- Reduce thumbnail cache size if memory is constrained
- Implement request debouncing for rapid API calls

### Reducing Memory Usage

- Lower thumbnail cache size
- Implement periodic cache cleanup
- Use more efficient image processing

## Security Considerations

### Network Exposure

By default, the application binds to `127.0.0.1` (localhost only). To expose to network:

1. Edit `settings.ini`:
   ```ini
   [SERVER]
   Host = 0.0.0.0
   Port = 5000
   ```

2. **Important**: This exposes the API to your local network. Consider:
   - Using a firewall to restrict access
   - Implementing authentication
   - Using a reverse proxy with SSL

### File Access

The application only accesses:
- Media player-provided artwork
- Designated temporary directories
- Configuration files in the application directory

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test thoroughly
5. Commit with conventional commit format
6. Push to your fork: `git push origin feature/my-feature`
7. Create a pull request

## License

This project is based on [smtc-bridge](https://github.com/nuttylmao/smtc-bridge) and maintains compatibility with its API while adding cross-platform support.
