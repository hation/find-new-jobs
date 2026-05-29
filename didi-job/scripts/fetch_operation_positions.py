#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按照用户提供的请求数据获取滴滴运营岗位
完全按照提供的请求参数和头信息
"""

import json
import requests
from datetime import datetime

def fetch_operation_positions():
    """按照用户提供的请求数据获取运营岗位"""
    
    print("🚀 按照用户提供的请求数据获取滴滴运营岗位")
    print("=" * 60)
    
    # 完全按照用户提供的请求数据
    url = "https://talent.didiglobal.com/recruit-portal-service/api/job/front/list"
    params = {
        "jobType": 5,        # 运营岗位类型
        "page": 1,           # 第1页
        "recruitType": 1,    # 常规招聘
        "size": 16           # 每页16个
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "https://talent.didiglobal.com/social/list/1?jobType=5",
        "Origin": "https://talent.didiglobal.com",
        "Sec-Ch-Ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Priority": "u=1, i"
    }
    
    cookies = {
        "_OMGID": "ec27041c-eb2d-4492-b532-8ec163593281",
        "language": "zh_cn",
        "SESSION": "1841c93d-6134-4802-9e94-c33567821687"
    }
    
    print(f"📡 请求URL: {url}")
    print(f"📋 请求参数: {json.dumps(params, ensure_ascii=False)}")
    print(f"🍪 Cookie: {json.dumps(cookies, ensure_ascii=False)}")
    print(f"📄 Referer: {headers.get('Referer')}")
    print("-" * 60)
    
    try:
        # 发送请求
        response = requests.get(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=30
        )
        
        print(f"✅ 请求成功!")
        print(f"📊 状态码: {response.status_code}")
        print(f"⏰ 响应时间: {response.elapsed.total_seconds():.2f}秒")
        
        # 检查响应头
        print(f"\n📋 响应头信息:")
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'date', 'via', 'x-application-context', 'x-ratelimit-remaining-second']:
                print(f"  • {key}: {value}")
        
        # 解析JSON响应
        result = response.json()
        
        # 检查API响应状态
        meta = result.get("meta", {})
        if meta.get("code") == 0:
            print(f"\n🎉 API响应成功!")
        else:
            print(f"\n❌ API响应错误: {meta.get('message', '未知错误')}")
        
        # 提取数据
        data = result.get("data", {})
        total = data.get("total", 0)
        positions = data.get("items", [])
        
        print(f"\n📊 数据统计:")
        print(f"  • 总岗位数: {total}")
        print(f"  • 本页岗位数: {len(positions)}")
        print(f"  • 总页数: {max(1, (total + 15) // 16)}")  # 向上取整
        
        if positions:
            print(f"\n📋 第1页运营岗位列表:")
            for i, pos in enumerate(positions, 1):
                jd_id = pos.get("jdId", "")
                jd_no = pos.get("jdNo", "")
                job_name = pos.get("jobName", "")
                work_area = pos.get("workArea", "")
                dept_name = pos.get("deptName", "")
                create_time = pos.get("createTime", "")
                
                print(f"{i:2d}. {job_name} ({jd_no})")
                print(f"    地点: {work_area}, 部门: {dept_name}")
                print(f"    创建时间: {create_time}, ID: {jd_id}")
                print()
            
            # 保存数据
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"output/didi_operation_page1_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "meta": meta,
                    "data": data,
                    "request_info": {
                        "url": url,
                        "params": params,
                        "timestamp": timestamp
                    }
                }, f, ensure_ascii=False, indent=2)
            
            print(f"💾 数据已保存到: {output_file}")
            
            # 分析岗位类型
            print(f"\n🔍 运营岗位分析:")
            job_names = [p.get("jobName", "") for p in positions]
            
            # 统计关键词
            keywords = ['运营', '市场', '营销', '增长', '活动', '社区', '内容', '用户', '产品']
            keyword_counts = {}
            
            for name in job_names:
                for keyword in keywords:
                    if keyword in name:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            print(f"  岗位关键词分布:")
            for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"    • {keyword}: {count}个 ({count/len(positions)*100:.1f}%)")
        
        else:
            print("📭 本页没有运营岗位数据")
            
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        print(f"📄 响应内容前500字符: {response.text[:500]}")
        return None
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        return None

def fetch_all_pages(max_pages=10):
    """获取所有页的运营岗位数据"""
    print(f"\n🚀 开始获取所有页的运营岗位数据 (最多{max_pages}页)")
    print("=" * 60)
    
    all_positions = []
    
    for page in range(1, max_pages + 1):
        print(f"\n📄 正在获取第 {page} 页...")
        
        # 构建请求
        url = "https://talent.didiglobal.com/recruit-portal-service/api/job/front/list"
        params = {
            "jobType": 5,
            "page": page,
            "recruitType": 1,
            "size": 16
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": f"https://talent.didiglobal.com/social/list/1?jobType=5",
        }
        
        cookies = {
            "_OMGID": "ec27041c-eb2d-4492-b532-8ec163593281",
            "language": "zh_cn",
            "SESSION": "1841c93d-6134-4802-9e94-c33567821687"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, cookies=cookies, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("meta", {}).get("code") != 0:
                print(f"❌ 第{page}页API错误: {result.get('meta', {}).get('message', '未知错误')}")
                break
            
            data = result.get("data", {})
            positions = data.get("items", [])
            total = data.get("total", 0)
            
            if not positions:
                print(f"📭 第{page}页没有数据，停止爬取")
                break
            
            all_positions.extend(positions)
            
            print(f"✅ 第{page}页获取成功: {len(positions)}个岗位")
            print(f"📊 累计: {len(all_positions)}/{total} ({len(all_positions)/total*100:.1f}%)")
            
            # 添加延迟
            import time
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ 第{page}页获取失败: {e}")
            break
    
    print(f"\n🎉 所有页获取完成!")
    print(f"📊 总获取岗位数: {len(all_positions)}")
    
    if all_positions:
        # 保存所有数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output/didi_operation_all_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_positions": len(all_positions),
                "positions": all_positions,
                "timestamp": timestamp
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 所有数据已保存到: {output_file}")
        
        # 生成统计报告
        print(f"\n📈 运营岗位统计报告:")
        print(f"  • 总岗位数: {len(all_positions)}")
        
        # 工作地点分布
        locations = {}
        for pos in all_positions:
            location = pos.get("workArea", "未知")
            locations[location] = locations.get(location, 0) + 1
        
        print(f"  • 工作地点分布:")
        for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True):
            print(f"    • {location}: {count}个 ({count/len(all_positions)*100:.1f}%)")
        
        # 部门分布
        departments = {}
        for pos in all_positions:
            dept = pos.get("deptName", "未知")
            departments[dept] = departments.get(dept, 0) + 1
        
        print(f"  • 热门部门 (Top 10):")
        for dept, count in sorted(departments.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"    • {dept}: {count}个")
    
    return all_positions

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        fetch_all_pages(max_pages=10)
    else:
        fetch_operation_positions()