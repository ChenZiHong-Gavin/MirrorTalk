import os

def load_env_file(path: str = ".env"):
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if "=" not in s:
                    continue
                k, v = s.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass

def get_runtime_config():
    base_url = os.environ.get("BASE_URL") or os.environ.get("OPENAI_BASE_URL")
    api_key = os.environ.get("API_KEY") or os.environ.get("OPENAI_API_KEY") or "none"
    model_name = os.environ.get("MODEL_NAME") or "gpt-4o-mini"
    return base_url, api_key, model_name

