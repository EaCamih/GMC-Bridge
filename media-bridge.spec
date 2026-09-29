# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# Initialize lists
datas = []
binaries = []
hiddenimports = ['flask', 'flask_cors', 'psutil', 'pystray', 'PIL', 'plyer']

# Add src package
hiddenimports.extend(['src', 'src.core', 'src.media', 'src.ui', 'src.utils'])
hiddenimports.extend(['src.core.config', 'src.core.server'])
hiddenimports.extend(['src.media.base', 'src.media.windows', 'src.media.linux'])
hiddenimports.extend(['src.ui.tray'])
hiddenimports.extend(['src.utils.startup'])

# Platform-specific configuration
import platform
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

if IS_WINDOWS:
    # Try to include icon if it exists
    import os
    if os.path.exists('media-bridge.ico'):
        datas.append(('media-bridge.ico', '.'))
    else:
        print("Warning: media-bridge.ico not found, building without icon")
    
    # Only include winsdk if it's available
    try:
        import winsdk
        hiddenimports.extend(['winsdk', 'winsdk._winrt'])
        # Collect all necessary files for complex packages
        for pkg in ['winsdk', 'plyer']:
            tmp_ret = collect_all(pkg)
            if tmp_ret:
                datas += tmp_ret[0]
                binaries += tmp_ret[1]
                hiddenimports += tmp_ret[2]
    except ImportError:
        print("Warning: winsdk not available, building without Windows media support")
        print("Install winsdk for full functionality: pip install winsdk")
        # Still collect plyer files
        tmp_ret = collect_all('plyer')
        if tmp_ret:
            datas += tmp_ret[0]
            binaries += tmp_ret[1]
            hiddenimports += tmp_ret[2]
    
    # Add specific platform backend for plyer
    hiddenimports.append('plyer.platforms.win.notification')

elif IS_LINUX:
    # Try to include icon if it exists
    import os
    if os.path.exists('media-bridge.png'):
        datas.append(('media-bridge.png', '.'))
    else:
        print("Warning: media-bridge.png not found, building without icon")
    
    hiddenimports.extend(['dbus', 'gi'])
    
    # Collect necessary files for Linux packages
    for pkg in ['plyer']:
        tmp_ret = collect_all(pkg)
        if tmp_ret:
            datas += tmp_ret[0]
            binaries += tmp_ret[1]
            hiddenimports += tmp_ret[2]
    
    # Add specific platform backend for plyer
    hiddenimports.append('plyer.platforms.linux.notification')
else:
    # Fallback for other platforms
    print(f"Warning: Unsupported platform {platform.system()}, building with basic functionality")
    tmp_ret = collect_all('plyer')
    if tmp_ret:
        datas += tmp_ret[0]
        binaries += tmp_ret[1]
        hiddenimports += tmp_ret[2]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Media-Bridge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['media-bridge.ico'] if IS_WINDOWS else None,
)
