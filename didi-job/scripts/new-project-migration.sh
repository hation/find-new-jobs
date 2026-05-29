#!/bin/bash

# 🚀 夸克项目模板一键迁移工具
# 将夸克项目的完整知识体系迁移到新项目

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "夸克项目模板一键迁移工具"
    echo ""
    echo "用法: $0 [选项] <新项目名称>"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示此帮助信息"
    echo "  -d, --dir <目录>    指定新项目目录（默认：当前目录）"
    echo "  -t, --type <类型>   项目类型：crawler（爬虫，默认）、api、data-processing"
    echo "  -f, --force         强制覆盖已存在的文件"
    echo "  --skip-docs         跳过文档模板迁移"
    echo "  --skip-scripts      跳过脚本文件迁移"
    echo "  --skip-memory       跳过记忆系统迁移"
    echo "  --dry-run           只显示将要执行的操作，不实际执行"
    echo ""
    echo "示例:"
    echo "  $0 字节跳动招聘爬取器"
    echo "  $0 -d ~/projects -t crawler 美团招聘爬取器"
    echo "  $0 --dry-run 测试项目"
}

# 解析命令行参数
PROJECT_NAME=""
TARGET_DIR="."
PROJECT_TYPE="crawler"
FORCE_OVERWRITE=false
SKIP_DOCS=false
SKIP_SCRIPTS=false
SKIP_MEMORY=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--dir)
            TARGET_DIR="$2"
            shift 2
            ;;
        -t|--type)
            PROJECT_TYPE="$2"
            shift 2
            ;;
        -f|--force)
            FORCE_OVERWRITE=true
            shift
            ;;
        --skip-docs)
            SKIP_DOCS=true
            shift
            ;;
        --skip-scripts)
            SKIP_SCRIPTS=true
            shift
            ;;
        --skip-memory)
            SKIP_MEMORY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -*)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
        *)
            PROJECT_NAME="$1"
            shift
            ;;
    esac
done

# 验证参数
if [ -z "$PROJECT_NAME" ]; then
    log_error "请提供新项目名称"
    show_help
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")"

# 新项目路径
NEW_PROJECT_PATH="$TARGET_DIR/$PROJECT_NAME"

# 显示迁移信息
echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│              🚀 夸克项目模板迁移工具                    │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│ 源项目: 夸克校园招聘爬取器                              │"
echo "│ 新项目: $PROJECT_NAME"
echo "│ 项目类型: $PROJECT_TYPE"
echo "│ 目标目录: $NEW_PROJECT_PATH"
echo "│ 迁移模式: $([ "$DRY_RUN" = true ] && echo "模拟运行" || echo "实际执行")"
echo "│ 模板版本: v1.1.0（优化增强版）                          │"
echo "│ 包含优化: ✅ Cookie管理 ✅ 参数验证 ✅ 数据质量          │"
echo "└─────────────────────────────────────────────────────────┘"

# 显示优化信息
if [ "$DRY_RUN" = false ]; then
    echo "📋 本次迁移包含以下优化（基于滴滴项目经验）:"
    echo "  1. 🍪 Cookie管理增强: SESSION自动更新、多Cookie轮换"
    echo "  2. 🎯 参数智能验证: jobType等参数自动发现和验证"
    echo "  3. 📊 数据质量保证: 实时保存、完整性检查、断点续传"
    echo "  4. 🔔 智能监控预警: 实时监控、智能预警、趋势分析"
    echo "  5. 🔄 经验反哺机制: 教训沉淀、模板更新、知识共享"
    echo ""
fi
echo ""

