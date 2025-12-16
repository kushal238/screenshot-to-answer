#!/usr/bin/env python3
"""Quick test to manually process a screenshot"""
import sys
sys.path.insert(0, '/Users/kushalagarwal/screenshot-to-answer')

from pathlib import Path
from watcher import process_screenshot

screenshot_path = Path("/Users/kushalagarwal/Desktop/screenshots/Screenshot 2025-12-15 at 5.36.41 AM.png")

if screenshot_path.exists():
    print(f"Processing: {screenshot_path}")
    process_screenshot(screenshot_path)
    print("Done!")
else:
    print(f"File not found: {screenshot_path}")

