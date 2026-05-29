#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
夸克完整架构 - 主程序入口
基于夸克项目的完整业务框架
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src/framework"))

print("=" * 70)
print("🚀 夸克项目完整业务框架")
print("=" * 70)
print(f"项目根目录: {project_root}")
print(f"公司名称: {os.environ.get('COMPANY_NAME', '未设置')}")
print()

# 检查可用框架组件
available_components = []

try:
    from framework.smart_crawler_selector import SmartCrawlerSelector
    available_components.append("✅ smart_crawler_selector - 智能爬取器选择器")
except ImportError as e:
    available_components.append(f"❌ smart_crawler_selector - 导入失败: {e}")

try:
    from framework.unified_crawler_entry import UnifiedCrawlerEntry
    available_components.append("✅ unified_crawler_entry - 统一爬取器入口")
except ImportError as e:
    available_components.append(f"❌ unified_crawler_entry - 导入失败: {e}")

try:
    from framework.data_exporter import DataExporter
    available_components.append("✅ data_exporter - 数据导出框架")
except ImportError as e:
    available_components.append(f"❌ data_exporter - 导入失败: {e}")

# 显示可用组件
print("📦 可用业务框架组件:")
for component in available_components:
    print(f"  {component}")

print()
print("🎯 使用说明:")
print("1. 配置环境: cp config/.env.example config/.env")
print("2. 配置业务: 编辑 memory-system/CORE_BUSINESS_INFO.md")
print("3. 执行检查: 按照 docs/CHECKLIST.md 逐项检查")
print("4. 开发实现: 基于 src/framework/ 中的框架进行开发")
print("5. 测试验证: 运行 tests/ 中的测试")
print()

print("🔧 框架定制指南:")
print("• 智能爬取器: 继承 SmartCrawlerSelector，实现业务逻辑")
print("• 统一入口: 使用 UnifiedCrawlerEntry 作为命令行入口")
print("• 数据导出: 使用 DataExporter 导出多种格式数据")
print()

print("📚 文档参考:")
print("• 架构设计: docs/ARCHITECTURE.md")
print("• 快速开始: docs/QUICK_START.md")
print("• 业务知识: docs/BUSINESS_KNOWLEDGE_SYSTEM.md")
print("• 模板使用: docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md")
print()

print("=" * 70)
print("💡 提示: 基于夸克项目完整业务框架，包含智能爬取器、统一入口、数据导出器")
print("=" * 70)

if __name__ == "__main__":
    # 这里可以添加实际的启动逻辑
    print()
    print("要运行具体功能，请查看示例:")
    print("  python src/examples/bytedance_migration_demo.py")
    print()
    print("或创建自己的业务实现:")
    print("  1. 继承 SmartCrawlerSelector 实现业务逻辑")
    print("  2. 配置 UnifiedCrawlerEntry 作为入口")
    print("  3. 使用 DataExporter 导出数据")
