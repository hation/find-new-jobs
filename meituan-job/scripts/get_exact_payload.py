#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取美团API准确请求参数
按照夸克规范：手动获取准确参数，避免猜测
"""

import json
import requests
import time

def get_actual_payload_from_browser():
    """从浏览器获取实际请求参数"""
    print("=" * 60)
    print("🔍 获取美团API准确请求参数")
    print("=" * 60)
    
    print("🎯 目标: 获取 https://zhaopin.meituan.com/api/official/job/getJobList 的准确参数")
    
    print("\n📋 手动步骤:")
    print("1. 🌐 打开浏览器，访问: https://zhaopin.meituan.com/web/social")
    print("2. 🔍 应用筛选条件:")
    print("   - 城市: 深圳")
    print("   - 类别: 产品、运营、市场、金融、销售")
    print("3. 🛠️ 按F12打开开发者工具")
    print("4. 📡 切换到Network标签")
    print("5. 🔄 刷新页面或点击筛选")
    print("6. 📋 找到 'getJobList' 请求")
    print("7. 📝 点击该请求，查看 'Request Payload'")
    print("8. 📋 复制完整的JSON参数")
    
    print("\n💡 观察要点:")
    print("• 参数名称: 是 cityList 还是 city? jfJgList 还是 categories?")
    print("• 参数格式: 字符串还是数组? 逗号分隔还是JSON数组?")
    print("• 其他参数: 是否有 page, pageSize, sortField, sortOrder?")
    print("• 特殊字段: 是否需要 timestamp, signature, token?")
    
    print("\n📊 已知信息:")
    print("• API地址: https://zhaopin.meituan.com/api/official/job/getJobList")
    print("• 请求方法: POST")
    print("• Content-Type: application/json")
    print("• 城市代码: 001019002 (深圳)")
    print("• 类别代码: 11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001")
    
    print("\n❓ 待确认:")
    print("1. 参数名称: cityList? city? location?")
    print("2. 参数类型: 字符串? 数组?")
    print("3. 类别参数: jfJgList? categories? jobTypes?")
    print("4. 分页参数: page? pageNum? current?")
    print("5. 排序参数: sortField? sort? order?")
    
    return None

def test_with_common_formats():
    """测试常见的参数格式"""
    print("\n" + "=" * 60)
    print("🧪 测试常见参数格式")
    print("=" * 60)
    
    api_url = "https://zhaopin.meituan.com/api/official/job/getJobList"
    
    # 建立会话
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Referer": "https://zhaopin.meituan.com/web/social",
        "X-Requested-With": "XMLHttpRequest"
    })
    
    # 先访问页面建立会话
    print("1. 🔄 建立会话...")
    session.get("https://zhaopin.meituan.com/web/social", timeout=10)
    time.sleep(1)
    
    # 常见的参数格式组合
    test_cases = [
        # 格式1: 可能是美团内部格式
        {
            "name": "美团可能格式1",
            "params": {
                "city": "001019002",
                "jobType": ["11002_-1", "11003_-1", "11005_-1", "11007_-1", "11010_1101001"],
                "pageNo": 1,
                "pageSize": 10
            }
        },
        # 格式2: 可能是简写
        {
            "name": "美团可能格式2", 
            "params": {
                "c": "001019002",
                "t": "11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001",
                "p": 1,
                "ps": 10
            }
        },
        # 格式3: 可能是完整格式
        {
            "name": "美团可能格式3",
            "params": {
                "cityCode": "001019002",
                "categoryCodes": ["11002_-1", "11003_-1", "11005_-1", "11007_-1", "11010_1101001"],
                "currentPage": 1,
                "pageSize": 10,
                "sortType": "update_time_desc"
            }
        },
        # 格式4: 可能是带签名的格式
        {
            "name": "美团可能格式4",
            "params": {
                "data": {
                    "city": "001019002",
                    "categories": ["11002_-1", "11003_-1", "11005_-1", "11007_-1", "11010_1101001"],
                    "page": 1,
                    "size": 10
                },
                "timestamp": int(time.time() * 1000),
                "sign": "test_signature"
            }
        }
    ]
    
    print("2. 🧪 测试不同格式...")
    
    for test in test_cases:
        print(f"\n📋 测试: {test['name']}")
        print(f"📦 参数: {json.dumps(test['params'], ensure_ascii=False)}")
        
        try:
            response = session.post(
                api_url,
                json=test['params'],
                timeout=10
            )
            
            print(f"📥 响应: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                message = result.get('message', '无消息')
                print(f"📊 消息: {message}")
                
                if result.get('code') == 200:
                    print("✅ 成功!")
                    data = result.get('data', {})
                    print(f"📋 数据字段: {list(data.keys())}")
                    if 'list' in data:
                        print(f"📊 岗位数量: {len(data['list'])}")
                    return test['params']
                else:
                    print(f"❌ 失败: {message}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"💥 异常: {str(e)}")
    
    return None

def analyze_success_case():
    """分析成功案例（空参数返回成功）"""
    print("\n" + "=" * 60)
    print("🔍 分析成功案例")
    print("=" * 60)
    
    print("🎯 发现: 空参数 {} 返回 '成功'")
    print("💡 这意味着:")
    print("1. ✅ API端点可访问")
    print("2. ✅ 认证/会话正常")
    print("3. ❌ 参数格式不正确")
    
    print("\n🔧 可能的原因:")
    print("1. 📝 参数名称错误: 不是 cityList/jfJgList")
    print("2. 🔄 参数类型错误: 需要特定类型")
    print("3. 🕒 需要时间戳/签名")
    print("4. 📋 需要特定字段顺序")
    
    print("\n🎯 建议:")
    print("1. 🔍 必须手动查看浏览器中的实际请求")
    print("2. 📋 复制完整的 Request Payload")
    print("3. 🔄 使用完全相同的参数测试")
    print("4. 📝 记录成功案例供后续使用")
    
    return None

def main():
    """主函数"""
    print("🚀 美团API参数获取工具")
    print("按照夸克规范：必须获取准确参数")
    print("=" * 60)
    
    # 步骤1: 显示手动获取步骤
    get_actual_payload_from_browser()
    
    # 步骤2: 测试常见格式
    print("\n" + "=" * 60)
    print("🔄 自动测试常见格式（辅助验证）")
    print("=" * 60)
    
    successful_format = test_with_common_formats()
    
    if successful_format:
        print("\n" + "=" * 60)
        print("🎉 找到成功格式!")
        print("=" * 60)
        print(f"📋 成功格式: {json.dumps(successful_format, ensure_ascii=False)}")
        
        # 保存格式
        with open("meituan_successful_format.json", "w", encoding="utf-8") as f:
            json.dump({
                "discovery_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "api_url": "https://zhaopin.meituan.com/api/official/job/getJobList",
                "successful_format": successful_format,
                "note": "自动测试发现的成功格式"
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 成功格式已保存: meituan_successful_format.json")
        return successful_format
    
    # 步骤3: 分析空参数成功案例
    analyze_success_case()
    
    print("\n" + "=" * 60)
    print("📋 按照夸克规范，必须手动验证")
    print("=" * 60)
    
    print("\n🔧 请执行以下操作:")
    print("1. 🌐 手动访问美团招聘网站")
    print("2. 🔍 应用筛选条件")
    print("3. 📡 查看网络请求")
    print("4. 📋 复制 Request Payload")
    print("5. 🔄 在此脚本中测试")
    
    print("\n💡 复制后，可以:")
    print("1. 直接修改此脚本测试")
    print("2. 或告诉我准确的参数格式")
    print("3. 我将更新爬取器")
    
    return None

if __name__ == "__main__":
    result = main()
    
    if result:
        print("\n🎯 下一步:")
        print("1. 🔄 使用成功格式更新爬取器")
        print("2. 🧪 进行单页测试验证")
        print("3. 📊 开始完整数据爬取")
    else:
        print("\n⚠️ 需要手动获取参数格式")
        print("💡 请按照上述步骤操作，然后告诉我准确的参数")