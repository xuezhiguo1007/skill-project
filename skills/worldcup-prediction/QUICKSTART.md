# 世界杯比分预测 Skill - 快速开始

## 一分钟快速体验

### 方式1：CLI命令（最简单）

```bash
# 进入项目目录
cd /Users/xuezhiguo/PycharmProjects/skill-project

# 运行预置的世界杯预测场景
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py run --scenario worldcup-prediction
```

### 方式2：自定义对阵

```bash
# 预测你指定的对阵
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py run \
  --scenario worldcup-prediction \
  --prompt "请预测世界杯对阵比分：日本 vs 韩国、美国 vs 墨西哥"
```

### 方式3：启动API服务

```bash
# 启动FastAPI服务
UV_CACHE_DIR=/tmp/uv-cache uv run uvicorn skill_project.api.main:app --reload

# 在另一个终端调用API
curl -X POST http://127.0.0.1:8000/api/v1/run-scenario \
  -H "Content-Type: application/json" \
  -d '{"scenario": "worldcup-prediction", "model": "gpt-4.1-mini"}'
```

## 输出示例

运行后会得到如下格式的输出：

```markdown
# 世界杯足球比分预测报告

## [对阵：巴西 vs 阿根廷]

### 基础实力对比
- FIFA排名对比：巴西第1位，阿根廷第3位
- 洞际足球层级：南美第一梯队
- 球星阵容底蕴：巴西拥有内马尔、维尼修斯；阿根廷拥有梅西、迪马利亚

### 核心变量分析
1. **FIFA排名**：巴西排名领先，纸面实力更强
2. **历史交锋**：近10场交锋巴西5胜3平2负
3. **球员状态**：双方核心球员状态良好
4. **场地影响**：中立场地
5. **近期状态**：巴西3连胜，阿根廷2胜1平

### 预测结论
- **风格定义**：平衡型
- **胜负平倾向**：主胜（巴西胜）倾向
- **概率区间**：巴西胜45%-55%，平局25%-30%，阿根廷胜20%-25%
- **核心依据**：FIFA排名领先、历史交锋优势、近期状态出色
- **预测比分**：2-1 或 1-1

---

## 预测汇总表

| 对阵 | 预测比分 | 胜负倾向 | 概率区间 |
|------|---------|---------|---------|
| 巴西 vs 阿根廷 | 2-1 或 1-1 | 巴西胜 | 45%-55% |
| 法国 vs 德国 | 1-1 或 2-1 | 法国胜 | 40%-50% |
| 英格兰 vs 西班牙 | 1-0 或 1-1 | 英格兰胜 | 35%-45% |
```

## 核心功能

### 1. 多场对阵批量预测
支持一次性预测多场对阵，自动生成汇总表。

### 2. 分层概率分析
基于5个核心变量进行综合分析：
- FIFA排名
- 历史交锋记录
- 球员伤病状态
- 场地气候影响
- 近期竞技状态

### 3. 明确比分输出
每场对阵给出明确比分预测，不含糊。

### 4. 概率区间标注
给出胜负平倾向和对应概率区间。

## Skill识别验证

```bash
# 查看所有可用skills
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py list-skills

# 输出中应包含 worldcup-prediction
```

## 文件结构

```
skills/worldcup-prediction/
├── SKILL.md           # Skill定义文件
├── template.md        # 输出格式模板
├── README.md          # 使用文档
└── test-cases.md      # 测试用例

data/worldcup/
└── reference-guide.md # 参考资料
```

## 配置要求

确保 `config/local.toml` 配置正确：

```toml
[llm]
default_model = "gpt-4.1-mini"
openai_api_key = "your_key"
openai_base_url = ""
```

## 常见问题

### Q1: Skill未被触发怎么办？
检查SKILL.md的description字段是否准确描述了触发场景。

### Q2: 输出格式不完整怎么办？
对照template.md检查输出结构是否完整。

### Q3: 如何添加更多数据？
编辑 `data/worldcup/reference-guide.md` 添加更多参考资料。

### Q4: 如何修改预测逻辑？
编辑 `skills/worldcup-prediction/SKILL.md` 中的预测原则。

## 下一步

- 查看完整文档：`skills/worldcup-prediction/README.md`
- 查看测试用例：`skills/worldcup-prediction/test-cases.md`
- 查看参考资料：`data/worldcup/reference-guide.md`

## 技术实现

基于DeepAgents风格实现：

- 使用 `create_deep_agent(...)` 创建智能代理
- 本地skills目录：`skills=["/skills"]`
- 根据prompt自动命中对应skill
- 支持多场对阵批量处理

## 预测原则

1. 完全依托纸面硬实力、排名、历史战绩
2. 优先强队不败，极少考虑冷门
3. 兼顾实力与客观变数（伤病、停赛、场地、士气）
4. 每场对阵给出明确比分

## 注意事项

- 预测结果仅供参考
- 实际比赛结果可能受临场变数影响
- Skill会主动搜索最新数据
- 建议结合实际情况和个人判断使用