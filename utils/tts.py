from openai import OpenAI
import os
import uuid
import tempfile

def generate_audio(text, voice="alloy", model="tts-1", filename=None):
    base_url = os.environ.get("OPENAI_BASE_URL") or os.environ.get("BASE_URL")
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("API_KEY") or "none"
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
    try:
        target = filename or os.path.join(tempfile.gettempdir(), f"mirrortalk_{uuid.uuid4().hex}.mp3")
        response = client.audio.speech.create(model=model, voice=voice, input=text)
        response.stream_to_file(target)
        return target
    except Exception:
        return None
