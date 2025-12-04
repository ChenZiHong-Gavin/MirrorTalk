import streamlit as st
import uuid
from utils.vocab_book import list_items
from .assets import _img_b64

def init_session_state():
    if "user_id" not in st.session_state:
        params = st.query_params
        uid = params.get("uid")
        if isinstance(uid, list):
            uid = uid[0] if uid else None
        if not uid:
            uid = uuid.uuid4().hex
            st.query_params["uid"] = uid
        st.session_state.user_id = uid
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "scene_context" not in st.session_state:
        st.session_state.scene_context = None
    if "courage_score" not in st.session_state:
        st.session_state.courage_score = 0
    if "selected_scene" not in st.session_state:
        st.session_state.selected_scene = None
    if "preset_image_path" not in st.session_state:
        st.session_state.preset_image_path = None
    if "scene_image_bytes" not in st.session_state:
        st.session_state.scene_image_bytes = None
    if "last_feedback_note" not in st.session_state:
        st.session_state.last_feedback_note = None
    if "coser" not in st.session_state:
        st.session_state.coser = None
    if "native_language" not in st.session_state:
        st.session_state.native_language = "中文"
    if "last_speech_feedback" not in st.session_state:
        st.session_state.last_speech_feedback = None
    if "show_home" not in st.session_state:
        st.session_state.show_home = True
    if "last_audio_fingerprint" not in st.session_state:
        st.session_state.last_audio_fingerprint = None
    if "last_recorded_audio_bytes" not in st.session_state:
        st.session_state.last_recorded_audio_bytes = None
    if "target_language" not in st.session_state:
        st.session_state.target_language = "英语"
    if "difficulty_level" not in st.session_state:
        st.session_state.difficulty_level = 1
    if "support_mode" not in st.session_state:
        st.session_state.support_mode = "温柔鼓励"
    if "show_translation" not in st.session_state:
        st.session_state.show_translation = True
    if "show_corrections" not in st.session_state:
        st.session_state.show_corrections = True
    if "tts_voice" not in st.session_state:
        st.session_state.tts_voice = "alloy"
    if "vocab_book" not in st.session_state:
        st.session_state.vocab_book = list_items(st.session_state.user_id)
    if "input_locked" not in st.session_state:
        st.session_state.input_locked = False
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    if "pending_user_input" not in st.session_state:
        st.session_state.pending_user_input = None
    if "vocab_dialog_open" not in st.session_state:
        st.session_state.vocab_dialog_open = False
    if "settings_dialog_open" not in st.session_state:
        st.session_state.settings_dialog_open = False
    if "user_avatar" not in st.session_state:
        try:
            st.session_state.user_avatar = f"data:image/png;base64,{_img_b64('resources/images/user.png')}"
        except Exception:
            st.session_state.user_avatar = "🧑"
    if "assistant_avatar" not in st.session_state:
        try:
            st.session_state.assistant_avatar = f"data:image/png;base64,{_img_b64('resources/images/assistant.png')}"
        except Exception:
            st.session_state.assistant_avatar = "🤖"
    if "runtime_overrides" not in st.session_state:
        st.session_state.runtime_overrides = {}
