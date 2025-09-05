#!/usr/bin/env python3
"""
Kokoro TTS Server for Japanese Flashcard Study Interface
"""

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import io
import os
import sys
import tempfile
import numpy as np

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from kokoro import generate
    from models import build_model
    import torch
    KOKORO_AVAILABLE = True
except ImportError:
    print("Warning: Kokoro not installed. Run: pip install kokoro")
    KOKORO_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable CORS for web requests

# Global variables for model and voices
model = None
voices = {}

def initialize_kokoro():
    """Initialize Kokoro TTS model and voices"""
    global model, voices

    if not KOKORO_AVAILABLE:
        print("Kokoro not available - TTS will not work")
        return False

    try:
        print("Initializing Kokoro TTS...")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {device}")

        # Load model
        model = build_model('kokoro-v0_19.pth', device)

        # Load voices
        voice_files = ['af', 'af_bella', 'af_nicole', 'af_sarah', 'af_sky',
                      'am_adam', 'am_michael', 'am_fenn', 'am_liam',
                      'bf_emma', 'bf_isabella', 'bm_george', 'bm_lewis',
                      'ef_dora', 'em_alex', 'em_santa',
                      'ff_siwis', 'fm_hartford', 'fm_nolan',
                      'hf_alpha', 'hf_beta', 'hm_omega', 'hm_psi',
                      'if_sara', 'im_nicola', 'jf_alpha', 'jf_gong', 'jm_kumo',
                      'pf_dora', 'pm_alex', 'pm_santa', 'zf_xiaobei', 'zf_xiaoni',
                      'zf_xiaoxiao', 'zf_xiaoyi', 'zm_yunjian', 'zm_yunxi',
                      'zm_yunxia', 'zm_yunyang']

        for voice_file in voice_files:
            try:
                voice_path = f'voices/{voice_file}.pt'
                if os.path.exists(voice_path):
                    voices[voice_file] = torch.load(voice_path, map_location=device, weights_only=True)
                    print(f"Loaded voice: {voice_file}")
            except Exception as e:
                print(f"Failed to load voice {voice_file}: {e}")

        print(f"Successfully loaded {len(voices)} voices")
        return True

    except Exception as e:
        print(f"Failed to initialize Kokoro: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'kokoro_available': KOKORO_AVAILABLE,
        'voices_loaded': len(voices) if voices else 0
    })

@app.route('/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech using Kokoro"""
    if not KOKORO_AVAILABLE or model is None:
        return jsonify({'error': 'Kokoro TTS not available'}), 503

    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        voice = data.get('voice', 'jf_alpha')  # Default Japanese female voice

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        if voice not in voices:
            return jsonify({'error': f'Voice {voice} not available'}), 400

        print(f"Generating TTS for: '{text}' with voice: {voice}")

        # Generate audio using Kokoro
        audio, _ = generate(model, text, voices[voice], lang='ja')

        # Convert to WAV format
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_filename = temp_file.name

        # Save as WAV
        import scipy.io.wavfile
        scipy.io.wavfile.write(temp_filename, 24000, audio)

        # Send the file
        response = send_file(
            temp_filename,
            mimetype='audio/wav',
            as_attachment=True,
            download_name='tts_output.wav'
        )

        # Clean up temp file after sending
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(temp_filename)
            except:
                pass

        return response

    except Exception as e:
        print(f"TTS Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/voices', methods=['GET'])
def list_voices():
    """List available voices"""
    return jsonify({
        'voices': list(voices.keys()),
        'japanese_voices': [v for v in voices.keys() if v.startswith(('j', 'z'))]
    })

if __name__ == '__main__':
    print("Starting Kokoro TTS Server...")

    if initialize_kokoro():
        print("✅ Kokoro TTS initialized successfully")
        print(f"📊 Loaded {len(voices)} voices")
        print("🎯 Japanese voices available:", [v for v in voices.keys() if v.startswith(('j', 'z'))])
    else:
        print("❌ Kokoro TTS initialization failed")

    print("🚀 Starting server on http://localhost:8001")
    print("📡 Endpoints:")
    print("   GET  /health     - Health check")
    print("   GET  /voices     - List available voices")
    print("   POST /tts        - Generate speech from text")

    app.run(host='127.0.0.1', port=8001, debug=True)
