#配置dify模型
##安装docker-配置本地dify-下载ollama-ollma内配置Qwen
你的电脑
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
