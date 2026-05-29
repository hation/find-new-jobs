#!/bin/bash
# 夸克项目决策框架检查脚本
# 版本: 1.0
# 功能: 检查决策框架状态，确保新会话正确加载

echo "🔍 检查夸克项目决策框架状态"
echo "========================================"

# 1. 检查核心文档存在性
echo "📋 检查核心文档..."
declare -a required_docs=(
    "DECISION_FRAMEWORK.md"
    "WORKFLOW_GUIDE.md"
    "ARCHITECTURE.md"
    "CHECKLIST.md"
    "LESSONS_LEARNED.md"
)

for doc in "${required_docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "✅ $doc 存在"
    else
        echo "❌ $doc 缺失 - 这是严重问题！"
        exit 1
    fi
done

# 2. 检查决策框架版本
echo ""
echo "📊 检查决策框架版本..."
if grep -q "版本:" DECISION_FRAMEWORK.md; then
    version=$(grep "版本:" DECISION_FRAMEWORK.md | head -1 | cut -d: -f2 | tr -d ' ')
    echo "✅ 决策框架版本: $version"
else
    echo "⚠️  无法确定决策框架版本"
fi

# 3. 检查项目结构
echo ""
echo "🏗️ 检查项目结构..."
if [ -d "quark_crawler" ]; then
    echo "✅ quark_crawler/ 目录存在"
    quark_files=$(find quark_crawler -type f -name "*.py" | wc -l)
    echo "   包含 $quark_files 个Python文件"
else
    echo "❌ quark_crawler/ 目录缺失 - 架构不完整"
    exit 1
fi

# 4. 检查记忆系统
echo ""
echo "🧠 检查记忆系统..."
if [ -f "memory_checkpoints.json" ]; then
    echo "✅ memory_checkpoints.json 存在"
    
    # 检查关键字段
    if python3 -c "import json; data=open('memory_checkpoints.json').read(); d=json.loads(data); print('项目:', d.get('project_info',{}).get('name','未知')); print('进度:', d.get('project_info',{}).get('progress_percentage',0), '%');" 2>/dev/null; then
        echo "✅ 记忆数据格式正确"
    else
        echo "⚠️  记忆数据格式可能有问题"
    fi
else
    echo "❌ memory_checkpoints.json 缺失 - 无法恢复状态"
fi

# 5. 检查插件化架构
echo ""
echo "🧩 检查插件化架构..."
if [ -f "quark_crawler/main.py" ]; then
    echo "✅ 插件化主程序存在"
    
    # 检查插件
    plugins_dir="quark_crawler/plugins"
    if [ -d "$plugins_dir" ]; then
        plugins=$(find "$plugins_dir" -maxdepth 1 -type d | tail -n +2 | wc -l)
        echo "   发现 $plugins 个插件"
        
        # 列出插件
        for plugin in "$plugins_dir"/*/; do
            plugin_name=$(basename "$plugin")
            if [ -f "$plugin/__init__.py" ]; then
                echo "   ✅ $plugin_name (已初始化)"
            else
                echo "   ⚠️  $plugin_name (未初始化)"
            fi
        done
    else
        echo "❌ 插件目录缺失"
    fi
else
    echo "❌ 主程序缺失"
fi

# 6. 生成检查报告
echo ""
echo "📈 生成检查报告..."
{
    echo "# 夸克项目决策框架检查报告"
    echo "检查时间: $(date)"
    echo "项目目录: $(pwd)"
    echo ""
    echo "## 文档检查结果"
    for doc in "${required_docs[@]}"; do
        if [ -f "$doc" ]; then
            echo "- ✅ $doc"
        else
            echo "- ❌ $doc"
        fi
    done
    echo ""
    echo "## 架构检查结果"
    echo "- quark_crawler/ 目录: $(if [ -d "quark_crawler" ]; then echo "✅ 存在"; else echo "❌ 缺失"; fi)"
    echo "- 记忆系统文件: $(if [ -f "memory_checkpoints.json" ]; then echo "✅ 存在"; else echo "❌ 缺失"; fi)"
    echo "- 插件数量: $plugins"
    echo ""
    echo "## 建议操作"
    if [ $plugins -lt 2 ]; then
        echo "- ⚠️  建议检查插件完整性"
    fi
    echo "- ✅ 决策框架状态良好，可以开始工作"
} > decision_framework_check_report_$(date +%Y%m%d_%H%M%S).md

echo "✅ 检查完成，报告已生成"
echo ""
echo "🚀 接下来您可以："
echo "1. 📖 阅读决策框架: cat DECISION_FRAMEWORK.md | head -30"
echo "2. 🏗️ 检查项目结构: tree quark_crawler/ -L 2"
echo "3. 📊 查看当前状态: cat memory_checkpoints.json | jq '.current_state'"
echo "4. 🚀 开始工作: 遵循五阶段工作流程"
echo ""
echo "========================================"
echo "🧠 记住：所有决策必须遵循 DECISION_FRAMEWORK.md"