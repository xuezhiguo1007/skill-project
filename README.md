# DeepAgents Skills Verification

这个项目基于 `deepagents` 做了一个最小中文示例，用来验证三件事：

1. 主代理可以根据任务自动命中本地中文 `skill`
2. 同一个项目里可以配置多个 `skill`，并通过一个场景模拟连续调用两个 `skill`
3. 你可以通过 CLI 或 FastAPI 直接触发一次验证

## 项目结构

- `main.py`: CLI 入口，支持列出 skills 和运行验证场景
- `skill_project/api/main.py`: FastAPI 入口，结构参考 `enowa-memory`
- `skill_project/api/schemas.py`: API 请求/响应模型
- `skill_project/api/lifespan.py`: 生命周期管理
- `skill_project/services/skill_service.py`: skill 调用与场景执行逻辑
- `skills/travel-itinerary`: 中文旅游行程规划 skill
- `skills/travel-shopping`: 中文旅游商品推荐 skill
- `data/travel/destination-guide.md`: 行程规划场景的中文输入数据
- `data/travel/shopping-guide.md`: 商品推荐场景的中文输入数据

## 安装依赖

```bash
UV_CACHE_DIR=/tmp/uv-cache uv sync
```

## 配置模型

```bash
export OPENAI_API_KEY=your_key
```

默认模型是 `gpt-4.1-mini`，也可以通过 `--model` 覆盖。

## 启动 FastAPI

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run uvicorn skill_project.api.main:app --reload
```

或者使用和 `enowa-memory` 一致的 `main` 启动方式：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m skill_project
```

启动后可访问：

- `GET /health`
- `GET /api/v1/skills`
- `GET /api/v1/scenarios`
- `POST /api/v1/validate-skill`
- `POST /api/v1/run-scenario`

直接验证任意提示词：

```bash
curl -X POST http://127.0.0.1:8000/api/v1/validate-skill \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4.1-mini",
    "prompt": "请读取 data/travel/destination-guide.md，为情侣设计一份北海涠洲岛四天三晚行程"
  }'
```

场景接口示例：

```bash
curl -X POST http://127.0.0.1:8000/api/v1/run-scenario \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "shopping"
  }'
```

双 skill 场景接口示例：

```bash
curl -X POST http://127.0.0.1:8000/api/v1/run-scenario \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "dual-skills"
  }'
```

## 查看已配置 skills

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py list-skills
```

## 验证场景 1: 命中 `travel-itinerary` skill

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py run --scenario itinerary
```

预期现象：

- 结果结构会遵循 `skills/travel-itinerary/template.md`
- 内容会基于 `data/travel/destination-guide.md`
- 输出会是中文、可执行的逐日旅行计划

## 验证场景 2: 命中 `travel-shopping` skill

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py run --scenario shopping
```

预期现象：

- 代理会处理旅行商品推荐和预算取舍
- 输出结构会遵循 `skills/travel-shopping/recommendation-template.md`
- 推荐内容会参考 `data/travel/shopping-guide.md`

## 验证场景 3: 模拟连续调用两个 skills

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py run --scenario dual-skills
```

预期现象：

- 输出中会同时包含“旅游行程规划”和“旅游商品推荐”两部分
- 第一部分会参考 `travel-itinerary` skill
- 第二部分会参考 `travel-shopping` skill

## 自定义提示词

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py run \
  --scenario itinerary \
  --prompt "请读取 data/travel/destination-guide.md，为亲子家庭写一份北海涠洲岛四日轻松行程"
```

## 说明

- 这个仓库当前没有提交锁文件更新；如果你执行了 `uv sync`，`uv.lock` 可能会变化。
- 如果你想继续验证更多 skills，直接在 `skills/` 下新增目录和 `SKILL.md`，再把路径接到 `create_deep_agent(...)` 即可。
