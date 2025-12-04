import json
from dataclasses import dataclass, asdict
from typing import Dict, Any
from utils.vlm_provider import VLMProvider
from .coser import Persona, Coser


@dataclass
class AnalysisResult:
    """场景分析结果"""
    scene_type: str
    scene_description: str
    subject_type: str
    subject_description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SceneAnalyzer:    
    def __init__(self, vlm_provider: VLMProvider):
        self.vlm_provider = vlm_provider
    
    def analyze(
        self, 
        image_file
    ):
        """
        分析图片场景和主体
        
        参数:
            image_file: 图片文件对象
            language: 输出语言
            custom_prompt: 自定义提示词
        
        """
        # 构建系统提示词
        system_prompt = """
        你是一个专业的图像分析助手，擅长识别场景和主体。
        你的任务是：
        1. 准确识别图片中的场景类型（如：咖啡厅、街道、超市等）
        2. 识别图片中的一个关键主体（如：人物、动物、建筑等）
        3. 提供详细的场景和主体描述
        4. 以结构化JSON格式返回结果
        """
        
        analysis_prompt = self._get_analysis_prompt()
        
        messages = [{"role": "system", "content": system_prompt}]
        final_messages = self.vlm_provider.build_messages(
            prompt=analysis_prompt,
            image_file=image_file,
            messages=messages
        )
        
        response = self.vlm_provider.generate(
            messages=final_messages,
            response_format={"type": "json_object"}
        )

        try:
            data = json.loads(response)
            return AnalysisResult(
                scene_type=data.get("scene_type", "神秘场景"),
                scene_description=data.get("scene_description", "一个看不透的神秘场景"),
                subject_type=data.get("subject_type", "神秘主体"),
                subject_description=data.get("subject_description", "一个看不透的神秘主体")
            )
        except json.JSONDecodeError:
            raise ValueError("API 返回的JSON格式无效")
    
    def _get_analysis_prompt(self) -> str:
        """获取语言特定的分析提示词"""
        prompt = """
            请分析这张图片，提供以下信息：
            {
                "scene_type": "场景类型（简短关键词）",
                "scene_description": "详细场景描述（包含环境特征、氛围、时间等）",
                "subject_type": "主体类型（如：年轻女性、猫、古老建筑等）",
                "subject_description": "详细主体描述（包含外貌、动作、状态等）"
            }
        """
        return prompt


    def create_cosplay_session(
        self,
        analysis: AnalysisResult,
        target_language: str = "英语",
        native_language: str = "中文",
        difficulty: int = 1,
        support_mode: str = "温柔鼓励",
    ) -> Coser:
        """
        创建角色扮演会话
        """
        
        # 创建人设
        persona_prompt = f"""
        基于以下信息创建沉浸式角色：
        
        场景：{analysis.scene_description}
        主体：{analysis.subject_description}
        
        生成包含 name, role, personality, background, interaction_style 的JSON。
        """
        
        messages = [
            {"role": "system", "content": "你是一位专业角色设定师。"},
            {"role": "user", "content": persona_prompt}
        ]
        
        response = self.vlm_provider.generate(
            messages=messages,
            response_format={"type": "json_object"}
        )

        persona_data = json.loads(response)


        persona = Persona(
            name=persona_data["name"] if "name" in persona_data else analysis.subject_type,
            role=persona_data["role"] if "role" in persona_data else analysis.subject_type,
            personality=persona_data["personality"] if "personality" in persona_data else "普通",
            background=persona_data["background"] if "background" in persona_data else "无",
            interaction_style=persona_data["interaction_style"] if "interaction_style" in persona_data else "普通"
        )

        print(persona.name)
        print(persona.role)
        print(persona.personality)
        print(persona.background)
        print(persona.interaction_style)

        return Coser(
            self.vlm_provider,
            persona,
            target_language=target_language,
            native_language=native_language,
            difficulty=difficulty,
            support_mode=support_mode,
        )
