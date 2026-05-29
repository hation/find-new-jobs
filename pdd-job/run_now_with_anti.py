#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
立即运行 - 使用新参数和大pageSize
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime

def main():
    print("🚀 立即运行大页PDD爬取器")
    print("="*70)
    
    # 使用您18:45提供的新参数
    anti_content = "0aqWfxUkMwVegarobC3nQXZAKmpYfWkCrgYYB03qcY9am461k7-FbQZGOcd-Idu02ik3HtubM0bqUtQ3wbJVbvtwF-fTmBvoS3qe-sID-BxEFst_S1lC-f5pFDwESfRHS37C-PxT3p3HfNl4r5JO6SPBkODM-5DM2IkBwFm7sIeBlKDM1cmM15eMwcDMZMD20TbwgToq7APHXqOGBqKtQEnHNHXqdSdnidYdn0apdYlY4ofGNLavo0XtySndT9ttQV6tyTKB2HgB3HBM8OIl2ed3t_B1qk3k3mKMxImLxMmt7ZbWbpbRhVK3BwM1qIb1qkS38OIlBud3WWMLZhD7lVkVt24uBfDe-gMvgh0wFw2HFvlTm1ESKsHvFwZ_MfgCSqIFLlfe83xVmA1WP7fC8f3HM-Rwvy6y_1EXM3USlCo1Wx8VTg9kr3ysquBFcNz"
    
    base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
    
    # 测试不同的pageSize
    test_sizes = [10, 20, 50, 100, 200]
    
    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Origin": "https://careers.pddglobalhr.com",
        "Referer": "https://careers.pddglobalhr.com/jobs",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Cookie": "_nano_fp=Xpm8lpgJn0EjXqdaXo_eBA4AmspK5Wx4Oawm5ox~"
    }
    
    # 创建输出目录
    output_dir = "output/pdd_optimized"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📝 参数信息:")
    print(f"   获取时间: 18:45 GMT+8")
    print(f"   参数长度: {len(anti_content)} 字符")
    print(f"   参数: {anti_content[:50]}...")
    
    # 测试最佳pageSize
    print(f"\n🔬 测试最佳pageSize...")
    
    optimal_size = 10  # 默认值
    max_supported = 10
    
    for size in test_sizes:
        print(f"   测试 pageSize={size}...")
        
        payload = {
            "job": "",
            "page": 1,
            "pageSize": size,
            "name": "",
            "workLocationList": [],
            "anti_content": anti_content
        }
        
        try:
            response = requests.post(base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    positions = data.get("result", {}).get("list", [])
                    total = data.get("result", {}).get("total", 0)
                    
                    print(f"      ✅ 成功: {len(positions)} 条，总计 {total} 条")
                    
                    if len(positions) == size:
                        optimal_size = size
                        max_supported = size
                        print(f"      🎯 支持 {size} 条/页")
                    else:
                        print(f"      ⚠️  实际返回 {len(positions)} 条，可能达到上限")
                        break
                else:
                    error_code = data.get("errorCode")
                    error_msg = data.get("errorMsg", "未知错误")
                    print(f"      ❌ API错误: {error_code} - {error_msg}")
                    break
            else:
                print(f"      ❌ HTTP错误: {response.status_code}")
                break
                
        except Exception as e:
            print(f"      ❌ 异常: {e}")
            break
        
        time.sleep(1)  # 避免请求过快
    
    print(f"\n🎯 确定最佳pageSize: {optimal_size} 条/页")
    print(f"   最大支持: {max_supported} 条/页")
    
    # 开始爬取所有数据
    print(f"\n🚀 开始爬取所有数据 (每页{optimal_size}条)...")
    start_time = time.time()
    
    all_positions = []
    current_page = 1
    total_positions = 0
    
    while True:
        print(f"\n📄 获取第{current_page}页...")
        
        payload = {
            "job": "",
            "page": current_page,
            "pageSize": optimal_size,
            "name": "",
            "workLocationList": [],
            "anti_content": anti_content
        }
        
        try:
            response = requests.post(base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ HTTP错误: {response.status_code}")
                break
            
            data = response.json()
            
            if not data.get("success", False):
                error_code = data.get("errorCode")
                error_msg = data.get("errorMsg", "未知错误")
                print(f"❌ API错误: {error_code} - {error_msg}")
                break
            
            result = data.get("result", {})
            positions = result.get("list", [])
            total = result.get("total", 0)
            
            if not positions:
                print(f"✅ 没有更多数据，爬取完成")
                break
            
            print(f"   ✅ 成功获取 {len(positions)} 条数据")
            all_positions.extend(positions)
            
            # 第一次请求获取总数
            if current_page == 1:
                total_positions = total
                print(f"   📊 总岗位数: {total_positions}")
                estimated_pages = (total_positions + optimal_size - 1) // optimal_size
                print(f"   📈 预计总页数: {estimated_pages}")
            
            # 显示进度
            progress = len(all_positions) / total_positions * 100 if total_positions > 0 else 0
            print(f"   📊 进度: {len(all_positions)}/{total_positions} ({progress:.1f}%)")
            
            # 检查是否已获取所有数据
            if len(positions) < optimal_size:
                print(f"✅ 已获取所有数据，爬取完成")
                break
            
            # 检查是否已达到总数
            if len(all_positions) >= total_positions:
                print(f"✅ 已达到总数据量，爬取完成")
                break
            
            current_page += 1
            
            # 页间延迟
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ 获取失败: {e}")
            break
    
    elapsed_time = time.time() - start_time
    print(f"\n✅ 数据获取完成!")
    print(f"   共获取 {len(all_positions)} 条记录")
    print(f"   请求次数: {current_page} 次")
    print(f"   用时: {elapsed_time:.2f} 秒")
    
    if not all_positions:
        print("❌ 没有获取到数据")
        return
    
    # 处理数据
    print(f"\n🔧 处理数据...")
    processed_data = []
    
    for pos in all_positions:
        processed_data.append({
            "岗位ID": pos.get("code", ""),
            "岗位名称": pos.get("name", ""),
            "工作地点": pos.get("workLocation", ""),
            "岗位类别": pos.get("job", ""),
            "更新时间": pos.get("updateTime", ""),
            "更新时间戳": pos.get("updateDate", 0),
            "详情页URL": f"https://careers.pddglobalhr.com/jobs/{pos.get('code', '')}",
            "爬取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    print(f"✅ 数据处理完成，共 {len(processed_data)} 条记录")
    
    # 导出到Excel
    print(f"\n📤 导出数据到Excel...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"pdd_optimized_{timestamp}.xlsx"
    excel_filepath = os.path.join(output_dir, excel_filename)
    
    try:
        df = pd.DataFrame(processed_data)
        
        with pd.ExcelWriter(excel_filepath, engine='openpyxl') as writer:
            # 主数据表
            df.to_excel(writer, sheet_name='所有岗位', index=False)
            
            # 统计表
            if '工作地点' in df.columns:
                location_stats = df['工作地点'].value_counts().reset_index()
                location_stats.columns = ['工作地点', '岗位数量']
                location_stats.to_excel(writer, sheet_name='地点分布', index=False)
            
            if '岗位类别' in df.columns:
                category_stats = df['岗位类别'].value_counts().reset_index()
                category_stats.columns = ['岗位类别', '岗位数量']
                category_stats.to_excel(writer, sheet_name='类别分布', index=False)
            
            # 爬取统计
            crawl_stats_data = {
                '统计项': ['总记录数', '唯一岗位ID数', '每页大小', '请求次数', '爬取用时', '数据源', '参数获取时间'],
                '数值': [len(df), df['岗位ID'].nunique(), optimal_size, current_page, 
                       f"{elapsed_time:.2f}秒", '拼多多招聘网站', '2026-05-22 18:45 GMT+8']
            }
            crawl_stats = pd.DataFrame(crawl_stats_data)
            crawl_stats.to_excel(writer, sheet_name='爬取统计', index=False)
            
            # 效率对比
            if optimal_size > 10:
                traditional_requests = (len(df) + 9) // 10  # 传统方式请求次数
                optimized_requests = current_page  # 优化方式请求次数
                
                if traditional_requests > 0:
                    reduction = (traditional_requests - optimized_requests) / traditional_requests * 100
                    
                    efficiency_data = {
                        '对比项': ['传统方式(10条/页)', '优化方式(优化后)', '效率提升'],
                        '每页大小': ['10条', f'{optimal_size}条', f'增加{optimal_size/10:.1f}倍'],
                        '请求次数': [f'{traditional_requests}次', f'{optimized_requests}次', f'减少{reduction:.1f}%'],
                        '预计用时': [f'约{traditional_requests*2}秒', f'{elapsed_time:.1f}秒', f'减少{max(0, (traditional_requests*2 - elapsed_time)/(traditional_requests*2)*100):.1f}%']
                    }
                    
                    efficiency_df = pd.DataFrame(efficiency_data)
                    efficiency_df.to_excel(writer, sheet_name='效率对比', index=False)
        
        file_size = os.path.getsize(excel_filepath)
        print(f"✅ Excel导出成功!")
        print(f"\n📊 导出结果:")
        print(f"   文件: {excel_filepath}")
        print(f"   大小: {file_size:,} 字节")
        print(f"   记录数: {len(processed_data)} 条")
        print(f"   工作表: 所有岗位、地点分布、类别分布、爬取统计、效率对比")
        
        # 显示数据预览
        print(f"\n📋 数据预览 (前5条):")
        for i, row in df.head(5).iterrows():
            print(f"   {i+1}. {row['岗位名称']} - {row['工作地点']}")
        
        # 导出到JSON
        json_filename = f"pdd_optimized_{timestamp}.json"
        json_filepath = os.path.join(output_dir, json_filename)
        
        export_data = {
            "export_info": {
                "export_time": datetime.now().isoformat(),
                "total_records": len(processed_data),
                "page_size_used": optimal_size,
                "requests_made": current_page,
                "elapsed_time": elapsed_time,
                "anti_content_obtained": "2026-05-22 18:45 GMT+8",
                "format": "json",
                "version": "1.0",
                "data_source": "拼多多招聘网站",
                "method": "optimized_large_page_size"
            },
            "data": processed_data
        }
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 JSON文件: {json_filepath}")
        
        # 生成报告
        report = {
            "success": True,
            "export_time": datetime.now().isoformat(),
            "total_records": len(processed_data),
            "optimal_page_size": optimal_size,
            "pages_crawled": current_page,
            "excel_file": excel_filepath,
            "json_file": json_filepath,
            "output_directory": output_dir,
            "elapsed_time_seconds": elapsed_time,
            "anti_content_info": {
                "obtained_at": "2026-05-22 18:45 GMT+8",
                "length": len(anti_content),
                "first_50_chars": anti_content[:50]
            },
            "efficiency_improvement": {
                "traditional_requests": (len(processed_data) + 9) // 10,
                "optimized_requests": current_page,
                "reduction_percent": ((len(processed_data) + 9) // 10 - current_page) / ((len(processed_data) + 9) // 10) * 100 if ((len(processed_data) + 9) // 10) > 0 else 0
            }
        }
        
        report_file = os.path.join(output_dir, "optimized_crawl_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告: {report_file}")
        
        # 显示效率对比
        print(f"\n📈 效率对比:")
        traditional = (len(processed_data) + 9) // 10
        print(f"   传统方式 (10条/页): 约{traditional}次请求")
        print(f"   优化方式 ({optimal_size}条/页): {current_page}次请求")
        
        if traditional > 0:
            reduction = (traditional - current_page) / traditional * 100
            print(f"   ✅ 请求次数减少: {reduction:.1f}%")
        
        print(f"\n🎯 任务完成！优化版Excel文档已生成: {excel_filepath}")
        
    except Exception as e:
        print(f"❌ Excel导出失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()