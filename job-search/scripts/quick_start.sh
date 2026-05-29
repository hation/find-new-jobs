#!/bin/bash
# 即时工作流快速启动脚本
# 一键完成策略A的完整工作流

echo "🚀 即时工作流快速启动"
echo "========================"

# 检查当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 工作目录: $SCRIPT_DIR"

# 检查必要文件
echo ""
echo "🔍 检查必要文件..."
REQUIRED_FILES=("immediate_workflow.py" "extended_excel_exporter.py" "export_to_excel.py")

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (缺失)"
        exit 1
    fi
done

# 检查Python环境
echo ""
echo "🐍 检查Python环境..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo "✅ $python_version"
else
    echo "❌ Python3未安装"
    exit 1
fi

# 检查boss命令
echo ""
echo "🔧 检查boss-cli..."
export PATH="/Users/xingan/Library/Python/3.12/bin:$PATH"

if command -v boss &> /dev/null; then
    echo "✅ boss命令可用"
else
    echo "❌ boss命令不可用"
    echo "💡 请安装boss-cli: pip3 install kabi-boss-cli"
    echo "💡 或检查PATH设置"
    exit 1
fi

# 显示使用指南
echo ""
echo "📖 使用指南:"
echo "=========="
echo "1. 首先登录BOSS直聘:"
echo "   boss login --cookie-source chrome"
echo ""
echo "2. 验证登录状态:"
echo "   boss status"
echo "   (应该显示: search=ok · recommend=ok)"
echo ""
echo "3. 运行即时工作流:"
echo "   python3 immediate_workflow.py --keyword AI --city 深圳"
echo ""
echo "4. 查看结果:"
echo "   结果会自动保存到 ~/招聘数据/即时采集_时间戳/"
echo ""

# 参数提示
echo "🎯 常用参数:"
echo "  --keyword AI         搜索关键词"
echo "  --city 深圳          目标城市"
echo "  --pages 2            搜索页数"
echo "  --max-details 10     每页最多详情数"
echo "  --delay 2            页间延迟(秒)"
echo ""

# 示例命令
echo "💡 示例命令:"
echo "  python3 immediate_workflow.py --keyword AI --city 深圳 --pages 2 --max-details 10"
echo "  python3 immediate_workflow.py --keyword 人工智能 --city 北京 --pages 1"
echo "  python3 immediate_workflow.py --keyword 机器学习 --city 上海 --pages 3 --delay 3"
echo ""

# 检查当前登录状态
echo "🔍 检查当前登录状态..."
boss_result=$(boss status 2>&1)

if echo "$boss_result" | grep -q "search=ok"; then
    echo "✅ 当前已登录 (search=ok)"
    echo ""
    echo "🎉 可以立即运行工作流!"
    echo "👉 运行: python3 immediate_workflow.py --keyword AI --city 深圳"
else
    echo "⚠️  当前未登录或登录状态异常"
    echo ""
    echo "💡 请先登录:"
    echo "   boss login --cookie-source chrome"
    echo "   然后立即运行工作流"
fi

echo ""
echo "📄 详细指南: cat IMMEDIATE_WORKFLOW_GUIDE.md"
echo "📋 参数帮助: python3 immediate_workflow.py --help"
echo "========================"
echo "✅ 快速启动脚本完成"