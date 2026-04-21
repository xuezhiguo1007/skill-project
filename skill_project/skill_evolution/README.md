# Skill Evolution

这个模块提供一版最小的“自生成 skill + 审批 + 回放评测 + 上线”骨架，目标是先把闭环搭起来，而不是一步到位做复杂自动优化。

目录说明：

- `models.py`: 轨迹、候选 skill、审批记录、回放报告
- `generator.py`: 从成功轨迹蒸馏出 `SKILL.md`
- `storage.py`: 本地仓库存储，保存 `candidate / approved / active / report`
- `evaluator.py`: 回放评测器，默认使用轻量模拟 executor
- `service.py`: 串起完整流程
- `bridge.py`: 把 `active` skill 转成现有 `SkillSpec`

默认仓库目录：

```text
generated_skills/
├── active/
├── approved/
├── candidates/
├── rejected/
└── reports/
```

最小示例：

```python
from skill_project.skill_evolution import ReplayCase, SkillEvolutionService, TaskTrajectory

service = SkillEvolutionService()
candidate = service.create_candidate(
    [
        TaskTrajectory(
            request="帮我整理销售 SQL 分析步骤",
            final_response="先确认指标，再确定粒度和过滤条件。",
            tools_used=["load_skill"],
            tags=["sql", "sales"],
        )
    ],
    skill_name="sales_sql_playbook",
)

service.approve_candidate(candidate.candidate_id, reviewer="alice")
report = service.replay_candidate(
    candidate.candidate_id,
    [
        ReplayCase(
            request="统计最近 30 天订单 GMV 趋势",
            expected_keywords=["goal", "procedure", "verification"],
        )
    ],
)
if report.passed:
    service.promote_candidate(candidate.candidate_id, report_id=report.report_id)
```

这版实现有意保持保守：

- 不在当前 session 热更新 skill
- 默认要求先审批，再评测，再 promote
- 回放 executor 是可替换的，后续可以接真实 LangGraph agent
