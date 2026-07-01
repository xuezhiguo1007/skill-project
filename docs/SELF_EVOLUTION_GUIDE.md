# 世界杯预测自进化系统使用指南

## 系统概述

这是一个完整的世界杯比分预测自进化系统，包含三个核心环节：

1. **预测记录**：执行预测并保存结果
2. **结果对比**：记录真实比分，评估预测准确率
3. **Skill优化**：分析失败案例，自动生成优化建议并更新Skill

## 工作流程图

```
┌──────────────┐
│ 执行预测     │ predict_and_record.py
│ 记录结果     │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ 真实比赛结果 │ compare_and_evolve.py --record-result
│ 记录与对比   │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ 性能分析     │ compare_and_evolve.py --analyze
│ 失败案例提取 │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ 优化建议生成 │ compare_and_evolve.py --optimize
│ Skill更新    │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ 循环迭代     │ 重复预测 → 验证 → 优化
│ 持续进化     │
└──────────────┘
```

## 脚本一：predict_and_record.py

### 功能

- 执行世界杯比分预测
- 自动记录预测结果到JSON文件
- 支持多场对阵批量预测
- 支持自定义模型和prompt

### 使用方法

#### 1. 执行预测

```bash
# 预测单场对阵
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/predict_and_record.py \
  --matchups "巴西 vs 阿根廷"

# 预测多场对阵
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/predict_and_record.py \
  --matchups "巴西 vs 阿根廷" "法国 vs 德国" "英格兰 vs 西班牙"

# 使用特定模型
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/predict_and_record.py \
  --matchups "日本 vs 韩国" \
  --model "gpt-4"

# 自定义prompt
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/predict_and_record.py \
  --matchups "巴西 vs 阿根廷" \
  --prompt "请重点考虑双方核心球员的伤病情况和近期状态..."
```

#### 2. 查看历史记录

```bash
# 列出所有预测记录
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/predict_and_record.py --list

# 列出待验证的预测记录
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/predict_and_record.py --pending
```

#### 3. 输出文件结构

预测记录保存在 `generated_skills/worldcup/predictions/prediction_YYYYMMDD_HHMMSS.json`

```json
{
  "timestamp": "2026-06-29T10:30:00",
  "model": "gpt-4.1-mini",
  "matchups": ["巴西 vs 阿根廷", "法国 vs 德国"],
  "prompt": "请预测以下世界杯对阵...",
  "response": "完整的预测响应文本...",
  "predictions": {
    "巴西 vs 阿根廷": {
      "predicted_score": "2-1",
      "tendency": "主胜",
      "probability_range": "45%-55%",
      "confidence": null,
      "raw_response": "..."
    }
  },
  "status": "pending"
}
```

---

## 脚本二：compare_and_evolve.py

### 功能

- 记录真实比赛结果
- 对比预测与实际结果
- 计算预测准确率
- 分析失败案例
- 生成优化建议
- 自动更新Skill文件

### 使用方法

#### 1. 记录真实结果

```bash
# 记录单场结果
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py \
  --record-result "巴西 vs 阿根廷" "2-1"

# 记录结果并添加日期和备注
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py \
  --record-result "巴西 vs 阿根廷" "2-1" \
  --match-date "2026-06-29" \
  --notes "阿根廷主力前锋受伤，影响发挥"
```

#### 2. 分析预测性能

```bash
# 分析所有预测记录的性能
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py --analyze
```

#### 3. 生成优化建议

```bash
# 分析性能并生成优化建议
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py \
  --analyze --optimize
```

#### 4. 应用优化建议

```bash
# 分析、优化、自动应用
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py \
  --analyze --optimize --apply
```

#### 5. 完整流程（一步执行）

```bash
# 默认执行：分析 → 优化 → 提示应用
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py
```

---

## 完整使用流程示例

### 场景：预测世界杯小组赛

#### 步骤1：执行预测

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/predict_and_record.py \
  --matchups "巴西 vs 阿根廷" "法国 vs 德国" "英格兰 vs 西班牙"

# 输出：
✅ 预测完成！
记录文件: generated_skills/worldcup/predictions/prediction_20260629_103000.json

预测结果摘要:
  巴西 vs 阿根廷: 2-1 (主胜)
  法国 vs 德国: 1-1 (平局)
  英格兰 vs 西班牙: 1-0 (主胜)
