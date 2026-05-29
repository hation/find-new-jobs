#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
滴滴出行数据岗位数据爬取器
按照用户提供的请求数据获取数据岗位基础信息 (jobType=4)
"""

import json
import requests
import pandas as pd
import os
import time
import sys
from datetime import datetime
from collections import Counter

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def fetch_data_positions():
    """按照用户提供的请求数据获取数据岗位"""
    
    print("🚀 按照用户提供的请求数据获取滴滴数据岗位")
    print("=" * 60)
    
    # 完全按照用户提供的请求数据
    url = "https://talent.didiglobal.com/recruit-portal-service/api/job/front/list"
    params = {
        "jobType": 4,        # 数据岗位类型
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
        "Referer": "https://talent.didiglobal.com/social/list/1?jobType=4",
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
        print(f"  • 总数据岗位数: {total}")
        print(f"  • 本页数据岗位数: {len(positions)}")
        print(f"  • 总页数: {max(1, (total + 15) // 16)}")  # 向上取整
        
        if positions:
            print(f"\n📋 第1页数据岗位列表:")
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
            output_file = f"output/didi_data_page1_{timestamp}.json"
            
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
            print(f"\n🔍 数据岗位分析:")
            job_names = [p.get("jobName", "") for p in positions]
            
            # 统计关键词
            keywords = ['数据', '算法', '分析', '挖掘', '机器学习', 'AI', '大数据', '开发', '工程师', '科学家']
            keyword_counts = {}
            
            for name in job_names:
                for keyword in keywords:
                    if keyword in name:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            print(f"  岗位关键词分布:")
            for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"    • {keyword}: {count}个 ({count/len(positions)*100:.1f}%)")
        
        else:
            print("📭 本页没有数据岗位数据")
            
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

def fetch_all_data_pages(max_pages=20):
    """获取所有页的数据岗位数据"""
    print(f"\n🚀 开始获取所有页的数据岗位数据 (最多{max_pages}页)")
    print("=" * 60)
    
    all_positions = []
    
    for page in range(1, max_pages + 1):
        print(f"\n📄 正在获取第 {page} 页...")
        
        # 构建请求
        url = "https://talent.didiglobal.com/recruit-portal-service/api/job/front/list"
        params = {
            "jobType": 4,        # 数据岗位
            "page": page,
            "recruitType": 1,    # 常规招聘
            "size": 16
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": f"https://talent.didiglobal.com/social/list/1?jobType=4",
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
            
            print(f"✅ 第{page}页获取成功: {len(positions)}个数据岗位")
            print(f"📊 累计: {len(all_positions)}/{total} ({len(all_positions)/total*100:.1f}%)")
            
            # 添加延迟
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ 第{page}页获取失败: {e}")
            break
    
    print(f"\n🎉 所有页获取完成!")
    print(f"📊 总获取数据岗位数: {len(all_positions)}")
    
    if all_positions:
        # 保存所有数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output/didi_data_all_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_positions": len(all_positions),
                "positions": all_positions,
                "timestamp": timestamp
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 所有数据已保存到: {output_file}")
        
        # 生成统计报告
        generate_data_report(all_positions)
    
    return all_positions

def generate_data_report(positions):
    """生成数据岗位统计报告"""
    print(f"\n📈 滴滴数据岗位统计报告")
    print("=" * 60)
    
    print(f"1. 📊 基础统计:")
    print(f"   • 总数据岗位数: {len(positions)}")
    
    # 工作地点分布
    locations = {}
    for pos in positions:
        location = pos.get("workArea", "未知")
        locations[location] = locations.get(location, 0) + 1
    
    print(f"\n2. 📍 工作地点分布:")
    print(f"   • 涉及城市数: {len(locations)}个")
    print(f"   • 主要城市分布:")
    for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]:
        percentage = count / len(positions) * 100
        print(f"     • {location}: {count}个 ({percentage:.1f}%)")
    
    # 部门分布
    departments = {}
    for pos in positions:
        dept = pos.get("deptName", "未知")
        departments[dept] = departments.get(dept, 0) + 1
    
    print(f"\n3. 🏢 部门分布:")
    print(f"   • 涉及部门数: {len(departments)}个")
    print(f"   • 热门部门 (Top 10):")
    for dept, count in sorted(departments.items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = count / len(positions) * 100
        print(f"     • {dept}: {count}个 ({percentage:.1f}%)")
    
    # 岗位类型分析
    print(f"\n4. 🎯 岗位类型分析:")
    job_names = [p.get("jobName", "") for p in positions]
    
    keywords = ['数据', '算法', '分析', '挖掘', '机器学习', 'AI', '大数据', '开发', '工程师', '科学家', '分析师']
    keyword_counts = {}
    
    for name in job_names:
        for keyword in keywords:
            if keyword in name:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
        percentage = count / len(positions) * 100
        print(f"   • {keyword}: {count}个 ({percentage:.1f}%)")
    
    # 最新发布岗位
    print(f"\n5. 📅 最新发布的数据岗位 (Top 5):")
    sorted_positions = sorted(positions, key=lambda x: x.get("createTime", ""), reverse=True)
    for i, pos in enumerate(sorted_positions[:5], 1):
        job_name = pos.get("jobName", "未知")
        work_area = pos.get("workArea", "未知")
        create_time = pos.get("createTime", "未知")[:16]
        print(f"   {i}. {job_name} ({work_area}) - {create_time}")
    
    print(f"\n💡 数据岗位特点:")
    print("1. 通常需要较强的技术背景和数据分析能力")
    print("2. 岗位类型多样：数据分析师、算法工程师、数据开发等")
    print("3. 部门可能涉及技术、算法、数据科学等")
    print("4. 工作地点可能集中在技术中心（如北京、杭州）")
    print("=" * 60)

def export_data_to_excel(positions):
    """导出数据岗位数据为Excel"""
    print(f"\n📤 开始导出数据岗位数据为Excel...")
    
    if not positions:
        print("❌ 没有数据岗位数据可导出")
        return
    
    # 转换为DataFrame
    df = pd.DataFrame(positions)
    
    # 创建Excel文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_dir = "output/didi_data_excel"
    os.makedirs(excel_dir, exist_ok=True)
    
    excel_file = f"{excel_dir}/滴滴数据岗位基础信息_{timestamp}.xlsx"
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # 1. 全部数据岗位
        df.to_excel(writer, sheet_name='全部数据岗位', index=False)
        
        # 2. 数据汇总
        summary_data = {
            '统计项目': ['总数据岗位数', '工作地点数量', '部门数量', '最新发布时间', '最早发布时间'],
            '数值': [
                len(df),
                df['workArea'].nunique(),
                df['deptName'].nunique(),
                df['createTime'].max() if 'createTime' in df.columns else '未知',
                df['createTime'].min() if 'createTime' in df.columns else '未知'
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='数据汇总', index=False)
        
        # 3. 工作地点分布
        location_dist = df['workArea'].value_counts().reset_index()
        location_dist.columns = ['工作地点', '岗位数量']
        location_dist['占比'] = location_dist['岗位数量'] / len(df) * 100
        location_dist['占比'] = location_dist['占比'].round(2)
        location_dist.to_excel(writer, sheet_name='地点分布', index=False)
        
        # 4. 部门分布
        dept_dist = df['deptName'].value_counts().reset_index()
        dept_dist.columns = ['部门名称', '岗位数量']
        dept_dist['占比'] = dept_dist['岗位数量'] / len(df) * 100
        dept_dist['占比'] = dept_dist['占比'].round(2)
        dept_dist.to_excel(writer, sheet_name='部门分布', index=False)
        
        # 5. 岗位关键词分析
        job_names = df['jobName'].tolist()
        keywords = ['数据', '算法', '分析', '挖掘', '机器学习', 'AI', '大数据', '开发', '工程师', '科学家', '分析师']
        keyword_counts = {}
        
        for name in job_names:
            for keyword in keywords:
                if keyword in name:
                    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        keyword_df = pd.DataFrame(list(keyword_counts.items()), columns=['关键词', '出现次数'])
        keyword_df = keyword_df.sort_values('出现次数', ascending=False)
        keyword_df['占比'] = keyword_df['出现次数'] / len(df) * 100
        keyword_df['占比'] = keyword_df['占比'].round(2)
        keyword_df.to_excel(writer, sheet_name='关键词分析', index=False)
    
    print(f"✅ Excel文件创建成功!")
    print(f"📁 文件位置: {excel_file}")
    print(f"📏 文件大小: {os.path.getsize(excel_file)/1024:.1f} KB")
    
    return excel_file

def compare_all_position_types():
    """对比所有岗位类型的数据"""
    print(f"\n📊 滴滴所有岗位类型对比分析")
    print("=" * 60)
    
    # 岗位类型映射
    position_types = {
        "产品岗位": {"jobType": 3, "file_pattern": "didi_operation_complete_*.json"},
        "数据岗位": {"jobType": 4, "file_pattern": "didi_data_all_*.json"},
        "运营岗位": {"jobType": 5, "file_pattern": "didi_operation_complete_*.json"},
        "销售岗位": {"jobType": 6, "file_pattern": "didi_sales_all_*.json"}
    }
    
    import glob
    
    comparison_data = []
    
    for position_type, info in position_types.items():
        files = glob.glob(f"output/{info['file_pattern']}")
        if files:
            latest_file = max(files, key=os.path.getctime)
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                positions = data.get('positions', [])
                
                # 基础统计
                total = len(positions)
                locations = len(set(p.get('workArea', '') for p in positions))
                departments = len(set(p.get('deptName', '') for p in positions))
                
                # 岗位关键词
                job_names = [p.get('jobName', '') for p in positions]
                
                if position_type == "产品岗位":
                    keywords = ['产品', '经理', '专家']
                elif position_type == "数据岗位":
                    keywords = ['数据', '算法', '分析']
                elif position_type == "运营岗位":
                    keywords = ['运营', '经理', '专家']
                else:  # 销售岗位
                    keywords = ['销售', '经理', '商务']
                
                keyword_counts = {}
                for name in job_names:
                    for keyword in keywords:
                        if keyword in name:
                            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
                
                top_keyword = max(keyword_counts.items(), key=lambda x: x[1]) if keyword_counts else ('无', 0)
                
                comparison_data.append({
                    '岗位类型': position_type,
                    'jobType': info['jobType'],
                    '岗位数量': total,
                    '工作地点数': locations,
                    '部门数量': departments,
                    '主要关键词': f'{top_keyword[0]} ({top_keyword[1]}/{total})'
                })
        else:
            print(f"⚠️ 未找到{position_type}数据文件")
    
    if comparison_data:
        df_comparison = pd.DataFrame(comparison_data)
        print(df_comparison.to_string(index=False))
        
        print(f"\n💡 滴滴人才战略洞察:")
        print("1. 各岗位类型规模对比")
        print("2. 地域分布特点分析")
        print("3. 部门需求差异分析")
        print("4. 岗位能力要求特征")
    
    else:
        print("暂无足够数据进行对比分析")
    
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            # 获取所有数据岗位数据
            positions = fetch_all_data_pages(max_pages=20)
            if positions:
                excel_file = export_data_to_excel(positions)
                print(f"\n🎉 数据岗位数据获取和导出完成!")
                print(f"📁 Excel文件: {excel_file}")
        elif sys.argv[1] == "compare":
            # 对比所有岗位类型
            compare_all_position_types()
        else:
            print("用法: python fetch_data_positions.py [all|compare]")
    else:
        # 只获取第1页
        fetch_data_positions()