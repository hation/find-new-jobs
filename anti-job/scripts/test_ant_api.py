#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蚂蚁国际招聘API测试脚本
基于从浏览器开发者工具获取的API信息
版本: v1.0.0
创建时间: 2026-05-22
"""

import json
import requests
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_api_config():
    """加载API配置"""
    config_path = project_root / "config" / "api_auth.json"
    
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 加载API配置: {config_path}")
        return config
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return None

def test_api_connection(config):
    """测试API连接"""
    print("\n" + "="*70)
    print("🚀 测试蚂蚁国际招聘API连接")
    print("="*70)
    
    # 获取API端点信息
    api_endpoints = config.get("api_endpoints", {})
    full_url = api_endpoints.get("full_url", "")
    base_url = api_endpoints.get("base_url", "")
    search_endpoint = api_endpoints.get("search_endpoint", "")
    
    if not full_url:
        print("❌ API端点URL未配置")
        return False
    
    print(f"📡 API端点: {full_url}")
    print(f"📡 请求方法: {api_endpoints.get('method', 'POST')}")
    
    # 构建请求头
    headers = {}
    auth_config = config.get("authentication", {})
    
    # 添加请求头
    if "headers" in auth_config:
        headers.update(auth_config["headers"])
    
    # 添加Cookie
    cookies = {}
    if "cookies" in auth_config:
        cookies.update(auth_config["cookies"])
    
    print(f"📋 请求头数量: {len(headers)}")
    print(f"🍪 Cookie数量: {len(cookies)}")
    
    # 构建请求体（模拟第一页请求）
    request_body = {
        "pageNo": 1,
        "pageSize": 10,
        "categories": "98,99,100,101,102,403,404,405,406,104,105,106,107,108,109,110,111,172,474,475,476,477,478,479,480,481,482,483,484,529,757,758,759,763,834,846,847,849,144,145,177,446,447,448,125,126,127,128,129,175,445,716,812,824,825,100000015,100000016,101300030,101300031,101300032,101300033,153,154,155,156,179,461,462,463,464,465,466,467,468,469,470,471,472,473,512,513,147,148,149,150,151,178,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426",
        "regions": ""
    }
    
    print(f"📦 请求体: {json.dumps(request_body, ensure_ascii=False, indent=2)}")
    
    try:
        print("\n🔗 发送API请求...")
        response = requests.post(
            full_url,
            headers=headers,
            cookies=cookies,
            json=request_body,
            timeout=30
        )
        
        print(f"📥 响应状态码: {response.status_code}")
        print(f"📥 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ API连接成功！")
            
            # 尝试解析响应
            try:
                data = response.json()
                print(f"📊 响应数据类型: {type(data)}")
                
                # 保存响应到文件
                output_dir = project_root / "output" / "test"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                output_file = output_dir / "api_test_response.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"💾 响应已保存到: {output_file}")
                
                # 分析响应结构
                analyze_response_structure(data)
                
                return True
                
            except json.JSONDecodeError:
                print("⚠️  响应不是有效的JSON格式")
                print(f"📝 响应文本: {response.text[:500]}...")
                return False
                
        else:
            print(f"❌ API请求失败，状态码: {response.status_code}")
            print(f"📝 响应文本: {response.text[:500]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
        return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def analyze_response_structure(data):
    """分析响应数据结构"""
    print("\n" + "="*70)
    print("🔍 分析响应数据结构")
    print("="*70)
    
    if not isinstance(data, dict):
        print(f"⚠️  响应数据不是字典类型: {type(data)}")
        return
    
    # 检查常见的关键字段
    common_fields = {
        "success": "成功状态字段",
        "code": "状态码字段", 
        "data": "数据字段",
        "list": "列表字段",
        "total": "总数字段",
        "pageNo": "当前页码",
        "pageSize": "页大小",
        "totalPage": "总页数"
    }
    
    print("📋 检查常见字段:")
    for field, description in common_fields.items():
        if field in data:
            value = data[field]
            print(f"  ✅ {field}: {value} ({description})")
        else:
            print(f"  ❌ {field}: 未找到 ({description})")
    
    # 如果存在data字段，进一步分析
    if "data" in data and isinstance(data["data"], dict):
        print("\n📊 分析data字段结构:")
        data_content = data["data"]
        
        if "list" in data_content and isinstance(data_content["list"], list):
            positions = data_content["list"]
            print(f"  📋 岗位数量: {len(positions)}")
            
            if positions:
                print(f"  🔍 第一个岗位的字段:")
                first_position = positions[0]
                for key, value in first_position.items():
                    print(f"    • {key}: {type(value).__name__} = {str(value)[:50]}...")
        
        # 检查分页信息
        pagination_fields = ["total", "pageNo", "pageSize", "totalPage"]
        for field in pagination_fields:
            if field in data_content:
                print(f"  📄 {field}: {data_content[field]}")
    
    # 保存数据结构分析
    output_dir = project_root / "output" / "test"
    structure_file = output_dir / "api_structure_analysis.json"
    
    analysis = {
        "response_type": type(data).__name__,
        "keys": list(data.keys()),
        "data_structure": extract_structure(data)
    }
    
    with open(structure_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"💾 结构分析已保存到: {structure_file}")

def extract_structure(data, depth=0, max_depth=3):
    """提取数据结构"""
    if depth > max_depth:
        return "..."
    
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                result[key] = extract_structure(value, depth + 1, max_depth)
            else:
                result[key] = f"{type(value).__name__}: {str(value)[:50]}"
        return result
    elif isinstance(data, list):
        if data:
            return [extract_structure(data[0], depth + 1, max_depth)]
        else:
            return []
    else:
        return f"{type(data).__name__}: {str(data)[:50]}"

def main():
    """主函数"""
    print("="*70)
    print("🚀 蚂蚁国际招聘API测试工具")
    print("="*70)
    
    # 1. 加载配置
    config = load_api_config()
    if not config:
        return
    
    # 2. 测试API连接
    success = test_api_connection(config)
    
    # 3. 输出结果
    print("\n" + "="*70)
    if success:
        print("🎉 API测试成功！")
        print("\n📋 下一步:")
        print("  1. 检查 output/test/api_test_response.json")
        print("  2. 分析响应数据结构")
        print("  3. 更新 config/api_auth.json 中的字段映射")
        print("  4. 测试分页功能")
    else:
        print("❌ API测试失败")
        print("\n🔧 排查建议:")
        print("  1. 检查Cookie是否过期")
        print("  2. 验证ctoken参数")
        print("  3. 检查网络连接")
        print("  4. 重新从浏览器获取最新的请求信息")
    
    print("="*70)

if __name__ == "__main__":
    main()