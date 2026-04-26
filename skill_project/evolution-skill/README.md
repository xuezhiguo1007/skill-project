# Evolution Skill

这个目录实现一版最小可运行的 skill 自进化能力。

能力边界：

- 接收当前 query
- 判断是否命中已有 evolved skill
- 如果未命中，则新建 skill
- 如果命中但 query 带来新的关键词或新例子，则更新 skill
- 以本地 JSON 形式持久化到 `generated_skills/evolution/skills`

接口层会统一暴露两个能力：

- 获取当前所有自进化生成的 skills
- 基于当前 query 持续演化 skills

当前实现是启发式版本，不依赖真实 LLM，总体目标是先跑通自进化闭环。
