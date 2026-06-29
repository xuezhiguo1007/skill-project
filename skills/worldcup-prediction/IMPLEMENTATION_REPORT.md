# 世界杯比分预测 Skill 封装完成报告

## 一、封装目标

将用户提供的足球比分预测提示词封装成一个可复用的DeepAgents风格skill，实现以下目标：

1. **自动化识别**：根据用户输入自动触发worldcup-prediction skill
2. **批量处理**：支持多场对阵批量预测
3. **标准化输出**：输出格式符合template.md定义
4. **分层分析**：基于FIFA排名、历史战绩等核心变量进行概率分析

## 二、Skill结构

### 文件清单

```
skills/worldcup-prediction/
├── SKILL.md           # Skill核心定义
├── template.md        # 输出格式模板
├── README.md          # 完整使用文档
├── test-cases.md      # 测试用例文档
└── QUICKSTART.md      # 快速开始指南

data/worldcup/
└── reference-guide.md # 参考资料（FIFA排名体系、洲际层级等）
```

### Skill核心定义（SKILL.md）

包含以下核心内容：

1. **name**: "worldcup-prediction"
2. **description**: 明确触发场景（预测世界杯比分、分析国家队对阵等）
3. **适用场景**: 世界杯小组赛、淘汰赛、批量预测
4. **工作要求**: 必须搜索5个核心变量、必须遵循分层输出格式
5. **分析框架**: 基础参考研判物料 + 核心变量维度
6. **预测原则**: 优先强队不败、极少考虑冷门、给出明确比分
7. **输出前自检**: 6项检查清单

## 三、核心变量分析框架

### 一、基础参考研判物料（固定权重）

- 各国国家队传统硬实力、世界杯历史战绩、大赛声誉、球星阵容底蕴
- 洞际足球层级基准：欧洲 > 南美 > 非洲/中北美及加勒比 > 亚洲

### 二、核心变量维度（优先参考）

必须全部纳入以下维度综合加权：

1. **FIFA官方最新国家队世界排名**
2. **两队历史直接交锋对战记录、胜负平局规律**
3. **双方核心主力球员伤病、红黄牌停赛名单**
4. **本场赛事主客场、中立场地、地理气候场地影响**
5. **两队最近世界杯正式比赛竞技状态、近期士气、攻防数据**

## 四、输出格式规范

### 标准输出结构

```markdown
# 世界杯足球比分预测报告

## [对阵：球队A vs 球队B]

### 基础实力对比
- FIFA排名对比：...
- 洞际足球层级：...
- 球星阵容底蕴：...

### 核心变量分析
1. **FIFA排名**：...
2. **历史交锋**：...
3. **球员状态**：...
4. **场地影响**：...
5. **近期状态**：...

### 预测结论
- **风格定义**：...
- **胜负平倾向**：...
- **概率区间**：...
- **核心依据**：...
- **预测比分**：...

---

## 预测汇总表

| 对阵 | 预测比分 | 胜负倾向 | 概率区间 |
|------|---------|---------|---------|
| ... | ... | ... | ... |
```

## 五、集成方式

### 1. DeepAgents集成

已更新 `skill_project/services/skill_service.py`：

- 添加 `worldcup-prediction` 场景到 `SCENARIOS`
- 更新 `system_prompt` 以支持世界杯预测场景
- skill通过 `skills=["/skills"]` 自动挂载

### 2. CLI调用支持

```bash
# 预置场景
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py run --scenario worldcup-prediction

# 自定义对阵
UV_CACHE_DIR=/tmp/uv-cache uv run python main.py run \
  --scenario worldcup-prediction \
  --prompt "请预测世界杯对阵比分：巴西 vs 阿根廷、法国 vs 德国"
```

### 3. FastAPI调用支持

```bash
# 预置场景
curl -X POST http://127.0.0.1:8000/api/v1/run-scenario \
  -H "Content-Type: application/json" \
  -d '{"scenario": "worldcup-prediction", "model": "gpt-4.1-mini"}'

# 自定义对阵
curl -X POST http://127.0.0.1:8000/api/v1/validate-skill \
  -H "Content-Type: application/json" \
  -d '{"prompt": "请预测世界杯对阵比分：日本 vs 韩国"}'
```

