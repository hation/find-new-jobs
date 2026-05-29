#!/bin/bash

# 🚀 项目启动示例脚本
# 这是一个简化的启动脚本示例

echo "========================================="
echo "🚀 欢迎使用夸克模板系统项目"
echo "========================================="
echo ""

# 检查必要文件
check_required_files() {
    echo "🔍 检查项目文件..."
    
    local files=(
        "docs/CORE_BUSINESS_INFO.md"
        "docs/CHECKLIST.md"
        "docs/QUICK_START.md"
    )
    
    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "❌ 缺少文件: $file"
            return 1
        fi
    done
    
    echo "✅ 必要文件检查通过"
    return 0
}

# 显示启动菜单
show_menu() {
    echo ""
    echo "请选择操作:"
    echo "1. 查看业务目标"
    echo "2. 执行检查清单"
    echo "3. 快速开始"
    echo "4. 查看架构设计"
    echo "5. 查看使用指南"
    echo "6. 退出"
    echo ""
    
    read -p "请输入选项 (1-6): " choice
    echo ""
    
    case $choice in
        1)
            echo "📋 业务目标文档: docs/CORE_BUSINESS_INFO.md"
            echo ""
            echo "请确保以下问题已明确:"
            echo "• 项目目标是什么？"
            echo "• 需要什么数据？"
            echo "• 成功标准是什么？"
            echo "• 业务规则有哪些？"
            echo ""
            read -p "按回车键返回菜单..." 
            show_menu
            ;;
        2)
            echo "🔍 执行检查清单: docs/CHECKLIST.md"
            echo ""
            echo "请逐项检查以下内容:"
            echo "1. 环境配置检查"
            echo "2. 业务规则验证"
            echo "3. 数据源确认"
            echo "4. 执行前最后检查"
            echo ""
            echo "✅ 检查完成后，在文档中标记完成状态"
            read -p "按回车键返回菜单..."
            show_menu
            ;;
        3)
            echo "⚡ 快速开始: docs/QUICK_START.md"
            echo ""
            echo "建议步骤:"
            echo "1. 环境搭建"
            echo "2. 配置测试"
            echo "3. 快速验证"
            echo "4. 问题排查"
            echo ""
            echo "🚀 开始执行快速开始指南"
            read -p "按回车键返回菜单..."
            show_menu
            ;;
        4)
            echo "🏗️ 架构设计: docs/ARCHITECTURE.md"
            echo ""
            echo "架构文档包含:"
            echo "• 系统架构图"
            echo "• 技术选型"
            echo "• 数据流设计"
            echo "• 部署方案"
            echo ""
            echo "📖 建议在开始编码前先了解架构"
            read -p "按回车键返回菜单..."
            show_menu
            ;;
        5)
            echo "📚 模板使用指南: docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md"
            echo ""
            echo "核心内容:"
            echo "• 一分钟了解模板系统"
            echo "• 四个关键阶段"
            echo "• 三个必用模板"
            echo "• 立即行动清单"
            echo ""
            echo "⏱️ 预计阅读时间: 5分钟"
            read -p "按回车键返回菜单..."
            show_menu
            ;;
        6)
            echo "退出启动脚本"
            echo ""
            echo "🎯 下一步建议:"
            echo "1. 填写 docs/CORE_BUSINESS_INFO.md"
            echo "2. 执行 docs/CHECKLIST.md"
            echo "3. 按照 docs/QUICK_START.md 开始"
            echo ""
            echo "祝项目顺利！🎉"
            exit 0
            ;;
        *)
            echo "❌ 无效选项，请重新选择"
            show_menu
            ;;
    esac
}

# 主函数
main() {
    echo "项目根目录: $(pwd)"
    echo ""
    
    # 检查必要文件
    if ! check_required_files; then
        echo ""
        echo "⚠️  项目文件不完整，请先完成初始化"
        echo "建议: 运行 ./scripts/new-project-migration.sh 重新迁移"
        exit 1
    fi
    
    # 显示欢迎信息
    if [ -f "config/project_config.json" ]; then
        project_name=$(grep -o '"name": "[^"]*' config/project_config.json | cut -d'"' -f4)
        echo "当前项目: $project_name"
    fi
    
    # 显示启动菜单
    show_menu
}

# 执行主函数
main "$@"