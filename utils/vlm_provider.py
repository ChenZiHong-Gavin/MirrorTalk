import base64
import imghdr
from typing import List, Optional, Dict, Any
from openai import OpenAI


class VLMProvider():
    def __init__(self, base_url: str, api_key: str, model_name: str = "gpt-4o-mini"):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model_name = model_name
    
    @staticmethod
    def encode_image(image_file) -> str:
        """将图片文件编码为 base64 字符串"""
        return base64.b64encode(image_file.read()).decode("utf-8")

    def build_messages(
        self,
        prompt: str,
        image_file: Optional[Any] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        history: Optional[List[List[str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        构建消息列表
        
        参数:
            prompt: 用户的问题或提示词
            image_file: 可选的图片文件对象
            messages: 现有的消息列表（将在其基础上追加）
            history: 历史对话 [[user_msg, assistant_msg], ...]
        
        返回:
            完整的消息列表
        """
        full_messages = messages.copy() if messages else []
        
        # 追加历史对话
        if history:
            for user_msg, assistant_msg in history:
                full_messages.append({
                    "role": "user", 
                    "content": [{"type": "text", "text": user_msg}]
                })
                full_messages.append({
                    "role": "assistant", 
                    "content": [{"type": "text", "text": assistant_msg}]
                })
        
        # 构建当前消息内容
        content = [{"type": "text", "text": prompt}]
        
        # 如果有图片，追加图片内容
        if image_file is not None:
            try:
                # 编码图片
                base64_image = self.encode_image(image_file)
                
                # 检测 MIME 类型
                image_file.seek(0)
                image_type = imghdr.what(image_file)
                mime_type = f"image/{image_type}" if image_type else "image/jpeg"
                
                # 追加图片
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}
                })
                
            except Exception as e:
                raise ValueError(f"图片处理失败: {str(e)}")
        
        # 追加当前用户消息
        full_messages.append({
            "role": "user",
            "content": content
        })
        
        return full_messages

    def generate(
        self, 
        messages: List[Dict[str, Any]], 
        **kwargs
    ) -> str:
        """
        调用 VLM API 生成响应
        
        参数:
            messages: 消息列表
            model: 模型名称
            **kwargs: 其他 API 参数（temperature, max_tokens 等）
        """

        

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"API 调用失败: {str(e)}")
