#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试蚂蚁国际招聘API
"""

import json
import requests
from datetime import datetime
from pathlib import Path

def main():
    print("="*70)
    print("🚀 快速测试蚂蚁国际招聘API")
    print("="*70)
    
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "output" / "quick_test"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. API端点
    api_url = "https://hrcareersweb.antgroup.com/api/social/position/search?ctoken=bigfish_ctoken_1a9652509k"
    
    # 2. 简化的请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json",
        "Origin": "https://talent.antgroup.com",
        "Referer": "https://talent.antgroup.com/",
        "front-user-id": "729d74a1-d280-4486-a5d6-18aa210e4aff43"
    }
    
    # 3. 关键Cookie
    cookies = {
        "ctoken": "bigfish_ctoken_1a9652509k",
        "SESSION": "OTEzODQxNjhEMzQ4OTdDOTFFNzAwNzMzMEYyMzMyOEI="
    }
    
    # 4. 请求体（使用确认的格式）
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
    
    print(f"📡 API端点: {api_url}")
    print(f"📋 请求头: {len(headers)}个")
    print(f"🍪 Cookie: {len(cookies)}个")
    print(f"📦 请求体: 主要类别{len(request_body['categories'].split(','))}个，子类别{len(request_body['subCategories'].split(','))}个")
    
    print(f"\n🔗 发送请求...")
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            cookies=cookies,
            json=request_body,
            timeout=30
        )
        
        print(f"📥 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ HTTP请求成功")
            
            try:
                data = response.json()
                print(f"📊 JSON解析成功")
                
                # 检查API响应
                if data.get("success") is True:
                    print("✅ API返回成功状态")
                    
                    total_count = data.get("totalCount", 0)
                    page_size = data.get("pageSize", 0)
                    current_page = data.get("currentPage", 0)
                    content = data.get("content", [])
                    
                    print(f"\n📊 数据统计:")
                    print(f"  总岗位数: {total_count}")
                    print(f"  每页数量: {page_size}")
                    print(f"  当前页码: {current_page}")
                    print(f"  返回岗位数: {len(content)}")
                    
                    if content:
                        print(f"\n🔍 第一个岗位信息:")
                        first = content[0]
                        print(f"  • ID: {first.get('id')}")
                        print(f"  • 名称: {first.get('name')}")
                        print(f"  • 地点: {first.get('workLocations')}")
                        print(f"  • 部门: {first.get('department')}")
                        
                        # 类别映射
                        category_map = {
                            "97": "产品类",
                            "103": "运营类",
                            "143": "数据类",
                            "124": "市场拓展",
                            "152": "销售类",
                            "146": "金融类"
                        }
                        
                        categories = first.get('categories', [])
                        if categories:
                            cat_names = []
                            for cat in categories:
                                cat_str = str(cat)
                                cat_names.append(category_map.get(cat_str, cat_str))
                            print(f"  • 类别: {', '.join(cat_names)}")
                    
                    # 保存响应
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = output_dir / f"api_response_{timestamp}.json"
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    print(f"\n💾 响应已保存到: {output_file}")
                    
                    # 显示所有岗位的简要信息
                    if content:
                        print(f"\n📋 本页所有岗位 ({len(content)}个):")
                        for i, position in enumerate(content[:5], 1):  # 只显示前5个
                            print(f"  {i}. {position.get('name')} - {position.get('workLocations')}")
                        
                        if len(content) > 5:
                            print(f"  ... 还有{len(content)-5}个岗位")
                    
                    return True
                    
                else:
                    error_msg = data.get("errorMsg", "未知错误")
                    error_code = data.get("errorCode", "未知")
                    print(f"❌ API返回失败: {error_msg} (代码: {error_code})")
                    return False
                    
            except json.JSONDecodeError:
                print("❌ 响应不是有效的JSON格式")
                print(f"📝 响应前500字符: {response.text[:500]}")
                return False
                
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"📝 响应前500字符: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
        return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    print("\n" + "="*70)
    if success:
        print("🎉 测试成功！API配置正确")
        print("\n📋 下一步:")
        print("  1. 检查 output/quick_test/ 目录下的响应文件")
        print("  2. 验证总岗位数是否合理")
        print("  3. 运行完整爬取器")
    else:
        print("❌ 测试失败")
        print("\n🔧 排查建议:")
        print("  1. 检查Cookie是否过期")
        print("  2. 验证ctoken参数")
        print("  3. 检查网络连接")
    print("="*70)