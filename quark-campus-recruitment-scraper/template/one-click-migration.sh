#!/bin/bash
# 🚀 一键迁移脚本 - 将模板系统迁移到新项目
# 版本: v1.0.0
# 创建时间: 2026-05-20
# 功能: 一键复制所有模板文件到新项目，并完成初始化配置

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

# 显示横幅
show_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                🚀 模板系统一键迁移工具                  ║"
    echo "║               版本: v1.0.0 | 2026-05-20                 ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 显示帮助
show_help() {
    echo "使用方法: $0 [选项] <项目名称>"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -v, --verbose  显示详细输出"
    echo "  -t, --test     测试模式（不实际创建文件）"
    echo "  -c, --company  指定公司名称（默认: 新公司）"
    echo "  -u, --url      指定招聘网站URL"
    echo ""
    echo "示例:"
    echo "  $0 字节跳动招聘爬取器"
    echo "  $0 -c \"阿里巴巴\" -u \"https://job.alibaba.com\" 阿里招聘爬取器"
    echo ""
    exit 0
}

# 参数解析
VERBOSE=false
TEST_MODE=false
COMPANY_NAME="新公司"
WEBSITE_URL="https://example.com"
PROJECT_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -t|--test)
            TEST_MODE=true
            shift
            ;;
        -c|--company)
            COMPANY_NAME="$2"
            shift 2
            ;;
        -u|--url)
            WEBSITE_URL="$2"
            shift 2
            ;;
        -*)
            log_error "未知选项: $1"
            show_help
            ;;
        *)
            PROJECT_NAME="$1"
            shift
            ;;
    esac
done

# 检查项目名称
if [ -z "$PROJECT_NAME" ]; then
    log_error "请提供项目名称"
    echo ""
    show_help
fi

# 检查目标目录是否已存在
if [ -d "$PROJECT_NAME" ] && [ "$TEST_MODE" = false ]; then
    log_warning "目录 '$PROJECT_NAME' 已存在"
    read -p "是否覆盖？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "操作已取消"
        exit 1
    fi
    rm -rf "$PROJECT_NAME"
fi

