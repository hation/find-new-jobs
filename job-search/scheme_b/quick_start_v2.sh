#!/bin/bash
# 方案B - 快速启动脚本 v2
# 适用于技能架构

echo "🚀 方案B - 快速启动脚本"
echo "=========================================="
echo "💡 基于已验证的解决方案B工作流"
echo "💡 解决token有效期短的问题"
echo "=========================================="

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查工作目录
echo -e "${BLUE}🔍 检查工作目录...${NC}"
if [ -z "$SCHEME_B_WORKSPACE" ]; then
    DEFAULT_WORKSPACE="$HOME/招聘数据/方案B_立即执行_20260515_010114"
    if [ -d "$DEFAULT_WORKSPACE" ]; then
        export SCHEME_B_WORKSPACE="$DEFAULT_WORKSPACE"
        echo -e "${GREEN}✅ 使用默认工作目录: $SCHEME_B_WORKSPACE${NC}"
    else
        echo -e "${RED}❌ 请设置 SCHEME_B_WORKSPACE 环境变量${NC}"
        echo -e "${YELLOW}💡 例如: export SCHEME_B_WORKSPACE=\"/path/to/your/workspace\"${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ 工作目录已设置: $SCHEME_B_WORKSPACE${NC}"
fi

# 检查目录是否存在
if [ ! -d "$SCHEME_B_WORKSPACE" ]; then
    echo -e "${RED}❌ 工作目录不存在: $SCHEME_B_WORKSPACE${NC}"
    exit 1
fi

# 进入工作目录
cd "$SCHEME_B_WORKSPACE" || {
    echo -e "${RED}❌ 无法进入工作目录${NC}"
    exit 1
}

echo -e "${GREEN}📁 当前工作目录: $(pwd)${NC}"

# 检查必要文件
echo -e "${BLUE}🔍 检查必要文件...${NC}"
REQUIRED_FILES=("all_security_ids_final.txt")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ 缺少必要文件: $file${NC}"
        exit 1
    fi
done

# 检查可选文件
echo -e "${BLUE}🔍 检查可选文件...${NC}"
OPTIONAL_FILES=("fetched_security_ids.txt" "职位详情/" "深圳AI岗位_*.xlsx")
for file in "${OPTIONAL_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${YELLOW}⚠️  可选文件不存在: $file${NC}"
    fi
done

# 检查boss命令
echo -e "${BLUE}🔍 检查boss命令...${NC}"
if command -v boss &> /dev/null; then
    echo -e "${GREEN}✅ boss命令可用${NC}"
    boss --version
else
    echo -e "${RED}❌ boss命令不可用${NC}"
    echo -e "${YELLOW}💡 请安装: pip install boss-cli${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}📋 可用操作:${NC}"
echo "=========================================="
echo "1. 🔑 登录BOSS直聘"
echo "2. 🚀 获取职位详情"
echo "3. 📊 合并Excel数据"
echo "4. 📈 查看数据状态"
echo "5. 🔄 完整工作流"
echo "6. ❌ 退出"
echo "=========================================="

read -p "请选择操作 (1-6): " choice

case $choice in
    1)
        echo -e "${BLUE}🔑 登录BOSS直聘${NC}"
        echo "=========================================="
        echo "💡 请确保:"
        echo "1. 完全关闭Chrome浏览器"
        echo "2. 重新打开Chrome并登录BOSS直聘"
        echo "3. 然后运行以下命令获取cookie"
        echo ""
        read -p "按 Enter 键继续..." 
        boss logout 2>/dev/null
        boss login --cookie-source chrome
        ;;
    2)
        echo -e "${BLUE}🚀 获取职位详情${NC}"
        echo "=========================================="
        echo "💡 激进策略: 每次登录获取2个详情"
        echo "💡 token有效期: 约3-5分钟"
        echo ""
        python3 "$(dirname "$0")/scripts/fetch_details_smart_v2.py"
        ;;
    3)
        echo -e "${BLUE}📊 合并Excel数据${NC}"
        echo "=========================================="
        echo "💡 使用正确的ID映射: Excel职位ID = JSON encryptId"
        echo ""
        python3 "$(dirname "$0")/scripts/scheme_b_excel_correct_merge_v2.py"
        ;;
    4)
        echo -e "${BLUE}📈 查看数据状态${NC}"
        echo "=========================================="
        python3 -c "
import os
import glob
import pandas as pd

print('📊 当前数据状态:')
print('=' * 40)

# 检查详情文件
detail_files = glob.glob('职位详情/detail_*.json')
print(f'📁 详情文件: {len(detail_files)} 个')

# 检查Excel文件
excel_files = sorted(glob.glob('深圳AI岗位_*.xlsx'))
if excel_files:
    latest = excel_files[-1]
    print(f'📊 Excel文件: {os.path.basename(latest)}')
    
    try:
        df = pd.read_excel(latest)
        print(f'   总职位数: {len(df)}')
        
        if '数据完整性' in df.columns:
            complete = (df['数据完整性'] == '完整').sum()
            print(f'   完整数据: {complete} ({complete/len(df)*100:.1f}%)')
        
        if '数据来源' in df.columns:
            sources = df['数据来源'].value_counts()
            print(f'   数据来源分布:')
            for source, count in sources.items():
                print(f'     • {source}: {count}')
    except:
        print('   无法读取Excel文件')
else:
    print('❌ 没有Excel文件')

# 检查获取记录
if os.path.exists('fetched_security_ids.txt'):
    with open('fetched_security_ids.txt', 'r') as f:
        fetched = sum(1 for _ in f)
    print(f'📝 已获取记录: {fetched} 个')

print('=' * 40)
"
        ;;
    5)
        echo -e "${BLUE}🔄 完整工作流${NC}"
        echo "=========================================="
        echo "💡 执行完整的工作流:"
        echo "1. 登录 → 2. 获取详情 → 3. 合并数据"
        echo ""
        read -p "按 Enter 键开始..." 
        
        # 步骤1: 登录
        echo -e "${YELLOW}步骤1: 登录BOSS直聘${NC}"
        echo "💡 请确保已在Chrome中登录BOSS直聘"
        read -p "按 Enter 键继续..." 
        boss logout 2>/dev/null
        boss login --cookie-source chrome
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 登录成功${NC}"
            
            # 步骤2: 获取详情
            echo -e "${YELLOW}步骤2: 获取职位详情${NC}"
            python3 "$(dirname "$0")/scripts/fetch_details_smart_v2.py"
            
            # 步骤3: 合并数据
            echo -e "${YELLOW}步骤3: 合并Excel数据${NC}"
            python3 "$(dirname "$0")/scripts/scheme_b_excel_correct_merge_v2.py"
            
            echo -e "${GREEN}✅ 完整工作流执行完成${NC}"
        else
            echo -e "${RED}❌ 登录失败，请重试${NC}"
        fi
        ;;
    6)
        echo -e "${BLUE}👋 退出${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ 操作完成${NC}"
echo "💡 下次使用: ./$(basename "$0")"