#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDD API连接
尝试不同的anti_content值
"""

import os
import sys
import json
import time
import requests
import logging
from typing import Dict, Any, Optional

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_env_config():
    """加载环境配置"""
    config = {}
    
    try:
        # 从.env文件读取
        env_path = "config/.env"
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"')
        
        logger.info("✅ 环境配置加载成功")
        return config
        
    except Exception as e:
        logger.error(f"❌ 加载环境配置失败: {e}")
        return {}

def test_api_with_anti_content(anti_content_value: str, test_name: str = "") -> bool:
    """
    使用指定的anti_content值测试API
    
    Args:
        anti_content_value: anti_content参数值
        test_name: 测试名称
        
    Returns:
        是否成功
    """
    config = load_env_config()
    
    # API端点
    api_url = config.get("PDD_API_FULL_URL", "https://careers.pddglobalhr.com/api/recruit/position/list")
    
    # 请求头
    headers = {
        "User-Agent": config.get("USER_AGENT", "Mozilla/5.0"),
        "Accept": config.get("ACCEPT", "*/*"),
        "Accept-Language": config.get("ACCEPT_LANGUAGE", "zh-CN,zh;q=0.9,en;q=0.8"),
        "Accept-Encoding": config.get("ACCEPT_ENCODING", "gzip, deflate, br"),
        "Content-Type": config.get("PDD_API_CONTENT_TYPE", "application/json"),
        "Origin": config.get("ORIGIN", "https://careers.pddglobalhr.com"),
        "Referer": config.get("REFERER", "https://careers.pddglobalhr.com/jobs"),
        "Cookie": f"_nano_fp={config.get('PDD_COOKIE_NANO_FP', '')}"
    }
    
    # 请求数据
    payload = {
        "page": 1,
        "pageSize": 10,
        "anti_content": anti_content_value
    }
    
    logger.info(f"🧪 测试API连接 ({test_name})")
    logger.info(f"   端点: {api_url}")
    logger.info(f"   anti_content: {anti_content_value[:50]}...")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        elapsed_time = time.time() - start_time
        
        logger.info(f"   ⏱️ 响应时间: {elapsed_time:.2f}秒")
        logger.info(f"   📊 状态码: {response.status_code}")
        
        # 尝试解析响应
        try:
            response_data = response.json()
            
            # 检查成功标志
            success = response_data.get("success", False)
            error_code = response_data.get("errorCode")
            error_msg = response_data.get("errorMsg", "")
            
            if success:
                logger.info(f"   ✅ API调用成功")
                
                # 检查数据
                result = response_data.get("result", {})
                data_list = result.get("list", [])
                total = result.get("total", 0)
                
                logger.info(f"   📈 获取到 {len(data_list)} 条数据，总计 {total} 条")
                
                if data_list:
                    # 显示第一条数据
                    first_item = data_list[0]
                    logger.info(f"   📋 示例数据:")
                    logger.info(f"      岗位代码: {first_item.get('code', 'N/A')}")
                    logger.info(f"      岗位名称: {first_item.get('name', 'N/A')}")
                    logger.info(f"      工作地点: {first_item.get('workLocation', 'N/A')}")
                
                return True
                
            else:
                logger.warning(f"   ⚠️ API返回失败: {error_code} - {error_msg}")
                
                # 保存错误响应供分析
                error_file = f"output/api_error_{test_name}.json"
                os.makedirs("output", exist_ok=True)
                with open(error_file, 'w', encoding='utf-8') as f:
                    json.dump(response_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"   📄 错误响应已保存: {error_file}")
                return False
                
        except json.JSONDecodeError:
            logger.error(f"   ❌ 响应不是有效的JSON")
            logger.debug(f"   响应内容: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"   ⏰ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        logger.error(f"   🔌 连接错误")
        return False
    except Exception as e:
        logger.error(f"   ❌ 请求异常: {e}")
        return False

def test_different_anti_content_values():
    """测试不同的anti_content值"""
    print("\n" + "="*60)
    print("🧪 测试不同的anti_content值")
    print("="*60)
    
    test_cases = [
        {
            "name": "空值测试",
            "value": "",
            "description": "测试空字符串是否有效"
        },
        {
            "name": "固定值测试1", 
            "value": "test_anti_content",
            "description": "测试固定字符串"
        },
        {
            "name": "时间戳测试",
            "value": str(int(time.time() * 1000)),
            "description": "测试时间戳作为参数"
        },
        {
            "name": "随机值测试",
            "value": "abc123xyz789",
            "description": "测试随机字符串"
        },
        {
            "name": "长字符串测试",
            "value": "a" * 100,
            "description": "测试长字符串"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🔬 {test_case['name']}: {test_case['description']}")
        
        success = test_api_with_anti_content(
            anti_content_value=test_case["value"],
            test_name=test_case["name"]
        )
        
        results.append({
            "test": test_case["name"],
            "value": test_case["value"],
            "success": success,
            "description": test_case["description"]
        })
        
        # 短暂延迟，避免请求过快
        time.sleep(1)
    
    # 生成测试报告
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"\n✅ 成功的测试: {len(successful_tests)}/{len(results)}")
    for result in successful_tests:
        print(f"   • {result['test']}: {result['value'][:30]}...")
    
    print(f"\n❌ 失败的测试: {len(failed_tests)}/{len(results)}")
    for result in failed_tests:
        print(f"   • {result['test']}: {result['value'][:30]}...")
    
    # 保存测试报告
    report = {
        "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": len(results),
        "successful_tests": len(successful_tests),
        "failed_tests": len(failed_tests),
        "results": results,
        "recommendation": ""
    }
    
    if successful_tests:
        report["recommendation"] = f"使用成功的参数值: {successful_tests[0]['value']}"
        print(f"\n💡 建议: {report['recommendation']}")
    else:
        report["recommendation"] = "所有测试都失败，可能需要动态生成anti_content参数"
        print(f"\n⚠️ 警告: {report['recommendation']}")
        print("   可能需要:")
        print("   1. 分析网站JavaScript代码")
        print("   2. 使用浏览器开发者工具获取真实参数")
        print("   3. 使用浏览器自动化方案")
    
    # 保存报告
    os.makedirs("output", exist_ok=True)
    report_file = "output/anti_content_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 测试报告已保存: {report_file}")
    
    return len(successful_tests) > 0

def try_browser_approach():
    """尝试浏览器方案"""
    print("\n" + "="*60)
    print("🌐 尝试浏览器自动化方案")
    print("="*60)
    
    print("由于API需要动态anti_content参数，我们可以:")
    print("1. 使用浏览器直接访问网页")
    print("2. 从网页中提取数据")
    print("3. 避免API参数问题")
    
    # 检查是否可以使用浏览器工具
    try:
        import webbrowser
        print("\n✅ 可以尝试浏览器方案")
        
        # 测试URL
        test_url = "https://careers.pddglobalhr.com/jobs"
        print(f"\n🔗 测试URL: {test_url}")
        print("💡 建议: 使用浏览器开发者工具分析网络请求")
        print("   1. 打开浏览器开发者工具 (F12)")
        print("   2. 转到Network选项卡")
        print("   3. 访问拼多多招聘网站")
        print("   4. 查看实际的API请求和参数")
        
        return True
        
    except ImportError:
        print("\n❌ 无法导入浏览器模块")
        return False

def main():
    """主函数"""
    print("PDD API连接测试工具")
    print("="*60)
    print("目的: 测试API连接，找到有效的anti_content参数")
    print("="*60)
    
    # 测试不同的anti_content值
    api_success = test_different_anti_content_values()
    
    if api_success:
        print("\n✅ API测试成功，可以开始爬取数据")
        print("\n下一步:")
        print("1. 使用成功的anti_content值运行爬取器")
        print("2. 爬取岗位列表数据")
        print("3. 导出Excel文档")
        return 0
    else:
        print("\n❌ API测试全部失败")
        print("\n备选方案:")
        
        # 尝试浏览器方案
        browser_available = try_browser_approach()
        
        if browser_available:
            print("\n🚀 可以尝试浏览器自动化方案")
            print("需要:")
            print("1. 安装浏览器自动化工具 (selenium/playwright)")
            print("2. 编写浏览器爬取脚本")
            print("3. 从网页中提取数据")
        else:
            print("\n⚠️ 需要用户提供正确的anti_content生成方法")
            print("请提供以下信息之一:")
            print("1. 有效的anti_content值")
            print("2. anti_content生成逻辑")
            print("3. 如何从网站获取这个参数")
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)