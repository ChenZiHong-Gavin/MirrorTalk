import os
import streamlit as st

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
    uid = st.session_state.get("user_id")
    overrides = st.session_state.get("runtime_overrides", {})
    if uid and uid in overrides:
        cfg = overrides[uid]
        base_url = cfg.get("base_url") or os.environ.get("BASE_URL") or os.environ.get("OPENAI_BASE_URL")
        api_key = cfg.get("api_key") or os.environ.get("API_KEY") or os.environ.get("OPENAI_API_KEY") or "none"
        model_name = cfg.get("model_name") or os.environ.get("MODEL_NAME") or "gpt-4o-mini"
        return base_url, api_key, model_name
    base_url = os.environ.get("BASE_URL") or os.environ.get("OPENAI_BASE_URL")
    api_key = os.environ.get("API_KEY") or os.environ.get("OPENAI_API_KEY") or "none"
    model_name = os.environ.get("MODEL_NAME") or "gpt-4o-mini"
    return base_url, api_key, model_name

def save_user_overrides(base_url: str = None, api_key: str = None, model_name: str = None):
    uid = st.session_state.get("user_id", "default")
    overrides = st.session_state.get("runtime_overrides", {})
    cur = overrides.get(uid, {})
    if base_url is not None:
        cur["base_url"] = base_url
    if api_key is not None:
        cur["api_key"] = api_key
    if model_name is not None:
        cur["model_name"] = model_name
    overrides[uid] = cur
    st.session_state.runtime_overrides = overrides
