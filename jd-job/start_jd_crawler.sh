#!/bin/bash
# 京东招聘数据爬取启动脚本

set -e

echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│        🚀 京东招聘数据爬取项目启动                       │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│ 项目: jd-job"
echo "│ 公司: 京东"
echo "│ 网站: https://zhaopin.jd.com"
echo "│ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "└─────────────────────────────────────────────────────────┘"
echo ""

echo "📋 项目概述:"
echo "基于夸克项目的完整架构，专门爬取京东招聘数据"
echo ""

echo "🔍 第一步: 环境检查"
echo "----------------------------------------"
# 检查Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3: $(python3 --version)"
else
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖
if [ -f "requirements.txt" ]; then
    echo "📦 依赖文件: requirements.txt"
    read -p "是否检查并安装依赖？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo "正在检查依赖..."
        pip install -r requirements.txt
    fi
fi

echo ""
echo "🔧 第二步: 配置验证"
echo "----------------------------------------"
echo "检查配置文件:"
if [ -f "config/.env" ]; then
    echo "✅ 环境配置: config/.env"
    source config/.env
    echo "   公司名称: $COMPANY_NAME"
    echo "   网站URL: $WEBSITE_URL"
else
    echo "❌ 环境配置文件不存在"
    echo "   请运行: cp config/.env.example config/.env"
    exit 1
fi

if [ -f "config/api_auth.json" ]; then
    echo "✅ API认证配置: config/api_auth.json"
else
    echo "❌ API认证配置文件不存在"
    exit 1
fi

echo ""
echo "📚 第三步: 项目架构验证"
echo "----------------------------------------"
echo "运行完整架构验证:"
python3 scripts/validate_complete_architecture.py

echo ""
echo "🚀 第四步: 启动京东爬虫"
echo "----------------------------------------"
echo "可用命令:"
echo ""
echo "1. 测试模式（只爬取1页）:"
echo "   python3 src/jd_crawler.py --test --format excel"
echo ""
echo "2. 完整模式（爬取10页）:"
echo "   python3 src/jd_crawler.py --pages 10 --format excel"
echo ""
echo "3. 自定义模式:"
echo "   python3 src/jd_crawler.py --pages <页数> --format <json|csv|excel>"
echo ""
echo "4. 查看帮助:"
echo "   python3 src/jd_crawler.py --help"
echo ""

echo "🎯 参数说明:"
echo "  --pages: 爬取的最大页数（默认: 5）"
echo "  --format: 输出格式（json, csv, excel，默认: excel）"
echo "  --test: 测试模式，只爬取1页"
echo ""

echo "📊 数据输出:"
echo "  数据将保存到: output/jd_jobs/"
echo "  日志将保存到: logs/jd_jobs/"
echo "  备份将保存到: backup/jd_jobs/"
echo ""

echo "💡 提示:"
echo "• 首次运行建议使用测试模式"
echo "• 如果Cookie失效，需要更新 config/api_auth.json"
echo "• 查看日志: logs/jd_jobs/*.log"
echo "• 数据验证: 检查 output/jd_jobs/ 目录下的文件"
echo ""

echo "🔧 第五步: 运行测试"
echo "----------------------------------------"
read -p "是否运行测试模式？(Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "正在启动测试模式..."
    python3 src/jd_crawler.py --test --format excel
fi

echo ""
echo "🎯 基于夸克项目的核心经验:"
echo "1. 📋 防错检查清单（53项标准检查）"
echo "2. 📝 教训记录和学习系统"
echo "3. 🔄 智能爬取器选择逻辑"
echo "4. 💾 实时数据保存机制"
echo "5. 📊 12字段数据完整性验证"
echo ""

echo "📞 快速帮助:"
echo "• 查看项目架构: python3 src/main.py"
echo "• 验证完整架构: python3 scripts/validate_complete_architecture.py"
echo "• 查看配置: cat config/.env"
echo "• 查看日志: tail -f logs/jd_jobs/*.log"
echo ""

echo "现在可以开始爬取京东招聘数据了！🚀"
echo ""
echo "运行完整爬取:"
echo "python3 src/jd_crawler.py --pages 10 --format excel"
echo ""