```

#### 步骤2：等待比赛结束，记录真实结果

```bash
# 巴西 vs 阿根廷 实际比分 2-1
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py \
  --record-result "巴西 vs 阿根廷" "2-1" \
  --notes "梅西状态出色"

# 法国 vs 德国 实际比分 0-1
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py \
  --record-result "法国 vs 德国" "0-1" \
  --notes "德国防守反击成功"

# 英格兰 vs 西班牙 实际比分 1-1
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py \
  --record-result "英格兰 vs 西班牙" "1-1"
```

#### 步骤3：分析性能

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py --analyze

# 输出：
📊 预测性能分析报告
总预测数: 3
完全准确: 1 (33.3%)
胜负方向正确: 2 (66.7%)
粗略正确: 0
预测错误: 1
解析错误: 0

❌ 失败案例:
  - 法国 vs 德国: 预测1-1, 实际0-1
```

#### 步骤4：生成优化建议

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py \
  --analyze --optimize

# 输出：
🔄 正在生成优化建议...

✅ 优化建议已生成！
建议文件: generated_skills/worldcup/evolution/suggestions_20260629_110000.md

# 性能问题诊断
当前预测准确率中等，主要问题：
- 对防守反击战术预测不足
- 过度依赖FIFA排名和纸面实力
- ...

# 核心优化建议
1. 增加"战术风格分析"变量
2. 调整强队对决的平局预测权重
3. ...

# SKILL.md更新建议
在"核心变量分析"部分添加：
- 6. 战术风格匹配度分析
...

# reference-guide.md更新建议
添加"战术风格类型"章节：
- 防守反击型球队特点
- ...
```

#### 步骤5：应用优化

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py \
  --analyze --optimize --apply

# 输出：
🤖 是否要自动应用这些优化建议？
请选择：
1. 自动更新SKILL.md
2. 自动更新reference-guide.md
3. 同时更新两个文件
4. 手动查看建议，暂不更新
5. 退出

请输入选择 (1-5): 3

🔄 正在更新文件: skills/worldcup-prediction/SKILL.md
✅ 文件已更新！
备份文件: skills/worldcup-prediction/SKILL_backup_20260629_110000.md
更新文件: skills/worldcup-prediction/SKILL.md

🔄 正在更新文件: data/worldcup/reference-guide.md
✅ 文件已更新！
备份文件: data/worldcup/reference-guide_backup_20260629_110000.md
更新文件: data/worldcup/reference-guide.md
```

#### 步骤6：循环迭代

继续预测新的对阵，重复步骤1-5，持续优化Skill。

---

## 预测准确度评级

系统使用以下标准评估预测准确度：

### 1. exact_match（完全准确）
预测比分与实际比分完全一致。

例如：
- 预测：2-1
- 实际：2-1

### 2. tendency_match（胜负方向正确）
预测的胜负方向正确，进球数差距≤1。

例如：
- 预测：2-1
- 实际：1-0（主队胜，进球差1）

### 3. rough_match（粗略正确）
胜负方向正确，进球数差距≤2。

例如：
- 预测：2-1
- 实际：3-0（主队胜，进球差2）

### 4. wrong_prediction（预测错误）
胜负方向错误。

例如：
- 预测：2-1（主胜）
- 实际：0-1（客胜）

### 5. parse_error（解析错误）
无法解析预测结果。

---

## 数据目录结构

```
generated_skills/worldcup/
├── predictions/              # 预测记录
│   ├── prediction_20260629_103000.json
│   ├── prediction_20260629_113000.json
│   └── ...
├── results/                  # 真实结果记录
│   ├── result_20260629_120000.json
│   ├── result_20260629_123000.json
│   └── ...
└── evolution/                # 优化进化记录
    ├── performance_20260629_110000.json
    ├── suggestions_20260629_110000.md
    ├── suggestions_20260629_130000.md
    └── ...
```

---

## 自进化机制

### 1. 数据驱动优化

基于实际比赛结果而非主观判断进行优化。

### 2. 失败案例学习

重点分析预测失败案例，提取关键失败原因。

### 3. 多维度优化

优化建议涵盖：
- 预测逻辑调整
- 数据源补充
- 输出格式优化
- 核心变量权重调整
- 新规则补充

### 4. 自动化流程

从分析到优化建议生成，再到Skill更新，自动化完成。

