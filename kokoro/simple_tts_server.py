#!/usr/bin/env python3
"""
Kokoro TTS Server using KPipeline for Japanese Flashcard Study Interface
"""

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from kokoro import KPipeline
import soundfile as sf
import io
import tempfile
import os
import sys

app = Flask(__name__)
CORS(app)  # Enable CORS for web requests

# Global TTS pipeline
pipeline = None
japanese_voices = ['jf_alpha', 'jf_gong', 'jm_kumo']  # Available Japanese voices

def initialize_tts():
    """Initialize Kokoro TTS pipeline with Japanese support"""
    global pipeline

    try:
        print("🎵 Initializing Kokoro TTS for Japanese...")

        # Initialize Japanese pipeline
        pipeline = KPipeline(lang_code='j')  # Japanese language code

        print("✅ Kokoro TTS pipeline initialized for Japanese")
        print(f"🎯 Available Japanese voices: {japanese_voices}")

        return True

    except Exception as e:
        print(f"❌ Failed to initialize Kokoro TTS: {e}")
        print("💡 Make sure you have installed: pip install kokoro misaki[ja] soundfile")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'tts_available': pipeline is not None,
        'voices_count': len(japanese_voices),
        'japanese_voices': len(japanese_voices),
        'lang_code': 'j'  # Japanese
    })

@app.route('/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech using Kokoro KPipeline"""
    if not pipeline:
        return jsonify({'error': 'TTS pipeline not available'}), 503

    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        voice = data.get('voice', 'jf_alpha')  # Default Japanese female voice

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        if voice not in japanese_voices:
            voice = 'jf_alpha'  # Fallback to default

        print(f"🎵 Generating TTS for: '{text}' using voice: {voice}")

        # Generate speech using Kokoro pipeline
        generator = pipeline(
            text,
            voice=voice,
            speed=1,
            split_pattern=r'\n+'
        )

        # Get the first (and typically only) audio segment
        audio_data = None
        for i, (gs, ps, audio) in enumerate(generator):
            audio_data = audio
            break  # We only need the first segment

        if audio_data is None:
            return jsonify({'error': 'Failed to generate audio'}), 500

        # Save to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_filename = temp_file.name

        # Save audio using soundfile
        sf.write(temp_filename, audio_data, 24000)  # Kokoro uses 24kHz sample rate

        # Verify file was created and has content
        if not os.path.exists(temp_filename) or os.path.getsize(temp_filename) == 0:
            return jsonify({'error': 'Failed to save audio file'}), 500

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
        print(f"❌ TTS Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/voices', methods=['GET'])
def list_voices():
    """List available Japanese voices"""
    if not pipeline:
        return jsonify({'error': 'TTS pipeline not available'}), 503

    voice_list = []

    for voice in japanese_voices:
        # Extract gender and other info from voice name
        gender = 'Female' if voice.startswith('jf') else 'Male' if voice.startswith('jm') else 'Unknown'
        name = voice.replace('jf_', 'Japanese Female ').replace('jm_', 'Japanese Male ').replace('j', 'Japanese ')

        voice_list.append({
            'id': voice,
            'name': name,
            'languages': ['ja'],  # Japanese
            'gender': gender,
            'age': 'Adult'
        })

    return jsonify({
        'voices': voice_list,
        'japanese_voices': voice_list  # All voices are Japanese
    })

@app.route('/set-voice', methods=['POST'])
def set_voice():
    """Set the TTS voice (Kokoro handles voice per request)"""
    if not pipeline:
        return jsonify({'error': 'TTS pipeline not available'}), 503

    try:
        data = request.get_json()
        voice_id = data.get('voice_id')

        if not voice_id:
            return jsonify({'error': 'No voice_id provided'}), 400

        if voice_id not in japanese_voices:
            return jsonify({'error': f'Voice {voice_id} not available'}), 404

        print(f"✅ Voice set to: {voice_id}")

        return jsonify({
            'success': True,
            'voice': {
                'id': voice_id,
                'name': voice_id.replace('jf_', 'Japanese Female ').replace('jm_', 'Japanese Male ').replace('j', 'Japanese '),
                'languages': ['ja']
            }
        })

    except Exception as e:
        print(f"❌ Error setting voice: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🎵 Starting Kokoro TTS Server...")
    print("📋 Features:")
    print("   - Kokoro KPipeline-based TTS")
    print("   - Native Japanese language support")
    print("   - High-quality Japanese voices")
    print("   - Web API interface")
    print()

    if initialize_tts():
        print("🚀 Starting server on http://localhost:8001")
        print("📡 Endpoints:")
        print("   GET  /health     - Health check")
        print("   GET  /voices     - List available Japanese voices")
        print("   POST /set-voice  - Change TTS voice")
        print("   POST /tts        - Generate speech from text")
        print()
        print("🎯 Japanese voices available: jf_alpha, jf_gong, jm_kumo")
        print("🎯 Language code: 'j' (Japanese)")
    else:
        print("❌ TTS initialization failed")
        print("💡 Make sure you have installed: pip install kokoro misaki[ja] soundfile")
        print("💡 And that you have the Kokoro model files")
        sys.exit(1)

    app.run(host='127.0.0.1', port=8001, debug=True)
