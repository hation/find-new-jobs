#!/bin/bash
# 美团招聘爬取项目启动脚本
# 基于夸克项目完整架构

set -e

echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│        🚀 美团招聘爬取项目启动                         │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│ 项目: 美团招聘数据爬取"
echo "│ 公司: 美团"
echo "│ 类型: crawler"
echo "│ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "└─────────────────────────────────────────────────────────┘"
echo ""

# 检查是否在项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "📋 项目概述:"
echo "基于夸克项目的完整架构，包含三个层次:"
echo "  1. 📚 知识层 - 文档模板 + 记忆系统"
echo "  2. 🔧 框架层 - 业务实现框架"
echo "  3. ⚙️ 配置层 - 配置模板 + 环境配置"
echo ""

echo "🔍 第一步: 环境检查"
echo "----------------------------------------"
# 检查Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo "✅ Python3: $PYTHON_VERSION"
else
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "📦 检查Python依赖..."
if [ -f "requirements.txt" ]; then
    echo "  发现依赖文件: requirements.txt"
    
    # 检查是否已安装主要依赖
    if python3 -c "import requests" 2>/dev/null; then
        echo "  ✅ requests 已安装"
    else
        echo "  ❌ requests 未安装"
        NEED_INSTALL=true
    fi
    
    if python3 -c "import pandas" 2>/dev/null; then
        echo "  ✅ pandas 已安装"
    else
        echo "  ❌ pandas 未安装"
        NEED_INSTALL=true
    fi
    
    if python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
        echo "  ✅ playwright 已安装"
    else
        echo "  ❌ playwright 未安装"
        NEED_INSTALL=true
    fi
    
    if [ "$NEED_INSTALL" = true ]; then
        read -p "是否安装缺失的依赖？(Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            echo "🔄 安装Python依赖..."
            pip3 install -r requirements.txt
        fi
    fi
else
    echo "⚠️ 未找到requirements.txt文件"
fi

echo ""
echo "🔧 第二步: 配置检查"
echo "----------------------------------------"
# 检查环境配置
if [ -f "config/.env" ]; then
    echo "✅ 环境配置: config/.env 已存在"
    # 显示关键配置
    echo "  关键配置:"
    grep -E "^(PROJECT_NAME|COMPANY_NAME|WEBSITE_URL|MEITUAN)" config/.env | head -10
else
    echo "⚠️ 环境配置: config/.env 不存在"
    if [ -f "config/.env.example" ]; then
        read -p "是否从示例文件创建配置？(Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            cp config/.env.example config/.env
            echo "✅ 已创建 config/.env，请编辑文件设置你的配置"
        fi
    fi
fi

# 检查项目配置
if [ -f "config/project_config.json" ]; then
    echo "✅ 项目配置: config/project_config.json 已存在"
else
    echo "❌ 项目配置: config/project_config.json 不存在"
fi

echo ""
echo "📚 第三步: 架构验证"
echo "----------------------------------------"
if [ -f "scripts/validate_complete_architecture.py" ]; then
    read -p "是否验证项目完整架构？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo "🔍 运行架构验证..."
        python3 scripts/validate_complete_architecture.py
    fi
else
    echo "⚠️ 架构验证脚本不存在"
fi

echo ""
echo "🔧 第四步: 美团爬取器"
echo "----------------------------------------"
echo "可用命令:"
echo "1. 测试连接:"
echo "   python3 src/meituan_crawler.py --mode test"
echo ""
echo "2. 浏览器爬取:"
echo "   python3 src/meituan_crawler.py --mode browser"
echo ""
echo "3. 智能爬取:"
echo "   python3 src/meituan_crawler.py --mode smart"
echo ""
echo "4. 查看公司信息:"
echo "   python3 src/meituan_crawler.py --mode test | grep -A20 '公司信息'"
echo ""
echo "5. 自定义URL爬取:"
echo "   python3 src/meituan_crawler.py --mode browser --url '你的URL'"
echo ""

echo "🚀 第五步: 立即开始"
echo "----------------------------------------"
echo "推荐步骤:"
echo "1. 测试连接: python3 src/meituan_crawler.py --mode test"
echo "2. 浏览器爬取: python3 src/meituan_crawler.py --mode browser"
echo "3. 查看数据: ls -la output/crawl_data/"
echo "4. 分析结果: 查看生成的JSON/CSV文件"
echo ""

echo "💡 提示:"
echo "• 首次运行浏览器模式可能需要安装浏览器驱动:"
echo "  python3 -m playwright install"
echo ""
echo "• 如果浏览器启动失败，尝试更新配置:"
echo "  编辑 config/.env，设置 HEADLESS_MODE=false"
echo ""
echo "• 查看详细日志:"
echo "  python3 src/meituan_crawler.py --mode browser --verbose"
echo ""

echo "📊 第六步: 数据导出"
echo "----------------------------------------"
echo "爬取完成后，数据会自动保存到:"
echo "• JSON格式: output/crawl_data/meituan_positions_*.json"
echo "• CSV格式: output/crawl_data/meituan_positions_*.csv"
echo ""
echo "可以使用以下工具进一步处理:"
echo "• Excel: 直接打开CSV文件"
echo "• Python: 使用pandas处理JSON/CSV"
echo "• 数据可视化: 使用Excel或Python库"
echo ""

echo "📋 基于夸克项目的核心经验:"
echo "1. 📋 防错检查清单（53项标准检查）"
echo "2. 📝 教训记录和学习系统"
echo "3. 🔄 智能爬取器选择逻辑"
echo "4. 💾 实时数据保存机制"
echo "5. 📊 12字段数据完整性验证"
echo ""

echo "🎯 美团招聘特殊注意事项:"
echo "1. 🌐 使用提供的筛选URL: https://zhaopin.meituan.com/web/social"
echo "2. 🏙️ 城市代码: 001019002 (深圳) - 重要纠正！"
echo "3. 📁 岗位类别: 技术、产品、运营、市场、数据类"
echo "4. ⚠️ 需要调研API端点（目前使用浏览器爬取）"
echo "5. 🕒 合理控制请求频率，避免被封IP"
echo ""

echo "现在可以立即开始美团招聘数据爬取了！🚀"
echo ""
echo "📞 快速帮助:"
echo "• 查看美团爬取器帮助: python3 src/meituan_crawler.py --help"
echo "• 查看框架组件: python3 src/main.py"
echo "• 查看文档: docs/QUICK_START.md"
echo "• 记录问题: docs/LESSONS_LEARNED.md"
echo ""

# 提供立即执行的选项
echo "立即执行选项:"
echo "1) 测试连接"
echo "2) 浏览器爬取"
echo "3) 查看帮助"
echo "4) 退出"
echo ""
read -p "请选择 (1-4): " -n 1 -r
echo

case $REPLY in
    1)
        echo "🔍 执行连接测试..."
        python3 src/meituan_crawler.py --mode test
        ;;
    2)
        echo "🌐 执行浏览器爬取..."
        python3 src/meituan_crawler.py --mode browser
        ;;
    3)
        echo "📖 显示帮助信息..."
        python3 src/meituan_crawler.py --help
        ;;
    4|*)
        echo "👋 退出脚本"
        exit 0
        ;;
esac

echo ""
echo "✅ 脚本执行完成!"
echo "📁 数据保存在: output/crawl_data/"
echo "📝 日志查看: 控制台输出 或 查看logs/目录"
echo ""
echo "感谢使用美团招聘爬取项目！🎉"