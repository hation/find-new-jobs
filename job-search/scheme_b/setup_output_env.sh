#!/bin/bash
# 方案B输出目录环境配置

echo "🚀 配置方案B输出目录环境"
echo "=========================================="

# 设置工作目录到技能output目录
export SCHEME_B_WORKSPACE="/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output"

echo "📁 工作目录: $SCHEME_B_WORKSPACE"
echo ""

# 检查目录存在
if [ ! -d "$SCHEME_B_WORKSPACE" ]; then
    echo "❌ 工作目录不存在: $SCHEME_B_WORKSPACE"
    echo "💡 请先创建目录或运行迁移脚本"
    exit 1
fi

echo "✅ 环境配置完成"
echo ""
echo "💡 现在可以直接使用技能脚本:"
echo "  python3 scripts/fetch_details_conservative_v2.py"
echo "  python3 scripts/fetch_details_smart_v2.py"
echo "  python3 scripts/complete_scheme_b_workflow.py"
echo ""
echo "💡 所有输出将保存在: $SCHEME_B_WORKSPACE"
