import streamlit as st
import hashlib
import json
import io
from .assets import _audio_b64, _audio_b64_bytes
from utils.vocab_book import add_item

def run_analysis(scene_analyzer, uploaded_file):
    if (not st.session_state.show_home) and ((uploaded_file or st.session_state.preset_image_path) and not st.session_state.scene_context):
        with st.spinner("正在通过「语镜」分析场景..."):
            center_cols = st.columns([1, 1, 1])
            with center_cols[1]:
                img_to_show = uploaded_file if uploaded_file else st.session_state.preset_image_path
                st.image(img_to_show, caption="当前镜像场景", width=400)
                if uploaded_file:
                    st.session_state.scene_image_bytes = uploaded_file.getvalue()
                else:
                    st.session_state.scene_image_bytes = None
        try:
            file_obj = uploaded_file if uploaded_file else open(st.session_state.preset_image_path, "rb")
            analysis = scene_analyzer.analyze(file_obj)
            st.session_state.scene_context = analysis.scene_description
            coser = scene_analyzer.create_cosplay_session(
                analysis,
                target_language=st.session_state.target_language,
                native_language=st.session_state.native_language,
                difficulty=st.session_state.difficulty_level,
                support_mode=st.session_state.support_mode,
            )
            greeting = coser.greet()
            st.session_state.messages.append({"role": "assistant", "content": greeting})
            st.session_state.coser = coser
            st.rerun()
        except Exception as e:
            st.error(f"分析失败: {e}")

