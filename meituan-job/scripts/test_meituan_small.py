#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美团招聘小规模测试脚本
按照夸克项目规范：先小规模测试，验证功能
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from src.meituan_crawler import MeituanCrawler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection():
    """测试连接功能"""
    print("=" * 60)
    print("🔍 测试1: 连接功能测试")
    print("=" * 60)
    
    crawler = MeituanCrawler()
    
    # 测试连接
    success, message, details = crawler.test_primary_connection()
    
    if success:
        print("✅ 连接测试通过")
        print(f"📝 消息: {message}")
        
        # 显示测试步骤
        if details and 'steps' in details:
            print("\n📋 测试步骤详情:")
            for step in details['steps']:
                status_icon = {
                    'success': '✅',
                    'failed': '❌',
                    'pending': '⚠️'
                }.get(step['status'], '❔')
                print(f"  {status_icon} {step['step']}: {step['message']}")
    else:
        print("❌ 连接测试失败")
        print(f"📝 消息: {message}")
    
    return success


def test_configuration():
    """测试配置功能"""
    print("\n" + "=" * 60)
    print("⚙️ 测试2: 配置功能测试")
    print("=" * 60)
    
    crawler = MeituanCrawler()
    
    # 检查配置
    config_checks = [
        ("公司名称", crawler.company_name, "美团"),
        ("城市代码", crawler.city_code, "001019002"),
        ("类别数量", len(crawler.category_mapping), 5),
        ("必填字段", len(crawler.field_mapping), 12)
    ]
    
    all_passed = True
    for check_name, actual, expected in config_checks:
        if actual == expected:
            print(f"✅ {check_name}: {actual} (符合预期)")
        else:
            print(f"❌ {check_name}: {actual} (预期: {expected})")
            all_passed = False
    
    # 显示类别映射
    print("\n📁 岗位类别映射:")
    for code, name in crawler.category_mapping.items():
        print(f"  {code}: {name}")
    
    return all_passed


def test_data_model():
    """测试数据模型"""
    print("\n" + "=" * 60)
    print("📊 测试3: 数据模型测试")
    print("=" * 60)
    
    crawler = MeituanCrawler()
    
    # 测试数据提取
    test_item = {"id": "test_001", "name": "测试岗位"}
    position_data = crawler._extract_position_data(test_item)
    
    required_fields = [
        "position_id", "position_name", "work_location",
        "position_category", "publish_time", "detail_url",
        "department", "education_requirement", "work_experience",
        "job_responsibilities", "job_requirements", "salary_range"
    ]
    
    print("📋 必填字段检查 (12个字段):")
    missing_fields = []
    for field in required_fields:
        if field in position_data and position_data[field]:
            print(f"  ✅ {field}: {position_data[field][:30]}...")
        else:
            print(f"  ❌ {field}: 缺失或为空")
            missing_fields.append(field)
    
    if missing_fields:
        print(f"\n⚠️ 警告: 缺少 {len(missing_fields)} 个必填字段")
        return False
    else:
        print(f"\n✅ 所有12个必填字段完整")
        return True


def test_output_structure():
    """测试输出结构"""
    print("\n" + "=" * 60)
    print("💾 测试4: 输出结构测试")
    print("=" * 60)
    
    crawler = MeituanCrawler()
    
    # 创建测试数据
    test_positions = [
        crawler._extract_position_data({"id": f"test_{i}", "name": f"测试岗位{i}"})
        for i in range(3)
    ]
    
    # 测试保存功能
    test_filename = "test_output.json"
    crawler.save_positions(test_positions, test_filename)
    
    # 检查文件是否存在
    import glob
    test_files = glob.glob(os.path.join(crawler.output_dir, "test_*.json"))
    
    if test_files:
        print(f"✅ 输出文件创建成功: {len(test_files)} 个文件")
        
        # 读取并验证文件内容
        for filepath in test_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"  📄 {os.path.basename(filepath)}:")
                print(f"    公司: {data.get('company', 'N/A')}")
                print(f"    岗位数: {data.get('total_positions', 0)}")
                print(f"    爬取时间: {data.get('crawl_time', 'N/A')}")
                
                # 清理测试文件
                os.remove(filepath)
                csv_file = filepath.replace('.json', '.csv')
                if os.path.exists(csv_file):
                    os.remove(csv_file)
                
            except Exception as e:
                print(f"  ❌ 文件读取失败: {str(e)}")
                return False
        
        print("🧹 测试文件已清理")
        return True
    else:
        print("❌ 输出文件创建失败")
        return False


def run_all_tests():
    """运行所有测试"""
    print("🚀 美团招聘项目小规模测试")
    print("按照夸克项目规范：先测试，后执行")
    print("=" * 60)
    
    test_results = []
    
    # 运行测试
    test_results.append(("连接测试", test_connection()))
    test_results.append(("配置测试", test_configuration()))
    test_results.append(("数据模型测试", test_data_model()))
    test_results.append(("输出结构测试", test_output_structure()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print(f"\n📈 通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！可以开始正式爬取")
        print("💡 建议下一步: 运行单页爬取测试")
        return True
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败，需要修复")
        print("💡 建议: 检查失败的项目，修复后重新测试")
        return False


def generate_test_report():
    """生成测试报告"""
    crawler = MeituanCrawler()
    
    report = {
        "project": "美团招聘爬取项目",
        "test_time": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "company_info": crawler.get_company_info(),
        "configuration": {
            "city_code": crawler.city_code,
            "city_name": "深圳",
            "category_count": len(crawler.category_mapping),
            "categories": crawler.category_mapping,
            "required_fields": list(crawler.field_mapping.keys()),
            "output_dir": crawler.output_dir
        },
        "test_summary": {
            "connection_test": "待运行",
            "config_test": "待运行",
            "data_model_test": "待运行",
            "output_test": "待运行"
        }
    }
    
    # 保存报告
    report_file = os.path.join(crawler.output_dir, "test_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"📋 测试报告已保存: {report_file}")
    return report_file


if __name__ == "__main__":
    # 生成测试报告
    report_file = generate_test_report()
    print(f"📋 测试报告生成: {report_file}")
    
    # 运行所有测试
    success = run_all_tests()
    
    if success:
        print("\n" + "=" * 60)
        print("🎯 小规模测试通过，按照夸克规范可以继续:")
        print("1. 单页爬取测试: python3 src/meituan_crawler.py --mode browser --pages 1")
        print("2. 数据质量验证: 检查输出的JSON/CSV文件")
        print("3. 完整爬取执行: 所有测试通过后执行完整爬取")
        print("=" * 60)
        
        # 询问是否进行单页测试
        print("\n🔍 是否进行单页爬取测试？(y/n): ", end="")
        response = input().strip().lower()
        
        if response == 'y':
            print("🚀 启动单页爬取测试...")
            os.system("python3 src/meituan_crawler.py --mode browser --pages 1 --verbose")
    else:
        print("\n" + "=" * 60)
        print("⚠️ 测试失败，需要修复问题后再继续")
        print("💡 建议:")
        print("1. 检查配置文件 config/.env")
        print("2. 验证网络连接")
        print("3. 检查依赖包安装")
        print("4. 查看详细日志")
        print("=" * 60)
        
        sys.exit(1)