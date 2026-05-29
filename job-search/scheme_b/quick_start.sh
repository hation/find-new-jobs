#!/bin/bash
# 方案B快速启动脚本

echo "🚀 方案B快速启动"
echo "=========================================="
echo "📅 时间: $(date)"
echo "💡 方案B: 分步工作流（大批量数据处理）"
echo "=========================================="
echo ""

# 检查环境
echo "🔍 环境检查..."
if [ ! -f "data/all_security_ids_final.txt" ]; then
    echo "❌ 错误: 核心数据文件不存在"
    echo "请检查: data/all_security_ids_final.txt"
    exit 1
fi

echo "✅ 核心数据文件: data/all_security_ids_final.txt"
echo "✅ 数据量: $(wc -l < data/all_security_ids_final.txt) 个securityId"
echo ""

# 显示菜单
echo "🎯 请选择操作:"
echo "----------------------------------------"
echo "1. 查看方案B状态和进度"
echo "2. 查看恢复执行检查清单"
echo "3. 执行恢复执行脚本"
echo "4. 查看完整工作流指南"
echo "5. 查看下次继续指南"
echo "6. 退出"
echo "----------------------------------------"
echo ""

read -p "请输入选项 (1-6): " choice
echo ""

case $choice in
    1)
        echo "📊 方案B当前状态:"
        echo "----------------------------------------"
        echo "✅ 已完成:"
        echo "  - 数据收集: 100个securityId"
        echo "  - 工具准备: 所有脚本就绪"
        echo "  - 文档准备: 完整指南创建"
        echo ""
        echo "🚧 待完成:"
        echo "  - 职位详情获取: 0/100个"
        echo "  - Excel导出: 未生成"
        echo "  - 数据分析: 未开始"
        echo ""
        echo "⏸️  暂停原因: 账号被封"
        echo "🚀 恢复条件: 账号解封后"
        echo ""
        echo "💡 恢复执行信号:"
        echo "  说\"继续方案B\"或\"恢复方案B执行\""
        ;;
    2)
        echo "📋 恢复执行检查清单:"
        echo "----------------------------------------"
        if [ -f "docs/恢复执行检查清单.md" ]; then
            head -30 docs/恢复执行检查清单.md
        else
            echo "❌ 文件不存在: docs/恢复执行检查清单.md"
        fi
        ;;
    3)
        echo "🚀 执行恢复执行脚本..."
        echo "----------------------------------------"
        if [ -f "恢复执行.sh" ]; then
            chmod +x 恢复执行.sh
            ./恢复执行.sh
        else
            echo "❌ 文件不存在: 恢复执行.sh"
        fi
        ;;
    4)
        echo "📖 完整工作流指南:"
        echo "----------------------------------------"
        if [ -f "docs/SCHEME_B_FULL_WORKFLOW.md" ]; then
            head -30 docs/SCHEME_B_FULL_WORKFLOW.md
            echo ""
            echo "💡 查看完整文件: docs/SCHEME_B_FULL_WORKFLOW.md"
        else
            echo "❌ 文件不存在: docs/SCHEME_B_FULL_WORKFLOW.md"
        fi
        ;;
    5)
        echo "📋 下次继续指南:"
        echo "----------------------------------------"
        if [ -f "docs/README_下次继续.md" ]; then
            head -30 docs/README_下次继续.md
            echo ""
            echo "💡 查看完整文件: docs/README_下次继续.md"
        else
            echo "❌ 文件不存在: docs/README_下次继续.md"
        fi
        ;;
    6)
        echo "👋 退出方案B快速启动"
        exit 0
        ;;
    *)
        echo "❌ 无效选项，请重新运行脚本"
        exit 1
        ;;
esac

echo ""
echo "🎉 方案B快速启动完成"
echo "💡 下次可以直接运行: ./quick_start.sh"