#!/bin/bash
# 拼多多招聘爬取器 - 依赖安装脚本

set -e  # 遇到错误时退出

echo "🔧 拼多多招聘爬取器 - 依赖安装"
echo "================================"

# 检查Python版本
echo "📋 检查Python版本..."
python3 --version

# 创建虚拟环境（可选）
if [ ! -d "venv" ]; then
    echo "🐍 创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖包..."
echo "   1. 安装最小依赖（用于测试）..."
pip install -r requirements_minimal.txt

echo "   2. 安装核心依赖..."
pip install requests python-dotenv

echo "   3. 安装数据处理工具..."
pip install pandas openpyxl

echo "   4. 安装开发工具..."
pip install black flake8 pytest

echo "✅ 依赖安装完成"

# 验证安装
echo "🔍 验证安装..."
python3 -c "import requests; print('✅ requests 版本:', requests.__version__)"
python3 -c "import pandas; print('✅ pandas 版本:', pandas.__version__)"

echo ""
echo "🎉 安装完成！"
echo ""
echo "下一步："
echo "1. 检查配置文件: config/.env 和 config/api_auth.json"
echo "2. 运行测试: python3 run_stage1.py"
echo "3. 选择选项2测试API连接"
echo ""
echo "如果需要安装完整依赖:"
echo "  pip install -r requirements.txt"