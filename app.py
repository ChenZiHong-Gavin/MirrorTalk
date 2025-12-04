import os
import streamlit as st
from utils.vlm_provider import VLMProvider
from core.scene_analyzer import SceneAnalyzer
from components.env import load_env_file, get_runtime_config
from components.session import init_session_state
from components.ui import inject_styles, render_home, render_sidebar, render_scenes
from components.flow import run_analysis, run_chat

inject_styles()
load_env_file()
base_url, api_key, model_name = get_runtime_config()
vlm_provider = VLMProvider(base_url=base_url, api_key=api_key, model_name=model_name)
scene_analyzer = SceneAnalyzer(vlm_provider)
init_session_state()
repo_url = os.environ.get("REPO_URL") or "https://github.com/"
dev_url = os.environ.get("DEV_URL") or repo_url
render_home(repo_url, dev_url)
render_sidebar()
uploaded_file = render_scenes()
run_analysis(scene_analyzer, uploaded_file)
run_chat(vlm_provider)
from components.ui import show_vocab_dialog
if st.session_state.get("vocab_dialog_open", False):
    show_vocab_dialog()
    st.session_state.vocab_dialog_open = False
