# 「语镜」MirrorTalk

「语镜」MirrorTalk - 为社恐人士打造的多语言学习对话情景生成器

面向社恐的多语言沉浸式对话陪练器。上传一张照片，AI识别场景并生成沉浸式角色与你进行语音/文字多轮对话，提供即时的学习反馈与渐进式“毕业”机制，帮助你从害怕开口到敢于交流。

<p align="center">
<img width="600" alt="image" src="https://github.com/user-attachments/assets/e0e4b1b2-6321-4ce4-87a6-a568f674a5da" />
</p>

## 特性
- 场景识别与角色扮演：上传照片 → 场景识别 → 生成情景上下文 → AI 角色扮演→多轮对话
- 支持语音与文字交流
- 支持同时学习多语言：英/日/韩/西/法/德/中/自定义（例如猫猫语）
- 提供学习反馈：每轮提供译文、表达改进、词汇知识点与交流技巧；语音输入还会有发音/流利度/语调建议
- 成长机制：累计成长值并给出鼓励，逐步过渡到现实对话

<p align="center">
  <img src="resources/images/feature1.png" width="30%" />
  <img src="resources/images/feature2.png" width="30%" />
  <img src="resources/images/feature3.png" width="30%" />
</p>

## 运行与环境
- 依赖：Python 3.10+
- 环境变量（`.env` 示例）：

```
OPENAI_BASE_URL=...
OPENAI_API_KEY=...
MODEL_NAME=...
```
- 启动：
```
python -m streamlit run app.py --server.port 8502
```

## 使用指南
- 选择一个示例场景或上传照片自定义场景

  <img width="600" alt="image" src="https://github.com/user-attachments/assets/c42471ec-4bbd-4e47-b6d4-2ed1e4c2a491" />

- 在侧边栏选择母语与目标语言、难度与支持风格、是否显示译文/表达改进
  
  <img width="600" alt="image" src="https://github.com/user-attachments/assets/fcead72b-290c-42f4-bef8-00bdcd1182a4" />

- 进入会话后可文字或语音输入；助理将以目标语言沉浸式回复，并生成音频回复
- 有语音输入时，可查看“语音反馈”（发音/流利度/语调与建议）

  <img width="600" alt="image" src="https://github.com/user-attachments/assets/27e51ffc-85e5-407c-8575-3e5c621e9741" />

- 每轮对话展开“学习反馈”查看译文、表达优化与词汇，词汇可加入词汇本保存

  <img width="600" alt="image" src="https://github.com/user-attachments/assets/a52a0353-1f25-4d70-b5e9-e6addc5cf14e" />

- 成长值满级会触发“毕业”鼓励，建议尝试现实对话


## 致谢
[Parallax](https://github.com/GradientHQ/parallax): 一个分布式推理框架，支持异构设备推理。

**为什么选择使用 Parallax 构建本地服务**
  - 降低学习成本：无需云端 API 费用或订阅
  - 数据完全私有：输入与输出保留在本地
  - 多模型支持：切换各种本地部署的 LLM 只需一键操作
  - 灵活硬件组合：支持 Apple 电脑与 Nvidia 主机异构组网，低成本运行大模型

**需要注意的是**
当前 parallax 不支持 VLM, TTS 和 STT模型，所以可以使用其它部署方式替代， parallax 可以用来部署角色扮演的 LLM。
