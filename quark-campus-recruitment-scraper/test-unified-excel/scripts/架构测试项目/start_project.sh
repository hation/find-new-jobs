#!/bin/bash

# 🚀 项目启动脚本
# 基于夸克模板系统的最佳实践启动流程

set -e

echo "========================================="
echo "🚀 启动项目: $(basename "$(pwd)")"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查环境
check_environment() {
    echo "🔍 检查项目环境..."
    
    # 检查必要目录
    local required_dirs=("docs" "config" "scripts" "src" "logs" "data")
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            echo -e "${RED}❌ 缺少目录: $dir${NC}"
            return 1
        fi
    done
    
    # 检查必要文件
    local required_files=(
        "docs/CORE_BUSINESS_INFO.md"
        "docs/CHECKLIST.md"
        "docs/QUICK_START.md"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo -e "${YELLOW}⚠️  缺少文件: $file${NC}"
            echo -e "${YELLOW}   请先完成项目初始化${NC}"
            return 1
        fi
    done
    
    echo -e "${GREEN}✅ 环境检查通过${NC}"
    return 0
}

# 显示启动选项
show_options() {
    echo ""
    echo "请选择启动选项:"
    echo "1. 查看业务目标 (docs/CORE_BUSINESS_INFO.md)"
    echo "2. 运行快速开始 (docs/QUICK_START.md)"
    echo "3. 执行检查清单 (docs/CHECKLIST.md)"
    echo "4. 查看项目架构 (docs/ARCHITECTURE.md)"
    echo "5. 查看模板使用指南 (docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md)"
    echo "6. 启动完整工作流程"
    echo "7. 退出"
    echo ""
    
    read -p "请输入选项 (1-7): " choice
    
    case $choice in
        1)
            echo "打开业务目标文档..."
            if command -v bat &> /dev/null; then
                bat docs/CORE_BUSINESS_INFO.md
            else
                less docs/CORE_BUSINESS_INFO.md
            fi
            ;;
        2)
            echo "执行快速开始指南..."
            if [ -f "docs/QUICK_START.md" ]; then
                echo "请按照 docs/QUICK_START.md 中的步骤操作"
                if command -v bat &> /dev/null; then
                    bat docs/QUICK_START.md
                else
                    less docs/QUICK_START.md
                fi
            else
                echo -e "${RED}快速开始指南不存在${NC}"
            fi
            ;;
        3)
            echo "执行检查清单..."
            if [ -f "docs/CHECKLIST.md" ]; then
                echo "请逐项检查 docs/CHECKLIST.md 中的项目"
                if command -v bat &> /dev/null; then
                    bat docs/CHECKLIST.md
                else
                    less docs/CHECKLIST.md
                fi
            else
                echo -e "${RED}检查清单不存在${NC}"
            fi
            ;;
        4)
            echo "查看项目架构..."
            if [ -f "docs/ARCHITECTURE.md" ]; then
                if command -v bat &> /dev/null; then
                    bat docs/ARCHITECTURE.md
                else
                    less docs/ARCHITECTURE.md
                fi
            else
                echo -e "${RED}架构文档不存在${NC}"
            fi
            ;;
        5)
            echo "查看模板使用指南..."
            if [ -f "docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md" ]; then
                if command -v bat &> /dev/null; then
                    bat docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md
                else
                    less docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md
                fi
            else
                echo -e "${RED}模板使用指南不存在${NC}"
            fi
            ;;
        6)
            echo "启动完整工作流程..."
            start_full_workflow
            ;;
        7)
            echo "退出启动脚本"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选项，请重新选择${NC}"
            show_options
            ;;
    esac
    
    # 继续显示选项
    show_options
}

# 启动完整工作流程
start_full_workflow() {
    echo ""
    echo "========================================="
    echo "🔄 启动完整工作流程"
    echo "========================================="
    
    # 1. 检查环境
    check_environment || {
        echo -e "${RED}环境检查失败，请先修复问题${NC}"
        return 1
    }
    
    # 2. 提醒查看业务目标
    echo ""
    echo -e "${YELLOW}📋 第一步：确认业务目标${NC}"
    echo "请打开 docs/CORE_BUSINESS_INFO.md 确认："
    echo "  • 项目目标是否清晰？"
    echo "  • 成功标准是否明确？"
    echo "  • 团队理解是否一致？"
    read -p "确认已完成？(y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "请先完成业务目标确认"
        return 1
    fi
    
    # 3. 提醒检查清单
    echo ""
    echo -e "${YELLOW}🔍 第二步：执行检查清单${NC}"
    echo "请打开 docs/CHECKLIST.md 执行检查："
    echo "  • 环境检查是否通过？"
    echo "  • 配置验证是否完成？"
    echo "  • 业务规则是否确认？"
    read -p "确认已完成？(y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "请先完成检查清单"
        return 1
    fi
    
    # 4. 提醒快速开始
    echo ""
    echo -e "${YELLOW}🚀 第三步：执行快速开始${NC}"
    echo "请按照 docs/QUICK_START.md 开始项目："
    echo "  • 环境搭建是否完成？"
    echo "  • 配置测试是否通过？"
    echo "  • 快速验证是否成功？"
    read -p "确认已完成？(y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "请先完成快速开始"
        return 1
    fi
    
    # 5. 提醒记录机制
    echo ""
    echo -e "${YELLOW}📝 第四步：设置记录机制${NC}"
    echo "请确保以下记录机制就绪："
    echo "  • 每日记忆模板: memory-system/DAILY_MEMORY_TEMPLATE.md"
    echo "  • 教训记录: docs/LESSONS_LEARNED.md"
    echo "  • 检查清单: docs/CHECKLIST.md"
    read -p "确认已设置？(y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "请先设置记录机制"
        return 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ 完整工作流程准备完成！${NC}"
    echo ""
    echo "下一步建议："
    echo "1. 开始正式开发工作"
    echo "2. 遇到问题立即记录在 docs/LESSONS_LEARNED.md"
    echo "3. 每日结束时整理 memory-system/DAILY_MEMORY_TEMPLATE.md"
    echo "4. 定期回顾和优化 docs/CHECKLIST.md"
    echo ""
    echo "祝项目顺利！🎉"
}

# 主函数
main() {
    echo "========================================="
    echo "🚀 夸克模板系统 - 项目启动助手"
    echo "========================================="
    
    # 检查环境
    if ! check_environment; then
        echo -e "${YELLOW}⚠️  环境检查未通过，请先完成项目初始化${NC}"
        echo "建议步骤："
        echo "1. 填写 docs/CORE_BUSINESS_INFO.md"
        echo "2. 配置必要环境"
        echo "3. 重新运行此脚本"
        exit 1
    fi
    
    # 显示启动选项
    show_options
}

# 执行主函数
main "$@"
