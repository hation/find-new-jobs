#!/bin/bash
# 夸克完整架构项目启动脚本

set -e

echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│        🚀 夸克完整架构项目启动                         │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│ 项目: ks-job"
echo "│ 公司: 新公司"
echo "│ 类型: crawler"
echo "│ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "└─────────────────────────────────────────────────────────┘"
echo ""

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
    echo "✅ Python3: $(python3 --version)"
else
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖
if [ -f "requirements.txt" ]; then
    echo "📦 发现依赖文件: requirements.txt"
    read -p "是否安装依赖？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        pip install -r requirements.txt
    fi
fi

echo ""
echo "🔧 第二步: 配置项目"
echo "----------------------------------------"
echo "1. 复制环境配置:"
echo "   cp config/.env.example config/.env"
echo "   # 编辑 config/.env 设置你的配置"
echo ""
echo "2. 配置API认证:"
echo "   编辑 config/api_auth.json 设置API密钥"
echo ""
echo "3. 填写业务信息:"
echo "   编辑 memory-system/CORE_BUSINESS_INFO.md"
echo ""

echo "📚 第三步: 学习架构"
echo "----------------------------------------"
echo "核心文档位置:"
echo "• 架构设计: docs/ARCHITECTURE.md"
echo "• 快速开始: docs/QUICK_START.md"
echo "• 检查清单: docs/CHECKLIST.md (53项标准检查)"
echo "• 业务知识: docs/BUSINESS_KNOWLEDGE_SYSTEM.md"
echo "• 模板使用: docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md"
echo ""

echo "🔧 第四步: 业务框架"
echo "----------------------------------------"
echo "可用业务框架组件:"
echo "1. 智能爬取器选择器: src/framework/smart_crawler_selector.py"
echo "   • API优先，浏览器备选"
echo "   • 智能错误恢复"
echo "   • 用户决策支持"
echo ""
echo "2. 统一爬取器入口: src/framework/unified_crawler_entry.py"
echo "   • 命令行参数解析"
echo "   • 多种运行模式"
echo "   • 状态查询功能"
echo ""
echo "3. 数据导出框架: src/framework/data_exporter.py"
echo "   • 支持Excel、CSV、JSON"
echo "   • 数据验证和清洗"
echo "   • 模板化输出"
echo ""

echo "🚀 第五步: 开始开发"
echo "----------------------------------------"
echo "开发流程:"
echo "1. 继承 SmartCrawlerSelector 实现业务逻辑"
echo "2. 配置 UnifiedCrawlerEntry 作为命令行入口"
echo "3. 使用 DataExporter 导出数据"
echo "4. 运行测试验证功能"
echo "5. 记录教训持续改进"
echo ""

echo "🔍 第六步: 验证架构"
echo "----------------------------------------"
echo "运行完整架构验证:"
echo "python scripts/validate_complete_architecture.py"
echo ""

echo "💡 提示:"
echo "• 遇到问题记录在 docs/LESSONS_LEARNED.md"
echo "• 每日工作记录在 memory-system/DAILY_MEMORY_TEMPLATE.md"
echo "• 定期回顾和优化检查清单"
echo ""

echo "🎯 基于夸克项目的核心经验:"
echo "1. 📋 防错检查清单（53项标准检查）"
echo "2. 📝 教训记录和学习系统"
echo "3. 🔄 智能爬取器选择逻辑"
echo "4. 💾 实时数据保存机制"
echo "5. 📊 12字段数据完整性验证"
echo ""

echo "现在可以立即开始你的数据爬取项目了！🚀"
echo ""
echo "📞 快速帮助:"
echo "• 查看示例: python src/examples/bytedance_migration_demo.py"
echo "• 运行主程序: python src/main.py"
echo "• 验证架构: python scripts/validate_complete_architecture.py"
