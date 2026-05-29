#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试蚂蚁国际招聘API请求体
验证筛选参数是否正确
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

def load_config():
    """加载配置文件"""
    config_path = project_root / "config" / "ant_api_auth.json"
    
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 加载配置文件: {config_path}")
        return config
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return None

def test_request_body(config):
    """测试请求体"""
    print("\n" + "="*70)
    print("🧪 测试蚂蚁国际招聘API请求体")
    print("="*70)
    
    # 获取API端点信息
    api_endpoints = config.get("api_endpoints", {})
    full_url = api_endpoints.get("full_url", "")
    
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
    
    # 构建请求体（基于确认的格式）
    request_body = {
        "regions": "",
        "categories": "97,103,143,124,152,146",
        "subCategories": "97,103,143,124,152,146,98,99,100,101,102,403,404,405,406,104,105,106,107,108,109,110,111,172,474,475,476,477,478,479,480,481,482,483,484,529,757,758,759,763,834,846,847,849,144,145,177,446,447,448,125,126,127,128,129,175,445,716,812,824,825,100000015,100000016,101300030,101300031,101300032,101300033,153,154,155,156,179,461,462,463,464,465,466,467,468,469,470,471,472,473,512,513,147,148,149,150,151,178,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426",
        "bgCode": "",
        "socialQrCode": "",
        "pageIndex": 1,
        "pageSize": 10,
        "channel": "group_official_site",
        "language": "zh"
    }
    
    print(f"\n📦 请求体结构:")
    print(json.dumps(request_body, ensure_ascii=False, indent=2))
    
    # 分析请求体
    print(f"\n🔍 请求体分析:")
    print(f"  📊 主要类别: {len(request_body['categories'].split(','))} 个")
    print(f"  📊 子类别: {len(request_body['subCategories'].split(','))} 个")
    print(f"  📄 地区筛选: {request_body['regions'] or '所有地区'}")
    print(f"  📄 渠道: {request_body['channel']}")
    print(f"  📄 语言: {request_body['language']}")
    print(f"  📄 页码: {request_body['pageIndex']}")
    print(f"  📄 页大小: {request_body['pageSize']}")
    
    # 检查类别数量
    main_categories = request_body['categories'].split(',')
    sub_categories = request_body['subCategories'].split(',')
    
    print(f"\n🔍 类别分析:")
    print(f"  ✅ 主要类别数量: {len(main_categories)} 个")
    print(f"  ✅ 子类别数量: {len(sub_categories)} 个")
    
    # 检查主要类别是否在子类别中
    missing_categories = []
    for category in main_categories:
        if category not in sub_categories:
            missing_categories.append(category)
    
    if missing_categories:
        print(f"  ⚠️  以下主要类别不在子类别中: {missing_categories}")
    else:
        print(f"  ✅ 所有主要类别都在子类别中")
    
    # 发送测试请求
    print(f"\n🔗 发送测试请求...")
    try:
        response = requests.post(
            full_url,
            headers=headers,
            cookies=cookies,
            json=request_body,
            timeout=30
        )
        
        print(f"📥 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API请求成功！")
            
            try:
                data = response.json()
                print(f"📊 响应数据类型: {type(data)}")
                
                # 检查响应结构
                if data.get("success") is True:
                    print(f"✅ API返回成功状态")
                    
                    total_count = data.get("totalCount", 0)
                    page_size = data.get("pageSize", 0)
                    current_page = data.get("currentPage", 0)
                    content = data.get("content", [])
                    
                    print(f"📊 总岗位数: {total_count}")
                    print(f"📊 每页数量: {page_size}")
                    print(f"📊 当前页码: {current_page}")
                    print(f"📊 返回岗位数: {len(content)}")
                    
                    if content:
                        print(f"\n🔍 第一个岗位信息:")
                        first_position = content[0]
                        print(f"  • ID: {first_position.get('id')}")
                        print(f"  • 名称: {first_position.get('name')}")
                        print(f"  • 地点: {first_position.get('workLocations')}")
                        print(f"  • 部门: {first_position.get('department')}")
                        print(f"  • 类别: {first_position.get('categories')}")
                    
                    # 保存响应到文件
                    output_dir = project_root / "output" / "test"
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    output_file = output_dir / "test_request_body_response.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    print(f"\n💾 响应已保存到: {output_file}")
                    
                    return True
                    
                else:
                    print(f"❌ API返回失败状态: {data}")
                    return False
                    
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