def run_chat(vlm_provider):
    if not st.session_state.show_home and st.session_state.scene_context:
        box = st.container(border=True)
        with box:
            row = st.columns([12, 1])
            with row[0]:
                st.markdown(f"📍 当前场景: {st.session_state.scene_context}")
            with row[1]:
                if st.button("↻", help="重新开始"):
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
                    st.rerun()
        img_src = st.session_state.scene_image_bytes if st.session_state.scene_image_bytes else st.session_state.preset_image_path
        if img_src:
            st.image(img_src, caption="当前镜像场景", width=400)
        if any(m.get("role") == "user" for m in st.session_state.messages):
            st.markdown("### 🌱 成长进度")
            progress = min(st.session_state.courage_score / 100, 1.0)
            st.progress(progress)
            st.caption(f"当前成长值: {st.session_state.courage_score}/100")
            if st.session_state.last_feedback_note:
                st.caption(f"建议: {st.session_state.last_feedback_note}")
            if st.session_state.courage_score >= 100:
                st.balloons()
                st.success("恭喜！你可以尝试去现实中对话了！")
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    if msg.get("audio_b64"):
                        if msg.get("role") == "user":
                            st.markdown(f"<audio controls src='data:audio/wav;base64,{msg['audio_b64']}'></audio>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<audio controls src='data:audio/mp3;base64,{msg['audio_b64']}'></audio>", unsafe_allow_html=True)
        prompt = st.chat_input("打字或语音", accept_audio=True, audio_sample_rate=16000, width="stretch", disabled=(st.session_state.get("input_locked", False) or st.session_state.get("is_processing", False)))
        user_input = None
        audio_file = None
        if not st.session_state.get("is_processing", False):
            if isinstance(prompt, str):
                user_input = prompt
            elif prompt:
                user_input = getattr(prompt, "text", None) or (prompt.get("text") if hasattr(prompt, "get") else None)
                audio_file = getattr(prompt, "audio", None) or (prompt.get("audio") if hasattr(prompt, "get") else None)
        if (not st.session_state.get("is_processing", False)) and (not user_input) and audio_file:
            try:
                buf = audio_file.getvalue() if hasattr(audio_file, "getvalue") else audio_file.read()
                fp = hashlib.sha1(buf).hexdigest()
                if st.session_state.get("last_audio_fingerprint") != fp:
                    with st.spinner("正在转写语音..."):
                        lang_map = {
                            "英语": "en",
                            "中文": "zh",
                            "日语": "ja",
                            "韩语": "ko",
                            "西班牙语": "es",
                            "法语": "fr",
                            "德语": "de"
                        }
                        lang_code = lang_map.get(st.session_state.get("target_language"))
                        file_like = io.BytesIO(buf)
                        setattr(file_like, "name", "input.wav")
                        trans = vlm_provider.client.audio.transcriptions.create(
                            model="whisper-1",
                            file=file_like,
                            language=lang_code,
                            temperature=0
                        )
                        user_input = getattr(trans, "text", None) or getattr(trans, "transcription", "")
                        st.session_state.last_audio_fingerprint = fp
                        st.session_state.last_recorded_audio_bytes = buf
                        st.info(f"语音转写结果：{user_input}")
            except Exception:
                st.warning("语音转写失败，继续使用文本输入。")
        current_audio_b64 = None
        if audio_file:
            try:
                data = audio_file.getvalue() if hasattr(audio_file, "getvalue") else audio_file.read()
                if data:
                    current_audio_b64 = _audio_b64_bytes(data)
            except Exception:
                pass
        elif st.session_state.last_recorded_audio_bytes:
            try:
                current_audio_b64 = _audio_b64_bytes(st.session_state.last_recorded_audio_bytes)
            except Exception:
                pass
            finally:
                st.session_state.last_recorded_audio_bytes = None
        if (not st.session_state.get("is_processing", False)) and user_input:
            st.session_state.pending_user_input = user_input
            st.session_state.is_processing = True
            st.session_state.input_locked = True
            st.rerun()

        if st.session_state.get("is_processing", False) and st.session_state.get("pending_user_input"):
            user_input = st.session_state.get("pending_user_input")
            try:
                st.session_state.messages.append({"role": "user", "content": user_input, "audio_b64": current_audio_b64})
                with st.chat_message("user"):
                    st.write(user_input)
                    if current_audio_b64:
                        st.markdown(f"<audio controls src='data:audio/wav;base64,{current_audio_b64}'></audio>", unsafe_allow_html=True)
                from utils.tts import generate_audio
                with st.chat_message("assistant"):
                    thinking = st.empty()
                    thinking.markdown("正在思考…")
                    stream = st.session_state.coser.chat_stream(user_input)
                    thinking.empty()
                    response = st.write_stream(stream)
                    audio_out = generate_audio(response, voice=st.session_state.tts_voice)
                    if audio_out:
                        b64 = _audio_b64(audio_out)
                        st.markdown(f"<audio controls src='data:audio/mp3;base64,{b64}'></audio>", unsafe_allow_html=True)
                    else:
                        b64 = None
                st.session_state.messages.append({"role": "assistant", "content": response, "audio_b64": b64})
                if st.session_state.coser:
                    st.session_state.coser.record_dialogue(user_input, response)
                    try:
                        fb = st.session_state.coser.coach_feedback(user_input, st.session_state.native_language)
                        st.session_state.last_coach_feedback = fb
                        if fb:
                            with st.expander("学习反馈", expanded=True):
                                if st.session_state.show_translation and fb.get("assistant_translation"):
                                    st.caption(f"助理回复译文（{st.session_state.native_language}）：{fb.get('assistant_translation')}")
                                if st.session_state.show_corrections:
                                    if fb.get("better_expression"):
                                        st.caption(f"更自然的表达建议（{st.session_state.target_language}）：{fb.get('better_expression')}")
                                    if fb.get("tips"):
                                        st.caption(f"提示：{fb.get('tips')}")
                                if fb.get("vocabulary"):
                                    st.caption("词汇知识点：")
                                    for idx, item in enumerate(fb.get("vocabulary")):
                                        term = item.get("term", "")
                                        explanation = item.get("explanation", "")
                                        example = item.get("example", "")
                                        row = st.columns([6, 2])
                                        with row[0]:
                                            st.caption(f"· {term} — {explanation}；例句：{example}")
                                        with row[1]:
                                            if st.button("加入词汇本", key=f"add_vocab_{idx}_{term}"):
                                                ok = add_item(term, explanation, example, st.session_state.target_language, st.session_state.user_id)
                                                if ok:
                                                    st.session_state.vocab_book.append({
                                                        "term": term,
                                                        "explanation": explanation,
                                                        "example": example,
                                                        "target_language": st.session_state.target_language
                                                    })
                                                    st.success(f"已加入：{term}")
                                                else:
                                                    st.info("已在词汇本中")
                                if fb.get("communication_skills"):
                                    st.caption("交流技巧：")
                                    for tip in fb.get("communication_skills"):
                                        st.caption(f"· {tip}")
                    except Exception:
                        pass
                    if st.session_state.get("last_audio_fingerprint") and user_input:
                        try:
                            sfb = st.session_state.coser.evaluate_speech(user_input)
                            st.session_state.last_speech_feedback = sfb
                            with st.expander("语音反馈", expanded=False):
                                st.caption(f"发音：{sfb.get('pronunciation', '')}")
                                st.caption(f"流利度：{sfb.get('fluency', '')}")
                                st.caption(f"语调：{sfb.get('intonation', '')}")
                                for s in sfb.get("suggestions", []):
                                    st.caption(f"· {s}")
                        except Exception:
                            pass
                try:
                    eval_raw = st.session_state.coser.evaluate_quality(st.session_state.scene_context, user_input)["raw"]
                    data = json.loads(eval_raw)
                    prev_score = st.session_state.courage_score
                    delta = int(data.get("delta", 0))
                    st.session_state.courage_score = max(0, min(100, prev_score + delta))
                    note = data.get("note")
                    st.session_state.last_feedback_note = note
                    delta_text = f"+{delta}" if delta >= 0 else f"{delta}"
                    msg = f"成长值 {prev_score} → {st.session_state.courage_score}（{delta_text}）"
                    if note:
                        msg += f" · {note}"
                    st.toast(msg, icon="🌱")
                except Exception:
                    pass
            finally:
                st.session_state.pending_user_input = None
                st.session_state.is_processing = False
                st.session_state.input_locked = False
                st.rerun()

        if st.session_state.get("last_coach_feedback") and not user_input:
            fb = st.session_state.get("last_coach_feedback")
            with st.expander("学习反馈", expanded=True):
                if st.session_state.show_translation and fb.get("assistant_translation"):
                    st.caption(f"助理回复译文（{st.session_state.native_language}）：{fb.get('assistant_translation')}")
                if st.session_state.show_corrections:
                    if fb.get("better_expression"):
                        st.caption(f"更自然的表达建议（{st.session_state.target_language}）：{fb.get('better_expression')}")
                    if fb.get("tips"):
                        st.caption(f"提示：{fb.get('tips')}")
                if fb.get("vocabulary"):
                    st.caption("词汇知识点：")
                    for idx, item in enumerate(fb.get("vocabulary")):
                        term = item.get("term", "")
                        explanation = item.get("explanation", "")
                        example = item.get("example", "")
                        row = st.columns([6, 2])
                        with row[0]:
                            st.caption(f"· {term} — {explanation}；例句：{example}")
                        with row[1]:
                            if st.button("加入词汇本", key=f"add_vocab_prev_{idx}_{term}"):
                                ok = add_item(term, explanation, example, st.session_state.target_language, st.session_state.user_id)
                                if ok:
                                    st.session_state.vocab_book.append({
                                        "term": term,
                                        "explanation": explanation,
                                        "example": example,
                                        "target_language": st.session_state.target_language
                                    })
                                    st.success(f"已加入：{term}")
                                else:
                                    st.info("已在词汇本中")
                if fb.get("communication_skills"):
                    st.caption("交流技巧：")
                    for tip in fb.get("communication_skills"):
                        st.caption(f"· {tip}")
