#!/bin/bash
# 简化的分步工作流脚本（方案B）
# 将搜索和详情获取分离，避免token过期问题

set -e

echo "🚀 分步工作流（方案B）"
echo "========================"

# 设置环境
export PATH="/Users/xingan/Library/Python/3.12/bin:$PATH"

# 检查参数
if [ $# -lt 2 ]; then
    echo "用法: $0 <关键词> <城市> [页数] [每页职位数]"
    echo "示例: $0 AI 深圳 2 10"
    exit 1
fi

KEYWORD="$1"
CITY="$2"
PAGES="${3:-1}"
MAX_JOBS="${4:-10}"
OUTPUT_DIR="$HOME/招聘数据/分步采集_$(date +%Y%m%d_%H%M%S)"

echo "📊 配置信息:"
echo "  关键词: $KEYWORD"
echo "  城市: $CITY"
echo "  页数: $PAGES"
echo "  每页职位数: $MAX_JOBS"
echo "  输出目录: $OUTPUT_DIR"
echo ""

# 创建输出目录
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

# ===== 步骤1：搜索并提取securityId =====
echo "📋 步骤1：搜索并提取securityId"
echo "----------------------------------------"

echo "🔑 请确保已在Chrome浏览器中登录BOSS直聘"
echo "⏳ 登录后按Enter键继续..."
read -p ""

# 登录
echo "🔑 执行登录..."
if ! boss login --cookie-source chrome; then
    echo "❌ 登录失败，请检查浏览器登录状态"
    exit 1
fi

# 检查登录状态
if ! boss status | grep -q "search=ok"; then
    echo "❌ 登录状态异常，请重新登录"
    exit 1
fi

echo "✅ 登录成功"

# 搜索并保存securityId
SECURITY_IDS_FILE="security_ids.txt"
echo "" > "$SECURITY_IDS_FILE"
TOTAL_IDS=0

for ((page=1; page<=PAGES; page++)); do
    echo "📄 搜索第 $page/$PAGES 页..."
    
    # 搜索并保存JSON
    SEARCH_FILE="search_page_${page}.json"
    if ! boss search "$KEYWORD" --city "$CITY" --page "$page" --json > "$SEARCH_FILE"; then
        echo "⚠️  第${page}页搜索失败，跳过"
        continue
    fi
    
    # 提取securityId
    echo "🔍 提取securityId..."
    if [ -f "$SEARCH_FILE" ]; then
        # 使用Python提取securityId
        python3 -c "
import json
import sys

try:
    with open('$SEARCH_FILE', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if data.get('ok'):
        jobs = data.get('data', {}).get('jobList', [])
        print(f'找到 {len(jobs)} 个职位')
        
        count = 0
        for job in jobs[:$MAX_JOBS]:
            security_id = job.get('securityId')
            job_name = job.get('jobName', '未知职位')
            
            if security_id:
                with open('$SECURITY_IDS_FILE', 'a', encoding='utf-8') as f:
                    f.write(f'{security_id}|{job_name}\\n')
                count += 1
                print(f'  [{count}] {job_name[:30]}...')
        
        print(f'✅ 提取到 {count} 个securityId')
        sys.exit(count)
    else:
        print('数据异常')
        sys.exit(0)
except Exception as e:
    print(f'提取失败: {e}')
    sys.exit(0)
" >> "extract_log_${page}.txt"
        
        PAGE_IDS=$?
        TOTAL_IDS=$((TOTAL_IDS + PAGE_IDS))
        
        if [ $PAGE_IDS -gt 0 ]; then
            echo "✅ 第${page}页提取到 $PAGE_IDS 个securityId"
        else:
            echo "⚠️  第${page}页没有提取到securityId"
        fi
    fi
    
    # 页间延迟
    if [ $page -lt $PAGES ]; then
        echo "⏳ 等待2秒..."
        sleep 2
    fi
done

echo ""
echo "✅ 步骤1完成"
echo "📊 总计提取: $TOTAL_IDS 个securityId"
echo "📁 securityId文件: $SECURITY_IDS_FILE"

if [ $TOTAL_IDS -eq 0 ]; then
    echo "❌ 没有提取到securityId，停止工作流"
    exit 1
fi

# ===== 步骤2：重新登录并获取详情 =====
echo ""
echo "📋 步骤2：重新登录并获取详情"
echo "----------------------------------------"

echo "💡 请等待片刻，然后重新登录"
echo "⏳ 准备好后按Enter键继续..."
read -p ""

echo "🔄 重新登录..."
if ! boss login --cookie-source chrome; then
    echo "❌ 重新登录失败，请检查浏览器登录状态"
    exit 1
fi

# 创建详情目录
DETAILS_DIR="职位详情"
mkdir -p "$DETAILS_DIR"

# 读取securityId并获取详情
SUCCESS_COUNT=0
FAIL_COUNT=0
LINE_NUM=0
TOTAL_LINES=$(wc -l < "$SECURITY_IDS_FILE")

echo "📊 准备获取 $TOTAL_LINES 个职位详情"
echo "⏳ 预计时间: $((TOTAL_LINES * 3)) 秒"

while IFS='|' read -r security_id job_name; do
    LINE_NUM=$((LINE_NUM + 1))
    
    echo ""
    echo "[$LINE_NUM/$TOTAL_LINES] $job_name"
    
    # 获取详情
    DETAIL_FILE="$DETAILS_DIR/detail_${LINE_NUM}.json"
    if boss detail "$security_id" --json > "$DETAIL_FILE" 2>/dev/null; then
        # 检查详情是否有效
        if grep -q '"ok": true' "$DETAIL_FILE"; then
            echo "   ✅ 获取成功"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo "   ❌ 数据异常"
            rm -f "$DETAIL_FILE"
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
    else
        echo "   ❌ 获取失败"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    
    # 延迟
    if [ $LINE_NUM -lt $TOTAL_LINES ]; then
        sleep 1
    fi
done < "$SECURITY_IDS_FILE"

echo ""
echo "✅ 步骤2完成"
echo "📊 获取结果:"
echo "  ✅ 成功: $SUCCESS_COUNT 个"
echo "  ❌ 失败: $FAIL_COUNT 个"
echo "  📊 成功率: $((SUCCESS_COUNT * 100 / TOTAL_LINES))%"

if [ $SUCCESS_COUNT -eq 0 ]; then
    echo "❌ 没有获取到任何详情"
    exit 1
fi

# ===== 步骤3：导出数据 =====
echo ""
echo "📋 步骤3：导出Excel数据"
echo "----------------------------------------"

# 创建Excel导出目录
EXCEL_DIR="Excel导出"
mkdir -p "$EXCEL_DIR"

# 合并所有详情文件
echo "🔗 合并详情数据..."
MERGED_FILE="$EXCEL_DIR/merged_details.json"
echo '{"details": [' > "$MERGED_FILE"

FIRST=true
for detail_file in "$DETAILS_DIR"/*.json; do
    if [ -f "$detail_file" ]; then
        if [ "$FIRST" = true ]; then
            FIRST=false
        else
            echo "," >> "$MERGED_FILE"
        fi
        cat "$detail_file" >> "$MERGED_FILE"
    fi
done

echo ']}' >> "$MERGED_FILE"

# 使用扩展导出器
echo "💾 导出到Excel..."
cd - > /dev/null  # 返回原目录

# 使用Python脚本导出
python3 -c "
import sys
import json
from datetime import datetime

sys.path.insert(0, '/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scripts')

try:
    from extended_excel_exporter import ExtendedExcelExporter
    
    # 加载合并的数据
    with open('$OUTPUT_DIR/$MERGED_FILE', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    details = data.get('details', [])
    print(f'📊 加载到 {len(details)} 个职位详情')
    
    if details:
        # 创建导出器
        exporter = ExtendedExcelExporter('$OUTPUT_DIR/$EXCEL_DIR')
        
        # 导出
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_files = exporter.export_detail_data(
            details,
            search_keyword='$KEYWORD',
            search_page=$PAGES,
            filename='${CITY}_${KEYWORD}_分步采集_${timestamp}.csv',
            include_stats=True
        )
        
        if output_files:
            print(f'✅ 导出成功!')
            print(f'📁 主文件: {output_files[0]}')
        else:
            print('❌ 导出失败')
    else:
        print('❌ 没有可导出的数据')
        
except ImportError as e:
    print(f'❌ 导入失败: {e}')
    print('💡 请确保扩展导出器可用')
except Exception as e:
    print(f'❌ 导出异常: {e}')
" 2>&1 | tee "$OUTPUT_DIR/export_log.txt"

echo ""
echo "🎉 分步工作流完成!"
echo "📊 采集统计:"
echo "  - 搜索关键词: $KEYWORD"
echo "  - 目标城市: $CITY"
echo "  - 处理页数: $PAGES"
echo "  - 提取securityId: $TOTAL_IDS 个"
echo "  - 获取详情: $SUCCESS_COUNT 个职位"
echo "  - 成功率: $((SUCCESS_COUNT * 100 / TOTAL_IDS))%"
echo "  - 输出目录: $OUTPUT_DIR"
echo ""
echo "📁 查看文件:"
echo "  ls -la $OUTPUT_DIR/"
echo ""
echo "📄 查看详情:"
echo "  ls -la $OUTPUT_DIR/$DETAILS_DIR/"
echo ""
echo "💾 查看Excel:"
echo "  ls -la $OUTPUT_DIR/$EXCEL_DIR/"