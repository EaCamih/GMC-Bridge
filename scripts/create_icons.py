#!/usr/bin/env python3
"""
Create icon files for Media Bridge
This script converts an existing PNG to ICO for Windows
"""

from PIL import Image
import os
import sys

def create_icons():
    # Get the project root directory (parent of scripts)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Source PNG file - check if provided as argument or use default
    if len(sys.argv) > 1:
        png_path = sys.argv[1]
        if not os.path.isabs(png_path):
            png_path = os.path.join(project_root, png_path)
    else:
        png_path = os.path.join(project_root, 'media-bridge.png')
    
    if not os.path.exists(png_path):
        print(f"Error: {png_path} not found.")
        print(f"Please provide a PNG file as an argument:")
        print(f"  python scripts/create_icons.py your-icon.png")
        print(f"Or place a media-bridge.png file in the project root.")
        return False
    
    # Load the PNG
    try:
        img = Image.open(png_path)
        print(f"Loaded {png_path} ({img.size})")
    except Exception as e:
        print(f"Error loading PNG: {e}")
        return False
    
    # Resize to 256x256 if needed (standard size for both Linux and Windows)
    target_size = (256, 256)
    if img.size != target_size:
        print(f"Resizing from {img.size} to {target_size}")
        img = img.resize(target_size, Image.Resampling.LANCZOS)
    
    # Save the resized PNG (this is the source for both platforms)
    png_output_path = os.path.join(project_root, 'media-bridge.png')
    try:
        img.save(png_output_path, 'PNG')
        print(f"Saved {png_output_path} ({target_size})")
    except Exception as e:
        print(f"Error saving PNG: {e}")
        return False
    
    # Convert to ICO with multiple sizes for Windows
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_path = os.path.join(project_root, 'media-bridge.ico')
    
    try:
        img.save(ico_path, 'ICO', sizes=icon_sizes)
        print(f"Created {ico_path} with sizes: {icon_sizes}")
        return True
    except Exception as e:
        print(f"Error creating ICO: {e}")
        return False

if __name__ == '__main__':
    success = create_icons()
    if success:
        print("Icon creation completed successfully!")
        print("Note: media-bridge.png is now 256x256 (used for both Linux and Windows)")
    else:
        print("Icon creation failed.")
        sys.exit(1)
