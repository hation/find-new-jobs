#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整架构验证脚本
验证夸克项目完整架构是否迁移成功
"""

import os
import sys
import json
from pathlib import Path

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"🔍 {text}")
    print("=" * 60)

def check_knowledge_layer():
    """检查知识层"""
    print_header("检查知识层（文档 + 记忆）")
    
    required_docs = [
        "docs/ARCHITECTURE.md",
        "docs/CHECKLIST.md", 
        "docs/CHECKLIST_EXCEL_EXPORT.md",
        "docs/LESSONS_LEARNED.md",
        "docs/QUICK_START.md",
        "docs/QUICK_START_UNIFIED_EXCEL.md",
        "docs/BUSINESS_KNOWLEDGE_SYSTEM.md",
        "docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md"
    ]
    
    required_memory = [
        "memory-system/CORE_BUSINESS_INFO.md",
        "memory-system/DAILY_MEMORY_TEMPLATE.md",
        "memory-system/MEMORY_SYSTEM_GUIDE.md"
    ]
    
    all_passed = True
    
    print("📚 文档模板:")
    for doc in required_docs:
        if os.path.exists(doc):
            print(f"  ✅ {doc}")
        else:
            print(f"  ❌ {doc} 缺失")
            all_passed = False
    
    print("\n🧠 记忆系统:")
    for mem in required_memory:
        if os.path.exists(mem):
            print(f"  ✅ {mem}")
        else:
            print(f"  ❌ {mem} 缺失")
            all_passed = False
    
    return all_passed

def check_framework_layer():
    """检查框架层"""
    print_header("检查框架层（业务实现）")
    
    required_frameworks = [
        "src/framework/smart_crawler_selector.py",
        "src/framework/unified_crawler_entry.py", 
        "src/framework/data_exporter.py",
        "src/framework/unified_excel_exporter.py",
        "src/main.py"
    ]
    
    all_passed = True
    
    print("🔧 业务框架:")
    for framework in required_frameworks:
        if os.path.exists(framework):
            # 检查文件是否为空
            file_size = os.path.getsize(framework)
            if file_size > 100:  # 大于100字节
                print(f"  ✅ {framework} ({file_size} 字节)")
            else:
                print(f"  ⚠️  {framework} 文件过小 ({file_size} 字节)")
                all_passed = False
        else:
            print(f"  ❌ {framework} 缺失")
            all_passed = False
    
    # 尝试导入框架模块
    print("\n📦 框架导入测试:")
    try:
        sys.path.insert(0, "src/framework")
        import smart_crawler_selector
        print("  ✅ smart_crawler_selector 可导入")
    except ImportError as e:
        print(f"  ❌ smart_crawler_selector 导入失败: {e}")
        all_passed = False
    
    try:
        import unified_crawler_entry
        print("  ✅ unified_crawler_entry 可导入")
    except ImportError as e:
        print(f"  ❌ unified_crawler_entry 导入失败: {e}")
        all_passed = False
    
    try:
        import unified_excel_exporter
        print("  ✅ unified_excel_exporter 可导入")
    except ImportError as e:
        print(f"  ❌ unified_excel_exporter 导入失败: {e}")
        all_passed = False
    
    return all_passed

def check_config_layer():
    """检查配置层"""
    print_header("检查配置层")
    
    required_configs = [
        "config/project_config.json",
        "config/api_auth.json",
        "config/browser_config.json",
        "config/excel_column_mapping.yaml",
        "config/.env.example"
    ]
    
    all_passed = True
    
    print("⚙️ 配置文件:")
    for config in required_configs:
        if os.path.exists(config):
            try:
                if config.endswith('.json'):
                    with open(config, 'r', encoding='utf-8') as f:
                        json.load(f)
                    print(f"  ✅ {config} (JSON格式正确)")
                else:
                    print(f"  ✅ {config}")
            except Exception as e:
                print(f"  ❌ {config} 格式错误: {e}")
                all_passed = False
        else:
            print(f"  ❌ {config} 缺失")
            all_passed = False
    
    return all_passed

def check_directory_structure():
    """检查目录结构"""
    print_header("检查目录结构")
    
    required_dirs = [
        "src/framework",
        "docs",
        "config", 
        "scripts",
        "tests",
        "memory-system",
        "data",
        "output",
        "logs"
    ]
    
    all_passed = True
    
    for directory in required_dirs:
        if os.path.isdir(directory):
            # 检查目录是否为空
            file_count = len([f for f in os.listdir(directory) if not f.startswith('.')])
            if file_count > 0:
                print(f"  ✅ {directory}/ ({file_count} 个文件)")
            else:
                print(f"  ⚠️  {directory}/ (空目录)")
        else:
            print(f"  ❌ {directory}/ 缺失")
            all_passed = False
    
    return all_passed

def check_tools_layer():
    """检查工具层"""
    print_header("检查工具层（工具脚本 + 工具库）")
    
    required_scripts = [
        "scripts/validate_complete_architecture.py",
        "scripts/start_project.py",
        "scripts/check_environment.py",
        "scripts/generate_unified_excel.py"
    ]
    
    required_utils = [
        "src/utils/data_extractors.py",
        "src/utils/data_validators.py",
        "src/utils/logging_config.py"
    ]
    
    all_passed = True
    
    print("📜 工具脚本:")
    for script in required_scripts:
        if os.path.exists(script):
            file_size = os.path.getsize(script)
            if file_size > 100:
                print(f"  ✅ {script} ({file_size} 字节)")
            else:
                print(f"  ⚠️  {script} 文件过小 ({file_size} 字节)")
                all_passed = False
        else:
            print(f"  ❌ {script} 缺失")
            all_passed = False
    
    print("\n🔧 工具库:")
    for util in required_utils:
        if os.path.exists(util):
            file_size = os.path.getsize(util)
            if file_size > 100:
                print(f"  ✅ {util} ({file_size} 字节)")
            else:
                print(f"  ⚠️  {util} 文件过小 ({file_size} 字节)")
                all_passed = False
        else:
            print(f"  ❌ {util} 缺失")
            all_passed = False
    
    return all_passed


def check_project_files():
    """检查项目文件"""
    print_header("检查项目文件")
    
    required_files = [
        "README.md",
        "requirements.txt",
        ".gitignore"
    ]
    
    all_passed = True
    
    for file in required_files:
        if os.path.exists(file):
            file_size = os.path.getsize(file)
            if file_size > 50:
                print(f"  ✅ {file} ({file_size} 字节)")
            else:
                print(f"  ⚠️  {file} 文件过小 ({file_size} 字节)")
        else:
            print(f"  ❌ {file} 缺失")
            all_passed = False
    
    return all_passed

def main():
    """主函数"""
    print("🚀 夸克项目完整架构验证")
    print("验证迁移是否包含所有三个层次：知识层 + 框架层 + 配置层")
    
    results = []
    
    # 执行检查
    results.append(("知识层", check_knowledge_layer()))
    results.append(("框架层", check_framework_layer()))
    results.append(("配置层", check_config_layer()))
    results.append(("工具层", check_tools_layer()))
    results.append(("目录结构", check_directory_structure()))
    results.append(("项目文件", check_project_files()))
    
    # 总结
    print_header("验证结果总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} - {name}")
    
    print(f"\n📊 总体: {passed}/{total} 项通过")
    
    if passed == total:
        print("\n🎉 恭喜！完整架构迁移验证全部通过！")
        print("💡 项目包含:")
        print("  • 📚 完整知识体系（文档 + 记忆）")
        print("  • 🔧 完整业务框架（智能爬取器 + 统一入口 + 数据导出器 + 统一Excel导出器）")
        print("  • ⚙️ 完整配置系统（项目 + API + 浏览器配置 + Excel列名映射）")
        print("  • 🛠️ 完整工具层（工具脚本 + 数据提取工具 + 统一Excel生成器）")
        print("  • 📁 完整目录结构")
        print("\n🚀 现在可以立即开始业务开发！")
        return 0
    else:
        print("\n⚠️  完整架构迁移验证未通过")
        print("💡 请根据上面的提示修复缺失的部分")
        print("📋 完整架构应该包含三个层次:")
        print("  1. 知识层（文档模板 + 记忆系统）")
        print("  2. 框架层（业务实现框架 + 统一Excel导出框架）")
        print("  3. 配置层（配置模板 + 环境配置 + Excel配置）")
        print("  4. 工具层（工具脚本 + 工具库）")
        return 1

if __name__ == "__main__":
    sys.exit(main())
