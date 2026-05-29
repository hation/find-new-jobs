#!/bin/bash
# 快手招聘爬取器启动脚本
# 基于夸克完整架构 + 快手API信息

set -e

echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│        🚀 快手招聘数据爬取器启动                       │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│ 项目: ks-job"
echo "│ 公司: 快手 (Kuaishou)"
echo "│ 数据源: 快手招聘官方API"
echo "│ 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "└─────────────────────────────────────────────────────────┘"
echo ""

echo "📋 项目概述:"
echo "基于夸克项目的完整架构，专门为快手招聘数据爬取定制"
echo "包含三个完整层次:"
echo "  1. 📚 知识层 - 文档模板 + 记忆系统"
echo "  2. 🔧 框架层 - 快手API爬取器实现"
echo "  3. ⚙️ 配置层 - API配置 + 认证信息"
echo ""

echo "🔍 第一步: 环境检查"
echo "----------------------------------------"
# 检查Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3: $(python3 --version)"
else
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖
if [ -f "requirements.txt" ]; then
    echo "📦 发现依赖文件: requirements.txt"
    read -p "是否安装依赖？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo "正在安装依赖..."
        pip3 install -r requirements.txt
    fi
else
    echo "⚠️ 未找到requirements.txt，跳过依赖安装"
fi

echo ""
echo "🔧 第二步: 配置检查"
echo "----------------------------------------"
# 检查配置文件
CONFIG_FILE="config/.env"
if [ -f "$CONFIG_FILE" ]; then
    echo "✅ 配置文件存在: $CONFIG_FILE"
    
    # 检查Cookie配置
    if grep -q "KS_COOKIE_PLACEHOLDER" "$CONFIG_FILE" && ! grep -q "KS_COOKIE_PLACEHOLDER=\"\"" "$CONFIG_FILE"; then
        echo "✅ Cookie配置已设置"
    else
        echo "⚠️ Cookie配置未设置或为空"
        echo "   请更新 $CONFIG_FILE 中的 KS_COOKIE_PLACEHOLDER"
        echo "   需要的Cookie字段: accessproxy_session, aliyungf_tc, apdid, weblogger_did"
    fi
else
    echo "❌ 配置文件不存在: $CONFIG_FILE"
    echo "   请先创建配置文件: cp config/.env.example config/.env"
    exit 1
fi

# 检查API配置
API_CONFIG_FILE="config/api_auth.json"
if [ -f "$API_CONFIG_FILE" ]; then
    echo "✅ API配置文件存在: $API_CONFIG_FILE"
else
    echo "❌ API配置文件不存在: $API_CONFIG_FILE"
    exit 1
fi

echo ""
echo "📚 第三步: 项目结构"
echo "----------------------------------------"
echo "核心文件位置:"
echo "• 主爬取器: src/ks_api_crawler.py"
echo "• 测试脚本: scripts/test_ks_crawler.py"
echo "• 配置目录: config/"
echo "• 输出目录: output/ks_data/"
echo "• 日志目录: logs/"
echo "• 文档目录: docs/"
echo ""

echo "🚀 第四步: 运行测试"
echo "----------------------------------------"
echo "建议先运行测试验证功能:"
echo "  python3 scripts/test_ks_crawler.py"
echo ""
read -p "是否运行测试？(Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "正在运行测试..."
    python3 scripts/test_ks_crawler.py
    echo ""
    read -p "测试完成，是否继续？(Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ -n $REPLY ]]; then
        echo "退出程序"
        exit 0
    fi
fi

echo ""
echo "🎯 第五步: 运行爬取器"
echo "----------------------------------------"
echo "运行模式选择:"
echo "1. 🔍 测试模式 - 爬取少量数据测试功能"
echo "2. 📄 完整模式 - 爬取所有岗位数据"
echo "3. ⚙️ 自定义模式 - 自定义爬取参数"
echo ""

read -p "请选择模式 (1/2/3): " -n 1 -r
echo

case $REPLY in
    1)
        echo "🔍 选择测试模式"
        echo "   爬取2页数据，每页5条"
        echo ""
        python3 src/ks_api_crawler.py
        ;;
    2)
        echo "📄 选择完整模式"
        echo "   爬取所有页面，每页10条"
        echo ""
        read -p "请输入最大爬取页数（默认全部）: " max_pages
        if [ -z "$max_pages" ]; then
            max_pages=""
        else
            max_pages="--max-pages $max_pages"
        fi
        
        # 这里可以添加完整模式的命令
        echo "运行完整爬取..."
        python3 -c "
