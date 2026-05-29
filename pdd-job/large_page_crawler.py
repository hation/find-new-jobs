#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大页PDD爬取器 - 每页获取100条数据
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime

def main():
    print("🚀 大页PDD爬取器 - 每页100条数据")
    print("="*70)
    
    # 需要用户提供新的anti_content参数
    print("\n📝 请提供新的anti_content参数:")
    print("   1. 访问 https://careers.pddglobalhr.com/jobs")
    print("   2. 按F12 → Network → 刷新页面")
    print("   3. 找到'list'请求 → Headers → Request Headers")
    print("   4. 复制'Anti-Content'头部的值")
    print("   5. 粘贴到下方")
    print("\n💡 参数示例: 0aqWfxUkM_VegaLQeEi6XnDAVD1OIVUYtueGzwqpFKt5IJyikn...")
    print("-"*70)
    
    # 在实际环境中这里会有input()，但当前环境无法交互
    # 所以我们需要用户直接提供参数
    
    # 使用您可能提供的新参数
    # 这里留空，等待用户提供
    anti_content = ""
    
    # 如果没有提供参数，显示错误
    if not anti_content:
        print("\n❌ 错误: 需要提供anti_content参数")
        print("\n💡 请将参数粘贴在下面的代码中:")
        print('   anti_content = "您的参数在这里"')
        print("\n然后重新运行")
        return
    
    base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
    
    # 关键：使用大pageSize
    page_size = 100  # 从10增加到100
    
    # 请求头（不在请求头中使用Anti-Content）
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
    
    # 请求体中使用anti_content
    payload_template = {
        "job": "",
        "page": 1,
        "pageSize": page_size,
        "name": "",
        "workLocationList": [],
        "anti_content": anti_content
    }
    
    # 创建输出目录
    output_dir = "output/pdd_large_page"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n🔧 配置:")
    print(f"   每页大小: {page_size} 条")
    print(f"   参数长度: {len(anti_content)} 字符")
    print(f"   参数: {anti_content[:50]}...")
    
    def test_page_size():
        """测试不同的pageSize是否有效"""
        print(f"\n🔬 测试不同的pageSize...")
        
        test_sizes = [10, 20, 50, 100, 200]
        
        for size in test_sizes:
            print(f"   测试 pageSize={size}...")
            
            test_payload = payload_template.copy()
            test_payload["pageSize"] = size
            
            try:
                response = requests.post(base_url, headers=headers, json=test_payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        positions = data.get("result", {}).get("list", [])
                        total = data.get("result", {}).get("total", 0)
                        print(f"      ✅ 成功: {len(positions)} 条，总计 {total} 条")
                        
                        # 如果实际返回的数据量小于请求的pageSize，说明有上限
                        if len(positions) < size:
                            print(f"      ⚠️  注意: 实际返回 {len(positions)} 条，可能达到上限")
                            return len(positions)  # 返回实际支持的最大值
                    else:
                        print(f"      ❌ API错误")
                else:
                    print(f"      ❌ HTTP错误: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ 异常: {e}")
            
            time.sleep(1)  # 避免请求过快
        
        return page_size  # 返回默认值
    
    # 测试最佳pageSize
    optimal_page_size = test_page_size()
    print(f"\n🎯 最佳每页大小: {optimal_page_size} 条")
    
    # 开始爬取
    print(f"\n🚀 开始爬取数据 (每页{optimal_page_size}条)...")
    start_time = time.time()
    
    all_positions = []
    current_page = 1
    
    while True:
        print(f"\n📄 获取第{current_page}页 (size={optimal_page_size})...")
        
        payload = payload_template.copy()
        payload["page"] = current_page
        payload["pageSize"] = optimal_page_size
        
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
            
            # 显示进度
            if current_page == 1:
                print(f"   📊 总岗位数: {total}")
                estimated_pages = (total + optimal_page_size - 1) // optimal_page_size
                print(f"   📈 预计总页数: {estimated_pages}")
            
            # 检查是否已获取所有数据
            if len(positions) < optimal_page_size:
                print(f"✅ 已获取所有数据，爬取完成")
                break
            
            # 检查是否已达到总数
            if len(all_positions) >= total:
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
    excel_filename = f"pdd_large_page_{timestamp}.xlsx"
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
            crawl_stats = pd.DataFrame({
                '统计项': ['总记录数', '唯一岗位ID数', '每页大小', '请求次数', '爬取用时', '数据源'],
                '数值': [len(df), df['岗位ID'].nunique(), optimal_page_size, current_page, 
                       f"{elapsed_time:.2f}秒", '拼多多招聘网站']
            })
            crawl_stats.to_excel(writer, sheet_name='爬取统计', index=False)
            
            # 效率对比
            efficiency = pd.DataFrame({
                '对比项': ['传统方式(10条/页)', '优化方式(100条/页)', '效率提升'],
                '请求次数': [f"约{len(df)//10}次", f"{current_page}次", f"减少{(len(df)//10 - current_page)/(len(df)//10)*100:.1f}%"],
                '预计用时': [f"约{len(df)//10*2}秒", f"{elapsed_time:.1f}秒", f"减少{(len(df)//10*2 - elapsed_time)/(len(df)//10*2)*100:.1f}%"]
            })
            efficiency.to_excel(writer, sheet_name='效率对比', index=False)
        
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
        json_filename = f"pdd_large_page_{timestamp}.json"
        json_filepath = os.path.join(output_dir, json_filename)
        
        export_data = {
            "export_info": {
                "export_time": datetime.now().isoformat(),
                "total_records": len(processed_data),
                "page_size_used": optimal_page_size,
                "requests_made": current_page,
                "elapsed_time": elapsed_time,
                "format": "json",
                "version": "1.0",
                "data_source": "拼多多招聘网站",
                "method": "large_page_size_optimization"
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
            "optimal_page_size": optimal_page_size,
            "pages_crawled": current_page,
            "excel_file": excel_filepath,
            "json_file": json_filepath,
            "output_directory": output_dir,
            "elapsed_time_seconds": elapsed_time,
            "efficiency_improvement": {
                "traditional_requests": len(processed_data) // 10,
                "optimized_requests": current_page,
                "reduction_percent": ((len(processed_data) // 10 - current_page) / (len(processed_data) // 10) * 100) if len(processed_data) // 10 > 0 else 0
            }
        }
        
        report_file = os.path.join(output_dir, "crawl_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告: {report_file}")
        
        # 显示效率对比
        print(f"\n📈 效率对比:")
        print(f"   传统方式 (10条/页): 约{len(processed_data)//10}次请求")
        print(f"   优化方式 ({optimal_page_size}条/页): {current_page}次请求")
        if len(processed_data) // 10 > 0:
            reduction = ((len(processed_data) // 10 - current_page) / (len(processed_data) // 10) * 100)
            print(f"   ✅ 请求次数减少: {reduction:.1f}%")
        
        print(f"\n🎯 任务完成！优化版Excel文档已生成: {excel_filepath}")
        
    except Exception as e:
        print(f"❌ Excel导出失败: {e}")

if __name__ == "__main__":
    main()