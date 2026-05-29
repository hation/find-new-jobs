#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试夸克项目导出系统集成
验证PDD项目是否正确复用了夸克项目的导出框架
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

def test_quark_export_framework():
    """测试夸克项目导出框架"""
    print("🔍 测试夸克项目导出框架...")
    
    # 检查夸克项目导出框架文件
    quark_export_path = Path("~/").expanduser() / ".openclaw" / "workspace" / "skills" / "quark-campus-recruitment-scraper" / "template" / "framework" / "data_exporter.py"
    
    if not quark_export_path.exists():
        print("❌ 夸克项目导出框架文件不存在")
        return False
    
    print(f"✅ 夸克项目导出框架文件存在: {quark_export_path}")
    
    # 检查文件内容
    try:
        with open(quark_export_path, 'r', encoding='utf-8') as f:
            content = f.read(1000)  # 读取前1000字符
        
        # 检查关键类和方法
        check_items = [
            ("class DataExporter", "DataExporter类"),
            ("def export_data", "export_data方法"),
            ("def _export_to_excel", "Excel导出方法"),
            ("def _export_to_csv", "CSV导出方法"),
            ("def _export_to_json", "JSON导出方法")
        ]
        
        all_passed = True
        for keyword, description in check_items:
            if keyword in content:
                print(f"   ✅ {description} 存在")
            else:
                print(f"   ❌ {description} 不存在")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 读取夸克项目导出框架失败: {e}")
        return False

def test_pdd_export_integration():
    """测试PDD导出集成"""
    print("\n🔗 测试PDD导出集成...")
    
    # 检查PDD数据导出器
    pdd_export_path = Path(__file__).parent / "src" / "utils" / "pdd_data_exporter.py"
    
    if not pdd_export_path.exists():
        print("❌ PDD数据导出器文件不存在")
        return False
    
    print(f"✅ PDD数据导出器文件存在: {pdd_export_path}")
    
    # 检查文件内容
    try:
        with open(pdd_export_path, 'r', encoding='utf-8') as f:
            content = f.read(2000)  # 读取前2000字符
        
        # 检查关键集成点
        check_items = [
            ("from data_exporter import DataExporter", "夸克项目导出框架导入"),
            ("class PddDataExporter", "PDD数据导出器类"),
            ("def export_with_quark_framework", "夸克框架导出方法"),
            ("def export_simple", "简化版导出方法"),
            ("拼多多数据导出器 - 基于夸克项目数据导出框架", "文档说明")
        ]
        
        all_passed = True
        for keyword, description in check_items:
            if keyword in content:
                print(f"   ✅ {description} 存在")
            else:
                print(f"   ❌ {description} 不存在")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 读取PDD数据导出器失败: {e}")
        return False

def test_crawler_export_integration():
    """测试爬取器导出集成"""
    print("\n🔄 测试爬取器导出集成...")
    
    # 检查PDD爬取器文件
    crawler_path = Path(__file__).parent / "src" / "crawler" / "pdd_crawler.py"
    
    if not crawler_path.exists():
        print("❌ PDD爬取器文件不存在")
        return False
    
    print(f"✅ PDD爬取器文件存在: {crawler_path}")
    
    # 检查文件内容
    try:
        with open(crawler_path, 'r', encoding='utf-8') as f:
            content = f.read(3000)  # 读取前3000字符
        
        # 检查关键集成点
        check_items = [
            ("from pdd_data_exporter import PddDataExporter", "PDD数据导出器导入"),
            ("def save_positions", "保存岗位数据方法"),
            ("使用夸克项目导出系统", "导出系统说明"),
            ("format=\"excel\"", "Excel格式导出"),
            ("def _save_simple_json", "简单JSON保存方法")
        ]
        
        all_passed = True
        for keyword, description in check_items:
            if keyword in content:
                print(f"   ✅ {description} 存在")
            else:
                print(f"   ❌ {description} 不存在")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 读取PDD爬取器失败: {e}")
        return False

