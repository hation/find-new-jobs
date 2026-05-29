#!/bin/bash
# 🚀 滴滴出行招聘真实API爬取器启动脚本

set -e

echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│        🚀 滴滴出行招聘数据爬取器（真实API版）          │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│ 项目: didi-job"
echo "│ 公司: 滴滴出行"
echo "│ 目标: 社招岗位数据爬取"
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
    read -p "是否检查核心依赖包？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo "检查核心依赖包..."
        python3 -c "
try:
    import requests
    import pandas
    import json
    import logging
    from datetime import datetime
    print('✅ 核心依赖包正常')
except ImportError as e:
    print(f'❌ 依赖包缺失: {e}')
    print('请运行: pip install -r requirements.txt')
"
    fi
fi

echo ""
echo "🔧 第二步: 配置检查"
echo "----------------------------------------"
echo "当前配置状态:"

# 检查配置文件
CONFIG_FILE="config/didi_api_auth.json"
if [ -f "$CONFIG_FILE" ]; then
    echo "✅ 滴滴招聘配置: $CONFIG_FILE (已配置)"
    # 显示基本信息
    echo "配置信息:"
    python3 -c "
import json
try:
    with open('$CONFIG_FILE', 'r', encoding='utf-8') as f:
        config = json.load(f)
    company = config.get('company_info', {}).get('name', '未知')
    website = config.get('company_info', {}).get('website', '未知')
    endpoints = config.get('api_endpoints', {})
    list_endpoint = endpoints.get('list_endpoint', '未知')
    detail_endpoint = endpoints.get('detail_endpoint', '未知')
    
    print(f'   • 公司: {company}')
    print(f'   • 网站: {website}')
    print(f'   • 列表API: {list_endpoint}')
    print(f'   • 详情API: {detail_endpoint}')
except Exception as e:
    print(f'   ❌ 配置文件读取失败: {e}')
"
else
    echo "⚠️ 滴滴招聘配置: $CONFIG_FILE (未配置)"
    echo "   使用默认配置运行"
fi

echo ""
echo "🚀 第三步: 测试API连接"
echo "----------------------------------------"
echo "测试滴滴招聘API连接..."
read -p "是否测试API连接？(Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "运行连接测试..."
    python3 src/didi_real_crawler.py --test
    echo ""
    read -p "API连接测试完成，是否继续爬取？(Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ -n $REPLY ]]; then
        echo "❌ 用户取消爬取"
        exit 0
    fi
fi

echo ""
echo "📊 第四步: 开始爬取"
echo "----------------------------------------"
echo "爬取选项:"
echo "1. 测试爬取 (1页，快速验证)"
echo "2. 完整爬取 (多页，获取完整数据)"
echo "3. 自定义爬取"
echo ""

read -p "请选择爬取模式 (1/2/3): " -n 1 -r
echo

case $REPLY in
    1)
        echo "🔍 选择测试爬取 (第1页，16个岗位)"
        PAGES=1
        START=1
        ;;
    2)
        echo "📈 选择完整爬取 (前5页，约80个岗位)"
        PAGES=5
        START=1
        ;;
    3)
        read -p "请输入爬取页数 (默认3): " PAGES
        PAGES=${PAGES:-3}
        read -p "请输入起始页码 (默认1): " START
        START=${START:-1}
        echo "🔧 自定义爬取: ${PAGES}页，从第${START}页开始"
        ;;
    *)
        echo "❌ 无效选择，使用默认测试爬取"
        PAGES=1
        START=1
        ;;
esac

echo ""
echo "🚀 开始爬取滴滴招聘数据..."
echo "----------------------------------------"
python3 src/didi_real_crawler.py --pages $PAGES --start $START

echo ""
echo "📁 第五步: 查看数据"
echo "----------------------------------------"
echo "数据保存位置:"
echo "• 实时保存: output/didi_positions/immediate/"
echo "• 批量导出: output/didi_positions/"
echo "• 日志文件: logs/didi_crawler_$(date '+%Y%m%d').log"
echo ""

# 显示最近保存的文件
echo "📋 最近保存的文件:"
find output/didi_positions/ -name "*.json" -type f | head -5 2>/dev/null || echo "   (暂无数据文件)"

echo ""
echo "🔍 第六步: 验证和测试"
echo "----------------------------------------"
echo "验证命令:"
echo "1. 测试连接: python3 src/didi_real_crawler.py --test"
echo "2. 查看配置: python3 -m json.tool config/didi_api_auth.json"
echo "3. 检查清单: 查看 docs/CHECKLIST.md (53项检查)"
echo "4. 运行测试: python3 -m pytest tests/ -v"
echo ""

echo "💡 重要提示:"
echo "• 认证信息: Cookie可能过期，需要定期更新"
echo "• 速率限制: API限制100请求/秒，请合理控制频率"
echo "• 数据验证: 确保爬取的数据完整性和准确性"
echo "• 错误处理: 遇到问题记录在 docs/LESSONS_LEARNED.md"
echo ""

echo "🎯 滴滴招聘爬取目标达成情况:"
echo "• ✅ 基于夸克完整架构框架"
echo "• ✅ 使用真实滴滴招聘API"
echo "• ✅ 支持分页爬取和详情获取"
echo "• ✅ 实时保存防止数据丢失"
echo "• ✅ 多格式导出支持"
echo "• ✅ 完整的错误处理和日志"
echo ""

echo "📞 帮助信息:"
echo "• 项目文档: docs/QUICK_START.md"
echo "• 架构设计: docs/ARCHITECTURE.md"
echo "• 检查清单: docs/CHECKLIST.md"
echo "• 业务知识: docs/BUSINESS_KNOWLEDGE_SYSTEM.md"
echo "• 模板使用: docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md"
echo ""

echo "🎉 滴滴出行招聘数据爬取器准备就绪！"
echo "基于夸克项目的完整业务框架，确保高质量数据爬取！🚀"