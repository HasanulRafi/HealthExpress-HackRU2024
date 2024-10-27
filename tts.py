from dotenv import load_dotenv
import os
import requests
import firebase_admin
from firebase_admin import credentials, storage
from conversation_logic import generate_openai_response

# Load environment variables from .env file
load_dotenv()

# Initialize Firebase app with credentials

# Language voice mapping (same as before)
language_voice_map = {
    "en": {"voice_id": "mCQMfsqGDT6IDkEKR20a", "language": "English"},
    "hi": {"voice_id": "mCQMfsqGDT6IDkEKR20a", "language": "Hindi"},
    "ta": {"voice_id": "mCQMfsqGDT6IDkEKR20a", "language": "Tamil"},
}


def translate_text(text, target_language):
    """
    Translates the given text to the target language using OpenAI's GPT model.
    """
    prompt = (
        f"Translate the following text to {target_language}:\n\n{text}\n\nTranslation:"
    )
    translated_text = generate_openai_response(prompt)
    return translated_text.strip()


def text_to_speech(text, language="en"):
    print(f"Starting text_to_speech function with text: {text[:50]}... and language: {language}")

    if language != "en":
        print(f"Translating text to {language}")
        text = translate_text(text, language_voice_map.get(language)["language"])
        print(f"Translated text: {text[:50]}...")

    CHUNK_SIZE = 1024
    voice_info = language_voice_map.get(language)
    voice_id = voice_info["voice_id"] if voice_info else None
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice_id
    print(f"Using voice ID: {voice_id}")

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": os.getenv("ELEVEN_API_KEY"),
    }
    print(f"API Key: {os.getenv('ELEVEN_API_KEY')[:5]}...")  # Print first 5 chars of API key

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.7, "similarity_boost": 0.8},
    }

    print("Sending request to Eleven Labs API")
    response = requests.post(url, json=data, headers=headers)
    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {response.headers}")

    if response.status_code != 200 or response.headers.get("Content-Type") != "audio/mpeg":
        print("Failed to retrieve valid audio data.")
        print(f"Response text: {response.text}")
        return None

    print("Successfully received audio data")
    binary_audio_data = b""
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            binary_audio_data += chunk
    print(f"Total audio data size: {len(binary_audio_data)} bytes")

    # Define the name for the Firebase object
    FIREBASE_OBJECT_NAME = "audio_files/audio_output.mp3"  # Update the path and filename as needed

    # Get a reference to Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(FIREBASE_OBJECT_NAME)  
    print(f"Uploading file to Firebase Storage: {blob.name}")

    # Upload audio data to Firebase
    blob.upload_from_string(binary_audio_data, content_type='audio/mpeg')
    print(f"File uploaded successfully to Firebase: {blob.public_url}")

    # Generate a download URL (Firebase automatically generates a public URL for blobs)
    download_url = blob.generate_signed_url(expiration=3600)  # 1 hour expiration
    print(f"Pre-signed URL generated: {download_url[:50]}...")
    return download_url

    print("Exiting text_to_speech function")