### 4. Python代码调用

```python
from skill_project.services.skill_service import run_validation

result = run_validation(
    prompt="请预测世界杯对阵比分：巴西 vs 阿根廷、法国 vs 德国",
    model_name="gpt-4.1-mini"
)
print(result["response"])
```

## 六、Skill验证

### 验证结果

```bash
$ UV_CACHE_DIR=/tmp/uv-cache uv run python main.py list-skills

[
  {
    "name": "worldcup-prediction",
    "description": "当任务需要预测世界杯足球比赛比分、分析国家队对阵胜负、生成足球赛事概率预测时使用...",
    "path": "skills/worldcup-prediction"
  },
  ...
]
```

✅ Skill已被正确识别和注册。

## 七、文档体系

### 1. QUICKSTART.md
- 一分钟快速体验指南
- 3种调用方式示例
- 输出示例展示
- 常见问题解答

### 2. README.md
- 完整功能介绍
- 详细使用方法
- 输出格式说明
- 预测风格定义
- 扩展建议

### 3. test-cases.md
- 6个完整测试用例
- 测试执行方法
- 成功/失败判定标准
- 测试记录模板

### 4. template.md
- 标准输出结构模板
- 必需章节定义

### 5. reference-guide.md
- FIFA排名体系
- 洞际足球层级基准
- 世界杯历史战绩
- 比赛影响因素

## 八、技术特性

### DeepAgents风格实现

- 使用 `create_deep_agent(...)` 创建智能代理
- 本地skills自动命中：`skills=["/skills"]`
- 根据prompt内容自动触发对应skill
- 支持批量处理多场对阵

### 核心优势

1. **自动化触发**：description字段准确描述触发场景
2. **标准化输出**：template.md定义严格输出格式
3. **分层分析**：基于5个核心变量的综合加权
4. **明确比分**：不使用模糊表述，给出具体比分
5. **概率区间**：标注胜负平倾向和概率百分比

## 九、使用场景

### 适用场景

- 世界杯小组赛比分预测
- 世界杯淘汰赛比分预测
- 多场对阵批量预测
- 基于数据分析的胜负概率研究

### 输入示例

```
请预测世界杯对阵比分：
巴西 vs 阿根廷
法国 vs 德国
英格兰 vs 西班牙
```

### 输出特点

1. 每场对阵完整分析
2. 包含5个核心变量分析
3. 给出明确预测比分（建议一个，不确定时可输出两个）
4. 包含胜负平倾向和概率区间
5. 自动生成预测汇总表

## 十、后续优化建议

### 短期优化

1. 添加更多实时数据源（如球队官网、FIFA官网）
2. 支持其他赛事预测（欧冠、联赛、杯赛）
3. 优化概率计算算法

### 中期优化

1. 引入机器学习模型优化预测准确率
2. 添加历史预测准确率统计
3. 支持自定义预测权重

### 长期优化

1. 集成实时比赛数据API
2. 支持多语言输出
3. 添加可视化图表输出
4. 支持团队协作和共享预测

## 十一、总结

### 完成内容

✅ 创建完整的skill文件结构
✅ 定义清晰的skill触发机制
✅ 建立标准化输出格式
✅ 编写完整的使用文档
✅ 设计6个测试用例
✅ 集成到DeepAgents框架
✅ 支持CLI、API、Python多种调用方式
✅ 验证skill正确识别和注册

### 核心价值

1. **复用性**：一次封装，多次使用
2. **标准化**：输出格式统一，易于理解
3. **自动化**：根据输入自动触发，无需手动指定
4. **专业性**：基于FIFA排名等权威数据进行分析
5. **灵活性**：支持单场预测和批量预测

### 使用建议

1. 阅读 `QUICKSTART.md` 快速上手
2. 参考 `README.md` 了解详细功能
3. 执行 `test-cases.md` 验证功能
4. 根据实际需求调整 `SKILL.md` 预测原则

---

**Skill封装完成！可以立即开始使用！**