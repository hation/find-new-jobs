#!/bin/bash
# 🔥 夸克项目强制性业务信息加载器
# 版本: 1.0
# 功能: 强制在新会话开始时加载和验证业务信息
# 使用: 所有夸克项目相关的新会话必须首先运行此脚本

echo "🚀 启动夸克项目强制性业务信息加载器"
echo "================================================"
echo "📅 时间: $(date)"
echo "👤 用户: $USER"
echo "================================================"

# 定义颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. 检查是否在正确目录
echo -e "${BLUE}📁 步骤1: 检查项目目录...${NC}"
if [ ! -f "CORE_BUSINESS_INFO.md" ]; then
    echo -e "${RED}❌ 错误: 不在夸克项目目录中!${NC}"
    echo -e "请先进入项目目录:"
    echo -e "cd ~/.openclaw/workspace/skills/quark-campus-recruitment-scraper"
    exit 1
fi
echo -e "${GREEN}✅ 项目目录正确${NC}"

# 2. 强制读取核心业务信息
echo -e "${BLUE}📖 步骤2: 强制读取核心业务信息...${NC}"
echo "================================================"
echo "🎯 **核心业务信息摘要**"
echo "================================================"

# 提取关键业务信息
echo -e "${YELLOW}🔗 关键网址:${NC}"
grep -A2 "列表页URL" CORE_BUSINESS_INFO.md | head -3
grep -A2 "详情页URL模板" CORE_BUSINESS_INFO.md | head -3

echo ""
echo -e "${YELLOW}🎯 业务目标:${NC}"
grep -A2 "目标岗位数" CORE_BUSINESS_INFO.md | head -3
grep -A2 "筛选类别" CORE_BUSINESS_INFO.md | head -5

echo ""
echo -e "${YELLOW}📊 数据字段:${NC}"
grep -A2 "核心12个字段" CORE_BUSINESS_INFO.md | head -5

echo ""
echo -e "${YELLOW}🔧 技术配置:${NC}"
grep -A2 "浏览器配置" CORE_BUSINESS_INFO.md | head -3
grep -A2 "提取策略" CORE_BUSINESS_INFO.md | head -3

echo "================================================"

# 3. 验证业务信息完整性
echo -e "${BLUE}🔍 步骤3: 验证业务信息完整性...${NC}"

# 检查关键信息是否存在
required_info=(
    "列表页URL"
    "详情页URL模板"
    "目标岗位数"
    "筛选类别"
    "核心12个字段"
)

all_present=true
for info in "${required_info[@]}"; do
    if grep -q "$info" CORE_BUSINESS_INFO.md; then
        echo -e "${GREEN}✅ $info 存在${NC}"
    else
        echo -e "${RED}❌ $info 缺失${NC}"
        all_present=false
    fi
done

if [ "$all_present" = false ]; then
    echo -e "${RED}⚠️  警告: 核心业务信息不完整!${NC}"
fi

# 4. 生成业务信息确认报告
echo -e "${BLUE}📝 步骤4: 生成业务信息确认报告...${NC}"

CONFIRMATION_REPORT="business_info_confirmation_$(date +%Y%m%d_%H%M%S).txt"
{
    echo "# 夸克项目业务信息确认报告"
    echo "生成时间: $(date)"
    echo "生成者: $USER"
    echo "会话ID: $$"
    echo ""
    echo "## 关键业务信息确认"
    echo ""
    echo "### 1. 网址信息"
    echo "- 列表页URL: https://talent.quark.cn/off-campus/position-list"
    echo "- 详情页模板: https://talent.quark.cn/off-campus/position-detail?lang=zh&positionId={positionId}"
    echo ""
    echo "### 2. 业务目标"
    echo "- 目标岗位数: 92个"
    echo "- 筛选类别: 7个 (产品类、运营类、数据类、市场拓展、销售类、游戏类、金融类)"
    echo "- 每页数量: 10个"
    echo ""
    echo "### 3. 数据规范"
    echo "- 核心字段: 12个"
    echo "- 默认策略: direct_url"
    echo "- 浏览器配置: profile='openclaw'"
    echo ""
    echo "## 确认声明"
    echo "我确认已读取并理解上述业务信息，将在本次会话中基于这些信息进行决策和执行。"
    echo ""
    echo "确认时间: $(date)"
} > "$CONFIRMATION_REPORT"

echo -e "${GREEN}✅ 确认报告已生成: $CONFIRMATION_REPORT${NC}"

# 5. 显示确认提示
echo "================================================"
echo -e "${YELLOW}🚨 重要提示:${NC}"
echo -e "${YELLOW}请将以下确认信息复制到您的会话中:${NC}"
echo ""
echo "我已运行强制性业务信息加载器，确认以下信息:"
echo "✅ 列表页URL: https://talent.quark.cn/off-campus/position-list"
echo "✅ 目标岗位: 92个 (7个筛选类别)"
echo "✅ 默认策略: direct_url"
echo "✅ 确认报告: $CONFIRMATION_REPORT"
echo ""
echo -e "${YELLOW}这样我可以验证您已正确加载业务信息。${NC}"

# 6. 提供后续操作指南
echo "================================================"
echo -e "${BLUE}🚀 步骤5: 后续操作指南...${NC}"
echo ""
echo "1. 📋 **检查当前状态**:"
echo "   cat memory_checkpoints.json | jq '.current_state'"
echo ""
echo "2. 📊 **查看进度**:"
echo "   cat memory_checkpoints.json | jq '.project_info.progress_percentage'"
echo ""
echo "3. 🎯 **开始工作**:"
echo "   # 使用直接URL方案继续"
echo "   python3 quark_crawler/main.py --strategy direct_url --page 2 --position 2"
echo ""
echo "4. 🛡️ **验证执行**:"
echo "   # 验证筛选状态"
echo "   # 验证页码显示 (X/10)"
echo "   # 验证岗位数量 (共92个岗位)"

# 7. 创建会话标记文件
echo -e "${BLUE}🏷️ 步骤6: 创建会话标记...${NC}"
SESSION_MARKER="session_marker_$(date +%Y%m%d_%H%M%S).txt"
{
    echo "夸克项目会话标记"
    echo "会话开始时间: $(date)"
    echo "业务信息加载时间: $(date)"
    echo "加载器版本: 1.0"
    echo "确认报告: $CONFIRMATION_REPORT"
    echo "业务信息摘要:"
    echo "  - 列表页URL: https://talent.quark.cn/off-campus/position-list"
    echo "  - 目标岗位: 92个"
    echo "  - 筛选类别: 7个"
    echo "  - 默认策略: direct_url"
} > "$SESSION_MARKER"

echo -e "${GREEN}✅ 会话标记已创建: $SESSION_MARKER${NC}"

echo "================================================"
echo -e "${GREEN}🎉 强制性业务信息加载完成!${NC}"
echo ""
echo -e "${YELLOW}📋 已创建的文件:${NC}"
echo "  1. $CONFIRMATION_REPORT - 业务信息确认报告"
echo "  2. $SESSION_MARKER - 会话标记文件"
echo ""
echo -e "${YELLOW}🚀 现在您可以:${NC}"
echo "  1. 将确认信息复制到会话中"
echo "  2. 开始夸克项目的具体工作"
echo "  3. 所有决策基于已确认的业务信息"
echo ""
echo "================================================"
echo -e "${RED}🚨 重要: 所有夸克项目相关工作必须基于本次加载的业务信息!${NC}"
echo "================================================"