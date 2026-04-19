# Skill Calling Verification

这个项目是一个最小验证仓库，目标不是做完整业务，而是验证两种不同的 `skill` 调用方式：

1. `DeepAgents` 风格：由主代理根据用户任务直接命中本地 skill
2. `LangChain / LangGraph` 官方风格：通过 on-demand skills 按需加载领域技能，而不是在一开始把全部上下文塞进 system prompt

项目里保留了两套示例，方便对比：

- `DeepAgents` 示例偏向“本地 skill 自动命中”
- `LangGraph` 示例偏向“官方 skill middleware + load_skill 工具 + 按需加载”

## 项目目标

这个仓库主要回答三个问题：

1. 本地 skill 能不能被正确识别和调用
2. 同一个项目里能不能同时验证不同 skill 框架的调用方式
3. 如何用 CLI 和 FastAPI 快速跑一遍验证

## 两种 skill 调用方式

### 1. DeepAgents 方式

这一套实现放在 `skill_project/services/skill_service.py` 和 `skills/` 目录。

核心特点：

- 使用 `create_deep_agent(...)`
- 主代理直接挂载本地 `skills=["/skills"]`
- 根据 prompt 内容自动命中对应 skill
- 支持一个请求里触发单 skill 或双 skill 场景

当前示例 skill：

- `skills/travel-itinerary`
- `skills/travel-shopping`

当前验证接口：

- `POST /api/v1/validate-skill`
- `POST /api/v1/run-scenario`

适合验证的问题：

- 给一段 prompt，代理是否会命中本地 skill
- 固定场景下，不同模型是否会稳定走到同一个 skill
- 一个请求里是否能连续处理两个交付物

### 2. LangChain / LangGraph 官方格式

这一套实现放在 `skill_project/langgraph_skill/` 和 `skill_project/api/langgraph_api.py`。

核心特点：

- 使用 `create_agent(...)`
- 通过 `SkillMiddleware` 暴露轻量 skill 简介
- 通过 `load_skill` 工具按需加载 skill 完整内容
- skill 不会在请求开始时全部注入上下文，而是由 agent 在需要时再加载

当前示例包括两类：

- 旅游 skill demo：`POST /api/v1/langgraph-skill`
- SQL assistant on-demand skills demo：`POST /api/v1/langgraph-sql-skill`

其中 SQL assistant 示例更接近官方教程的思路：

- 先暴露可用 skill 列表
- 再由模型决定是否调用 `load_skill`
- 按需加载 `sales_analytics` 或 `inventory_management`

适合验证的问题：

- agent 是否会在需要时调用 `load_skill`
- loaded skill 是否能进入当前 agent state
- 不同领域 skill 是否能被动态切换

## 项目结构图

```text
skill-project
├── main.py
├── skills
│   ├── travel-itinerary
│   │   └── SKILL.md
│   └── travel-shopping
│       └── SKILL.md
├── data
│   └── travel
│       ├── destination-guide.md
│       └── shopping-guide.md
└── skill_project
    ├── api
    │   ├── main.py
    │   ├── deep_agent_api.py
    │   ├── langgraph_api.py
    │   └── schemas.py
    ├── services
    │   └── skill_service.py
    ├── llm
    │   └── openai_client.py
    └── langgraph_skill
        ├── agent.py
        ├── middleware.py
        ├── tools.py
        ├── registry.py
        ├── graph.py
        ├── service.py
        ├── state.py
        └── example_skills
            └── travel_itinerary.py
```

## 调用关系图

### DeepAgents 路径

```text
Client / CLI
    ↓
deep_agent_api.py / main.py
    ↓
skill_service.py
    ↓
create_deep_agent(...)
    ↓
本地 skills 目录
    ├── travel-itinerary
    └── travel-shopping
```

### LangGraph 官方风格路径

```text
Client
    ↓
langgraph_api.py
    ↓
langgraph_skill/service.py
    ↓
create_agent(...)
    ↓
SkillMiddleware
    ↓
load_skill tool
    ↓
按需加载 skill content
```

## 安装依赖

```bash
UV_CACHE_DIR=/tmp/uv-cache uv sync
```

## 配置模型

默认读取 `config/local.toml`。

先编辑配置：

```bash
vim config/local.toml
```

填写模型参数：

```toml
[llm]
default_model = "gpt-4.1-mini"
openai_api_key = "your_key"
openai_base_url = ""
```

如果要切换环境，可以设置：

```bash
export APP_ENV=dev
```

支持的环境：

- `dev`
- `test`
- `local`
- `prod`

## 如何运行验证

### 方式一：启动 FastAPI

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run uvicorn skill_project.api.main:app --reload
```

或者：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m skill_project
```

启动后可访问这些接口：

- `GET /health`
- `GET /api/v1/skills`
- `GET /api/v1/scenarios`
- `POST /api/v1/validate-skill`
- `POST /api/v1/run-scenario`
- `POST /api/v1/langgraph-skill`
- `POST /api/v1/langgraph-sql-skill`

### 方式二：使用 CLI 跑 DeepAgents 场景

查看本地 skills：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py list-skills
```

运行预置场景：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py run --scenario itinerary
```

也可以运行其他场景：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py run --scenario shopping
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py run --scenario dual-skills
```

覆盖默认 prompt：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py run \
  --scenario itinerary \
  --prompt "请读取 data/travel/destination-guide.md，为亲子家庭写一份北海涠洲岛四日轻松行程"
```

## FastAPI 验证示例

### 1. 验证 DeepAgents 自定义 prompt

```bash
curl -X POST http://127.0.0.1:8000/api/v1/validate-skill \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4.1-mini",
    "prompt": "请读取 data/travel/destination-guide.md，为情侣设计一份北海涠洲岛四天三晚行程"
  }'
```

### 2. 验证 DeepAgents 预置场景

```bash
curl -X POST http://127.0.0.1:8000/api/v1/run-scenario \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "dual-skills",
    "model": "gpt-4.1-mini"
  }'
```

### 3. 验证 LangGraph 旅游 skill demo

```bash
curl -X POST http://127.0.0.1:8000/api/v1/langgraph-skill \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "帮我规划一个四天三晚的海岛旅行，并顺便推荐防晒和伴手礼"
  }'
```

### 4. 验证 LangGraph SQL on-demand skills

```bash
curl -X POST http://127.0.0.1:8000/api/v1/langgraph-sql-skill \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4.1-mini",
    "user_request": "帮我写一个按月统计销售额趋势的 SQL"
  }'
```

## 预期验证结果

### DeepAgents

- `validate-skill` 能直接执行自定义 prompt
- `run-scenario` 会读取服务端预置 prompt 再执行
- 旅游相关场景应命中 `travel-itinerary` 或 `travel-shopping`

### LangGraph

- `langgraph-skill` 用于展示 skill routing 的基本骨架
- `langgraph-sql-skill` 会真实请求模型
- SQL 请求应按需加载对应 skill，而不是预先加载全部领域说明

## 说明

- 这个项目的重点是“验证 skill 调用方式”，不是做完整生产功能
- `DeepAgents` 和 `LangGraph` 这两套实现是并行示例，便于横向比较
- 如果执行了 `uv sync`，`uv.lock` 可能变化
