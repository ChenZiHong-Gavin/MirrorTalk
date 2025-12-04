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

def save_env_overrides(base_url: str = None, api_key: str = None, model_name: str = None, path: str = ".env"):
    data = {}
    orig_lines = []
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                orig_lines = f.readlines()
                for line in orig_lines:
                    s = line.rstrip("\n")
                    if not s or s.strip().startswith("#") or "=" not in s:
                        continue
                    k, v = s.split("=", 1)
                    data[k.strip()] = v.strip()
    except Exception:
        orig_lines = []
        data = {}
    if base_url:
        data["BASE_URL"] = base_url
        data["OPENAI_BASE_URL"] = base_url
        os.environ["BASE_URL"] = base_url
        os.environ["OPENAI_BASE_URL"] = base_url
    if api_key:
        data["API_KEY"] = api_key
        data["OPENAI_API_KEY"] = api_key
        os.environ["API_KEY"] = api_key
        os.environ["OPENAI_API_KEY"] = api_key
    if model_name:
        data["MODEL_NAME"] = model_name
        os.environ["MODEL_NAME"] = model_name
    try:
        keys = {"BASE_URL", "OPENAI_BASE_URL", "API_KEY", "OPENAI_API_KEY", "MODEL_NAME"}
        updated = set()
        out_lines = []
        for line in orig_lines:
            s = line.rstrip("\n")
            if not s or s.strip().startswith("#") or "=" not in s:
                out_lines.append(line)
                continue
            k, _ = s.split("=", 1)
            kk = k.strip()
            if kk in keys and kk in data:
                out_lines.append(f"{kk}={data[kk]}\n")
                updated.add(kk)
            else:
                out_lines.append(line)
        for kk in keys:
            if kk in data and kk not in updated:
                out_lines.append(f"{kk}={data[kk]}\n")
        if not orig_lines and not os.path.exists(path):
            out_lines = [f"{kk}={data[kk]}\n" for kk in keys if kk in data]
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(out_lines)
    except Exception:
        pass