import sys
sys.path.insert(0, 'src')
from ks_api_crawler import KsAPICrawler, load_config
config = load_config()
crawler = KsAPICrawler(config)
max_pages = ${max_pages:-None}
stats = crawler.crawl_and_save(max_pages=max_pages)
print(f'🎉 爬取完成！')
print(f'   总岗位数: {stats[\"total_positions\"]}')
print(f'   有效岗位: {stats[\"valid_positions\"]} ({stats[\"valid_percentage\"]:.1f}%)')
print(f'   保存文件: {stats[\"saved_files\"]}')
print(f'   输出目录: {stats[\"output_dir\"]}')
        "
        ;;
    3)
        echo "⚙️ 选择自定义模式"
        echo ""
        read -p "请输入起始页码（默认1）: " start_page
        start_page=${start_page:-1}
        
        read -p "请输入每页数量（默认10）: " page_size
        page_size=${page_size:-10}
        
        read -p "请输入最大爬取页数（默认10）: " max_pages
        max_pages=${max_pages:-10}
        
        echo ""
        echo "自定义参数:"
        echo "   起始页码: $start_page"
        echo "   每页数量: $page_size"
        echo "   最大页数: $max_pages"
        echo ""
        
        # 这里可以添加自定义模式的命令
        echo "运行自定义爬取..."
        python3 -c "
import sys
sys.path.insert(0, 'src')
from ks_api_crawler import KsAPICrawler, load_config
config = load_config()
config['page_size'] = $page_size
crawler = KsAPICrawler(config)

# 爬取指定范围
all_positions = []
for page in range($start_page, $start_page + $max_pages):
    print(f'📄 爬取第 {page} 页...')
    positions, _ = crawler.fetch_positions_page(page, $page_size)
    if positions:
        all_positions.extend(positions)
    else:
        print(f'⚠️ 第 {page} 页获取失败')
        break

print(f'✅ 爬取完成，共获取 {len(all_positions)} 个岗位')
        "
        ;;
    *)
        echo "❌ 无效选择，退出程序"
        exit 1
        ;;
esac

echo ""
echo "📊 第六步: 查看结果"
echo "----------------------------------------"
echo "数据输出位置:"
echo "• JSON文件: output/ks_data/"
echo "• 日志文件: logs/ks_crawler.log"
echo "• 备份数据: backup/"
echo ""

if [ -d "output/ks_data" ]; then
    echo "📁 输出目录内容:"
    ls -la output/ks_data/ | head -10
    echo ""
    
    file_count=$(find output/ks_data -name "*.json" | wc -l)
    if [ "$file_count" -gt 0 ]; then
        echo "📊 统计信息:"
        echo "   文件数量: $file_count"
        
        # 显示最新文件
        latest_file=$(find output/ks_data -name "*.json" -type f -exec stat -f "%m %N" {} \; | sort -rn | head -1 | cut -d' ' -f2-)
        if [ -n "$latest_file" ]; then
            echo "   最新文件: $(basename "$latest_file")"
            echo "   文件大小: $(du -h "$latest_file" | cut -f1)"
        fi
    fi
fi

echo ""
echo "🔧 第七步: 后续操作"
echo "----------------------------------------"
echo "可选操作:"
echo "1. 📋 查看爬取日志: tail -f logs/ks_crawler.log"
echo "2. 📊 数据统计分析: python scripts/analyze_data.py"
echo "3. 📄 导出Excel格式: python scripts/export_to_excel.py"
echo "4. 🔄 定时任务设置: 配置cron定期爬取"
echo "5. 📚 查看完整文档: 阅读docs/目录下的文档"
echo ""

echo "💡 提示:"
echo "• 遇到问题查看 logs/ks_crawler.log"
echo "• 定期更新Cookie保持爬取正常"
echo "• 尊重网站规则，控制爬取频率"
echo "• 记录问题和解决方案到 docs/LESSONS_LEARNED.md"
echo ""

echo "🎉 快手招聘数据爬取器启动完成！"
echo "现在可以开始你的数据爬取和分析工作了！"
echo ""
echo "📞 快速帮助:"
echo "• 查看帮助: python src/ks_api_crawler.py --help"
echo "• 运行测试: python scripts/test_ks_crawler.py"
echo "• 查看文档: cat docs/QUICK_START.md"
echo ""

exit 0