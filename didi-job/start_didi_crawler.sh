#!/bin/bash
# 🚀 滴滴招聘爬取器快速启动脚本

set -e

echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│        🚀 滴滴招聘数据爬取器启动                       │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│ 项目: didi-job"
echo "│ 公司: 滴滴出行"
echo "│ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "└─────────────────────────────────────────────────────────┘"
echo ""

# 检查Python环境
echo "🔍 第一步: 环境检查"
echo "----------------------------------------"
if command -v python3 &> /dev/null; then
    echo "✅ Python3: $(python3 --version)"
else
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖
echo ""
echo "📦 检查依赖..."
if [ -f "requirements.txt" ]; then
    echo "✅ 依赖文件存在: requirements.txt"
    read -p "是否检查依赖安装状态？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo "检查核心依赖包..."
        python3 -c "import requests; import pandas; import playwright; print('✅ 核心依赖包正常')"
    fi
fi

echo ""
echo "🔧 第二步: 配置检查"
echo "----------------------------------------"
echo "当前配置状态:"
if [ -f "config/.env" ]; then
    echo "✅ 环境配置文件: config/.env (已配置)"
else
    echo "⚠️ 环境配置文件: config/.env (未配置)"
    echo "   运行: cp config/.env.example config/.env"
fi

if [ -f "config/api_auth.json" ]; then
    echo "✅ API认证配置: config/api_auth.json (已配置)"
else
    echo "⚠️ API认证配置: config/api_auth.json (未配置)"
fi

echo ""
echo "📚 第三步: 滴滴招聘配置"
echo "----------------------------------------"
echo "滴滴招聘网站: https://job.didiglobal.com"
echo ""
echo "需要配置的信息:"
echo "1. 🔑 API认证信息 (编辑 config/api_auth.json)"
echo "2. 🌐 浏览器配置 (编辑 config/browser_config.json)"
echo "3. 📊 数据字段定义 (编辑 memory-system/CORE_BUSINESS_INFO.md)"
echo ""

echo "🚀 第四步: 运行滴滴爬取器"
echo "----------------------------------------"
echo "运行方式:"
echo "1. 智能模式 (推荐):"
echo "   python3 src/didi_crawler.py --mode smart --max 10"
echo ""
echo "2. 仅API模式:"
echo "   python3 src/didi_crawler.py --mode api --max 5"
echo ""
echo "3. 仅浏览器模式:"
echo "   python3 src/didi_crawler.py --mode browser --max 5"
echo ""

echo "📊 第五步: 查看数据"
echo "----------------------------------------"
echo "数据保存位置:"
echo "• 实时保存: output/json/immediate/"
echo "• 批量导出: output/json/"
echo "• Excel格式: output/excel/"
echo "• CSV格式: output/csv/"
echo ""

echo "🔍 第六步: 验证和测试"
echo "----------------------------------------"
echo "验证命令:"
echo "1. 验证架构: python3 scripts/validate_complete_architecture.py"
echo "2. 运行测试: python3 -m pytest tests/ -v"
echo "3. 检查清单: 查看 docs/CHECKLIST.md (53项检查)"
echo ""

echo "💡 提示:"
echo "• 首次运行前，请填写 memory-system/CORE_BUSINESS_INFO.md"
echo "• 遇到问题记录在 docs/LESSONS_LEARNED.md"
echo "• 每日工作记录在 memory-system/DAILY_MEMORY_TEMPLATE.md"
echo "• 基于夸克项目的防错机制，确保数据完整性和稳定性"
echo ""

echo "🎯 滴滴招聘爬取目标:"
echo "• 获取滴滴出行所有招聘岗位"
echo "• 提取12个核心字段的完整信息"
echo "• 支持API优先 + 浏览器备用的智能爬取"
echo "• 实时保存防止数据丢失"
echo "• 多格式导出 (JSON, Excel, CSV)"
echo ""

# 询问是否立即运行
echo "🚀 是否立即运行滴滴招聘爬取器？"
read -p "输入Y开始爬取，输入N查看其他选项 (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo ""
    echo "开始运行滴滴招聘爬取器..."
    echo "----------------------------------------"
    python3 src/didi_crawler.py --mode smart --max 5
else
    echo ""
    echo "📋 其他选项:"
    echo "1. 查看架构: python3 src/main.py"
    echo "2. 查看示例: python3 src/examples/bytedance_migration_demo.py"
    echo "3. 验证环境: python3 scripts/validate_complete_architecture.py"
    echo "4. 编辑配置: vim config/api_auth.json"
    echo "5. 填写业务信息: vim memory-system/CORE_BUSINESS_INFO.md"
    echo ""
    echo "💡 建议先完成配置再开始爬取"
fi

echo ""
echo "📞 帮助信息:"
echo "• 项目文档: docs/QUICK_START.md"
echo "• 架构设计: docs/ARCHITECTURE.md"
echo "• 检查清单: docs/CHECKLIST.md"
echo "• 业务知识: docs/BUSINESS_KNOWLEDGE_SYSTEM.md"
echo "• 模板使用: docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md"
echo ""

echo "🎉 滴滴招聘爬取器准备就绪！"
echo "现在可以开始爬取滴滴出行的招聘数据了！🚀"