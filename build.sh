#!/bin/bash
# Build script for Media Bridge
# This script builds the application for the current platform

set -e

echo "=== Media Bridge Build Script ==="
echo "Platform: $(uname -s)"
echo ""

# Check Python version
echo "Checking Python version..."
python --version || python3 --version

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install pyinstaller
pip install -r requirements.txt

# Install platform-specific dependencies for Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing Linux system dependencies..."
    sudo apt-get update
    sudo apt-get install -y libdbus-1-dev libgirepository1.0-dev gir1.2-gtk-3.0
fi

# Generate icons
echo "Generating icons..."
if ls *.png 1> /dev/null 2>&1; then
    # Use the first PNG file found
    png_file=$(ls *.png | head -n 1)
    python scripts/create_icons.py "$png_file"
else
    echo "Warning: No PNG file found"
    echo "Please provide a PNG icon file in the project root"
    echo "The script will resize it to 256x256 and generate Windows .ico"
fi

# Build with PyInstaller
echo "Building with PyInstaller..."
pyinstaller --noconfirm media-bridge.spec

# Rename executable
echo "Renaming executable..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    mv dist/Media-Bridge dist/Media-Bridge-linux
    chmod +x dist/Media-Bridge-linux
    echo "Build complete: dist/Media-Bridge-linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    mv dist/Media-Bridge.exe dist/Media-Bridge-windows.exe
    echo "Build complete: dist/Media-Bridge-windows.exe"
else
    echo "Build complete: dist/Media-Bridge"
fi

echo ""
echo "=== Build Complete ==="
