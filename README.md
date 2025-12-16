# Screenshot to Answer - AI Agent

Automatically extracts questions from screenshots and answers them using Google Gemini, appending results to a markdown file in real-time.

## 🎯 What It Does

1. **Watches** your Desktop (or custom folder) for new screenshots
2. **Extracts** questions from the screenshot using Gemini Vision
3. **Answers** the questions using Gemini
4. **Appends** answers to `answers.md` in real-time
5. **Archives** processed screenshots to `_processed/` folder
6. **Notifies** you (optional) when each answer is ready


## 🚀 Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### 3. Configure

On first run, a `config.json` will be created. Edit it to add your API key:

```json
{
  "api_key": "YOUR_GEMINI_API_KEY_HERE",
  "screenshots_dir": "/Users/yourname/Desktop",
  "model": "gemini-2.0-flash-exp",
  "enable_notifications": true,
  "prompt": "Analyze this screenshot..."
}
```

### 4. Run

```bash
python watcher.py
```

## 📖 Usage

### Watch Live Answers

In another terminal, watch the answers file update in real-time:

```bash
tail -f answers.md
```

Or open `answers.md` in your favorite editor (it will auto-refresh in most modern editors).

### Take Screenshots

Just take screenshots as normal:
- **Mac**: `Cmd + Shift + 3` (full screen) or `Cmd + Shift + 4` (selection)

The agent will automatically:
1. Detect the new screenshot
2. Process it with Gemini
3. Append the answer to `answers.md`
4. Move the screenshot to `_processed/`

### Process Multiple Screenshots

Take all 35 screenshots back-to-back. They'll be queued and processed one at a time (preventing overlapping writes and out-of-order answers).

## 📁 Files

- `watcher.py` - Main script
- `config.json` - Configuration (API key, paths, etc.)
- `answers.md` - Your answers appear here
- `_processed/` - Archived screenshots

## ⚙️ Configuration Options

Edit `config.json` to customize:

| Option | Description | Default |
|--------|-------------|---------|
| `api_key` | Your Gemini API key | (required) |
| `screenshots_dir` | Where to watch for screenshots | `~/Desktop` |
| `model` | Gemini model to use | `gemini-2.5-pro` |
| `enable_notifications` | Show macOS notifications | `true` |
| `prompt` | Custom prompt for Gemini | See config.json |

### Available Models

- `gemini-2.5-pro` - Most capable, best for complex questions (recommended)
- `gemini-2.0-flash-exp` - Fast, great for Q&A
- `gemini-1.5-flash` - Fast, slightly older
- `gemini-1.5-pro` - Capable, slower

## 🔧 Troubleshooting

### "Please add your Gemini API key"

Edit `config.json` and add your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### Screenshots Not Being Detected

1. Check that `screenshots_dir` in `config.json` points to where your Mac saves screenshots
2. Default Mac location is Desktop (`~/Desktop`)
3. To find your screenshot location: Take a screenshot and check where it saved

### Change Screenshot Save Location

You can change where Mac saves screenshots:

```bash
# Save to Desktop (default)
defaults write com.apple.screencapture location ~/Desktop
killall SystemUIServer

# Or save to a custom folder
mkdir -p ~/Screenshots
defaults write com.apple.screencapture location ~/Screenshots
killall SystemUIServer
```

Then update `screenshots_dir` in `config.json` to match.

## 💡 Tips

1. **Watch in real-time**: Open `answers.md` in VS Code or any editor with auto-refresh
2. **Use `tail -f`**: Run `tail -f answers.md` in a terminal to see answers stream in
3. **Notifications**: Enable notifications so you don't even need to watch the file
4. **Custom prompts**: Edit the `prompt` in `config.json` to change how Gemini responds
5. **Batch processing**: Take all your screenshots first, then start the watcher

## 🎬 Quick Start Example

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure (add API key to config.json)
python watcher.py  # Creates config.json
nano config.json   # Add your API key

# 3. Start watcher
python watcher.py

# 4. In another terminal, watch live answers
tail -f answers.md

# 5. Take screenshots!
# They'll be processed automatically
```

## 📝 Example Output

Your `answers.md` will look like:

```markdown
# Screenshot Answers

Started: 2025-12-15 10:30:00

---

## Screenshot: Screen Shot 2025-12-15 at 10.31.20.png
**Time:** 2025-12-15 10:31:25

Question: What is the capital of France?
Answer: The capital of France is Paris.

---

## Screenshot: Screen Shot 2025-12-15 at 10.31.45.png
**Time:** 2025-12-15 10:31:50

Question: Explain quantum entanglement
Answer: Quantum entanglement is a physical phenomenon where pairs of particles...

---
```

## 🚦 Architecture

- **Single-threaded queue**: Processes one screenshot at a time (prevents race conditions)
- **Archive system**: Moves processed screenshots to `_processed/` (prevents re-processing)
- **Append-only**: Safe for watching with `tail -f` or live editors
- **Error handling**: Continues processing even if one screenshot fails

## 📄 License

MIT - Do whatever you want with it!

## 🤝 Contributing

Feel free to open issues or PRs if you want to improve this!

