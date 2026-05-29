#!/bin/bash
# 方案B恢复执行脚本
# 在账号解封后使用此脚本继续执行

echo "🚀 方案B恢复执行脚本"
echo "=========================================="
echo "📅 时间: $(date)"
echo "💡 使用说明: 在BOSS直聘账号解封后执行此脚本"
echo "=========================================="
echo ""

# 检查环境
echo "🔍 环境检查..."
export PATH="/Users/xingan/Library/Python/3.12/bin:$PATH"
cd /Users/xingan/招聘数据/方案B_立即执行_20260515_010114

if [ ! -f "all_security_ids_final.txt" ]; then
    echo "❌ 错误: 核心数据文件不存在"
    echo "请检查工作目录: $(pwd)"
    exit 1
fi

echo "✅ 工作目录: $(pwd)"
echo "✅ 核心数据文件: all_security_ids_final.txt"
echo "✅ 数据量: $(wc -l < all_security_ids_final.txt) 个securityId"
echo ""

# 步骤1：重新登录
echo "🔑 步骤1：重新登录"
echo "----------------------------------------"
echo "💡 请确保已在Chrome浏览器中登录BOSS直聘"
echo "💡 登录成功后，不要关闭浏览器"
echo ""
echo "按 Enter 键继续..."
read -r
echo ""

echo "🔄 登出旧凭证..."
boss logout 2>/dev/null || true

echo "🔐 从Chrome获取cookie..."
if boss login --cookie-source chrome 2>&1 | grep -q "✅"; then
    echo "✅ 登录成功"
else
    echo "❌ 登录失败"
    echo "请检查:"
    echo "  1. Chrome浏览器是否已登录BOSS直聘"
    echo "  2. Chrome浏览器是否正在运行"
    echo "  3. 重新运行此脚本"
    exit 1
fi
echo ""

# 步骤2：获取前3个详情（测试）
echo "🔍 步骤2：获取前3个职位详情（测试）"
echo "----------------------------------------"
echo "💡 必须在登录后立即执行，避免token过期"
echo ""

DETAILS_DIR="职位详情_恢复执行_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DETAILS_DIR"
echo "📁 详情目录: $DETAILS_DIR"
echo ""

SUCCESS_COUNT=0
for i in $(seq 1 3); do
    echo "[$i/3] 获取第 $i 个职位..."
    
    # 提取securityId
    LINE=$(head -n "$i" all_security_ids_final.txt | tail -1)
    SECURITY_ID=$(echo "$LINE" | cut -d'|' -f1)
    JOB_NAME=$(echo "$LINE" | cut -d'|' -f2)
    PAGE=$(echo "$LINE" | cut -d'|' -f3)
    
    echo "   职位: $JOB_NAME (第$PAGE页)"
    
    # 获取详情
    DETAIL_FILE="$DETAILS_DIR/detail_$i.json"
    
    if boss detail "$SECURITY_ID" --json > "$DETAIL_FILE" 2>&1; then
        if grep -q '"ok": true' "$DETAIL_FILE"; then
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            echo "      ✅ 成功"
        else
            echo "      ❌ 数据异常"
            grep -i "error\|异常\|expired" "$DETAIL_FILE" | head -2
        fi
    else
        echo "      ❌ 获取失败"
    fi
    
    # 延迟
    if [ $i -lt 3 ]; then
        sleep 1
    fi
done
echo ""

# 步骤3：结果统计
echo "📊 步骤3：获取结果统计"
echo "----------------------------------------"
echo "✅ 成功: $SUCCESS_COUNT 个"
echo "❌ 失败: $((3 - SUCCESS_COUNT)) 个"

if [ $SUCCESS_COUNT -eq 0 ]; then
    echo "❌ 所有获取都失败"
    echo "可能原因:"
    echo "  1. token已过期"
    echo "  2. securityId无效"
    echo "  3. 账号权限问题"
    echo "建议重新登录后重试"
    exit 1
elif [ $SUCCESS_COUNT -lt 2 ]; then
    echo "⚠️  成功率较低"
    echo "建议:"
    echo "  1. 重新登录"
    echo "  2. 减少每次获取的数量"
    echo "  3. 增加延迟时间"
else
    echo "✅ 测试成功！可以继续获取更多详情"
fi
echo ""

# 步骤4：导出Excel
echo "📊 步骤4：导出Excel数据"
echo "----------------------------------------"
if [ $SUCCESS_COUNT -gt 0 ]; then
    echo "💡 使用Excel导出工具..."
    
    if [ -f "scheme_b_excel_exporter.py" ]; then
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        OUTPUT_FILE="深圳AI岗位_恢复执行_${TIMESTAMP}.xlsx"
        
        echo "导出到: $OUTPUT_FILE"
        python3 scheme_b_excel_exporter.py --input all_security_ids_final.txt --output "$OUTPUT_FILE"
        
        if [ -f "$OUTPUT_FILE" ]; then
            echo "✅ Excel文件已生成: $OUTPUT_FILE"
            echo "📊 文件大小: $(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null) 字节"
        else
            echo "⚠️  Excel文件未生成"
            echo "可能原因: 详情数据不足"
        fi
    else
        echo "❌ Excel导出工具不存在"
        echo "请检查: scheme_b_excel_exporter.py"
    fi
else
    echo "⚠️  没有成功的详情，跳过Excel导出"
fi
echo ""

# 步骤5：后续建议
echo "🎯 步骤5：后续操作建议"
echo "----------------------------------------"
echo "如果测试成功，可以继续执行以下操作:"
echo ""
echo "1. 获取更多详情（每次5-10个）:"
echo "   for i in \$(seq 4 10); do"
echo "       # 获取详情代码"
echo "   done"
echo ""
echo "2. 使用完整工作流脚本:"
echo "   python3 complete_scheme_b_workflow.py"
echo ""
echo "3. 查看完整指南:"
echo "   查看 SCHEME_B_FULL_WORKFLOW.md"
echo ""
echo "4. 检查进度报告:"
echo "   查看 进度报告_暂停_20260515.md"
echo ""

echo "🎉 恢复执行完成！"
echo "💡 下次可以直接执行此脚本继续"