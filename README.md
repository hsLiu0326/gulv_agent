# AI营养师Agent

智能个性化营养饮食管理系统：用户上传体检报告，系统用 AI 解析健康指标、生成个性化食谱，
并提供每日膳食规划、口味偏好管理和营养知识库问答。

## 功能特性

- **体检报告上传**：支持粘贴文本、上传 .docx / .pdf 文件，自动提取并解析
  血糖、血压、尿酸、胆固醇、甘油三酯等指标（LLM 解析 + 正则兜底）
- **AI 个性化食谱**：LangGraph 多 Agent 工作流（健康分析 → 营养规划 → 食谱生成 → 质量审核），
  支持 SSE 流式输出，未通过审核最多自动回炉 3 次
- **营养知识库问答**：37 条种子营养知识，**Ollama 语义向量 + ChromaDB 向量库**
  做向量粗排，自研"余弦 + 词频"混合打分精排；哈希向量 / JSON 检索自动兜底
- **AI 对话助手**：多轮对话 + 知识库工具调用（function calling），流式回答
- **每日膳食规划**：菜单 → 餐次 → 菜品三层结构，自动汇总热量与营养
- **口味偏好管理**：喜欢/不喜欢/菜系/过敏原，参与食谱生成

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python FastAPI + SQLAlchemy + MySQL |
| AI | LangChain + LangGraph + DeepSeek API（OpenAI 兼容）+ Ollama embedding + ChromaDB |
| 前端 | Vue 3 + Vite + Element Plus + Pinia |
| 部署 | Docker Compose（MySQL + 后端 + Nginx 前端） |

## 快速启动（Docker Compose）

```bash
# 1. 准备环境变量（可选；也可直接在项目根目录创建 .env 覆盖 compose 变量）
cp backend/.env.example backend/.env

# 2. 一键启动（首次会自动构建镜像并初始化数据库）
docker compose up -d --build

# 国内网络下 pip 默认走阿里云镜像源；如需其他源：
# docker compose build --build-arg PIP_INDEX_URL=https://pypi.org/simple/ backend

# 3. 访问
#    前端: http://localhost
#    后端: http://localhost:8000/docs
```

> Ollama：默认从容器内访问宿主机的 `host.docker.internal:11434`，
> 需要本机已运行 Ollama 且有 `qwen-emb` 模型。

## 本地开发

### 后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt   # 测试依赖

# 配置 backend/.env（数据库、LLM、Ollama）
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 测试与评测

```bash
cd backend
python -m pytest tests -q

# AI 能力评测（报告解析 + 知识库检索）
python eval/run_eval.py --provider ollama
python eval/run_eval.py --provider hash    # 完全离线
```

## 关键配置（backend/.env）

| 变量 | 说明 |
|---|---|
| `DATABASE_URL` | MySQL 连接串 |
| `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `LLM_MODEL` | LLM 服务（默认 DeepSeek `deepseek-v4-flash`） |
| `EMBEDDING_PROVIDER` | `ollama`（语义向量）/ `hash`（离线兜底） |
| `OLLAMA_BASE_URL` / `OLLAMA_EMBED_MODEL` | Ollama embedding 服务 |
| `VECTOR_STORE` | 知识库存储后端：`chroma`（向量库）/ `json`（纯 Python 兜底） |
| `CHROMA_PERSIST_DIR` | 知识库数据目录（JSON 数据源 + Chroma 索引 + 向量缓存） |

> Windows 提示：若本机 VC++ 运行库过旧导致 ChromaDB/onnxruntime 原生库崩溃，
> 先运行 `python scripts/setup_win_runtime.py`（从 Ollama 目录复制新版运行库到
> `backend/vendor/win_runtime`），应用启动时会在任何第三方库导入前自动完成引导。

## 项目结构

```text
backend/
  app/
    agents/       # 多 Agent 工作流、对话助手、提示词管理
    api/          # REST / SSE 接口
    core/         # 配置、数据库、安全
    models/       # SQLAlchemy 模型
    schemas/      # Pydantic 模式
    services/     # 知识库、报告解析、文档提取
  tests/          # pytest 单元测试
  eval/           # AI 能力评测样例与脚本
frontend/
  src/views/      # 页面（控制台/报告/食谱/对话/知识库等）
docker-compose.yml
```
