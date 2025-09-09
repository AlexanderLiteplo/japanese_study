# Japanese Flashcards Study Interface

## 🚀 Quick Start

1. **Install TTS dependencies (optional for audio):**
```bash
cd kokoro
source tts_env/bin/activate  # Activate the virtual environment
pip install -r requirements_simple_tts.txt
```

2. **Start the web server:**
```bash
cd /Users/alexander/Documents/Code/japanese_study
python3 -m http.server 8000
```

3. **Start TTS server (optional, in another terminal):**
```bash
cd kokoro
source tts_env/bin/activate
python simple_tts_server.py
```

4. **Open in browser:**
   - Go to: `http://127.0.0.1:8000/study.html`
   - **Do NOT** open `study.html` directly in your browser (file://)

## 📱 How to Study

1. **Cards show English first** - Think about the Japanese translation
2. **Click the card** to flip and **automatically hear the Japanese word!** 🔊
3. **Click the 🔊 buttons** to hear pronunciation again:
   - Word button: Pronounces just the vocabulary word
   - Sentence button: Pronounces the full example sentence
4. **Rate your recall** using the colored buttons:
   - 🔴 **AGAIN** - Complete blackout, review immediately
   - 🟠 **HARD** - Difficult, some memory
   - 🟢 **GOOD** - Recalled with effort
   - 🟣 **EASY** - Perfect recall
5. **Click the 📊 button** (right side) to view your study dashboard with progress stats!

## 💾 Progress Saving

- Progress is **automatically saved** after each review to browser localStorage
- Click **"Export Progress"** to download your progress as a JSON file
- **To persist progress permanently**: Save the downloaded file as `flashcard_generation/flashcard_generation/flashcard_progress.json`
- Your progress in localStorage persists between browser sessions, but to save it permanently you need to export and replace the JSON file

## 📊 Study Dashboard

Click the **📊 button** on the right side to open your study dashboard! It shows:

- **Total Studied** - All cards you've ever studied
- **Studied Today** - Cards studied in the last 24 hours
- **Studied This Week** - Cards studied in the last 7 days
- **Current Streak** - Consecutive days with at least one study
- **Accuracy Rate** - Your overall correct/incorrect ratio with progress bar
- **Avg Difficulty** - Average ease factor of studied cards

## 🎯 Features

- ✅ **Spaced Repetition** - Anki SM-2 algorithm
- ✅ **Smart Scheduling** - Cards appear when due
- ✅ **Progress Tracking** - Statistics and streaks
- ✅ **Card Flipping** - English → Japanese reveal with **automatic audio!** 🔊
- ✅ **Text-to-Speech** - Kokoro TTS for pronunciation
- ✅ **Study Dashboard** - Progress stats and analytics 📊
- ✅ **Mobile Friendly** - Works on all devices
- ✅ **No Installation** - Just open in browser

## 🔧 Troubleshooting

### Progress Not Saving?
- **Open browser developer tools** (F12) and check the Console tab
- Look for messages like "✅ Progress saved to localStorage successfully"
- Use the **debug buttons** below the stats to test saving/loading:
  - **Debug Save**: Manually trigger save and check console
  - **Debug Load**: Manually trigger load and check console
  - **Clear Storage**: Reset localStorage and reload page
- **Export Progress** to download your current progress as a file

### CORS Error?
If you see "CORS policy" errors:
- **Don't open the HTML file directly**
- **Use the web server URL**: `http://127.0.0.1:8000/study.html`

### TTS Not Working?
- Make sure the TTS server is running: `cd kokoro && source tts_env/bin/activate && python simple_tts_server.py`
- Check that voices are loaded at: `http://localhost:8001/health`
- ✅ **Kokoro TTS is now fully functional** with Japanese voices (jf_alpha, jf_gong, jm_kumo)
- Test audio generation: `curl -X POST http://localhost:8001/tts -H "Content-Type: application/json" -d '{"text":"こんにちは"}'`

### No Cards Loading?
- Check that the JSON files exist:
  - `flashcard_generation/flashcard_generation/flashcards_with_ids.json`
  - `flashcard_generation/flashcard_generation/flashcard_progress.json`

### Server Not Starting?
- Make sure you're in the correct directory
- Try: `python3 -m http.server 8000 --bind 127.0.0.1`

## 📊 Statistics

The header shows:
- **Due**: Cards ready for review
- **New**: Cards never studied
- **Studied**: Total cards you've practiced

Happy studying! 🎌
