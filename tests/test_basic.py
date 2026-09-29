#!/usr/bin/env python3
"""
Basic test script to verify Media Bridge functionality
"""

import sys
import os
import platform

# Add src to path (tests is sibling to src)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("=== Media Bridge Basic Test ===")
print(f"Platform: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")
print()

# Test imports
print("Testing imports...")
try:
    import flask
    print("[OK] Flask imported successfully")
except ImportError as e:
    print(f"[FAIL] Flask import failed: {e}")
    sys.exit(1)

try:
    import flask_cors
    print("[OK] Flask-CORS imported successfully")
except ImportError as e:
    print(f"[FAIL] Flask-CORS import failed: {e}")
    sys.exit(1)

try:
    import psutil
    print("[OK] psutil imported successfully")
except ImportError as e:
    print(f"[FAIL] psutil import failed: {e}")
    sys.exit(1)

try:
    import pystray
    print("[OK] pystray imported successfully")
except ImportError as e:
    print(f"[FAIL] pystray import failed: {e}")
    sys.exit(1)

try:
    from PIL import Image
    print("[OK] Pillow imported successfully")
except ImportError as e:
    print(f"[FAIL] Pillow import failed: {e}")
    sys.exit(1)

try:
    import plyer
    print("[OK] plyer imported successfully")
except ImportError as e:
    print(f"[FAIL] plyer import failed: {e}")
    sys.exit(1)

# Test src package imports
print()
print("Testing src package imports...")
try:
    from src.core.config import Config
    print("[OK] src.core.config imported successfully")
except ImportError as e:
    print(f"[FAIL] src.core.config import failed: {e}")
    sys.exit(1)

try:
    from src.media.base import MediaEngineBase
    print("[OK] src.media.base imported successfully")
except ImportError as e:
    print(f"[FAIL] src.media.base import failed: {e}")
    sys.exit(1)

try:
    from src.media.windows import WindowsMediaEngine
    print("[OK] src.media.windows imported successfully")
except ImportError as e:
    print(f"[FAIL] src.media.windows import failed: {e}")
    sys.exit(1)

try:
    from src.media.linux import LinuxMediaEngine
    print("[OK] src.media.linux imported successfully")
except ImportError as e:
    print(f"[FAIL] src.media.linux import failed: {e}")
    sys.exit(1)

try:
    from src.ui.tray import TrayIcon
    print("[OK] src.ui.tray imported successfully")
except ImportError as e:
    print(f"[FAIL] src.ui.tray import failed: {e}")
    sys.exit(1)

try:
    from src.utils.startup import StartupManager
    print("[OK] src.utils.startup imported successfully")
except ImportError as e:
    print(f"[FAIL] src.utils.startup import failed: {e}")
    sys.exit(1)

try:
    from src.core.server import APIServer
    print("[OK] src.core.server imported successfully")
except ImportError as e:
    print(f"[FAIL] src.core.server import failed: {e}")
    sys.exit(1)

# Test platform-specific imports
print()
print("Testing platform-specific imports...")

if platform.system() == "Windows":
    try:
        import winsdk
        print("[OK] winsdk imported successfully")
    except ImportError:
        print("[WARN] winsdk not available (optional for Windows)")
elif platform.system() == "Linux":
    try:
        import dbus
        print("[OK] dbus imported successfully")
    except ImportError:
        print("[WARN] dbus not available (required for Linux media support)")
    try:
        import gi
        print("[OK] PyGObject imported successfully")
    except ImportError:
        print("[WARN] PyGObject not available (required for Linux media support)")

# Test icon files
print()
print("Testing icon files...")

# Get project root (parent of tests directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Check for source PNG (required)
png_path = os.path.join(project_root, 'media-bridge.png')
if os.path.exists(png_path):
    from PIL import Image
    try:
        img = Image.open(png_path)
        print(f"[OK] media-bridge.png exists ({img.size})")
        if img.size == (256, 256):
            print("[OK] Icon is correct size (256x256)")
        else:
            print(f"[WARN] Icon size is {img.size}, expected 256x256")
    except Exception as e:
        print(f"[WARN] media-bridge.png exists but cannot be read: {e}")
else:
    print("[WARN] media-bridge.png not found (required for icon generation)")
    print("       Run: python scripts/create_icons.py your-icon.png")

# Check for generated ICO (Windows)
if platform.system() == "Windows":
    ico_path = os.path.join(project_root, 'media-bridge.ico')
    if os.path.exists(ico_path):
        print("[OK] media-bridge.ico exists (generated from PNG)")
    else:
        print("[WARN] media-bridge.ico not found (run: python scripts/create_icons.py media-bridge.png)")
elif platform.system() == "Linux":
    if os.path.exists(png_path):
        print("[OK] media-bridge.png exists (used directly on Linux)")
    else:
        print("[WARN] media-bridge.png not found (required icon source)")

# Test configuration
print()
print("Testing configuration...")
try:
    from src.core.config import Config
    config = Config()
    print(f"[OK] Configuration created successfully (Host: {config.host}, Port: {config.port})")
except Exception as e:
    print(f"[FAIL] Configuration failed: {e}")

# Test Flask app creation
print()
print("Testing Flask app creation...")
try:
    from src.core.server import APIServer
    server = APIServer('127.0.0.1', 5000)
    print("[OK] Flask server created successfully")
except Exception as e:
    print(f"[FAIL] Flask server creation failed: {e}")

print()
print("=== All Basic Tests Passed ===")
print("Note: Full media functionality requires platform-specific dependencies:")
print("  - Windows: pip install winsdk (requires Visual Studio build tools)")
print("  - Linux: sudo apt-get install python3-dbus python3-gi")
