#!/usr/bin/env python3
"""
Setup script for Kokoro TTS
Downloads model and voices for Japanese TTS
"""

import os
import urllib.request
import zipfile
import sys

def download_file(url, filename):
    """Download a file with progress"""
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"✅ Downloaded {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        return False

def setup_kokoro():
    """Download Kokoro model and voices"""
    print("Setting up Kokoro TTS for Japanese flashcards...")

    # Create directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('voices', exist_ok=True)

    success = True

    # Download model
    model_url = "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v0_19.pth"
    if not download_file(model_url, "models/kokoro-v0_19.pth"):
        success = False

    # Download voices
    voices_url = "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices.zip"
    if download_file(voices_url, "voices_temp.zip"):
        try:
            # Extract voices
            print("Extracting voices...")
            with zipfile.ZipFile("voices_temp.zip", 'r') as zip_ref:
                zip_ref.extractall(".")

            # Clean up
            os.remove("voices_temp.zip")
            print("✅ Voices extracted")
        except Exception as e:
            print(f"❌ Failed to extract voices: {e}")
            success = False
    else:
        success = False

    if success:
        print("✅ Kokoro setup complete!")
        print("📁 Model: models/kokoro-v0_19.pth")
        print("📁 Voices: voices/ directory")
        print("\n🚀 To start the TTS server:")
        print("   python simple_tts_server.py")
    else:
        print("❌ Setup failed - some files may not have downloaded")
        print("\nManual setup:")
        print("1. Download model: https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v0_19.pth")
        print("2. Download voices: https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices.zip")
        print("3. Extract voices.zip to voices/ directory")
        print("4. Place model in models/ directory")

if __name__ == "__main__":
    setup_kokoro()
