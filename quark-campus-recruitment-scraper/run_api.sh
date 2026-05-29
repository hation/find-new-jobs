#!/bin/bash
# 夸克校园招聘API爬取器启动脚本
# 使用API优先的智能爬取系统

set -e  # 出错时退出

echo "🚀 夸克校园招聘API爬取器启动"
echo "=========================================="

# 检查Python环境
echo "🔍 检查Python环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

# 检查项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 项目目录: $SCRIPT_DIR"

# 检查依赖
echo "🔍 检查Python依赖..."
if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "⚠️  未找到requirements.txt，跳过依赖检查"
else
    echo "📦 检查并安装依赖..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt" --quiet
fi

# 检查配置文件
echo "🔧 检查配置文件..."
if [ ! -f "$SCRIPT_DIR/config.yaml" ]; then
    echo "⚠️  未找到config.yaml，使用默认配置"
    echo "💡 提示：可以创建config.yaml来自定义配置"
fi

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p "$SCRIPT_DIR/output/positions"
mkdir -p "$SCRIPT_DIR/output/backups"
mkdir -p "$SCRIPT_DIR/logs"

# 运行主程序
echo "🚀 启动智能爬取系统..."
echo "=========================================="
echo "📋 使用智能选择器：默认API优先，支持切换到浏览器模式"
echo "💡 如需强制模式，请使用:"
echo "   --force-api     强制使用API模式"
echo "   --force-browser 强制使用浏览器模式"
echo "   --mode mixed    混合模式"
echo "=========================================="

cd "$SCRIPT_DIR"
python3 scripts/main.py "$@"

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "✅ 执行成功！"
    echo "📁 数据保存在: $SCRIPT_DIR/output/positions/"
    echo "📄 日志保存在: $SCRIPT_DIR/logs/"
    echo "=========================================="
else
    echo "=========================================="
    echo "❌ 执行失败，请检查日志"
    echo "📄 查看日志: less $SCRIPT_DIR/logs/quark_crawler_*.log"
    echo "=========================================="
    exit 1
fi