#!/bin/bash
# 🧠 夸克校园招聘爬取器 - 智能启动器
# 版本: 1.0
# 创建时间: 2026-05-19T15:03:08.023545

set -e  # 遇到错误立即退出

echo ""
echo "🧠 夸克校园招聘爬取器 记忆系统启动器"
echo "========================================"
echo ""

# 项目信息
PROJECT_NAME="夸克校园招聘爬取器"
PROJECT_PATH="/Users/xingan/.openclaw/workspace/skills/find_new_jobs/quark-campus-recruitment-scraper"
PROJECT_TYPE="web_scraper"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查是否在项目目录
if [ "$(pwd)" != "$PROJECT_PATH" ]; then
    print_warning "当前不在项目目录"
    print_info "建议切换到项目目录: cd $PROJECT_PATH"
    read -p "是否自动切换? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$PROJECT_PATH"
        print_success "已切换到项目目录: $(pwd)"
    fi
fi

# 1. 加载项目配置
print_info "1. 加载项目配置..."
CONFIG_FILE="config/memory_config.json"
if [ -f "$CONFIG_FILE" ]; then
    PROJECT_NAME=$(grep -o '"project_name":"[^"]*"' "$CONFIG_FILE" | cut -d'"' -f4 2>/dev/null || echo "$PROJECT_NAME")
    PROJECT_TYPE=$(grep -o '"project_type":"[^"]*"' "$CONFIG_FILE" | cut -d'"' -f4 2>/dev/null || echo "$PROJECT_TYPE")
    print_success "项目: $PROJECT_NAME ($PROJECT_TYPE)"
else
    print_warning "配置文件不存在: $CONFIG_FILE"
fi

# 2. 检查记忆文件完整性
print_info "2. 检查记忆文件完整性..."
REQUIRED_FILES=("ARCHITECTURE.md" "CHECKLIST.md" "LESSONS_LEARNED.md" "memory_checkpoints.json")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "  ✅ $file"
    else
        print_error "  ❌ $file"
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    print_warning "缺失文件: ${MISSING_FILES[*]}"
    print_info "建议运行: init-memory-system 重新初始化"
fi

# 3. 加载记忆检查点
print_info "3. 加载记忆检查点..."
CHECKPOINT_FILE="memory_checkpoints.json"
if [ -f "$CHECKPOINT_FILE" ]; then
    LAST_ACTION=$(grep -o '"last_action":"[^"]*"' "$CHECKPOINT_FILE" | cut -d'"' -f4 2>/dev/null || echo "未知")
    NEXT_ACTION=$(grep -o '"next_action":"[^"]*"' "$CHECKPOINT_FILE" | cut -d'"' -f4 2>/dev/null || echo "定义项目需求")
    PROGRESS=$(grep -o '"progress":[0-9]*' "$CHECKPOINT_FILE" | cut -d':' -f2 2>/dev/null || echo "0")
    
    print_success "  最后行动: $LAST_ACTION"
    print_success "  待办事项: $NEXT_ACTION"
    print_success "  当前进度: $PROGRESS%"
else
    print_warning "检查点文件不存在"
fi

# 4. 显示架构原则摘要
print_info "4. 显示架构原则摘要..."
ARCH_FILE="ARCHITECTURE.md"
if [ -f "$ARCH_FILE" ]; then
    echo ""
    grep -E "^## 🎯|^[0-9]+\. " "$ARCH_FILE" | head -5 | while read line; do
        echo "   📌 $line"
    done
else
    print_warning "架构文档不存在"
fi

# 5. 生成标准化指令
print_info "5. 生成标准化指令..."
echo ""
echo "🚀 基于记忆系统的标准化指令"
echo "========================================"
echo ""
echo "📋 项目: $PROJECT_NAME"
echo "🎯 待办: $NEXT_ACTION"
echo "📅 最后更新: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📊 进度: $PROGRESS%"
echo ""
echo "📝 执行命令:"
echo "执行${PROJECT_NAME}任务：步骤1验证记忆完整性，步骤2检查待办事项，步骤3${NEXT_ACTION}"
echo ""
echo "💡 提示: 复制上方指令发送给助手即可开始"
echo ""

# 6. 可选：自动运行记忆加载器
if [ -f "scripts/auto_memory_loader.py" ]; then
    read -p "是否运行自动记忆加载器? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "运行自动记忆加载器..."
        python scripts/auto_memory_loader.py
    fi
fi

echo ""
echo "========================================"
echo "🧠 记忆系统启动完成，祝工作顺利！"
echo ""