# LangGraph Skill Skeleton

这个目录提供一套适合接入现有 LangGraph / LangChain 1.0 项目的最小 skill 骨架。

包含的模块：

- `models.py`: skill 元数据定义
- `registry.py`: skill 注册与匹配
- `tools.py`: `load_skill` on-demand 加载工具
- `middleware.py`: 把 skill 简介注入 system prompt 的 middleware
- `agent.py`: 对齐 LangChain 官方教程的 skill agent 创建方式
- `nodes.py`: skill 路由、上下文加载、结果收口节点
- `example_skills/travel_itinerary.py`: 示例 subgraph skill
- `graph.py`: 一个可编译的 demo graph

建议接入方式：

1. 保留你现有的主图结构。
2. 对上下文型 skill，使用 `SkillMiddleware + load_skill` 实现官方的 on-demand loading。
3. 对稳定流程型 skill，继续使用 subgraph。
4. 把 `build_skill_router_node(...)` 接到你的意图识别或预处理之后，决定是走默认流程、context skill 还是 subgraph。

最小使用示例：

```python
from skill_project.langgraph_skill import build_demo_skill_graph

graph = build_demo_skill_graph()
result = graph.invoke({"user_request": "帮我规划一个四天三晚的北海行程"})
print(result["final_response"])
```

官方 on-demand skills 风格示例：

```python
from langchain_openai import ChatOpenAI
from skill_project.langgraph_skill import create_skill_agent

model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
agent = create_skill_agent(model)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "去海边玩需要准备哪些防晒和伴手礼？"}]},
    config={"configurable": {"thread_id": "demo-thread"}},
)
```
