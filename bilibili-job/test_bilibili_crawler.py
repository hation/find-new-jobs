#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站爬取器测试脚本
测试所有组件的功能
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src/framework"))

print("=" * 70)
print("🧪 B站爬取器功能测试")
print("=" * 70)

# 测试计数器
tests_passed = 0
tests_failed = 0

def test_result(test_name: str, passed: bool, message: str = ""):
    """记录测试结果"""
    global tests_passed, tests_failed
    
    if passed:
        print(f"✅ {test_name}: 通过")
        if message:
            print(f"   📝 {message}")
        tests_passed += 1
    else:
        print(f"❌ {test_name}: 失败")
        if message:
            print(f"   💡 {message}")
        tests_failed += 1

def test_1_config_files():
    """测试配置文件"""
    print("\n📋 测试1: 配置文件")
    
    # 1.1 检查API配置文件
    config_path = Path("config/api_auth.json")
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            bilibili_config = config.get("bilibili")
            if bilibili_config:
                test_result("API配置文件", True, f"包含{len(bilibili_config)}个配置项")
            else:
                test_result("API配置文件", False, "缺少bilibili配置")
        except json.JSONDecodeError as e:
            test_result("API配置文件", False, f"JSON格式错误: {e}")
    else:
        test_result("API配置文件", False, "文件不存在")
    
    # 1.2 检查环境配置文件
    env_path = Path("config/.env")
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        if "BILIBILI_API_BASE_URL" in env_content:
            test_result("环境配置文件", True, "包含B站配置")
        else:
            test_result("环境配置文件", False, "缺少B站配置")
    else:
        test_result("环境配置文件", False, "文件不存在")