def compare_with_old_request():
    """对比新旧请求体"""
    print("\n" + "="*70)
    print("🔄 对比新旧请求体")
    print("="*70)
    
    old_request = {
        "pageNo": 1,
        "pageSize": 10,
        "categories": "98,99,100,101,102,403,404,405,406,104,105,106,107,108,109,110,111,172,474,475,476,477,478,479,480,481,482,483,484,529,757,758,759,763,834,846,847,849,144,145,177,446,447,448,125,126,127,128,129,175,445,716,812,824,825,100000015,100000016,101300030,101300031,101300032,101300033,153,154,155,156,179,461,462,463,464,465,466,467,468,469,470,471,472,473,512,513,147,148,149,150,151,178,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426",
        "regions": ""
    }
    
    new_request = {
        "regions": "",
        "categories": "97,103,143,124,152,146",
        "subCategories": "97,103,143,124,152,146,98,99,100,101,102,403,404,405,406,104,105,106,107,108,109,110,111,172,474,475,476,477,478,479,480,481,482,483,484,529,757,758,759,763,834,846,847,849,144,145,177,446,447,448,125,126,127,128,129,175,445,716,812,824,825,100000015,100000016,101300030,101300031,101300032,101300033,153,154,155,156,179,461,462,463,464,465,466,467,468,469,470,471,472,473,512,513,147,148,149,150,151,178,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426",
        "bgCode": "",
        "socialQrCode": "",
        "pageIndex": 1,
        "pageSize": 10,
        "channel": "group_official_site",
        "language": "zh"
    }
    
    print("📊 旧请求体:")
    print(f"  参数数量: {len(old_request)}")
    print(f"  页码参数: pageNo")
    print(f"  类别参数: categories ({len(old_request['categories'].split(','))}个)")
    
    print("\n📊 新请求体:")
    print(f"  参数数量: {len(new_request)}")
    print(f"  页码参数: pageIndex")
    print(f"  主要类别: categories ({len(new_request['categories'].split(','))}个)")
    print(f"  子类别: subCategories ({len(new_request['subCategories'].split(','))}个)")
    print(f"  新增参数: bgCode, socialQrCode, channel, language")
    
    print("\n🔍 关键差异:")
    print("  1. 页码参数名: pageNo → pageIndex")
    print("  2. 类别拆分: 单一categories → categories + subCategories")
    print("  3. 新增参数: channel和language")
    print("  4. 主要类别: 从98个减少到6个")
    
    return new_request

def main():
    """主函数"""
    print("="*70)
    print("🧪 蚂蚁国际招聘API请求体测试工具")
    print("="*70)
    
    # 1. 加载配置
    config = load_config()
    if not config:
        return 1
    
    # 2. 对比新旧请求体
    compare_with_old_request()
    
    # 3. 测试新请求体
    success = test_request_body(config)
    
    # 4. 输出结果
    print("\n" + "="*70)
    if success:
        print("🎉 请求体测试成功！")
        print("\n📋 下一步:")
        print("  1. 检查 output/test/test_request_body_response.json")
        print("  2. 验证总岗位数是否正确")
        print("  3. 运行完整爬取: python scripts/ant_api_crawler_configurable.py")
    else:
        print("❌ 请求体测试失败")
        print("\n🔧 排查建议:")
        print("  1. 检查Cookie是否过期")
        print("  2. 验证ctoken参数")
        print("  3. 检查筛选参数格式")
        print("  4. 确认API端点是否正确")
    
    print("="*70)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())