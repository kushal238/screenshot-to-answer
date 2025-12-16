#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime
import google.generativeai as genai

# Load config
with open('/Users/kushalagarwal/screenshot-to-answer/config.json') as f:
    config = json.load(f)

print(f"Using model: {config['model']}")
print(f"API Key: {config['api_key'][:20]}...")

# Initialize Gemini
genai.configure(api_key=config["api_key"])
model = genai.GenerativeModel(config["model"])

# Find screenshot
screenshot_path = Path('/Users/kushalagarwal/Desktop/screenshots/Screenshot 2025-12-15 at 5.36.41 AM.png')

print(f"\nProcessing: {screenshot_path.name}")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Read and process
try:
    with open(screenshot_path, 'rb') as f:
        image_data = f.read()
    
    print(f"Image size: {len(image_data)} bytes")
    print("Sending to Gemini...")
    
    response = model.generate_content([
        config["prompt"],
        {"mime_type": "image/png", "data": image_data}
    ])
    
    answer = response.text.strip()
    print(f"\n{'='*60}")
    print("ANSWER:")
    print(f"{'='*60}")
    print(answer)
    print(f"{'='*60}\n")
    
    # Append to answers
    answers_file = Path('/Users/kushalagarwal/screenshot-to-answer/answers.md')
    with open(answers_file, 'a', encoding='utf-8') as f:
        f.write(f"\n## Screenshot: {screenshot_path.name}\n")
        f.write(f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"{answer}\n\n")
        f.write(f"---\n")
    
    print(f"✓ Appended to answers.md")
    
except Exception as e:
    print(f"✗ Error: {e}")

