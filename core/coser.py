from dataclasses import dataclass, asdict
from datetime import datetime
import json
from typing import Dict, Any, List
from utils.vlm_provider import VLMProvider

@dataclass
class Persona:
    name: str
    role: str
    personality: str
    background: str
    interaction_style: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Coser:
    """角色扮演"""
    
    def __init__(
        self, 
        vlm_provider: VLMProvider, 
        persona: Persona, 
        target_language: str = "英语",
        native_language: str = "中文",
        difficulty: int = 1,
        support_mode: str = "温柔鼓励",
    ):
        self.provider = vlm_provider
        self.persona = persona
        self.target_language = target_language
        self.native_language = native_language
        self.difficulty = max(1, min(5, difficulty))
        self.support_mode = support_mode
        self.history: List[Dict[str, Any]] = []
        self.conversation_start_time = datetime.now()

        self._setup_persona()

    def update_settings(self, target_language: str = None, native_language: str = None, difficulty: int = None, support_mode: str = None):
        if target_language is not None:
            self.target_language = target_language
        if native_language is not None:
            self.native_language = native_language
        if difficulty is not None:
            self.difficulty = max(1, min(5, int(difficulty)))
        if support_mode is not None:
            self.support_mode = support_mode
        self._setup_persona()

    def _setup_persona(self):
        """设置角色系统提示词"""
        self.system_message = {
            "role": "system",
            "content": f"""
            你是 **{self.persona.name}**，{self.persona.role}。
            
            背景设定：
            {self.persona.background}
            
            性格特征：
            {self.persona.personality}
            
            互动风格：
            {self.persona.interaction_style}
            
            对话语言与风格约束：
            - 助理主回复语言：始终使用 {self.target_language}
            - 支持风格：{self.support_mode}（给社恐用户低压力、温柔鼓励、渐进式引导）
            - 难度等级：{self.difficulty}/5（难度越高，词汇更丰富、句子更复杂；保持可理解性）
            - 不要在主回复中切换到 {self.native_language}，中文/母语解释仅通过单独的学习反馈面板提供
            
            规则：
            1. 始终保持角色设定，用第一人称回应
            2. 根据场景和角色背景给出符合身份的回应
            3. 回应要自然、生动，有代入感
            4. 保持简洁分段，便于阅读与跟随
            """
        }
    
    def greet(self) -> str:
        """返回沉浸式开场白"""
        # 构建欢迎消息
        welcome_prompt = f"""
        作为 {self.persona.name}，请根据你的背景设定，给用户一个自然的开场白。
        这个开场白应该：
        1. 体现你的角色身份和性格
        2. 让用户感受到场景氛围
        3. 邀请用户开始对话
        4. 简短、生动、有吸引力
        
        直接返回开场白文本，不要包含其他内容。
        """
        
        messages = [self.system_message, {
            "role": "user",
            "content": welcome_prompt
        }]
        
        greeting = self.provider.generate(
            messages=messages
        )
        
        # 记录到历史
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": greeting,
            "type": "greeting"
        })
        
        return greeting

    def _history_pairs(self) -> List[List[str]]:
        pairs = []
        buf_user = None
        for h in self.history:
            if h.get("type") == "dialogue":
                pairs.append([h.get("user_input", ""), h.get("assistant_response", "")])
        return pairs

    def chat_stream(self, user_input: str):
        messages = [self.system_message]
        final_messages = self.provider.build_messages(
            prompt=user_input,
            messages=messages,
            history=self._history_pairs()
        )
        return self.provider.client.chat.completions.create(
            model=self.provider.model_name,
            messages=final_messages,
            stream=True
        )

    def record_dialogue(self, user_input: str, assistant_response: str):
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": assistant_response,
            "type": "dialogue",
            "user_input": user_input,
            "assistant_response": assistant_response,
        })

    def evaluate_quality(self, scene_context: str, user_input: str) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": "请只输出JSON，包含字段 delta(-10到10的整数) 和 note(简短建议)。根据场景与用户输入评价其社交对话质量。"},
            {"role": "user", "content": f"场景: {scene_context}\n用户输入: {user_input}"}
        ]
        resp = self.provider.client.chat.completions.create(
            model=self.provider.model_name,
            messages=messages
        )
        return {"raw": resp.choices[0].message.content}
    
    def coach_feedback(self, user_input: str, native_language: str) -> Dict[str, Any]:
        """生成学习反馈：助理回复的母语译文、改进表达、提示、词汇与交流技巧"""
        last_dialogue = None
        for h in reversed(self.history):
            if h.get("type") == "dialogue":
                last_dialogue = h
                break
        assistant_resp = last_dialogue.get("assistant_response") if last_dialogue else ""

        sys = {
            "role": "system",
            "content": (
                "你是语言学习教练。只输出 JSON。"
                "字段说明：assistant_translation(NATIVE)，better_expression(TARGET)，tips(NATIVE)，"
                "vocabulary(数组对象，包含term/explanation/example)，communication_skills(字符串数组)。"
            )
        }
        prompt = {
            "role": "user",
            "content": (
                f"目标语言: {self.target_language}\n母语: {native_language}\n"
                f"我的发言: {user_input}\n助理回复: {assistant_resp}\n"
                "请生成上述结构化反馈，简洁可读。"
            )
        }
        resp = self.provider.client.chat.completions.create(
            model=self.provider.model_name,
            messages=[sys, prompt],
            response_format={"type": "json_object"}
        )
        try:
            return json.loads(resp.choices[0].message.content)
        except Exception:
            return {
                "assistant_translation": "",
                "better_expression": "",
                "tips": "",
                "vocabulary": [],
                "communication_skills": []
            }

    def evaluate_speech(self, transcript: str) -> Dict[str, Any]:
        """语音层面的反馈（基于转写文本进行可理解性、语速、停顿等建议）"""
        sys = {
            "role": "system",
            "content": "只输出 JSON：pronunciation, fluency, intonation, suggestions(列表)。"
        }
        usr = {
            "role": "user",
            "content": (
                f"目标语言: {self.target_language}\n转写文本: {transcript}\n"
                "请给出温和具体的改进建议，适合社恐用户。"
            )
        }
        resp = self.provider.client.chat.completions.create(
            model=self.provider.model_name,
            messages=[sys, usr],
            response_format={"type": "json_object"}
        )
        try:
            return json.loads(resp.choices[0].message.content)
        except Exception:
            return {
                "pronunciation": "",
                "fluency": "",
                "intonation": "",
                "suggestions": []
            }
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取完整对话历史"""
        return self.history.copy()
