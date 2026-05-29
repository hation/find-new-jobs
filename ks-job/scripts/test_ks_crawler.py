#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘爬取器测试脚本
测试 ks_api_crawler.py 的功能
"""

import sys
import os
import json
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from src.ks_api_crawler import KsAPICrawler, load_config


def test_config_loading():
    """测试配置加载"""
    print("🧪 测试配置加载...")
    config = load_config()
    
    required_keys = [
        "base_url", "api_path", "page_size", 
        "position_category_codes", "position_nature_code",
        "recruit_project", "work_location_code"
    ]
    
    missing_keys = []
    for key in required_keys:
        if key not in config:
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ 配置缺失: {missing_keys}")
        return False
    
    print(f"✅ 配置加载成功")
    print(f"   API地址: {config['base_url']}{config['api_path']}")
    print(f"   默认参数: pageSize={config['page_size']}")
    print(f"   岗位类别: {config['position_category_codes']}")
    return True


def test_crawler_initialization():
    """测试爬取器初始化"""
    print("\n🧪 测试爬取器初始化...")
    
    config = load_config()
    
    try:
        crawler = KsAPICrawler(config)
        print("✅ 爬取器初始化成功")
        print(f"   API地址: {crawler.api_url}")
        print(f"   默认参数: {crawler.default_params}")
        return crawler
    except Exception as e:
        print(f"❌ 爬取器初始化失败: {e}")
        return None


def test_single_page_crawling(crawler):
    """测试单页爬取"""
    print("\n🧪 测试单页爬取...")
    
    try:
        start_time = time.time()
        positions, pagination = crawler.fetch_positions_page(1, 5)  # 只取5条测试
        
        elapsed_time = time.time() - start_time
        
        if positions:
            print(f"✅ 单页爬取成功")
            print(f"   获取岗位: {len(positions)} 个")
            print(f"   总岗位数: {pagination.get('total', 0)}")
            print(f"   总页数: {pagination.get('pages', 0)}")
            print(f"   耗时: {elapsed_time:.2f}秒")
            
            # 显示第一个岗位的详细信息
            if positions:
                first_position = positions[0]
                print(f"\n📋 第一个岗位详情:")
                print(f"   ID: {first_position.get('id')}")
                print(f"   名称: {first_position.get('name')}")
                print(f"   地点: {first_position.get('workLocationCode')}")
                print(f"   类别: {first_position.get('positionCategoryCode')}")
                print(f"   更新时间: {first_position.get('updateTime')}")
            
            return True, positions, pagination
        else:
            print("❌ 未获取到岗位数据")
            return False, [], {}
            
    except Exception as e:
        print(f"❌ 单页爬取失败: {e}")
        return False, [], {}


def test_field_extraction(crawler, raw_position):
    """测试字段提取"""
    print("\n🧪 测试字段提取...")
    
    try:
        standard_position = crawler.extract_standard_fields(raw_position)
        
        # 检查12个核心字段
        required_fields = [
            "positionId", "positionName", "workLocation", "positionCategory",
            "publishTime", "detailUrl", "department", "educationRequirement",
            "workExperience", "jobResponsibilities", "jobRequirements", "salaryRange"
        ]
        
        missing_fields = []
        for field in required_fields:
            if not standard_position.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"⚠️ 缺失字段: {missing_fields}")
        else:
            print("✅ 所有12个核心字段提取成功")
        
        print(f"\n📋 提取的字段示例:")
        for field in required_fields[:6]:  # 只显示前6个
            value = standard_position.get(field, "")
            print(f"   {field}: {value[:50]}{'...' if len(str(value)) > 50 else ''}")
        
        return standard_position
        
    except Exception as e:
        print(f"❌ 字段提取失败: {e}")
        return None


def test_data_validation(crawler, standard_position):
    """测试数据验证"""
    print("\n🧪 测试数据验证...")
    
    try:
        is_valid = crawler.validate_position_data(standard_position)
        
        if is_valid:
            print("✅ 数据验证通过")
        else:
            print("⚠️ 数据验证未通过（某些字段缺失）")
        
        return is_valid
        
    except Exception as e:
        print(f"❌ 数据验证失败: {e}")
        return False


def test_data_saving(crawler, standard_position):
    """测试数据保存"""
    print("\n🧪 测试数据保存...")
    
    # 创建测试输出目录
    test_output_dir = "output/test_data"
    os.makedirs(test_output_dir, exist_ok=True)
    
    try:
        filepath = crawler.save_position_data(standard_position, test_output_dir)
        
        if filepath and os.path.exists(filepath):
            print(f"✅ 数据保存成功")
            print(f"   文件路径: {filepath}")
            
            # 验证文件内容
            with open(filepath, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            print(f"   文件大小: {os.path.getsize(filepath)} 字节")
            print(f"   岗位ID: {saved_data.get('positionId')}")
            print(f"   岗位名称: {saved_data.get('positionName')}")
            
            return True, filepath
        else:
            print("❌ 数据保存失败")
            return False, ""
            
    except Exception as e:
        print(f"❌ 数据保存失败: {e}")
        return False, ""


def test_small_scale_crawling(crawler):
    """测试小规模爬取（2页）"""
    print("\n🧪 测试小规模爬取（2页）...")
    
    try:
        start_time = time.time()
        
        # 爬取2页数据
        all_positions = []
        for page_num in range(1, 3):
            print(f"   正在爬取第 {page_num} 页...")
            positions, _ = crawler.fetch_positions_page(page_num, 3)  # 每页3条
            if positions:
                all_positions.extend(positions)
            time.sleep(2)  # 避免请求过快
        
        elapsed_time = time.time() - start_time
        
        if all_positions:
            print(f"✅ 小规模爬取成功")
            print(f"   获取岗位: {len(all_positions)} 个")
            print(f"   耗时: {elapsed_time:.2f}秒")
            
            # 处理并保存所有数据
            test_output_dir = "output/test_batch"
            os.makedirs(test_output_dir, exist_ok=True)
            
            saved_count = 0
            for raw_position in all_positions:
                standard_position = crawler.extract_standard_fields(raw_position)
                filepath = crawler.save_position_data(standard_position, test_output_dir)
                if filepath:
                    saved_count += 1
            
            print(f"   保存文件: {saved_count}/{len(all_positions)}")
            return True
        else:
            print("❌ 未获取到任何岗位数据")
            return False
            
    except Exception as e:
        print(f"❌ 小规模爬取失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("🧪 快手招聘爬取器测试套件")
    print("=" * 70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = {}
    
    # 测试1: 配置加载
    test_results["config_loading"] = test_config_loading()
    
    # 测试2: 爬取器初始化
    crawler = test_crawler_initialization()
    test_results["crawler_init"] = crawler is not None
    
    if not crawler:
        print("\n❌ 爬取器初始化失败，后续测试终止")
        return test_results
    
    # 测试3: 单页爬取
    success, positions, pagination = test_single_page_crawling(crawler)
    test_results["single_page"] = success
    
    if not success or not positions:
        print("\n❌ 单页爬取失败，后续测试终止")
        return test_results
    
    # 测试4: 字段提取
    raw_position = positions[0]
    standard_position = test_field_extraction(crawler, raw_position)
    test_results["field_extraction"] = standard_position is not None
    
    if not standard_position:
        print("\n❌ 字段提取失败，后续测试终止")
        return test_results
    
    # 测试5: 数据验证
    test_results["data_validation"] = test_data_validation(crawler, standard_position)
    
    # 测试6: 数据保存
    success, filepath = test_data_saving(crawler, standard_position)
    test_results["data_saving"] = success
    
    # 测试7: 小规模爬取
    test_results["small_scale"] = test_small_scale_crawling(crawler)
    
    # 汇总测试结果
    print("\n" + "=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    for test_name, result in test_results.items():
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
    
    print("\n💡 建议:")
    if passed == total:
        print("   所有测试通过！可以开始正式爬取")
    elif passed >= total * 0.7:
        print("   大部分测试通过，建议检查失败项后开始正式爬取")
    else:
        print("   多个测试失败，建议先解决问题再继续")
    
    print("=" * 70)
    
    return test_results


if __name__ == "__main__":
    # 确保日志目录存在
    os.makedirs("logs", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    # 运行测试
    results = run_all_tests()
    
    # 根据测试结果给出建议
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    if passed == total:
        print("\n🎉 所有测试通过！下一步：")
        print("   1. 更新 config/.env 中的 Cookie 信息")
        print("   2. 运行完整爬取: python src/ks_api_crawler.py")
        print("   3. 查看输出数据: ls -la output/ks_data/")
    else:
        print("\n🔧 需要修复的问题：")
        for test_name, result in results.items():
            if not result:
                print(f"   • {test_name}: 测试失败")
        
        print("\n💡 常见问题解决方案：")
        print("   1. Cookie无效: 从浏览器复制有效的Cookie")
        print("   2. 网络问题: 检查网络连接和代理设置")
        print("   3. API变更: 确认API地址和参数是否正确")