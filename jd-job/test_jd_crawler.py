#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京东招聘爬取器测试脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_imports():
    """测试导入"""
    print("🧪 测试导入...")
    
    try:
        from src.jd_crawler import JDJobCrawler
        print("✅ JDJobCrawler 导入成功")
    except ImportError as e:
        print(f"❌ JDJobCrawler 导入失败: {e}")
        return False
    
    try:
        from src.framework.smart_crawler_selector import SmartCrawlerSelector
        print("✅ SmartCrawlerSelector 导入成功")
    except ImportError as e:
        print(f"❌ SmartCrawlerSelector 导入失败: {e}")
        return False
    
    try:
        from src.framework.data_exporter import DataExporter
        print("✅ DataExporter 导入成功")
    except ImportError as e:
        print(f"❌ DataExporter 导入失败: {e}")
        return False
    
    return True

def test_config_files():
    """测试配置文件"""
    print("\n🧪 测试配置文件...")
    
    config_files = [
        ("config/.env", "环境配置"),
        ("config/api_auth.json", "API认证配置"),
        ("config/browser_config.json", "浏览器配置"),
        ("config/project_config.json", "项目配置"),
    ]
    
    all_exists = True
    for file_path, description in config_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}: {file_path} 不存在")
            all_exists = False
    
    return all_exists

def test_directory_structure():
    """测试目录结构"""
    print("\n🧪 测试目录结构...")
    
    directories = [
        ("src/framework", "框架目录"),
        ("output/jd_jobs", "输出目录"),
        ("logs/jd_jobs", "日志目录"),
        ("data/jd_jobs", "数据目录"),
        ("backup/jd_jobs", "备份目录"),
    ]
    
    all_exists = True
    for dir_path, description in directories:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✅ {description}: {dir_path}")
        else:
            print(f"⚠️ {description}: {dir_path} 不存在，将自动创建")
            # 创建目录
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ 已创建目录: {dir_path}")
    
    return True

def test_crawler_initialization():
    """测试爬虫初始化"""
    print("\n🧪 测试爬虫初始化...")
    
    try:
        from src.jd_crawler import JDJobCrawler
        
        crawler = JDJobCrawler()
        print("✅ JDJobCrawler 初始化成功")
        
        # 测试配置加载
        if hasattr(crawler, 'company_name'):
            print(f"  公司名称: {crawler.company_name}")
        if hasattr(crawler, 'base_url'):
            print(f"  网站URL: {crawler.base_url}")
        if hasattr(crawler, 'default_params'):
            print(f"  默认参数: {crawler.default_params.get('pageSize', 'N/A')} 条/页")
        
        return True
        
    except Exception as e:
        print(f"❌ JDJobCrawler 初始化失败: {e}")
        return False

def test_data_processing():
    """测试数据处理"""
    print("\n🧪 测试数据处理...")
    
    try:
        from src.jd_crawler import JDJobCrawler
        
        crawler = JDJobCrawler()
        
        # 测试数据提取函数
        test_qualification = """
        1.本科及以上学历，法律、金融等相关3年以上工作经验优先
        2.具备与监管机构、行政机构对接沟通经验
        3.熟悉信贷、征信、支付、融担、技术相关业务的法律法规
        """
        
        education = crawler.extract_education(test_qualification)
        experience = crawler.extract_experience(test_qualification)
        
        print(f"✅ 学历提取: {education}")
        print(f"✅ 经验提取: {experience}")
        
        # 测试数据处理
        test_job = {
            "id": 163332,
            "positionName": "监管风控岗",
            "workCity": "北京市",
            "positionDeptName": "京东科技",
            "qualification": test_qualification,
            "workContent": "负责监管风险合规体系建立",
            "formatPublishTime": "2026-05-22",
            "reqNumber": "ZP2605221881",
            "jobType": "运营类",
            "isHot": 1
        }
        
        processed = crawler.process_job_data([test_job])
        if processed:
            print(f"✅ 数据处理成功，处理了 {len(processed)} 个岗位")
            print(f"   岗位名称: {processed[0].get('position_name', 'N/A')}")
            print(f"   工作地点: {processed[0].get('work_location', 'N/A')}")
            print(f"   部门: {processed[0].get('department', 'N/A')}")
            return True
        else:
            print("❌ 数据处理失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据处理测试失败: {e}")
        return False

def test_output_directories():
    """测试输出目录"""
    print("\n🧪 测试输出功能...")
    
    try:
        from src.jd_crawler import JDJobCrawler
        
        crawler = JDJobCrawler()
        
        # 创建测试数据
        test_jobs = [
            {
                "position_id": "test_001",
                "position_name": "测试岗位",
                "work_location": "北京市",
                "department": "测试部门",
                "education_requirement": "本科及以上",
                "work_experience": "3年以上",
                "position_description": "测试工作内容",
                "position_requirements": "测试任职要求",
                "publish_date": "2026-05-22",
                "company_info": "京东",
                "recruitment_number": "TEST001",
                "job_type": "测试类",
                "is_hot": 0,
                "raw_data": "{}"
            }
        ]
        
        # 测试JSON输出
        json_file = crawler.save_jobs_to_file(test_jobs, format="json")
        print(f"✅ JSON输出: {json_file}")
        
        # 测试CSV输出
        csv_file = crawler.save_jobs_to_file(test_jobs, format="csv")
        print(f"✅ CSV输出: {csv_file}")
        
        # 测试Excel输出
        excel_file = crawler.save_jobs_to_file(test_jobs, format="excel")
        print(f"✅ Excel输出: {excel_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 输出测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 京东招聘爬取器测试")
    print("=" * 60)
    
    tests = [
        ("导入测试", test_imports),
        ("配置文件测试", test_config_files),
        ("目录结构测试", test_directory_structure),
        ("爬虫初始化测试", test_crawler_initialization),
        ("数据处理测试", test_data_processing),
        ("输出功能测试", test_output_directories),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 执行: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📈 通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！京东爬取器可以正常使用。")
        print("\n🚀 下一步:")
        print("1. 运行测试模式: python3 src/jd_crawler.py --test")
        print("2. 运行完整爬取: python3 src/jd_crawler.py --pages 5")
        print("3. 查看帮助: python3 src/jd_crawler.py --help")
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败，请检查问题。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)