#!/usr/bin/env python3
"""
Screenshot Question Answering Agent
Watches for new screenshots, extracts questions, answers them using Gemini,
and appends to a markdown file.
"""

import os
import time
import json
import shutil
import base64
from pathlib import Path
from datetime import datetime
from queue import Queue
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import mimetypes

# Try importing both AI libraries
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Configuration
SCREENSHOTS_DIR = Path.home() / "Desktop"  # Default Mac screenshot location
PROCESSED_DIR = Path(__file__).parent / "_processed"
ANSWERS_FILE = Path(__file__).parent / "answers.md"
STATUS_FILE = Path(__file__).parent / "status.json"
CONFIG_FILE = Path(__file__).parent / "config.json"

# Load or create config
def load_config():
    """Load configuration from config.json or create default"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        default_config = {
            "api_key": "",
            "provider": "openai",  # "openai" or "gemini"
            "screenshots_dir": str(SCREENSHOTS_DIR),
            "model": "gpt-4o-mini",
            "enable_notifications": True,
            "prompt": "Analyze this screenshot. If there is a question in the image, extract it and provide a clear, concise answer. If there are multiple questions, answer all of them. Format your response as:\n\nQuestion: [extracted question]\nAnswer: [your answer]\n\nIf there's no question in the image, just describe what you see."
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"Created config.json - Please add your API key!")
        return default_config

config = load_config()

# Handle prompt as array or string
if isinstance(config.get("prompt"), list):
    config["prompt"] = "\n".join(config["prompt"])

# Initialize AI client based on provider
if not config.get("api_key"):
    print("ERROR: Please add your API key to config.json")
    exit(1)

provider = config.get("provider", "openai").lower()
ai_client = None

if provider == "openai":
    if not OPENAI_AVAILABLE:
        print("ERROR: OpenAI library not installed. Run: pip install openai")
        exit(1)
    ai_client = OpenAI(api_key=config["api_key"])
    print(f"Using OpenAI with model: {config['model']}")
elif provider == "anthropic":
    if not ANTHROPIC_AVAILABLE:
        print("ERROR: Anthropic library not installed. Run: pip install anthropic")
        exit(1)
    ai_client = Anthropic(api_key=config["api_key"])
    print(f"Using Anthropic with model: {config['model']}")
elif provider == "gemini":
    if not GEMINI_AVAILABLE:
        print("ERROR: Gemini library not installed. Run: pip install google-generativeai")
        exit(1)
    genai.configure(api_key=config["api_key"])
    ai_client = genai.GenerativeModel(config["model"])
    print(f"Using Gemini with model: {config['model']}")
else:
    print(f"ERROR: Unknown provider '{provider}'. Use 'openai', 'anthropic', or 'gemini'")
    exit(1)

# Create directories
SCREENSHOTS_DIR = Path(config["screenshots_dir"])
PROCESSED_DIR.mkdir(exist_ok=True)

# Processing queue
screenshot_queue = Queue()

def send_notification(title, message):
    """Send macOS notification"""
    if config.get("enable_notifications", True):
        os.system(f'''osascript -e 'display notification "{message}" with title "{title}"' ''')

def is_image_file(filepath):
    """Check if file is an image"""
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type and mime_type.startswith('image')

def update_status(filename, status, details=""):
    """Update status.json for the viewer"""
    try:
        data = {
            "filename": filename,
            "status": status,
            "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "details": details
        }
        with open(STATUS_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass  # Ignore errors in status update

def process_screenshot(screenshot_path):
    """Process a single screenshot with AI"""
    try:
        print(f"\n{'='*60}")
        print(f"📸 DETECTED: {screenshot_path.name}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        update_status(screenshot_path.name, "Processing", "Reading file...")
        
        # Read the image
        print(f"📖 Reading file...")
        with open(screenshot_path, 'rb') as f:
            image_data = f.read()
        size_kb = len(image_data)/1024
        print(f"   Size: {size_kb:.1f} KB")
        
        update_status(screenshot_path.name, "Processing", f"Size: {size_kb:.1f} KB - Sending to AI...")
        
        # Send to AI based on provider
        provider = config.get("provider", "openai").lower()
        print(f"🚀 Sending to {provider.upper()} ({config['model']})...")
        
        if provider == "openai":
            # Encode image to base64
            print(f"   Encoding image...")
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            print(f"   Waiting for API response...")
            response = ai_client.chat.completions.create(
                model=config["model"],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": config["prompt"]},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            answer = response.choices[0].message.content.strip()
            
        elif provider == "anthropic":
            # Encode image to base64
            print(f"   Encoding image...")
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            print(f"   Waiting for API response...")
            response = ai_client.messages.create(
                model=config["model"],
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": base64_image
                                }
                            },
                            {
                                "type": "text",
                                "text": config["prompt"]
                            }
                        ]
                    }
                ]
            )
            answer = response.content[0].text.strip()
            
        elif provider == "gemini":
            print(f"   Waiting for API response...")
            response = ai_client.generate_content([
                config["prompt"],
                {"mime_type": "image/png", "data": image_data}
            ])
            answer = response.text.strip()
        
        print(f"✨ Received answer ({len(answer)} chars)")
        
        # Prepend to answers file (add at top, below header)
        print(f"📝 Updating answers.md...")
        if ANSWERS_FILE.exists():
            with open(ANSWERS_FILE, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        else:
            existing_content = "# Screenshot Answers\n\nStarted: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n---\n"
        
        # Find the position after the first "---" (end of header)
        header_end = existing_content.find("---\n")
        if header_end != -1:
            header = existing_content[:header_end + 4]  # Include the "---\n"
            rest = existing_content[header_end + 4:]
        else:
            header = existing_content
            rest = ""
        
        # Build new content with latest answer at top
        new_entry = f"\n## Screenshot: {screenshot_path.name}\n"
        new_entry += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        new_entry += f"{answer}\n\n"
        new_entry += f"---\n"
        
        new_content = header + new_entry + rest
        
        with open(ANSWERS_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Added to top of {ANSWERS_FILE.name}")
        
        # Move to processed folder
        print(f"📦 Archiving screenshot...")
        processed_path = PROCESSED_DIR / screenshot_path.name
        
        # Handle duplicate names
        counter = 1
        while processed_path.exists():
            stem = screenshot_path.stem
            suffix = screenshot_path.suffix
            processed_path = PROCESSED_DIR / f"{stem}_{counter}{suffix}"
            counter += 1
        
        shutil.move(str(screenshot_path), str(processed_path))
        print(f"✅ Moved to {processed_path.relative_to(Path(__file__).parent)}")
        
        # Send notification
        send_notification("Screenshot Answered", f"Answer added to {ANSWERS_FILE.name}")
        
        update_status(screenshot_path.name, "Completed", "Answer added to viewer")
        print(f"🎉 DONE! Ready for next screenshot.\n")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {screenshot_path.name}: {e}")
        send_notification("Error", f"Failed to process screenshot: {str(e)[:50]}")
        update_status(screenshot_path.name, "Error", str(e))
        return False

def queue_worker():
    """Worker thread that processes screenshots from queue"""
    while True:
        screenshot_path = screenshot_queue.get()
        if screenshot_path is None:  # Poison pill to stop worker
            break
        
        process_screenshot(screenshot_path)
        screenshot_queue.task_done()

class ScreenshotHandler(FileSystemEventHandler):
    """Handles new screenshot files"""
    
    def __init__(self):
        self.processing = set()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        filepath = Path(event.src_path)
        
        print(f"[DEBUG] File detected: {filepath.name}")
        
        # Only process image files
        if not is_image_file(filepath):
            print(f"[DEBUG] Not an image file, skipping")
            return
        
        # Avoid processing files we've already seen
        if filepath in self.processing:
            print(f"[DEBUG] Already processing, skipping")
            return
        
        # Check if it's a screenshot (Mac screenshots usually start with "Screen Shot" or "Screenshot")
        if not (filepath.name.startswith("Screen Shot") or 
                filepath.name.startswith("Screenshot") or
                filepath.name.lower().startswith("screen")):
            print(f"[DEBUG] Doesn't match screenshot name pattern, skipping: {filepath.name}")
            return
        
        # Wait a bit to ensure file is fully written
        time.sleep(0.5)
        
        if filepath.exists() and filepath.stat().st_size > 0:
            print(f"\n📸 New screenshot detected: {filepath.name}")
            self.processing.add(filepath)
            screenshot_queue.put(filepath)

def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         Screenshot Question Answering Agent                   ║
║                   Powered by Gemini                           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    print(f"📁 Watching: {SCREENSHOTS_DIR}")
    print(f"📝 Answers: {ANSWERS_FILE}")
    print(f"📦 Archive: {PROCESSED_DIR}")
    print(f"🤖 Model: {config['model']}")
    print(f"\n{'='*60}")
    print("Ready! Take screenshots and they'll be processed automatically.")
    print(f"{'='*60}\n")
    
    # Initialize answers file if it doesn't exist
    if not ANSWERS_FILE.exists():
        with open(ANSWERS_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# Screenshot Answers\n\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"---\n\n")
    
    # Start worker thread
    worker = Thread(target=queue_worker, daemon=True)
    worker.start()
    
    # Start watching for new screenshots
    event_handler = ScreenshotHandler()
    observer = Observer()
    observer.schedule(event_handler, str(SCREENSHOTS_DIR), recursive=False)
    observer.start()
    print(f"[DEBUG] Observer started, watching {SCREENSHOTS_DIR}")
    print(f"[DEBUG] Observer is alive: {observer.is_alive()}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        observer.stop()
        screenshot_queue.put(None)  # Stop worker
        
    observer.join()
    worker.join()
    print("✓ Stopped")

if __name__ == "__main__":
    main()

