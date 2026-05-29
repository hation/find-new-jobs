#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDD爬取器基本功能
阶段1：基础API爬取验证
"""

import os
import sys
import json
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_config_files():
    """测试配置文件"""
    print("🔍 测试配置文件...")
    
    required_files = [
        "config/.env",
        "config/api_auth.json", 
        "config/project_config.json"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path} 存在")
            
            # 检查文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    
                # 检查关键配置
                if file_path == "config/.env":
                    if "PDD_API_FULL_URL" in content:
                        print("      ✅ 包含API端点配置")
                    else:
                        print("      ⚠️ 缺少API端点配置")
                        
                elif file_path == "config/api_auth.json":
                    if "template_version" in content:
                        print("      ✅ 配置文件格式正确")
                    else:
                        print("      ⚠️ 配置文件格式可能不正确")
                        
            except Exception as e:
                print(f"      ⚠️ 读取失败: {e}")
                all_exist = False
        else:
            print(f"   ❌ {file_path} 不存在")
            all_exist = False
    
    return all_exist

def test_dependencies():
    """测试依赖包"""
    print("\n📦 测试依赖包...")
    
    required_packages = [
        ("requests", "网络请求"),
        ("pandas", "数据处理"),
        ("openpyxl", "Excel支持")
    ]
    
    all_available = True
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} ({description}) 可用")
        except ImportError as e:
            print(f"   ❌ {package} ({description}) 不可用: {e}")
            all_available = False
    
    return all_available

def test_pdd_crawler_import():
    """测试PDD爬取器导入"""
    print("\n🐍 测试PDD爬取器导入...")
    
    try:
        # 添加路径
        sys.path.insert(0, str(Path(__file__).parent / "src" / "crawler"))
        sys.path.insert(0, str(Path(__file__).parent / "src" / "utils"))
        
        from pdd_crawler import PddCrawlerSelector
        print("   ✅ PddCrawlerSelector 导入成功")
        
        # 创建实例
        crawler = PddCrawlerSelector()
        print("   ✅ PddCrawlerSelector 实例化成功")
        
        return True, crawler
        
    except ImportError as e:
        print(f"   ❌ 导入失败: {e}")
        return False, None
    except Exception as e:
        print(f"   ❌ 实例化失败: {e}")
        return False, None

def test_pdd_exporter_import():
    """测试PDD导出器导入"""
    print("\n📤 测试PDD导出器导入...")
    
    try:
        from pdd_data_exporter import PddDataExporter
        print("   ✅ PddDataExporter 导入成功")
        
        # 创建实例
        exporter = PddDataExporter()
        print(f"   ✅ PddDataExporter 实例化成功")
        print(f"      夸克框架可用: {exporter.use_quark_framework}")
        print(f"      输出目录: {exporter.output_dir}")
        
        return True, exporter
        
    except ImportError as e:
        print(f"   ❌ 导入失败: {e}")
        return False, None
    except Exception as e:
        print(f"   ❌ 实例化失败: {e}")
        return False, None

def test_export_functionality(exporter):
    """测试导出功能"""
    print("\n🧪 测试导出功能...")
    
    # 创建测试数据
    test_positions = [
        {
            "position_id": "DEMO001",
            "position_name": "演示岗位1",
            "work_location": "上海",
            "position_category": "技术类",
            "update_time_str": "2026-05-22",
            "update_timestamp": 1779500000000,
            "detail_url": "https://careers.pddglobalhr.com/jobs/DEMO001"
        },
        {
            "position_id": "DEMO002", 
            "position_name": "演示岗位2",
            "work_location": "北京",
            "position_category": "运营类",
            "update_time_str": "2026-05-22",
            "update_timestamp": 1779501000000,
            "detail_url": "https://careers.pddglobalhr.com/jobs/DEMO002"
        }
    ]
    
    # 测试JSON导出
    print("   测试JSON导出...")
    result_json = exporter.export_positions(test_positions, format="json")
    
    if result_json.get("success"):
        print(f"     ✅ JSON导出成功")
        print(f"       文件: {result_json.get('filepath', 'N/A')}")
        
        if result_json.get('filepath') and os.path.exists(result_json.get('filepath')):
            print("     ✅ JSON文件存在")
        else:
            print("     ❌ JSON文件不存在")
    else:
        print(f"     ❌ JSON导出失败: {result_json.get('error')}")
    
    # 测试Excel导出
    print("   测试Excel导出...")
    result_excel = exporter.export_positions(test_positions, format="excel")
    
    if result_excel.get("success"):
        print(f"     ✅ Excel导出成功")
        print(f"       文件: {result_excel.get('filepath', 'N/A')}")
        
        if result_excel.get('filepath') and os.path.exists(result_excel.get('filepath')):
            print("     ✅ Excel文件存在")
            
            # 检查扩展名
            if result_excel.get('filepath', '').endswith('.xlsx'):
                print("     ✅ 扩展名正确 (.xlsx)")
            else:
                print(f"     ⚠️ 扩展名可能不正确: {result_excel.get('filepath')}")
        else:
            print("     ❌ Excel文件不存在")
    else:
        print(f"     ❌ Excel导出失败: {result_excel.get('error')}")
    
    return result_json.get("success") and result_excel.get("success")

def generate_test_report(config_ok, deps_ok, crawler_ok, exporter_ok, export_ok):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("PDD爬取器 - 阶段1 基本功能测试报告")
    print("=" * 60)
    
    report = {
        "test_time": "2026-05-22 16:30",
        "project": "拼多多招聘爬取器",
        "phase": "阶段1 - 基础API爬取",
        "tests": {
            "配置文件": "✅ 通过" if config_ok else "❌ 失败",
            "依赖包": "✅ 通过" if deps_ok else "❌ 失败",
            "爬取器导入": "✅ 通过" if crawler_ok else "❌ 失败",
            "导出器导入": "✅ 通过" if exporter_ok else "❌ 失败",
            "导出功能": "✅ 通过" if export_ok else "❌ 失败"
        },
        "overall_status": "✅ 通过" if all([config_ok, deps_ok, crawler_ok, exporter_ok, export_ok]) else "❌ 失败",
        "recommendations": []
    }
    
    # 显示结果
    print("📊 测试结果:")
    for test_name, test_result in report["tests"].items():
        print(f"   {test_name}: {test_result}")
    
    print(f"\n🎯 总体状态: {report['overall_status']}")
    
    # 生成建议
    if not config_ok:
        report["recommendations"].append("检查配置文件是否存在且格式正确")
    if not deps_ok:
        report["recommendations"].append("安装缺失的依赖包: pip install -r requirements_minimal.txt")
    if not crawler_ok:
        report["recommendations"].append("检查PDD爬取器代码导入问题")
    if not exporter_ok:
        report["recommendations"].append("检查PDD导出器代码导入问题")
    if not export_ok:
        report["recommendations"].append("检查导出功能实现")
    
    if report["recommendations"]:
        print(f"\n💡 建议:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"   {i}. {rec}")
    
    # 保存报告
    os.makedirs("output", exist_ok=True)
    report_file = "output/basic_functionality_test_report.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 报告已保存: {report_file}")
    print("=" * 60)
    
    return report["overall_status"] == "✅ 通过"

def main():
    """主函数"""
    print("PDD爬取器 - 阶段1 基本功能测试")
    print("=" * 60)
    print("目的: 验证阶段1开发的基本功能是否正常")
    print("=" * 60)
    
    # 运行测试
    config_ok = test_config_files()
    deps_ok = test_dependencies()
    crawler_ok, crawler = test_pdd_crawler_import()
    exporter_ok, exporter = test_pdd_exporter_import()
    
    export_ok = False
    if exporter_ok and exporter:
        export_ok = test_export_functionality(exporter)
    
    # 生成报告
    all_passed = generate_test_report(config_ok, deps_ok, crawler_ok, exporter_ok, export_ok)
    
    if all_passed:
        print("\n✅ 基本功能测试通过，可以开始API连接测试")
        print("\n下一步:")
        print("1. 运行API连接测试: python3 run_stage1.py (选择选项2)")
        print("2. 运行小规模测试: python3 run_stage1.py (选择选项3)")
        print("3. 如果API测试通过，运行完整爬取")
        return 0
    else:
        print("\n❌ 基本功能测试失败，需要修复问题")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)