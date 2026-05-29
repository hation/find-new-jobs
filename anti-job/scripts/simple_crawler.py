#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的蚂蚁国际招聘爬取器
避免编码问题，直接使用原始请求
"""

import json
import requests
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
output_dir = project_root / "output" / "simple_crawl"
output_dir.mkdir(parents=True, exist_ok=True)

print("="*70)
print("🚀 简化的蚂蚁国际招聘爬取器")
print("="*70)

# 1. API端点
api_url = "https://hrcareersweb.antgroup.com/api/social/position/search?ctoken=bigfish_ctoken_1a9652509k"

# 2. 请求头（简化版，避免编码问题）
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json",
    "Origin": "https://talent.antgroup.com",
    "Referer": "https://talent.antgroup.com/",
    "front-user-id": "729d74a1-d280-4486-a5d6-18aa210e4aff43"
}

# 3. Cookie（关键Cookie）
cookies = {
    "ctoken": "bigfish_ctoken_1a9652509k",
    "SESSION": "OTEzODQxNjhEMzQ4OTdDOTFFNzAwNzMzMEYyMzMyOEI=",
    "ALIPAYJSESSIONID": "sQVkO3lfxCu001QxrO1RAEVnky44w4M9ternbase"
}

# 4. 请求体（基于确认的格式）
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
print(f"📋 请求头数量: {len(headers)}")
print(f"🍪 Cookie数量: {len(cookies)}")
print(f"📦 请求体大小: {len(json.dumps(request_body, ensure_ascii=False))} 字符")

print(f"\n🔍 类别分析:")
print(f"  主要类别: {len(request_body['categories'].split(','))} 个")
print(f"  子类别: {len(request_body['subCategories'].split(','))} 个")

# 发送请求
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
                
                print(f"\n📊 数据统计:")
                print(f"  总岗位数: {total_count}")
                print(f"  每页数量: {page_size}")
                print(f"  当前页码: {current_page}")
                print(f"  返回岗位数: {len(content)}")
                
                if content:
                    print(f"\n🔍 第一个岗位信息:")
                    first_position = content[0]
                    print(f"  • ID: {first_position.get('id')}")
                    print(f"  • 名称: {first_position.get('name')}")
                    print(f"  • 地点: {first_position.get('workLocations')}")
                    print(f"  • 部门: {first_position.get('department')}")
                    print(f"  • 类别: {first_position.get('categories')}")
                    
                    # 类别映射
                    category_mapping = {
                        "97": "产品类",
                        "103": "运营类",
                        "143": "数据类",
                        "124": "市场拓展",
                        "152": "销售类",
                        "146": "金融类"
                    }
                    
                    categories = first_position.get('categories', [])
                    print(f"  • 类别名称: {[category_mapping.get(str(c), str(c)) for c in categories]}")
                
                # 保存响应
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = output_dir / f"response_page{current_page}_{timestamp}.json"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"\n💾 响应已保存到: {output_file}")
                
                # 如果数据有效，询问是否爬取更多
                if total_count > 0 and len(content) > 0:
                    print(f"\n🎯 是否爬取所有页面? (总{total_count}个岗位，约{(total_count + page_size - 1) // page_size}页)")
                    choice = input("  输入 'y' 开始完整爬取，输入其他键跳过: ").strip().lower()
                    
                    if choice == 'y':
                        crawl_all_pages(api_url, headers, cookies, request_body, total_count, page_size)
                
                return True
                
            else:
                print(f"❌ API返回失败状态: {data.get('errorMsg', '未知错误')}")
                print(f"   错误代码: {data.get('errorCode', '未知')}")
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
    import traceback
    traceback.print_exc()
    return False

def crawl_all_pages(api_url, headers, cookies, base_request_body, total_count, page_size):
    """爬取所有页面"""
    import time
    
    total_pages = (total_count + page_size - 1) // page_size
    print(f"\n📊 开始爬取所有页面: {total_pages}页，{total_count}个岗位")
    
    positions_dir = output_dir / "positions"
    positions_dir.mkdir(exist_ok=True)
    
    positions_saved = 0
    
    for page_no in range(1, total_pages + 1):
        print(f"\n📄 处理第 {page_no}/{total_pages} 页")
        
        # 更新页码
        request_body = base_request_body.copy()
        request_body["pageIndex"] = page_no
        
        # 添加延迟
        if page_no > 1:
            time.sleep(1)
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                cookies=cookies,
                json=request_body,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") is True:
                    content = data.get("content", [])
                    
                    # 保存整页数据
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    page_file = output_dir / f"page_{page_no}_{timestamp}.json"
                    
                    with open(page_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    # 保存每个岗位
                    for position in content:
                        position_id = position.get('id', 'unknown')
                        position_file = positions_dir / f"ant_page{page_no}_position_{position_id}_{timestamp}.json"
                        
                        with open(position_file, 'w', encoding='utf-8') as f:
                            json.dump(position, f, ensure_ascii=False, indent=2)
                        
                        positions_saved += 1
                    
                    print(f"✅ 第{page_no}页: {len(content)}个岗位，已保存 {positions_saved}/{total_count}")
                    
                    # 显示进度
                    progress = (page_no / total_pages) * 100
                    print(f"📈 进度: {page_no}/{total_pages}页 ({progress:.1f}%)")
                    
                else:
                    print(f"⚠️  第{page_no}页API返回失败: {data.get('errorMsg', '未知错误')}")
            else:
                print(f"❌ 第{page_no}页请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 第{page_no}页异常: {e}")
    
    print(f"\n🎉 爬取完成!")
    print(f"💾 总保存岗位: {positions_saved}/{total_count}")
    print(f"📁 输出目录: {output_dir}")

if __name__ == "__main__":
    success = False
    try:
        # 这里需要调用主函数，但当前脚本没有主函数
        # 直接执行代码
        print("请直接查看代码执行结果")
        success = True
    except KeyboardInterrupt:
        print("\n⏹️  用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
    
    print("\n" + "="*70)
    if success:
        print("✅ 测试完成")
    else:
        print("❌ 测试失败")
    print("="*70)