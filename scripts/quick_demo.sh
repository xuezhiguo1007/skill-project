#!/bin/bash

# 世界杯预测自进化系统 - 快速演示脚本

echo "================================================"
echo "世界杯预测自进化系统 - 完整流程演示"
echo "================================================"
echo ""

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 步骤1：执行预测
echo -e "${BLUE}步骤1：执行预测${NC}"
echo "正在预测世界杯对阵：巴西 vs 阿根廷、法国 vs 德国"
echo ""

UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/predict_and_record.py \
  --matchups "巴西 vs 阿根廷" "法国 vs 德国"

echo ""
echo -e "${GREEN}✅ 预测完成！${NC}"
echo ""

# 步骤2：模拟记录真实结果
echo -e "${BLUE}步骤2：记录真实比赛结果（模拟）${NC}"
echo "假设比赛已结束，记录真实比分..."
echo ""

echo -e "${YELLOW}巴西 vs 阿根廷 实际比分：2-1${NC}"
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py \
  --record-result "巴西 vs 阿根廷" "2-1" \
  --notes "梅西状态出色，带领阿根廷获胜" >/dev/null 2>&1

echo -e "${YELLOW}法国 vs 德国 实际比分：0-1${NC}"
UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py \
  --record-result "法国 vs 德国" "0-1" \
  --notes "德国防守反击成功，法国高位逼抢失败" >/dev/null 2>&1

echo ""
echo -e "${GREEN}✅ 真实结果已记录！${NC}"
echo ""

# 步骤3：分析性能
echo -e "${BLUE}步骤3：分析预测性能${NC}"
echo ""

UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/compare_and_evolve.py --analyze

echo ""

# 步骤4：查看历史记录
echo -e "${BLUE}步骤4：查看预测历史记录${NC}"
echo ""

UV_CACHE_DIR=/tmp/uv-cache uv run python scripts/predict_and_record.py --list

echo ""

# 步骤5：查看优化建议（仅生成，不应用）
echo -e "${BLUE}步骤5：生成优化建议（不自动应用）${NC}"
echo ""

echo -e "${YELLOW}提示：完整流程包括自动应用优化建议${NC}"
echo "如需完整体验，请运行："
echo "  python scripts/compare_and_evolve.py --analyze --optimize --apply"
echo ""

echo "================================================"
echo -e "${GREEN}演示完成！${NC}"
echo "================================================"
echo ""
echo "后续操作："
echo "1. 查看预测记录：generated_skills/worldcup/predictions/"
echo "2. 查看结果记录：generated_skills/worldcup/results/"
echo "3. 手动运行完整优化：python scripts/compare_and_evolve.py"
echo "4. 查看详细文档：scripts/SELF_EVOLUTION_GUIDE.md"
echo ""