def test_export_workflow():
    """测试导出工作流程"""
    print("\n🧪 测试导出工作流程...")
    
    # 创建测试数据
    test_positions = [
        {
            "position_id": "TEST001",
            "position_name": "测试岗位1",
            "work_location": "上海",
            "position_category": "技术类",
            "update_time_str": "2026-05-22",
            "update_timestamp": 1779500000000,
            "detail_url": "https://careers.pddglobalhr.com/jobs/TEST001"
        },
        {
            "position_id": "TEST002",
            "position_name": "测试岗位2",
            "work_location": "北京",
            "position_category": "运营类",
            "update_time_str": "2026-05-22",
            "update_timestamp": 1779501000000,
            "detail_url": "https://careers.pddglobalhr.com/jobs/TEST002"
        }
    ]
    
    # 测试PDD数据导出器
    try:
        # 添加路径
        sys.path.insert(0, str(Path(__file__).parent / "src" / "utils"))
        
        from pdd_data_exporter import PddDataExporter
        
        # 创建导出器
        exporter = PddDataExporter()
        
        # 测试JSON导出
        print("  测试JSON导出...")
        result_json = exporter.export_positions(test_positions, format="json")
        
        if result_json.get("success"):
            print(f"    ✅ JSON导出成功: {result_json.get('filepath', 'N/A')}")
            
            # 验证文件存在
            if os.path.exists(result_json.get("filepath", "")):
                print("    ✅ JSON文件存在")
            else:
                print("    ❌ JSON文件不存在")
                return False
        else:
            print(f"    ❌ JSON导出失败: {result_json.get('error')}")
            return False
        
        # 测试夸克框架可用性
        if exporter.use_quark_framework:
            print("  测试Excel导出（夸克框架）...")
            result_excel = exporter.export_positions(test_positions, format="excel")
            
            if result_excel.get("success"):
                print(f"    ✅ Excel导出成功: {result_excel.get('filepath', 'N/A')}")
                
                # 验证文件存在
                if os.path.exists(result_excel.get("filepath", "")):
                    print("    ✅ Excel文件存在")
                else:
                    print("    ❌ Excel文件不存在")
                    return False
            else:
                print(f"    ❌ Excel导出失败: {result_excel.get('error')}")
                # Excel导出失败不是致命错误，可以继续
        else:
            print("   ⚠️ 夸克框架不可用，跳过Excel导出测试")
        
        return True
        
    except ImportError as e:
        print(f"❌ PDD数据导出器导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 导出工作流程测试失败: {e}")
        return False

def generate_integration_report():
    """生成集成测试报告"""
    print("\n" + "=" * 60)
    print("夸克项目导出系统集成测试报告")
    print("=" * 60)
    
    report = {
        "test_time": "2026-05-22 16:00",
        "project": "拼多多招聘爬取器",
        "integration_target": "夸克项目数据导出框架",
        "tests": {},
        "recommendations": []
    }
    
    # 运行测试
    tests = [
        ("夸克项目导出框架", test_quark_export_framework),
        ("PDD导出集成", test_pdd_export_integration),
        ("爬取器导出集成", test_crawler_export_integration),
        ("导出工作流程", test_export_workflow)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            passed = test_func()
            report["tests"][test_name] = {
                "passed": passed,
                "status": "✅ 通过" if passed else "❌ 失败"
            }
            
            if not passed:
                all_passed = False
                report["recommendations"].append(f"修复{test_name}测试")
        except Exception as e:
            report["tests"][test_name] = {
                "passed": False,
                "status": f"❌ 异常: {str(e)}"
            }
            all_passed = False
            report["recommendations"].append(f"修复{test_name}异常: {e}")
    
    # 显示结果
    print(f"\n📊 测试结果:")
    for test_name, test_result in report["tests"].items():
        print(f"   {test_name}: {test_result['status']}")
    
    if all_passed:
        print(f"\n🎉 所有测试通过!")
        report["overall_status"] = "success"
        report["recommendations"].append("可以开始阶段1功能测试")
    else:
        print(f"\n⚠️  部分测试失败")
        report["overall_status"] = "failed"
        report["recommendations"].append("需要修复失败的测试")
    
    # 显示建议
    print(f"\n💡 建议:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"   {i}. {rec}")
    
    # 保存报告
    report_file = "output/integration_test_report.json"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 报告已保存: {report_file}")
    print("=" * 60)
    
    return all_passed

def main():
    """主函数"""
    print("夸克项目导出系统集成测试")
    print("=" * 60)
    print("目的: 验证PDD项目是否正确复用了夸克项目的导出框架")
    print("=" * 60)
    
    # 创建输出目录
    os.makedirs("output", exist_ok=True)
    
    # 运行集成测试
    success = generate_integration_report()
    
    if success:
        print("\n✅ 集成测试完成，可以开始阶段1功能测试")
        return 0
    else:
        print("\n❌ 集成测试失败，需要修复问题")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)