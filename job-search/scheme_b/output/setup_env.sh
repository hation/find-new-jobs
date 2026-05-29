#!/bin/bash
# 方案B执行环境配置脚本

echo "🚀 配置方案B执行环境"
echo "=========================================="

# 设置工作目录
export SCHEME_B_WORKSPACE="/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output"

echo "📁 工作目录: $SCHEME_B_WORKSPACE"
echo ""

# 检查目录存在
if [ ! -d "$SCHEME_B_WORKSPACE" ]; then
    echo "❌ 工作目录不存在: $SCHEME_B_WORKSPACE"
    echo "💡 请先运行迁移脚本"
    exit 1
fi

echo "✅ 环境配置完成"
echo ""
echo "💡 使用技能脚本:"
echo "  cd ~/.openclaw/workspace/skills/job-search/scheme_b"
echo "  python3 scripts/fetch_details_conservative_v2.py"
echo ""
echo "💡 或使用完整工作流:"
echo "  python3 scripts/complete_scheme_b_workflow.py"
