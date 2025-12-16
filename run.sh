#!/bin/bash
# Quick start script for Screenshot to Answer

echo "🚀 Screenshot to Answer Agent"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import google.generativeai" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

# Check if config exists
if [ ! -f "config.json" ]; then
    echo "⚠️  config.json not found. Running watcher to create it..."
    echo ""
    python3 watcher.py
    exit 1
fi

# Check if API key is set
if grep -q "YOUR_GEMINI_API_KEY_HERE" config.json 2>/dev/null; then
    echo "⚠️  Please add your Gemini API key to config.json"
    echo "Get your API key from: https://aistudio.google.com/app/apikey"
    echo ""
    echo "Then edit config.json and replace YOUR_GEMINI_API_KEY_HERE with your actual API key"
    exit 1
fi

# Run the watcher
echo "✅ Starting watcher..."
echo ""
python3 watcher.py