### 5. 版本追溯

每次更新保留备份文件，可追溯历史版本。

### 6. 循环迭代

通过持续预测→验证→优化循环，不断提升预测准确率。

---

## 高级功能

### 1. 批量预测与验证

```bash
# 执行批量预测
python scripts/predict_and_record.py \
  --matchups "巴西 vs 阿根廷" "法国 vs 德国" "英格兰 vs 西班牙" "日本 vs 韩国"

# 批量记录结果（通过脚本自动化）
for matchup in "巴西 vs 阿根廷 2-1" "法国 vs 德国 0-1"; do
  python scripts/compare_and_evolve.py --record-result $matchup
done
```

### 2. 性能监控

定期执行性能分析，监控准确率变化：

```bash
# 每周执行一次性能分析
python scripts/compare_and_evolve.py --analyze
```

### 3. 定向优化

针对特定类型的失败案例进行定向优化：

```bash
# 记录失败案例时添加详细备注
python scripts/compare_and_evolve.py \
  --record-result "法国 vs 德国" "0-1" \
  --notes "德国采用防守反击战术，法国高位逼抢失败，防线被打穿"
```

---

## 最佳实践建议

### 1. 预测阶段

- 使用统一的预测模型，便于对比
- 预测时记录详细的对阵信息
- 保持prompt结构一致

### 2. 验证阶段

- 及时记录真实结果，避免遗忘
- 添加详细的备注说明比赛关键因素
- 记录比赛日期便于后续分析

### 3. 优化阶段

- 定期执行性能分析（建议每周）
- 关注失败案例的共同特征
- 审慎应用优化建议，必要时手动调整

### 4. 迭代阶段

- 保持预测→验证→优化的循环节奏
- 监控准确率变化趋势
- 积累足够案例后再调整核心逻辑

---

## 常见问题

### Q1: 预测记录文件太多怎么办？

定期清理旧记录，或移动到历史目录：

```bash
# 创建历史目录
mkdir -p generated_skills/worldcup/predictions/history

# 移动30天前的记录
find generated_skills/worldcup/predictions -name "prediction_*.json" -mtime +30 \
  -exec mv {} generated_skills/worldcup/predictions/history/ \;
```

### Q2: 如何回滚错误的Skill更新？

使用备份文件恢复：

```bash
# 查看备份文件
ls skills/worldcup-prediction/SKILL_backup_*.md

# 恢复到指定版本
cp skills/worldcup-prediction/SKILL_backup_20260629_110000.md \
   skills/worldcup-prediction/SKILL.md
```

### Q3: 如何调整优化建议生成逻辑？

修改 `compare_and_evolve.py` 中的 `generate_optimization_suggestions` 方法的prompt。

### Q4: 如何添加新的评估指标？

修改 `_calculate_accuracy` 方法，添加新的准确度评级标准。

---

## 技术实现细节

### 1. 预测记录脚本（predict_and_record.py）

核心类：`WorldCupPredictionRecorder`

主要方法：
- `predict_and_record()`: 执行预测并记录
- `_parse_predictions()`: 解析预测结果
- `_save_record()`: 保存JSON记录
- `list_predictions()`: 列出所有记录
- `get_pending_predictions()`: 获取待验证记录

### 2. 对比优化脚本（compare_and_evolve.py）

核心类：`WorldCupPredictionEvaluator`

主要方法：
- `record_actual_result()`: 记录真实结果
- `_calculate_accuracy()`: 计算预测准确度
- `analyze_performance()`: 分析整体性能
- `generate_optimization_suggestions()`: 生成优化建议
- `apply_skill_evolution()`: 应用优化更新

---

## 扩展建议

### 1. 添加更多数据源

- 集成FIFA官网API获取实时排名
- 连接比赛数据API获取历史战绩
- 添加球员数据库获取伤病信息

### 2. 优化解析逻辑

- 使用更强大的NLP模型解析预测结果
- 提取更多结构化信息（如核心依据）
- 支持多语言输出解析

### 3. 增强优化机制

- 实现多轮优化对话
- 支持用户手动编辑优化建议
- 添加优化效果预测和验证

### 4. 可视化展示

- 添加预测准确率趋势图表
- 失败案例可视化分析
- 优化建议可视化对比

---

**系统已完成！可以立即开始使用自进化世界杯预测系统！** 🎉