import streamlit as st
import random
from .assets import _img_b64
from utils.vocab_book import remove_item, list_items
from components.env import get_runtime_config, save_env_overrides

def inject_styles():
    st.set_page_config(page_title="语镜 MirrorTalk", page_icon="🪞", layout="wide", initial_sidebar_state="collapsed")
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=ZCOOL+KuaiLe&display=swap');
        h1, h2, h3 { font-family: 'ZCOOL KuaiLe', -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Microsoft YaHei', sans-serif !important; }
        .scene-card { display:block; border:1px solid #e5e5e5; border-radius:10px; padding:12px; text-decoration:none; color:#333; transition:box-shadow .15s ease; position:relative; }
        .scene-card:hover { box-shadow:0 2px 8px rgba(0,0,0,0.08); }
        .scene-card-link { position:absolute; inset:0; display:block; border-radius:10px; }
        .scene-card-title { font-size:1.1rem; font-weight:700; margin:0 0 6px 0; color:#f5f5f5; }
        .scene-card-desc { font-size:1rem; color:#e5e5e5; margin:0 0 8px 0; }
        .scene-card-img { height:140px; border:1px dashed #d0d0d0; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#888; overflow:hidden; }
        .scene-card-img img { width:100%; height:100%; object-fit:cover; border-radius:8px; }
        .top-icons { display:flex; justify-content:center; align-items:center; gap:12px; margin:6px 0 12px 0; }
        .top-icon { width:96px; height:96px; border-radius:50%; background:#181717; color:#fff; display:flex; align-items:center; justify-content:center; text-decoration:none; box-shadow:0 2px 6px rgba(0,0,0,0.2); }
        .top-icon img { width:80px; height:80px; }
        .top-icon.github { background:transparent; box-shadow:none; border:none; width:96px; height:96px; border-radius:50%; }
        </style>
        """,
        unsafe_allow_html=True,
        )
    st.markdown(
        """
        <style>
        div[data-testid="stSidebar"] { position: relative; }
        .sidebar-gear-wrap { position:absolute; left:12px; right:12px; bottom:12px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

@st.dialog("词汇本", width="large")
def show_vocab_dialog():
    items = list_items(st.session_state.get("user_id", "default"))
    st.markdown(
        """
        <style>
        .vocab-word { font-size:2rem; font-weight:800; margin:0 0 6px 0; letter-spacing:0.5px; }
        .vocab-meta { color:#6b7280; font-size:0.95rem; margin-bottom:10px; }
        .vocab-example { font-size:1rem; color:#374151; border-left:3px solid #e5e7eb; padding-left:12px; }
        .vocab-list-row { padding:8px 0; border-bottom:1px solid #f0f2f5; }
        .vocab-actions button { margin-right:6px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    tabs = st.tabs(["列表模式", "单词模式"])
    with tabs[0]:
        if not items:
            st.caption("暂无已保存词汇")
        else:
            page_size = st.session_state.get("vocab_page_size", 10)
            page_size = st.slider("每页数量", 5, 20, page_size)
            st.session_state.vocab_page_size = page_size
            total = len(items)
            pages = max(1, (total + page_size - 1) // page_size)
            page_index = st.session_state.get("vocab_page_index", 1)
            left, center1, center2, right = st.columns([1,2,2,1])
            with center1:
                st.caption(f"共 {total} 条 · 第 {page_index}/{pages} 页")
            with left:
                if st.button("上一页"):
                    page_index = max(1, page_index - 1)
            with right:
                if st.button("下一页"):
                    page_index = min(pages, page_index + 1)
            st.session_state.vocab_page_index = page_index
            start = (page_index - 1) * page_size
            end = min(total, start + page_size)
            for i, it in enumerate(items[start:end], start=start):
                term = it.get("term", "")
                explanation = it.get("explanation", "")
                example = it.get("example", "")
                lang = it.get("target_language", "")
                cols = st.columns([6,2])
                with cols[0]:
                    st.markdown(f"<div class='vocab-list-row'><strong>{term}</strong>（{lang}） — {explanation}；例句：{example}</div>", unsafe_allow_html=True)
                with cols[1]:
                    if st.button("学会了", key=f"rm_vocab_list_{i}_{term}"):
                        if remove_item(term, lang, st.session_state.get("user_id", "default")):
                            st.session_state.vocab_book = [x for x in st.session_state.vocab_book if not (x.get("term") == term and x.get("target_language") == lang)]
                            st.success(f"已移除：{term}")
    with tabs[1]:
        if not items:
            st.caption("暂无已保存词汇")
        else:
            idx = st.session_state.get("vocab_current_index", 0)
            idx = min(max(idx, 0), len(items) - 1)
            nav_cols = st.columns([1,1,1,2])
            with nav_cols[0]:
                if st.button("上一词", key="vocab_prev"):
                    idx = max(0, idx - 1)
            with nav_cols[1]:
                if st.button("下一词", key="vocab_next"):
                    idx = min(len(items) - 1, idx + 1)
            with nav_cols[2]:
                if st.button("随机", key="vocab_rand"):
                    idx = random.randint(0, len(items) - 1)
            st.session_state.vocab_current_index = idx
            it = items[idx]
            term = it.get("term", "")
            explanation = it.get("explanation", "")
            example = it.get("example", "")
            lang = it.get("target_language", "")
            st.markdown(f"<div class='vocab-word'>{term}</div><div class='vocab-meta'>{lang}</div><div class='vocab-example'>{explanation}<br/>例句：{example}</div>", unsafe_allow_html=True)
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            action_cols = st.columns([3,1])
            with action_cols[1]:
                if st.button("学会了", key=f"rm_vocab_single_{idx}_{term}"):
                    if remove_item(term, lang, st.session_state.get("user_id", "default")):
                        st.session_state.vocab_book = [x for x in st.session_state.vocab_book if not (x.get("term") == term and x.get("target_language") == lang)]
                        st.success(f"已移除：{term}")
                        st.session_state.vocab_current_index = min(idx, max(0, len(st.session_state.vocab_book) - 1))
            

@st.dialog("全局设置", width="medium")
def show_settings_dialog():
    base_url_default, api_key_default, model_name_default = get_runtime_config()
    base_url = st.text_input("Base URL", value=base_url_default or "")
    api_key = st.text_input("API Key", value=(api_key_default if api_key_default != "none" else ""), type="password")
    model_name = st.text_input("Model Name", value=model_name_default or "gpt-4o-mini")
    cols = st.columns([1,1])
    with cols[0]:
        if st.button("保存", type="primary"):
            save_env_overrides(base_url.strip() or None, api_key.strip() or None, model_name.strip() or None)
            st.success("已保存并应用")
            st.session_state.settings_dialog_open = False
            st.rerun()
    with cols[1]:
        if st.button("取消"):
            st.session_state.settings_dialog_open = False

def render_home(repo_url: str = "https://github.com/ChenZiHong-Gavin/MirrorTalk", dev_url: str = "https://github.com/ChenZiHong-Gavin"):
    hero_cols = st.columns([1, 3, 1])
    with hero_cols[1]:
        st.markdown("<h1 style='text-align:center; margin-bottom:0;'>🪞「语镜」MirrorTalk</h1>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:0.5rem 0 1rem 0;'>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:1.1rem;'>为社恐人士打造的多语言学习对话情景生成器</p>", unsafe_allow_html=True)
        if st.session_state.get("show_home", True):
            github_b64 = _img_b64("resources/images/github-icon.png")
            developer_b64 = _img_b64("resources/images/developer-icon.png")
            st.markdown(
                f"<div class='top-icons'><a class='top-icon github' href='{repo_url}' target='_blank' title='GitHub'><img src='data:image/png;base64,{github_b64}' alt='GitHub'/></a><a class='top-icon dev' href='{dev_url}' target='_blank' title='developer'><img src='data:image/png;base64,{developer_b64}' alt='Developer'/></a></div>",
                unsafe_allow_html=True,
            )
    if st.session_state.show_home:
        st.markdown(
            """
            <style>
            div[data-testid="stSidebar"] { display:none; }
            .home-hero { padding:32px 0 8px 0; background: linear-gradient(135deg, #f3f4f7 0%, #ffffff 100%); border-radius:16px; position: relative; }
            .home-badges { display:flex; gap:12px; justify-content:center; align-items:center; margin:8px 0 16px 0; }
            .cta-wrap { display:flex; justify-content:center; margin:8px 0 24px 0; }
            .cta-wrap button { font-size:1.1rem; }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<hr style='margin:0.5rem 0 1rem 0;'>", unsafe_allow_html=True)
        st.markdown("### 🌟 「语镜」是如何帮到社恐学习外语的？")
        cols = st.columns(3)
        cols[0].markdown("#### **STEP1: 场景识别 📷**\n\n")
        cols[0].markdown("AI 解析场景并模拟场景对话主体\n\n")
        cols[0].image("resources/images/feature1.png", width=600)
        cols[1].markdown("#### **STEP2: 沉浸式对话 🗣️**\n\n")
        cols[1].markdown("和模拟主体练习外语对话，就像在现实世界一样\n\n")
        cols[1].image("resources/images/feature2.png", width=600)
        cols[2].markdown("#### **STEP3: 成长进度 🌱**\n\n")
        cols[2].markdown("在对话练习中累计成长值，提升外语能力\n\n")
        cols[2].image("resources/images/feature3.png", width=600)
        start_cols = st.columns([1,1,1])
        with start_cols[1]:
            if st.button("开始练习", use_container_width=True):
                st.session_state.vocab_dialog_open = False
                st.session_state.show_home = False
                st.rerun()

def render_sidebar():
    if not st.session_state.show_home:
        with st.sidebar:
            st.markdown("### 练习设置")
            st.session_state.native_language = st.selectbox(
                "母语",
                ["中文", "英语", "日语", "韩语", "西班牙语", "法语", "德语", "自定义语言"],
                index=0,
            )
            if st.session_state.native_language == "自定义语言":
                st.session_state.native_language = st.text_input("输入母语名称（例如：粤语/俄语）", value="中文")
            st.session_state.target_language = st.selectbox(
                "练习语言",
                ["英语", "日语", "韩语", "西班牙语", "法语", "德语", "中文", "自定义语言"],
                index=0,
            )
            if st.session_state.target_language == "自定义语言":
                st.session_state.target_language = st.text_input("输入练习语言名称（例如：葡萄牙语）", value="英语")
            st.session_state.difficulty_level = st.slider("难度等级", 1, 5, st.session_state.difficulty_level)
            st.session_state.support_mode = st.selectbox("支持风格", ["温柔鼓励", "中性指导", "真实还原"], index=0)
            st.session_state.show_translation = st.checkbox("显示助理回复的母语译文", value=st.session_state.show_translation)
            st.session_state.show_corrections = st.checkbox("给出我的表达改进建议", value=st.session_state.show_corrections)
            st.session_state.tts_voice = st.selectbox("语音播报", ["alloy", "aria", "verse"], index=0)
            if st.session_state.get("coser"):
                st.session_state.coser.update_settings(
                    target_language=st.session_state.target_language,
                    native_language=st.session_state.native_language,
                    difficulty=st.session_state.difficulty_level,
                    support_mode=st.session_state.support_mode,
                )
            if st.button("打开词汇本", use_container_width=True):
                st.session_state.vocab_dialog_open = True
            st.markdown("<div class='sidebar-gear-wrap'>", unsafe_allow_html=True)
            if st.button("⚙️ 设置", key="open_settings", use_container_width=True):
                st.session_state.settings_dialog_open = True
            st.markdown("</div>", unsafe_allow_html=True)

def render_scenes():
    uploaded_file = None
    if st.session_state.show_home:
        return uploaded_file
    st.header("上传一张你想练习对话的照片")
    st.caption("以下是可练习的示例场景：")
    ex_cols = st.columns(3)
    with ex_cols[0]:
        scene1_b64 = _img_b64("resources/images/scene1.png")
        st.markdown(
            f"""
            <div class='scene-card'>
                <div class='scene-card-title'>☕ 国外第一次买咖啡</div>
                <div class='scene-card-desc'>在国外点咖啡，练习简单礼貌的英文交流。</div>
                <div class='scene-card-img'>
                    <img src='data:image/png;base64,{scene1_b64}' alt='国外首次买咖啡' style='width:100%; height:100%; object-fit:cover; border-radius:8px;'>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("选择咖啡场景", key="card_coffee", use_container_width=True):
            st.session_state.selected_scene = "coffee"
            st.session_state.preset_image_path = "resources/images/scene1.png"
            st.session_state.messages = []
            st.session_state.scene_context = None
            st.session_state.coser = None
            st.session_state.courage_score = 0
            st.session_state.last_feedback_note = None
            st.session_state.last_speech_feedback = None
            st.session_state.last_audio_fingerprint = None
            st.session_state.last_recorded_audio_bytes = None
            st.session_state.last_coach_feedback = None
            st.session_state.input_locked = False
            st.session_state.is_processing = False
            st.session_state.pending_user_input = None
            st.session_state.vocab_dialog_open = False
            st.rerun()
    with ex_cols[1]:
        scene2_b64 = _img_b64("resources/images/scene2.png")
        st.markdown(
            f"""
            <div class='scene-card'>
                <div class='scene-card-title'>🚇 在地铁上遇到心动对象</div>
                <div class='scene-card-desc'>在车厢里看到心动对象，尝试自然开启话题。</div>
                <div class='scene-card-img'>
                    <img src='data:image/png;base64,{scene2_b64}' alt='地铁搭讪心动对象' style='width:100%; height:100%; object-fit:cover; border-radius:8px;'>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("选择地铁场景", key="card_subway", use_container_width=True):
            st.session_state.selected_scene = "subway"
            st.session_state.preset_image_path = "resources/images/scene2.png"
            st.session_state.messages = []
            st.session_state.scene_context = None
            st.session_state.coser = None
            st.session_state.courage_score = 0
            st.session_state.last_feedback_note = None
            st.session_state.last_speech_feedback = None
            st.session_state.last_audio_fingerprint = None
            st.session_state.last_recorded_audio_bytes = None
            st.session_state.last_coach_feedback = None
            st.session_state.input_locked = False
            st.session_state.is_processing = False
            st.session_state.pending_user_input = None
            st.session_state.vocab_dialog_open = False
            st.rerun()
    with ex_cols[2]:
        scene3_b64 = _img_b64("resources/images/scene3.png")
        st.markdown(
            f"""
            <div class='scene-card'>
                <div class='scene-card-title'>🐈 与晒太阳的小猫交流</div>
                <div class='scene-card-desc'>遇到晒太阳的小猫，跨越物种障碍与小猫互动。</div>
                <div class='scene-card-img'>
                    <img src='data:image/png;base64,{scene3_b64}' alt='与晒太阳的小猫交流' style='width:100%; height:100%; object-fit:cover; border-radius:8px;'>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("选择小猫场景", key="card_cat", use_container_width=True):
            st.session_state.selected_scene = "cat"
            st.session_state.preset_image_path = "resources/images/scene3.png"
            st.session_state.messages = []
            st.session_state.scene_context = None
            st.session_state.coser = None
            st.session_state.courage_score = 0
            st.session_state.last_feedback_note = None
            st.session_state.last_speech_feedback = None
            st.session_state.last_audio_fingerprint = None
            st.session_state.last_recorded_audio_bytes = None
            st.session_state.last_coach_feedback = None
            st.session_state.input_locked = False
            st.session_state.is_processing = False
            st.session_state.pending_user_input = None
            st.session_state.vocab_dialog_open = False
            st.rerun()
    uploaded_file = st.file_uploader("选择你的照片...", type=["jpg", "png", "jpeg"])
    return uploaded_file
