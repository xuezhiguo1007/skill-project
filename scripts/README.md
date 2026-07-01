# 世界杯预测示例

本目录包含世界杯预测系统的示例脚本。

## 可用脚本

### `one_click_evolution.py` - 一键进化演示
完整的预测 → 记录 → 分析 → 优化流程。

```bash
python scripts/one_click_evolution.py
```

### `predict_and_record.py` - 预测与记录核心库
提供 `WorldCupPredictionRecorder` 类，用于：
- 执行比分预测
- 记录预测结果
- 管理预测历史

### `compare_and_evolve.py` - 评估与进化核心库
提供 `WorldCupPredictionEvaluator` 类，用于：
- 记录真实比赛结果
- 对比预测准确性
- 分析失败案例
- 生成优化建议
- 应用 skill 进化

## 使用示例

### 快速开始

```python
from predict_and_record import WorldCupPredictionRecorder

# 创建记录器
recorder = WorldCupPredictionRecorder()

# 执行预测
prediction = recorder.predict_and_record(
    matchups=["巴西 vs 阿根廷", "法国 vs 德国"],
    model_name="glm-5-no-think-fast"
)

# 查看结果
print(prediction["predictions"])
```

### 评估与优化

```python
from compare_and_evolve import WorldCupPredictionEvaluator

# 创建评估器
evaluator = WorldCupPredictionEvaluator()

# 记录真实结果
evaluator.record_actual_result(
    matchup="巴西 vs 阿根廷",
    actual_score="2-1",
    notes="巴西主场优势明显"
)

# 分析性能
performance = evaluator.analyze_performance()

# 生成优化建议
suggestions = evaluator.generate_optimization_suggestions(performance)

# 应用优化
evaluator.apply_skill_evolution(suggestions)
```

## 数据存储

所有预测结果存储在项目根目录的 `generated_skills/worldcup/predictions/` 中。