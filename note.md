#配置dify模型
##安装docker-配置本地dify-下载ollama-ollma内配置Qwen

教学[https://blog.csdn.net/zohan134/article/details/149301536?utm_source=chatgpt.com]

dify功能教学[https://docs.dify.ai/zh/use-dify/getting-started/quick-start]

👉 当你把 知识检索 + LLM 组合起来时：

✔️ 知识检索模块会把相关文本检索出来

✔️ Dify 会 自动把这些检索结果拼接到 LLM 的上下文里

✔️ 你在 System / Prompt 中不需要也看不到直接的 result 变量名

✔️ 但这些检索出的文本内容确实会“隐式”地被加入到 LLM 的输入里

┌──────────────────────────────────────────┐

│ Docker （容器管理）                       │

│  ├ Dify 前端 UI                          │

│  ├ Dify API 服务                        │

│  ├ Redis / 数据库 / 后台服务             │

│  └ ………                                   │

└──────────────────────────────────────────┘

        │
        └─ Dify 通过 HTTP 请求调用
              ↓
     Ollama 本地模型推理服务（非 Docker）
        │
        └─ Qwen3 模型被 Ollama 加载与调用
