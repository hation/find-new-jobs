#!/bin/bash
# 夸克招聘爬取更新触发器
# 手动触发更新检查清单和错误教训记录

set -e

echo "========================================="
echo "🔄 夸克招聘爬取系统更新触发器"
echo "========================================="

# 配置路径
WORKSPACE_ROOT="$HOME/.openclaw/workspace"
SKILL_DIR="$WORKSPACE_ROOT/skills/quark-campus-recruitment-scraper"
SCRIPTS_DIR="$SKILL_DIR/scripts"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}❌ 错误:${NC} $1"
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠️ 警告:${NC} $1"
}

# 1. 检查环境
log "步骤1: 检查环境"
if [ ! -d "$SCRIPTS_DIR" ]; then
    error "脚本目录不存在: $SCRIPTS_DIR"
    exit 1
fi

cd "$SCRIPTS_DIR" || {
    error "无法进入脚本目录"
    exit 1
}

# 2. 检查Python环境
log "步骤2: 检查Python环境"
if ! command -v python3 &> /dev/null; then
    error "未找到python3命令"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
success "Python版本: $PYTHON_VERSION"

# 3. 选择更新模式
echo ""
echo "📋 选择更新模式:"
echo "1. 快速更新 (只更新检查清单)"
echo "2. 完整更新 (更新检查清单和错误教训)"
echo "3. 分析模式 (生成分析报告)"
echo "4. 全面模式 (运行所有更新和分析)"
echo ""

read -p "请选择模式 (1-4): " mode

case $mode in
    1)
        log "执行快速更新模式"
        echo ""
        python3 error_detector.py
        echo ""
        log "快速更新完成"
        ;;
    2)
        log "执行完整更新模式"
        echo ""
        python3 error_detector.py
        echo ""
        log "错误检测完成，开始更新文件..."
        echo ""
        
        # 读取错误检测结果
        if [ -f "../error_report.txt" ]; then
            echo "📄 错误报告:"
            cat "../error_report.txt"
            echo ""
        fi
        
        # 更新检查清单
        log "更新检查清单..."
        if [ -f "../CHECKLIST.md" ]; then
            backup_file="../CHECKLIST.md.backup.$(date +%Y%m%d_%H%M%S)"
            cp "../CHECKLIST.md" "$backup_file"
            log "已备份原文件: $(basename "$backup_file")"
        fi
        
        # 更新错误教训
        log "更新错误教训记录..."
        if [ -f "../LESSONS_LEARNED.md" ]; then
            backup_file="../LESSONS_LEARNED.md.backup.$(date +%Y%m%d_%H%M%S)"
            cp "../LESSONS_LEARNED.md" "$backup_file"
            log "已备份原文件: $(basename "$backup_file")"
        fi
        
        # 运行自动更新
        python3 auto_updater.py &
        UPDATE_PID=$!
        
        # 等待更新完成
        log "等待更新完成..."
        sleep 5
        
        # 检查更新状态
        if ps -p $UPDATE_PID > /dev/null; then
            log "更新进程运行中，将在后台继续..."
            echo "更新进程ID: $UPDATE_PID"
        else
            wait $UPDATE_PID
            UPDATE_STATUS=$?
            if [ $UPDATE_STATUS -eq 0 ]; then
                success "完整更新完成"
            else
                error "更新失败，退出码: $UPDATE_STATUS"
            fi
        fi
        ;;
    3)
        log "执行分析模式"
        echo ""
        python3 error_detector.py
        echo ""
        
        # 生成分析报告
        log "生成分析报告..."
        REPORT_FILE="../analysis_report_$(date +%Y%m%d_%H%M%S).md"
        
        cat > "$REPORT_FILE" << EOF
# 夸克招聘爬取系统分析报告
生成时间: $(date '+%Y-%m-%d %H:%M:%S')

## 📊 系统状态

### 文件状态
EOF
        
        # 检查文件状态
        for file in "../CHECKLIST.md" "../LESSONS_LEARNED.md" "../errors_database.json"; do
            if [ -f "$file" ]; then
                size=$(du -h "$file" | cut -f1)
                mtime=$(stat -f "%Sm" "$file")
                echo "- **$(basename "$file")**: $size, 最后修改: $mtime" >> "$REPORT_FILE"
            else
                echo "- **$(basename "$file")**: 不存在" >> "$REPORT_FILE"
            fi
        done
        
        # 添加执行统计
        cat >> "$REPORT_FILE" << EOF

### 执行统计
- 触发时间: $(date '+%Y-%m-%d %H:%M:%S')
- 更新模式: 分析模式
- 脚本目录: $SCRIPTS_DIR

## 🎯 建议

### 立即行动
1. 检查所有备份文件
2. 验证检查清单完整性
3. 更新错误教训记录中的统计信息

### 长期改进
1. 实现自动错误检测
2. 建立定期更新机制
3. 优化错误预防策略
EOF
        
        success "分析报告已生成: $(basename "$REPORT_FILE")"
        echo ""
        echo "📄 报告内容摘要:"
        tail -20 "$REPORT_FILE"
        ;;
    4)
        log "执行全面模式"
        echo ""
        
        # 运行全面更新
        log "启动全面更新系统..."
        python3 auto_updater.py --full &
        FULL_PID=$!
        
        log "全面更新进程已启动 (PID: $FULL_PID)"
        echo ""
        echo "📋 全面更新将执行以下任务:"
        echo "1. 错误检测与分析"
        echo "2. 检查清单更新"
        echo "3. 错误教训记录更新"
        echo "4. 生成详细分析报告"
        echo "5. 建立更新历史记录"
        echo ""
        echo "🔄 更新将在后台运行，请查看日志文件:"
        echo "   - auto_updater.log (更新日志)"
        echo "   - error_report.txt (错误报告)"
        echo "   - analysis_report.md (分析报告)"
        echo ""
        
        # 提供监控命令
        echo "🔍 监控命令:"
        echo "tail -f auto_updater.log"
        echo "tail -f ../error_report.txt"
        echo ""
        
        success "全面更新已启动，进程ID: $FULL_PID"
        ;;
    *)
        error "无效的选择: $mode"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "🎯 更新触发器执行完成"
echo "========================================="

# 显示更新后的文件状态
echo ""
echo "📁 更新后文件状态:"
echo "------------------"

for file in "../CHECKLIST.md" "../LESSONS_LEARNED.md"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        lines=$(wc -l < "$file")
        echo "$(basename "$file"): $size, $lines 行"
    fi
done

# 检查备份文件
backup_count=$(find .. -name "*.backup.*" -type f | wc -l)
if [ $backup_count -gt 0 ]; then
    echo ""
    echo "💾 备份文件: $backup_count 个"
    find .. -name "*.backup.*" -type f -exec basename {} \; | head -5
    if [ $backup_count -gt 5 ]; then
        echo "... 还有 $(($backup_count - 5)) 个"
    fi
fi

echo ""
echo "🚀 下次更新:"
echo "1. 手动运行: ./trigger_update.sh"
echo "2. 定时运行: 添加到cron任务"
echo "3. 自动运行: 使用 auto_updater.py 调度器"
echo "========================================="