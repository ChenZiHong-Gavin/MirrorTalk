from openai import OpenAI
import uuid
import tempfile
from components.env import get_runtime_config

def generate_audio(text, voice="alloy", model="tts-1", filename=None):
    base_url, api_key, _ = get_runtime_config()
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
    try:
        allowed = {"nova", "shimmer", "echo", "onyx", "fable", "alloy", "ash", "sage", "coral"}
        v = voice if voice in allowed else "alloy"
        target = filename or os.path.join(tempfile.gettempdir(), f"mirrortalk_{uuid.uuid4().hex}.mp3")
        response = client.audio.speech.create(model=model, voice=v, input=text)
        response.stream_to_file(target)
        return target
    except Exception:
        return None