# 主函数
main() {
    show_banner
    
    log_info "开始迁移模板系统到新项目: $PROJECT_NAME"
    log_info "公司名称: $COMPANY_NAME"
    log_info "网站URL: $WEBSITE_URL"
    log_info "测试模式: $TEST_MODE"
    echo ""
    
    # 步骤1: 创建项目目录
    log_info "步骤1: 创建项目目录结构"
    if [ "$TEST_MODE" = false ]; then
        mkdir -p "$PROJECT_NAME"
        cd "$PROJECT_NAME" || exit 1
    else
        log_info "[测试模式] 将创建目录: $PROJECT_NAME"
        mkdir -p "/tmp/$PROJECT_NAME"
        cd "/tmp/$PROJECT_NAME" || exit 1
    fi
    
    # 步骤2: 复制模板文件
    log_info "步骤2: 复制模板文件"
    TEMPLATE_DIR="$(dirname "$0")"
    
    if [ "$VERBOSE" = true ]; then
        log_info "从 $TEMPLATE_DIR 复制文件..."
    fi
    
    if [ "$TEST_MODE" = false ]; then
        # 复制整个模板目录
        cp -r "$TEMPLATE_DIR"/. .
        # 移除脚本自身（避免递归）
        rm -f one-click-migration.sh
    else
        log_info "[测试模式] 将复制模板文件"
    fi
    
    # 步骤3: 重命名核心文档
    log_info "步骤3: 重命名核心文档"
    
    rename_files=(
        "docs/CHECKLIST_TEMPLATE.md:docs/CHECKLIST.md"
        "docs/LESSONS_LEARNED_TEMPLATE.md:docs/LESSONS_LEARNED.md"
        "memory-system/CORE_BUSINESS_INFO_TEMPLATE.md:CORE_BUSINESS_INFO.md"
        "memory-system/MEMORY_SYSTEM_GUIDE.md:MEMORY_SYSTEM_GUIDE.md"
    )
    
    for pair in "${rename_files[@]}"; do
        src="${pair%%:*}"
        dst="${pair##*:}"
        
        if [ "$TEST_MODE" = false ]; then
            if [ -f "$src" ]; then
                mv "$src" "$dst"
                if [ "$VERBOSE" = true ]; then
                    log_info "重命名: $src → $dst"
                fi
            else
                log_warning "文件不存在: $src"
            fi
        else
            log_info "[测试模式] 将重命名: $src → $dst"
        fi
    done
    
    # 步骤4: 创建项目目录结构
    log_info "步骤4: 创建项目目录结构"
    
    directories=(
        "output"
        "logs"
        "backup"
        "screenshots"
        "config"
        "scripts"
        "tests"
        "data"
    )
    
    for dir in "${directories[@]}"; do
        if [ "$TEST_MODE" = false ]; then
            mkdir -p "$dir"
            if [ "$VERBOSE" = true ]; then
                log_info "创建目录: $dir"
            fi
        else
            log_info "[测试模式] 将创建目录: $dir"
        fi
    done
    
    # 步骤5: 配置公司信息
    log_info "步骤5: 配置公司信息"
    
    if [ "$TEST_MODE" = false ]; then
        # 更新API认证配置
        if [ -f "config/api_auth_template.json" ]; then
            mv "config/api_auth_template.json" "config/api_auth.json"
            
            # 使用sed更新公司信息
            sed -i.bak "s/TODO: 填写公司名称（如：字节跳动、腾讯、阿里巴巴）/$COMPANY_NAME/g" config/api_auth.json
            sed -i.bak "s|TODO: 填写公司招聘网站URL|$WEBSITE_URL|g" config/api_auth.json
            
            # 清理备份文件
            rm -f config/api_auth.json.bak
            
            if [ "$VERBOSE" = true ]; then
                log_info "更新API配置: 公司=$COMPANY_NAME, URL=$WEBSITE_URL"
            fi
        fi
        
        # 更新项目配置
        if [ -f "config/project_config_template.json" ]; then
            mv "config/project_config_template.json" "config/project_config.json"
        fi
        
        # 更新核心业务信息
        if [ -f "CORE_BUSINESS_INFO.md" ]; then
            sed -i.bak "s/{项目名称}/$PROJECT_NAME/g" CORE_BUSINESS_INFO.md
            sed -i.bak "s/{你的公司名称}/$COMPANY_NAME/g" CORE_BUSINESS_INFO.md
            sed -i.bak "s|{招聘网站URL}|$WEBSITE_URL|g" CORE_BUSINESS_INFO.md
            sed -i.bak "s/{创建日期}/$(date '+%Y-%m-%d')/g" CORE_BUSINESS_INFO.md
            rm -f CORE_BUSINESS_INFO.md.bak
        fi
    else
        log_info "[测试模式] 将配置公司信息: $COMPANY_NAME ($WEBSITE_URL)"
    fi
    
    # 步骤6: 创建初始文件
    log_info "步骤6: 创建初始文件"
    
    if [ "$TEST_MODE" = false ]; then
        # 创建README.md
        cat > README.md << EOF
# $PROJECT_NAME

## 项目简介
基于模板系统快速创建的项目，用于爬取 $COMPANY_NAME 的招聘信息。

## 快速开始
\`\`\`bash
# 安装依赖
pip install -r requirements.txt

# 配置认证信息
# 编辑 config/api_auth.json 填写实际的API认证信息

# 运行测试
python template/framework/unified_crawler_entry.py --mode test
\`\`\`

## 目录结构
\`\`\`
$PROJECT_NAME/
├── CORE_BUSINESS_INFO.md          # 核心业务信息
├── docs/                          # 文档
│   ├── CHECKLIST.md              # 检查清单
│   └── LESSONS_LEARNED.md        # 教训记录
├── config/                        # 配置
│   ├── api_auth.json             # API认证
│   └── project_config.json       # 项目配置
├── memory-system/                 # 记忆系统
├── output/                        # 输出数据
├── logs/                         # 日志文件
├── scripts/                      # 脚本工具
└── template/                     # 原始模板（备份）
\`\`\`

## 使用说明
详细使用指南请参考: [MEMORY_SYSTEM_GUIDE.md](MEMORY_SYSTEM_GUIDE.md)

## 注意事项
1. 首次使用前，必须配置 \`config/api_auth.json\` 中的认证信息
2. 执行前请阅读 \`docs/CHECKLIST.md\` 检查清单
3. 遇到问题时，在 \`docs/LESSONS_LEARNED.md\` 中记录教训

---
**创建时间**: $(date '+%Y-%m-%d %H:%M:%S')
**模板版本**: v1.0.0
**项目状态**: 初始化完成
\`\`\`
EOF
        
        # 创建requirements.txt
        cat > requirements.txt << EOF
# 项目依赖包
requests>=2.28.0
pandas>=1.5.0
openpyxl>=3.0.0
python-dotenv>=0.21.0

# 开发依赖
pytest>=7.0.0
black>=22.0.0
flake8>=5.0.0

# 可选依赖
# beautifulsoup4>=4.11.0  # 如果需要HTML解析
# selenium>=4.0.0        # 如果需要浏览器自动化
EOF
        
        # 创建.gitignore
        cat > .gitignore << EOF
# 环境文件
.env
.venv
venv/
env/

# 日志文件
logs/*.log
*.log

# 输出文件
output/*
!output/.gitkeep

# 备份文件
backup/*

# 系统文件
.DS_Store
Thumbs.db

# IDE文件
.vscode/
.idea/
*.swp
*.swo

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 配置文件（包含敏感信息）
config/api_auth.json
config/local_*.json
EOF
        
        # 创建output目录占位文件
        touch output/.gitkeep
        touch logs/.gitkeep
        touch backup/.gitkeep
    else
        log_info "[测试模式] 将创建初始文件"
    fi
    
    # 步骤7: 创建验证脚本
    log_info "步骤7: 创建验证脚本"
    
    if [ "$TEST_MODE" = false ]; then
        cat > verify_setup.py << 'EOF'
#!/usr/bin/env python3
"""
项目设置验证脚本
验证模板迁移是否成功
"""

import os
import json
import sys

def check_required_files():
    """检查必需的文件是否存在"""
    required_files = [
        "CORE_BUSINESS_INFO.md",
        "docs/CHECKLIST.md",
        "docs/LESSONS_LEARNED.md",
        "MEMORY_SYSTEM_GUIDE.md",
        "config/api_auth.json",
        "config/project_config.json",
        "memory-system/CHECKPOINT_SYSTEM_TEMPLATE.json",
        "README.md",
        "requirements.txt",
        ".gitignore"
    ]
    
    print("📋 检查必需文件:")
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} 缺失")
            all_exist = False
    
    return all_exist

def check_json_files():
    """检查JSON文件格式"""
    json_files = [
        "config/api_auth.json",
        "config/project_config.json",
        "memory-system/CHECKPOINT_SYSTEM_TEMPLATE.json"
    ]
    
    print("\n📊 检查JSON文件格式:")
    all_valid = True
    for json_file in json_files:
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"  ✅ {json_file} 格式正确")
            except Exception as e:
                print(f"  ❌ {json_file} 格式错误: {e}")
                all_valid = False
        else:
            print(f"  ⚠️  {json_file} 不存在")
    
    return all_valid

def check_directories():
    """检查目录结构"""
    required_dirs = [
        "output",
        "logs",
        "backup",
        "config",
        "docs",
        "memory-system",
        "scripts"
    ]
    
    print("\n📁 检查目录结构:")
    all_exist = True
    for directory in required_dirs:
        if os.path.isdir(directory):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ 缺失")
            all_exist = False
    
    return all_exist

def check_todo_markers():
    """检查TODO标记（提醒用户需要配置）"""
    print("\n⚠️  需要配置的TODO标记:")
    
    todo_files = [
        "config/api_auth.json",
        "CORE_BUSINESS_INFO.md"
    ]
    
    has_todo = False
    for file in todo_files:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'TODO' in content:
                    print(f"  📝 {file} 中有TODO标记需要填写")
                    has_todo = True
    
    if not has_todo:
        print("  ✅ 没有发现TODO标记（或已全部配置）")
    
    return not has_todo

def main():
    print("🔍 项目设置验证")
    print("=" * 50)
    
    results = []
    
    # 执行检查
    results.append(("必需文件", check_required_files()))
    results.append(("JSON格式", check_json_files()))
    results.append(("目录结构", check_directories()))
    results.append(("TODO标记", check_todo_markers()))
    
    # 总结
    print("\n" + "=" * 50)
    print("🎯 验证结果:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} - {name}")
    
    print(f"\n📊 总结: {passed}/{total} 项通过")
    
    if passed == total:
        print("\n🎉 恭喜！项目设置验证全部通过！")
        print("💡 下一步: 配置 config/api_auth.json 中的认证信息")
        return 0
    else:
        print("\n⚠️  项目设置验证未通过，请根据提示修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF
        
        chmod +x verify_setup.py
    else
        log_info "[测试模式] 将创建验证脚本"
    fi
    
    # 步骤8: 创建启动脚本
    log_info "步骤8: 创建启动脚本"
    
    if [ "$TEST_MODE" = false ]; then
        cat > start_project.sh << 'EOF'
#!/bin/bash
# 项目启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 启动 $PROJECT_NAME 项目${NC}"
echo "=" * 50

# 检查Python环境
echo -e "${BLUE}🔧 检查Python环境...${NC}"
python --version
pip --version

# 检查依赖
echo -e "${BLUE}📦 检查依赖包...${NC}"
if [ -f "requirements.txt" ]; then
    echo "发现 requirements.txt"
    read -p "是否安装依赖？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        pip install -r requirements.txt
    fi
else
    echo "未找到 requirements.txt"
fi

# 验证设置
echo -e "${BLUE}🔍 验证项目设置...${NC}"
if [ -f "verify_setup.py" ]; then
    python verify_setup.py
else
    echo "验证脚本不存在"
fi

# 显示下一步
echo -e "${GREEN}🎯 下一步操作:${NC}"
echo "1. 编辑 config/api_auth.json 配置认证信息"
echo "2. 阅读 docs/CHECKLIST.md 执行检查清单"
echo "3. 运行 python verify_setup.py 验证配置"
echo "4. 开始开发！"
echo ""
echo -e "${BLUE}📚 相关文档:${NC}"
echo "- 核心业务信息: CORE_BUSINESS_INFO.md"
echo "- 记忆系统指南: MEMORY_SYSTEM_GUIDE.md"
echo "- 检查清单: docs/CHECKLIST.md"
EOF
        
        chmod +x start_project.sh
        
        # 替换脚本中的项目名称
        sed -i.bak "s/\$PROJECT_NAME/$PROJECT_NAME/g" start_project.sh
        rm -f start_project.sh.bak
    else
        log_info "[测试模式] 将创建启动脚本"
    fi
    
    # 完成
    echo ""
    log_success "✅ 模板迁移完成！"
    echo ""
    
    if [ "$TEST_MODE" = false ]; then
        echo "📁 项目位置: $(pwd)"
        echo ""
        echo "🚀 快速开始:"
        echo "  1. cd $(pwd)"
        echo "  2. ./start_project.sh"
        echo "  3. 配置 config/api_auth.json"
        echo "  4. 阅读 README.md 和 MEMORY_SYSTEM_GUIDE.md"
        echo ""
        echo "📊 验证迁移:"
        echo "  python verify_setup.py"
        echo ""
        echo "💡 提示: 使用 './start_project.sh' 启动项目"
    else
        echo "📝 [测试模式] 迁移流程验证完成"
        echo "💡 实际使用时请移除 -t 参数"
        # 清理测试目录
        cd ..
        rm -rf "/tmp/$PROJECT_NAME"
    fi
    
    echo ""
    echo "🎉 迁移完成！开始你的新项目吧！"
}

# 执行主函数
main "$@"