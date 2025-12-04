import base64

def _img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def _audio_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def _audio_b64_bytes(data: bytes):
    return base64.b64encode(data).decode("utf-8")

