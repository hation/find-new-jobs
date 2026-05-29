#!/bin/bash
# 🎬 夸克模板系统迁移演示脚本
# 展示如何将模板应用到新项目

set -e

echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│          🎬 夸克模板系统迁移演示                        │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│ 演示内容: 如何将夸克项目模板应用到新项目                │"
echo "│ 创建项目: 演示项目-字节跳动招聘爬取器                   │"
echo "│ 演示模式: 实际执行（将创建真实文件和目录）              │"
echo "└─────────────────────────────────────────────────────────┘"
echo ""

# 设置演示目录
DEMO_DIR="/tmp/quark_template_demo_$(date +%Y%m%d_%H%M%S)"
DEMO_PROJECT_NAME="演示项目-字节跳动招聘爬取器"
TEMPLATE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "📁 演示目录: $DEMO_DIR"
echo "📦 模板目录: $TEMPLATE_DIR"
echo "🎯 演示项目: $DEMO_PROJECT_NAME"
echo ""

read -p "按回车键开始演示..." </dev/tty

# 创建演示目录
echo ""
echo "🔧 步骤1: 创建演示目录"
echo "----------------------------------------"
mkdir -p "$DEMO_DIR"
cd "$DEMO_DIR"
echo "✅ 创建目录: $DEMO_DIR"

# 运行迁移脚本
echo ""
echo "🚀 步骤2: 运行迁移脚本"
echo "----------------------------------------"
echo "执行: $TEMPLATE_DIR/scripts/new-project-migration.sh \\"
echo "      -d \"$DEMO_DIR\" \\"
echo "      \"$DEMO_PROJECT_NAME\""
echo ""

"$TEMPLATE_DIR/scripts/new-project-migration.sh" -d "$DEMO_DIR" "$DEMO_PROJECT_NAME"

# 进入新项目
echo ""
echo "📂 步骤3: 查看创建的项目"
echo "----------------------------------------"
cd "$DEMO_DIR/$DEMO_PROJECT_NAME"
echo "进入项目目录: $(pwd)"
echo ""

# 显示项目结构
echo "📁 项目结构:"
echo "----------------------------------------"
find . -type f -name "*.md" -o -name "*.json" -o -name "*.sh" -o -name "*.py" | head -20 | sort | sed 's/^/  /'
echo ""

# 显示核心文件
echo "📄 核心文件预览:"
echo "----------------------------------------"
echo "1. 业务目标文档 (docs/CORE_BUSINESS_INFO.md)"
head -5 docs/CORE_BUSINESS_INFO.md
echo ""

echo "2. 检查清单 (docs/CHECKLIST.md)"
head -5 docs/CHECKLIST.md
echo ""

echo "3. 配置文件 (config/project_config.json)"
cat config/project_config.json | python3 -m json.tool | head -20
echo ""

# 运行验证脚本
echo "🔍 步骤4: 验证迁移结果"
echo "----------------------------------------"
if [ -f "scripts/validate_config.py" ]; then
    python3 scripts/validate_config.py
else
    echo "使用内置验证脚本..."
    python3 << 'EOF'
import json
import os

config_file = "config/project_config.json"
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    print("✅ 配置文件验证通过")
    print(f"   项目名称: {config.get('project', {}).get('name', 'N/A')}")
    print(f"   项目类型: {config.get('project', {}).get('type', 'N/A')}")
else:
    print("❌ 配置文件不存在")
EOF
fi

# 运行启动脚本
echo ""
echo "🚀 步骤5: 运行启动脚本"
echo "----------------------------------------"
echo "执行: ./start_project.sh"
echo ""
echo "（演示中将模拟选择选项1）"
echo ""

# 创建模拟启动的示例
cat << 'EOF'
=========================================
🚀 欢迎使用夸克模板系统项目
=========================================

项目根目录: /tmp/quark_template_demo_20260521_150202/演示项目-字节跳动招聘爬取器

🔍 检查项目文件...
✅ 必要文件检查通过

当前项目: 演示项目-字节跳动招聘爬取器

请选择操作:
1. 查看业务目标
2. 执行检查清单
3. 快速开始
4. 查看架构设计
5. 查看使用指南
6. 退出

请输入选项 (1-6): 1

📋 业务目标文档: docs/CORE_BUSINESS_INFO.md

请确保以下问题已明确:
• 项目目标是什么？
• 需要什么数据？
• 成功标准是什么？
• 业务规则有哪些？

按回车键返回菜单...
EOF

# 显示下一步建议
echo ""
echo "🎯 步骤6: 下一步建议"
echo "----------------------------------------"
cat << 'EOF'
在实际项目中，你应该：

1. 📋 填写业务信息
   cd $(pwd)
   vim docs/CORE_BUSINESS_INFO.md
   # 填写你的业务目标、数据需求、成功标准

2. 🔍 执行检查清单
   ./start_project.sh
   # 选择选项2，逐项检查

3. 🚀 开始开发
   # 按照 docs/QUICK_START.md 快速开始
   # 按照 docs/ARCHITECTURE.md 设计架构
   # 遇到问题记录在 docs/LESSONS_LEARNED.md

4. 📝 记录工作
   # 每日使用 memory-system/DAILY_MEMORY_TEMPLATE.md
   # 定期回顾 docs/LESSONS_LEARNED.md
   # 持续优化 docs/CHECKLIST.md
EOF

# 显示总结
echo ""
echo "🎉 演示总结"
echo "----------------------------------------"
cat << EOF
演示完成！通过迁移脚本，我们：

✅ 创建了新项目: $DEMO_PROJECT_NAME
✅ 复制了11个核心模板文档
✅ 创建了完整的项目结构
✅ 配置了项目信息和启动脚本
✅ 建立了防错和学习系统

迁移内容包括:
• 📁 完整文档体系 (docs/)
• 🧠 记忆系统 (memory-system/)
• ⚙️ 配置管理 (config/)
• 🔧 工具脚本 (scripts/)
• 🚀 启动向导 (start_project.sh)

你现在可以:
1. 查看创建的项目: cd $DEMO_DIR/$DEMO_PROJECT_NAME
2. 探索文档: ls -la docs/
3. 开始使用: ./start_project.sh

要迁移到真实项目:
cd /path/to/your/template
./scripts/new-project-migration.sh "你的真实项目名称"
EOF

echo ""
echo "🔚 演示结束"
echo "----------------------------------------"
echo "演示目录: $DEMO_DIR"
echo "如需清理演示文件: rm -rf $DEMO_DIR"
echo ""
echo "🎯 记住: 迁移不仅是复制文件，更是复制成功的工作方法！"