@echo off
setlocal

echo === Media Bridge Build Script ===
echo Platform: Windows
echo.

echo Checking Python version...
python --version

echo.
echo Installing dependencies...
python -m pip install --upgrade pip
pip install pyinstaller
pip install -r requirements.txt

echo.
echo Generating icons...
if exist "GMC-Bridge.png" (
    python scripts\create_icons.py GMC-Bridge.png
) else if exist "media-bridge.png" (
    python scripts\create_icons.py media-bridge.png
) else (
    echo Warning: No PNG file found
    echo Please provide a PNG icon file in the project root
    echo The script will resize it to 256x256 and generate Windows .ico
)

echo.
echo Building with PyInstaller...
python -m PyInstaller --noconfirm media-bridge.spec

echo.
echo Renaming executable...
move dist\Media-Bridge.exe dist\Media-Bridge-windows.exe

echo.
echo === Build Complete ===
echo Output: dist\Media-Bridge-windows.exe
pause