# 显示优化信息
if [ "$DRY_RUN" = false ]; then
    echo "📋 本次迁移包含以下优化（基于滴滴项目经验）:"
    echo "  1. 🍪 Cookie管理增强: SESSION自动更新、多Cookie轮换"
    echo "  2. 🎯 参数智能验证: jobType等参数自动发现和验证"
    echo "  3. 📊 数据质量保证: 实时保存、完整性检查、断点续传"
    echo "  4. 🔔 智能监控预警: 实时监控、智能预警、趋势分析"
    echo "  5. 🔄 经验反哺机制: 教训沉淀、模板更新、知识共享"
    echo ""
fi

if [ "$DRY_RUN" = true ]; then
    log_info "模拟运行模式：只显示将要执行的操作"
fi

# 检查目标目录是否存在
if [ -d "$NEW_PROJECT_PATH" ] && [ "$FORCE_OVERWRITE" = false ]; then
    log_error "目录已存在: $NEW_PROJECT_PATH"
    log_error "使用 -f 选项强制覆盖，或选择其他目录"
    exit 1
fi

# 创建新项目目录结构
create_project_structure() {
    log_info "创建新项目目录结构..."
    
    local dirs=(
        "$NEW_PROJECT_PATH"
        "$NEW_PROJECT_PATH/docs"
        "$NEW_PROJECT_PATH/config"
        "$NEW_PROJECT_PATH/scripts"
        "$NEW_PROJECT_PATH/src"
        "$NEW_PROJECT_PATH/tests"
        "$NEW_PROJECT_PATH/logs"
        "$NEW_PROJECT_PATH/data"
        "$NEW_PROJECT_PATH/data/raw"
        "$NEW_PROJECT_PATH/data/processed"
        "$NEW_PROJECT_PATH/data/backup"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            if [ "$DRY_RUN" = true ]; then
                log_info "[模拟] 创建目录: $dir"
            else
                mkdir -p "$dir"
                log_success "创建目录: $dir"
            fi
        fi
    done
}

# 迁移文档模板
migrate_docs() {
    if [ "$SKIP_DOCS" = true ]; then
        log_warning "跳过文档模板迁移"
        return
    fi
    
    log_info "迁移文档模板..."
    
    local docs=(
        "CORE_BUSINESS_INFO_TEMPLATE.md:CORE_BUSINESS_INFO.md"
        "ARCHITECTURE_TEMPLATE.md:ARCHITECTURE.md"
        "CHECKLIST_TEMPLATE.md:CHECKLIST.md"
        "LESSONS_LEARNED_TEMPLATE.md:LESSONS_LEARNED.md"
        "PROJECT_STRUCTURE.md:PROJECT_STRUCTURE.md"
        "QUICK_START_TEMPLATE.md:QUICK_START.md"
        "API_DOCUMENTATION_TEMPLATE.md:API_DOCUMENTATION.md"
        "MIGRATION_TEMPLATE.md:MIGRATION.md"
        "BUSINESS_KNOWLEDGE_SYSTEM.md:BUSINESS_KNOWLEDGE_SYSTEM.md"
        "BUSINESS_TEMPLATE_FLOW.md:BUSINESS_TEMPLATE_FLOW.md"
        "TEMPLATE_SYSTEM_EXECUTION_GUIDE.md:TEMPLATE_SYSTEM_EXECUTION_GUIDE.md"
    )
    
    for doc_pair in "${docs[@]}"; do
        local src="${doc_pair%%:*}"
        local dst="${doc_pair##*:}"
        local src_path="$TEMPLATE_DIR/docs/$src"
        local dst_path="$NEW_PROJECT_PATH/docs/$dst"
        
        if [ -f "$src_path" ]; then
            if [ "$DRY_RUN" = true ]; then
                log_info "[模拟] 复制文档: $src → $dst"
            else
                cp "$src_path" "$dst_path"
                
                # 替换模板中的占位符
                sed -i.bak "s/{项目名称}/$PROJECT_NAME/g" "$dst_path"
                sed -i.bak "s/{创建日期}/$(date '+%Y-%m-%d')/g" "$dst_path"
                sed -i.bak "s/{项目类型}/$PROJECT_TYPE/g" "$dst_path"
                rm -f "$dst_path.bak"
                
                log_success "迁移文档: $dst"
            fi
        else
            log_warning "源文件不存在: $src_path"
        fi
    done
}

# 迁移记忆系统
migrate_memory_system() {
    if [ "$SKIP_MEMORY" = true ]; then
        log_warning "跳过记忆系统迁移"
        return
    fi
    
    log_info "迁移记忆系统..."
    
    local memory_files=(
        "DAILY_MEMORY_TEMPLATE.md:DAILY_MEMORY_TEMPLATE.md"
        "CORE_BUSINESS_INFO_TEMPLATE.md:CORE_BUSINESS_INFO_TEMPLATE.md"
        "MEMORY_SYSTEM_GUIDE.md:MEMORY_SYSTEM_GUIDE.md"
    )
    
    # 创建记忆系统目录
    local memory_dir="$NEW_PROJECT_PATH/memory-system"
    if [ ! -d "$memory_dir" ]; then
        if [ "$DRY_RUN" = true ]; then
            log_info "[模拟] 创建目录: $memory_dir"
        else
            mkdir -p "$memory_dir"
        fi
    fi
    
    for mem_pair in "${memory_files[@]}"; do
        local src="${mem_pair%%:*}"
        local dst="${mem_pair##*:}"
        local src_path="$TEMPLATE_DIR/memory-system/$src"
        local dst_path="$memory_dir/$dst"
        
        if [ -f "$src_path" ]; then
            if [ "$DRY_RUN" = true ]; then
                log_info "[模拟] 复制记忆文件: $src → $dst"
            else
                cp "$src_path" "$dst_path"
                log_success "迁移记忆文件: $dst"
            fi
        else
            log_warning "源文件不存在: $src_path"
        fi
    done
}

# 迁移脚本文件
migrate_scripts() {
    if [ "$SKIP_SCRIPTS" = true ]; then
        log_warning "跳过脚本文件迁移"
        return
    fi
    
    log_info "迁移脚本文件..."
    
    # 复制本迁移脚本
    local script_dst="$NEW_PROJECT_PATH/scripts/new-project-migration.sh"
    if [ "$DRY_RUN" = true ]; then
        log_info "[模拟] 复制迁移脚本: $script_dst"
    else
        cp "$0" "$script_dst"
        chmod +x "$script_dst"
        log_success "迁移脚本: new-project-migration.sh"
    fi
    
    # 复制其他示例脚本
    local example_scripts=(
        "start_project.sh"
        "validate_config.py"
        "generate_report.py"
        "backup_data.sh"
    )
    
    for script in "${example_scripts[@]}"; do
        local src_path="$TEMPLATE_DIR/scripts/examples/$script"
        local dst_path="$NEW_PROJECT_PATH/scripts/$script"
        
        if [ -f "$src_path" ]; then
            if [ "$DRY_RUN" = true ]; then
                log_info "[模拟] 复制示例脚本: $script"
            else
                cp "$src_path" "$dst_path"
                chmod +x "$dst_path"
                log_success "迁移示例脚本: $script"
            fi
        fi
    done
    
    # 复制核心工具（包括经验反哺工具）
    local core_tools=(
        "component_registry.py"      # 组件注册系统（meituan-job经验）
        "check_integration.py"       # 集成检查脚本（meituan-job经验）
        "fix_integration.py"         # 自动修复脚本（meituan-job经验）
        "template_knowledge_sync.py" # 模板知识同步（经验反哺工具）
        "update_template_docs.py"    # 模板文档更新（经验反哺工具）
    )
    
    for tool in "${core_tools[@]}"; do
        local src_path="$TEMPLATE_DIR/scripts/$tool"
        local dst_path="$NEW_PROJECT_PATH/scripts/$tool"
        
        if [ -f "$src_path" ]; then
            if [ "$DRY_RUN" = true ]; then
                log_info "[模拟] 复制核心工具: $tool"
            else
                cp "$src_path" "$dst_path"
                log_success "迁移核心工具: $tool"
            fi
        else
            log_warning "核心工具不存在: $src_path"
        fi
    done
}

# 创建项目配置文件
create_config_files() {
    log_info "创建项目配置文件..."
    
    # 创建核心配置文件
    local config_file="$NEW_PROJECT_PATH/config/project_config.json"
    if [ "$DRY_RUN" = true ]; then
        log_info "[模拟] 创建配置文件: $config_file"
    else
        cat > "$config_file" << EOF
{
  "project": {
    "name": "$PROJECT_NAME",
    "type": "$PROJECT_TYPE",
    "created_date": "$(date '+%Y-%m-%d')",
    "version": "1.0.0",
    "description": "基于夸克项目模板创建的 $PROJECT_TYPE 项目"
  },
  "template_system": {
    "source": "夸克校园招聘爬取器",
    "migration_date": "$(date '+%Y-%m-%d %H:%M:%S')",
    "templates_migrated": [
      "CORE_BUSINESS_INFO_TEMPLATE.md",
      "ARCHITECTURE_TEMPLATE.md", 
      "CHECKLIST_TEMPLATE.md",
      "LESSONS_LEARNED_TEMPLATE.md",
      "PROJECT_STRUCTURE.md",
      "QUICK_START_TEMPLATE.md",
      "API_DOCUMENTATION_TEMPLATE.md",
      "MIGRATION_TEMPLATE.md"
    ]
  },
  "workflow": {
    "use_checklist": true,
    "record_lessons": true,
    "daily_memory": true,
    "auto_backup": true
  }
}
EOF
        log_success "创建配置文件: project_config.json"
    fi
    
    # 创建环境配置文件示例
    local env_example="$NEW_PROJECT_PATH/config/.env.example"
    if [ "$DRY_RUN" = true ]; then
        log_info "[模拟] 创建环境配置示例: $env_example"
    else
        cat > "$env_example" << EOF
# 项目环境变量配置
PROJECT_NAME="$PROJECT_NAME"
PROJECT_TYPE="$PROJECT_TYPE"

# API配置（如果是API项目）
API_BASE_URL="https://api.example.com"
API_KEY="your_api_key_here"
API_SECRET="your_api_secret_here"

# 数据库配置（如果需要）
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="${PROJECT_NAME// /_}"
DB_USER="postgres"
DB_PASSWORD="your_password"

# 日志配置
LOG_LEVEL="INFO"
LOG_DIR="./logs"

# 数据目录
DATA_DIR="./data"
RAW_DATA_DIR="\${DATA_DIR}/raw"
PROCESSED_DATA_DIR="\${DATA_DIR}/processed"
EOF
        log_success "创建环境配置示例: .env.example"
    fi
}

# 创建项目启动说明
create_startup_guide() {
    log_info "创建项目启动说明..."
    
    local readme_file="$NEW_PROJECT_PATH/README.md"
    if [ "$DRY_RUN" = true ]; then
        log_info "[模拟] 创建README: $readme_file"
    else
        cat > "$readme_file" << 'EOF'
# 🚀 项目启动指南

## 📋 项目概述

这是一个基于**夸克项目模板系统**创建的项目，继承了完整的最佳实践和经验体系。

## 🎯 立即开始

### 第一步：理解业务目标
1. 打开 `docs/CORE_BUSINESS_INFO.md`
2. 与团队一起填写业务信息
3. 明确项目目标和成功标准

### 第二步：设计技术方案
1. 参考 `docs/ARCHITECTURE.md` 设计架构
2. 根据 `docs/PROJECT_STRUCTURE.md` 组织代码
3. 制定 `docs/CHECKLIST.md` 中的检查项

### 第三步：开始执行
1. 按照 `docs/QUICK_START.md` 快速启动
2. 执行前检查 `docs/CHECKLIST.md`
3. 遇到问题记录在 `docs/LESSONS_LEARNED.md`

## 🔧 核心工作流程

### 每日工作
1. **早晨**: 查看今日任务和检查清单
2. **执行前**: 运行检查清单验证
3. **执行中**: 记录关键决策和发现
4. **执行后**: 更新进度和记录教训
5. **晚上**: 整理每日记忆

### 遇到问题时
1. 立即在 `docs/LESSONS_LEARNED.md` 中记录
2. 分析根本原因和解决方案
3. 更新 `docs/CHECKLIST.md` 防止重复犯错

## 📁 项目结构

```
项目根目录/
├── docs/                    # 项目文档
│   ├── CORE_BUSINESS_INFO.md     # 核心业务信息
│   ├── ARCHITECTURE.md           # 架构设计
│   ├── CHECKLIST.md              # 检查清单
│   ├── LESSONS_LEARNED.md        # 教训记录
│   ├── PROJECT_STRUCTURE.md      # 项目结构
│   ├── QUICK_START.md            # 快速开始
│   ├── API_DOCUMENTATION.md      # API文档
│   ├── MIGRATION.md              # 迁移指南
│   └── TEMPLATE_SYSTEM_EXECUTION_GUIDE.md # 模板使用指南
├── config/                  # 配置文件
├── scripts/                # 工具脚本
├── src/                    # 源代码
├── tests/                  # 测试代码
├── logs/                   # 日志文件
├── data/                   # 数据文件
└── memory-system/          # 记忆系统
```

## 🔄 模板系统说明

本项目基于夸克校园招聘爬取器的模板系统，包含：

1. **防错系统**: 通过检查清单防止重复犯错
2. **学习系统**: 通过教训记录持续改进
3. **记忆系统**: 通过每日记忆积累知识
4. **传承系统**: 通过标准化模板传递经验

## 🆘 快速帮助

### 常见问题
1. **Q: 从哪里开始？**
   A: 从 `docs/CORE_BUSINESS_INFO.md` 开始，明确业务目标。

2. **Q: 如何确保质量？**
   A: 使用 `docs/CHECKLIST.md` 进行检查，遇到问题记录在 `docs/LESSONS_LEARNED.md`。

3. **Q: 如何记录工作？**
   A: 使用 `memory-system/DAILY_MEMORY_TEMPLATE.md` 记录每日工作。

### 紧急情况
- 查看 `docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md` 获取快速指南
- 查看 `docs/BUSINESS_TEMPLATE_FLOW.md` 理解模板关联
- 查看 `docs/BUSINESS_KNOWLEDGE_SYSTEM.md` 获取完整知识体系

## 📞 联系支持

如果遇到模板使用问题，可以参考：
- 夸克项目原始文档
- 模板系统中的使用指南
- 团队内部知识库

---

**项目基于夸克模板系统创建，祝您项目顺利！** 🚀
EOF
        log_success "创建README.md"
    fi
}

# 创建项目启动脚本
create_startup_script() {
    log_info "创建项目启动脚本..."
    
    local startup_script="$NEW_PROJECT_PATH/start_project.sh"
    if [ "$DRY_RUN" = true ]; then
        log_info "[模拟] 创建启动脚本: $startup_script"
    else
        cat > "$startup_script" << 'EOF'
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
EOF
        chmod +x "$startup_script"
        log_success "创建启动脚本: start_project.sh"
    fi
}

# 验证迁移结果
validate_migration() {
    log_info "验证迁移结果..."
    
    local validation_passed=true
    
    # 检查核心文件是否存在
    local core_files=(
        "$NEW_PROJECT_PATH/docs/CORE_BUSINESS_INFO.md"
        "$NEW_PROJECT_PATH/docs/CHECKLIST.md"
        "$NEW_PROJECT_PATH/docs/LESSONS_LEARNED.md"
        "$NEW_PROJECT_PATH/README.md"
        "$NEW_PROJECT_PATH/config/project_config.json"
    )
    
    for file in "${core_files[@]}"; do
        if [ ! -f "$file" ] && [ "$DRY_RUN" = false ]; then
            log_error "缺少核心文件: $(basename "$file")"
            validation_passed=false
        fi
    done
    
    if [ "$validation_passed" = true ]; then
        log_success "迁移验证通过"
    else
        log_error "迁移验证失败，请检查日志"
        return 1
    fi
}

# 显示完成信息
show_completion() {
    echo ""
    echo "┌─────────────────────────────────────────────────────────┐"
    echo "│              🎉 迁移完成！                              │"
    echo "├─────────────────────────────────────────────────────────┤"
    echo "│                                                         │"
    echo "│  新项目已创建: $NEW_PROJECT_PATH"
    echo "│                                                         │"
    echo "│  📁 包含以下内容:                                       │"
    echo "│  • 完整的文档模板体系                                   │"
    echo "│  • 记忆系统和每日记录模板                               │"
    echo "│  • 项目配置和启动脚本                                   │"
    echo "│  • 一键迁移工具（可继续迁移）                           │"
    echo "│                                                         │"
    echo "│  🚀 立即开始:                                           │"
    echo "│  1. cd $NEW_PROJECT_PATH"
    echo "│  2. ./start_project.sh                                  │"
    echo "│  3. 按照向导开始项目                                    │"
    echo "│                                                         │"
    echo "│  📚 核心文档位置:                                       │"
    echo "│  • 业务目标: docs/CORE_BUSINESS_INFO.md                 │"
    echo "│  • 检查清单: docs/CHECKLIST.md                          │"
    echo "│  • 快速开始: docs/QUICK_START.md                        │"
echo "│  • 教训记录: docs/LESSONS_LEARNED.md（滴滴经验）         │"
echo "│  • 架构设计: docs/ARCHITECTURE.md（优化版）             │"
echo "│  • 流程优化: docs/BUSINESS_TEMPLATE_FLOW.md（增强版）    │"
echo "│  • 使用指南: docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md    │"
echo "│                                                         │"
echo "│  🚀 包含的优化功能（基于滴滴项目）:                      │"
echo "│  • 🍪 Cookie管理增强（防SESSION过期）                   │"
echo "│  • 🎯 参数智能验证（自动发现jobType等）                 │"
echo "│  • 📊 数据质量保证（实时保存+完整性检查）               │"
echo "│  • 🔔 智能监控预警（实时监控+趋势分析）                 │"
echo "│  • 🔄 经验反哺机制（教训沉淀+模板更新）                 │"
echo "│                                                         │"
echo "│                                                         │"
    echo "│  🔄 继续迁移:                                           │"
    echo "│  如果需要将本项目经验迁移到其他项目，可以运行:          │"
    echo "│  ./scripts/new-project-migration.sh 新项目名称           │"
    echo "│                                                         │"
    echo "└─────────────────────────────────────────────────────────┘"
    echo ""
    
    if [ "$DRY_RUN" = false ]; then
        log_success "迁移完成！新项目已准备就绪。"
        log_info "下一步：按照 README.md 中的指南开始项目"
    else
        log_info "模拟运行完成，显示将要执行的操作"
        log_info "实际执行命令: $0 -f $PROJECT_NAME"
    fi
}

# 主执行流程
main() {
    log_info "开始迁移夸克项目模板到新项目: $PROJECT_NAME"
    
    # 执行各个迁移步骤
    create_project_structure
    migrate_docs
    migrate_memory_system
    migrate_scripts
    create_config_files
    create_startup_guide
    create_startup_script
    
    if [ "$DRY_RUN" = false ]; then
        validate_migration
    fi
    
    show_completion
}

# 执行主函数
main

exit 0