def test_2_business_info():
    """测试业务信息文件"""
    print("\n📋 测试2: 业务信息文件")
    
    info_path = Path("memory-system/CORE_BUSINESS_INFO.md")
    if info_path.exists():
        with open(info_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_sections = [
            "业务目标",
            "数据字段映射", 
            "技术配置",
            "实施计划"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if not missing_sections:
            test_result("核心业务信息", True, f"包含所有{len(required_sections)}个必需部分")
        else:
            test_result("核心业务信息", False, f"缺少部分: {', '.join(missing_sections)}")
    else:
        test_result("核心业务信息", False, "文件不存在")

def test_3_directory_structure():
    """测试目录结构"""
    print("\n📋 测试3: 目录结构")
    
    required_dirs = [
        "data/bilibili",
        "data/bilibili/raw",
        "output/bilibili", 
        "logs/bilibili",
        "config",
        "src",
        "src/framework",
        "memory-system"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if not missing_dirs:
        test_result("目录结构", True, f"所有{len(required_dirs)}个目录都存在")
    else:
        test_result("目录结构", False, f"缺少目录: {', '.join(missing_dirs[:3])}")

def test_4_framework_import():
    """测试框架导入"""
    print("\n📋 测试4: 框架导入")
    
    try:
        from framework.smart_crawler_selector import SmartCrawlerSelector
        from framework.data_exporter import DataExporter
        from framework.unified_crawler_entry import UnifiedCrawlerEntry
        
        test_result("框架导入", True, "成功导入SmartCrawlerSelector, DataExporter, UnifiedCrawlerEntry")
    except ImportError as e:
        test_result("框架导入", False, f"导入失败: {e}")

def test_5_bilibili_crawler_import():
    """测试B站爬取器导入"""
    print("\n📋 测试5: B站爬取器导入")
    
    try:
        # 尝试导入我们创建的爬取器
        from src.bilibili_api_crawler import BilibiliAPICrawler
        from src.bilibili_smart_crawler import BilibiliSmartCrawler
        
        test_result("B站爬取器导入", True, "成功导入BilibiliAPICrawler和BilibiliSmartCrawler")
    except ImportError as e:
        test_result("B站爬取器导入", False, f"导入失败: {e}")
    except Exception as e:
        test_result("B站爬取器导入", False, f"其他错误: {e}")

def test_6_config_validation():
    """测试配置验证"""
    print("\n📋 测试6: 配置验证")
    
    try:
        from src.bilibili_api_crawler import BilibiliAPICrawler
        
        # 尝试创建爬取器实例
        crawler = BilibiliAPICrawler("config/api_auth.json")
        
        # 检查配置
        config = crawler.config
        required_fields = ["base_url", "api_endpoint", "request_headers", "default_params", "field_mapping"]
        
        missing_fields = []
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
        
        if not missing_fields:
            test_result("配置验证", True, f"所有{len(required_fields)}个必需字段都存在")
        else:
            test_result("配置验证", False, f"缺少字段: {', '.join(missing_fields)}")
    
    except Exception as e:
        test_result("配置验证", False, f"验证失败: {e}")

def test_7_data_structure():
    """测试数据结构"""
    print("\n📋 测试7: 数据结构")
    
    try:
        from src.bilibili_api_crawler import BilibiliAPICrawler
        
        crawler = BilibiliAPICrawler("config/api_auth.json")
        
        # 检查字段映射
        field_mapping = crawler.field_mapping
        required_mappings = ["position_id", "title", "category", "location", "publish_time"]
        
        missing_mappings = []
        for field in required_mappings:
            if field not in field_mapping:
                missing_mappings.append(field)
        
        if not missing_mappings:
            test_result("字段映射", True, f"所有{len(required_mappings)}个必需映射都存在")
        else:
            test_result("字段映射", False, f"缺少映射: {', '.join(missing_mappings)}")
        
        # 检查请求参数
        default_params = crawler.default_params
        if "pageSize" in default_params and "pageNum" in default_params:
            test_result("请求参数", True, "包含分页参数")
        else:
            test_result("请求参数", False, "缺少分页参数")
    
    except Exception as e:
        test_result("数据结构", False, f"检查失败: {e}")

def test_8_quick_start():
    """测试快速启动"""
    print("\n📋 测试8: 快速启动")
    
    # 检查快速启动文档
    quick_start_path = Path("docs/QUICK_START.md")
    if quick_start_path.exists():
        with open(quick_start_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "bilibili" in content.lower() or "B站" in content:
            test_result("快速启动文档", True, "包含B站相关内容")
        else:
            test_result("快速启动文档", False, "需要更新为B站内容")
    else:
        test_result("快速启动文档", False, "文件不存在")

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行B站爬取器功能测试")
    print("=" * 70)
    
    # 运行测试
    test_1_config_files()
    test_2_business_info()
    test_3_directory_structure()
    test_4_framework_import()
    test_5_bilibili_crawler_import()
    test_6_config_validation()
    test_7_data_structure()
    test_8_quick_start()
    
    # 显示总结
    print("\n" + "=" * 70)
    print("📊 测试结果总结")
    print("=" * 70)
    print(f"✅ 通过: {tests_passed} 项")
    print(f"❌ 失败: {tests_failed} 项")
    print(f"📈 总计: {tests_passed + tests_failed} 项")
    
    if tests_failed == 0:
        print("\n🎉 所有测试通过！B站爬取器准备就绪！")
    else:
        print(f"\n⚠️  有{tests_failed}项测试失败，需要修复")
    
    # 提供下一步建议
    print("\n📋 下一步建议:")
    if tests_failed > 0:
        print("1. 🔧 修复失败的测试项")
        print("2. 🧪 重新运行测试")
    else:
        print("1. 🚀 运行B站API爬取器测试")
        print("2. 📊 查看生成的数据文件")
        print("3. 🔧 根据需要调整配置")
    
    print("\n💡 运行以下命令测试爬取器:")
    print("  python3 src/bilibili_api_crawler.py")
    print("  python3 src/bilibili_smart_crawler.py")
    
    return tests_failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 测试完成，B站爬取器功能完整！")
    else:
        print("⚠️  测试完成，需要修复一些问题")
    print("=" * 70)