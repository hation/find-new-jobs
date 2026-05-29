#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终PDD爬取器 - 成功获取数据并导出Excel
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime

def main():
    print("🚀 PDD岗位数据爬取 - 最终版本")
    print("="*60)
    
    # 使用您提供的anti_content
    anti_content = "0aqWfxUkM_VegaLQeEi6XnDAVD1OIVUYtueGzwqpFKt5IJyiknd5jfd5bHj4-fpySTqFxfYnKHyFolYimTqFbKkKOxSXE_eaG8sYvTQ8n0wYlGwqlYvaOYuyOUpvcCwJlYpxnd9aOGnYnVOKngZPS1fTFl5k7k-PEcsI7iRz7kQdItRIkL2VKkoeSfMEF-RueDjVMAWp7IQ9-29adiePvG2y40Wy0dWEsT2OD9VfYvNluFrOydCjlZuYiZnwuTmPNdE_yuZfYnrzugildFrEjT2QDnKTYAzJi0gwON92274ginp5YtZ7ZKyPV1qGEPtyHJq0sqYPV1dg5TqbjQA6gyuubOGogJ0tyYNgNcYdCnHLUIPzU-2sZkwLvM1QvEstvkkRE11IkSsBDzLqESLtxMJnurYRLUbr9P09g5AATFS21GCX"
    
    base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
    
    # 在请求头中添加Anti-Content
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
        "Sec-Ch-Ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=1, i",
        "Cookie": "_nano_fp=Xpm8lpgJn0EjXqdaXo_eBA4AmspK5Wx4Oawm5ox~",
        "Anti-Content": anti_content  # 关键：在请求头中添加
    }
    
    # 创建输出目录
    output_dir = "output/pdd_final"
    os.makedirs(output_dir, exist_ok=True)
    
    def fetch_page(page=1, page_size=10):
        """获取单页数据"""
        # 简单的请求载荷
        payload = {
            "page": page,
            "pageSize": page_size
        }
        
        try:
            print(f"📥 获取第 {page} 页数据...")
            
            response = requests.post(
                base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ HTTP错误: {response.status_code}")
                return None
            
            # 解析响应
            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"❌ JSON解析失败")
                return None
            
            # 检查成功标志
            if not data.get("success", False):
                error_code = data.get("errorCode")
                error_msg = data.get("errorMsg", "未知错误")
                print(f"❌ API错误: {error_code} - {error_msg}")
                return None
            
            # 提取数据
            result = data.get("result", {})
            positions = result.get("list", [])
            total = result.get("total", 0)
            
            print(f"   ✅ 成功获取 {len(positions)} 条数据，总计 {total} 条")
            
            if positions:
                first = positions[0]
                print(f"   📋 示例: {first.get('name', 'N/A')} - {first.get('workLocation', 'N/A')}")
            
            return {
                "page": page,
                "page_size": page_size,
                "total": total,
                "positions": positions,
                "raw_response": data
            }
            
        except Exception as e:
            print(f"❌ 获取第 {page} 页失败: {e}")
            return None
    
    # 开始爬取
    print("\n🔍 开始爬取数据...")
    start_time = time.time()
    
    # 获取第一页
    first_page = fetch_page(1)
    
    if not first_page:
        print("❌ 获取第一页失败")
        return
    
    # 修复类型错误：确保total和page_size是整数
    total_positions = int(first_page["total"])
    page_size = int(first_page["page_size"])
    total_pages = (total_positions + page_size - 1) // page_size
    
    print(f"\n📊 数据统计:")
    print(f"   总岗位数: {total_positions}")
    print(f"   每页大小: {page_size}")
    print(f"   总页数: {total_pages}")
    
    # 收集所有数据
    all_positions = first_page["positions"]
    
    # 决定爬取多少页
    print("\n📄 请选择爬取策略:")
    print("   1. 快速测试 (爬取3页)")
    print("   2. 完整爬取 (爬取所有页，共{total_pages}页)")
    print("   3. 自定义页数")
    
    choice = input("\n请选择 (1/2/3, 默认1): ").strip() or "1"
    
    if choice == "1":
        pages_to_fetch = min(total_pages, 3)
        print(f"✅ 选择快速测试，爬取 {pages_to_fetch} 页")
    elif choice == "2":
        pages_to_fetch = total_pages
        print(f"✅ 选择完整爬取，爬取 {pages_to_fetch} 页")
    else:
        try:
            custom_pages = int(input("请输入要爬取的页数: "))
            pages_to_fetch = min(total_pages, max(1, custom_pages))
            print(f"✅ 选择自定义爬取，爬取 {pages_to_fetch} 页")
        except:
            pages_to_fetch = min(total_pages, 3)
            print(f"⚠️ 输入无效，使用默认3页")
    
    # 获取剩余页
    for page in range(2, pages_to_fetch + 1):
        print(f"\n📥 获取第 {page}/{pages_to_fetch} 页...")
        
        page_data = fetch_page(page)
        if page_data:
            all_positions.extend(page_data["positions"])
        else:
            print(f"⚠️ 第 {page} 页获取失败，跳过")
        
        # 避免请求过快
        time.sleep(0.5)
    
    elapsed_time = time.time() - start_time
    print(f"\n✅ 数据获取完成!")
    print(f"   共获取 {len(all_positions)} 条记录")
    print(f"   用时: {elapsed_time:.2f} 秒")
    
    if not all_positions:
        print("❌ 没有获取到数据")
        return
    
    # 处理数据
    print("\n🔧 处理数据...")
    processed_data = []
    
    for pos in all_positions:
        processed_pos = {
            "岗位ID": pos.get("code", ""),
            "岗位名称": pos.get("name", ""),
            "工作地点": pos.get("workLocation", ""),
            "岗位类别": pos.get("job", ""),
            "更新时间": pos.get("updateTime", ""),
            "更新时间戳": pos.get("updateDate", 0),
            "详情页URL": f"https://careers.pddglobalhr.com/jobs/{pos.get('code', '')}",
            "爬取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        processed_data.append(processed_pos)
    
    print(f"✅ 数据处理完成，共 {len(processed_data)} 条记录")
    
    # 导出到Excel
    print("\n📤 导出数据到Excel...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"pdd_positions_{timestamp}.xlsx"
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
            
            # 数据摘要
            time_stats = pd.DataFrame({
                '统计项': ['总记录数', '唯一岗位ID数', '数据源', '爬取时间'],
                '数值': [len(df), df['岗位ID'].nunique(), '拼多多招聘网站', timestamp]
            })
            time_stats.to_excel(writer, sheet_name='数据摘要', index=False)
        
        file_size = os.path.getsize(excel_filepath)
        print(f"✅ Excel导出成功！")
        print(f"\n📊 导出结果:")
        print(f"   文件: {excel_filepath}")
        print(f"   大小: {file_size:,} 字节")
        print(f"   记录数: {len(processed_data)} 条")
        print(f"   工作表: 所有岗位、地点分布、类别分布、数据摘要")
        
        # 显示数据预览
        print(f"\n📋 数据预览:")
        print(df[['岗位名称', '工作地点', '岗位类别']].head(5).to_string(index=False))
        
        # 导出到JSON
        json_filename = f"pdd_positions_{timestamp}.json"
        json_filepath = os.path.join(output_dir, json_filename)
        
        export_data = {
            "export_info": {
                "export_time": datetime.now().isoformat(),
                "total_records": len(processed_data),
                "format": "json",
                "version": "1.0",
                "data_source": "拼多多招聘网站",
                "crawl_method": "API with Anti-Content header"
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
            "pages_crawled": pages_to_fetch,
            "total_pages_available": total_pages,
            "excel_file": excel_filepath,
            "json_file": json_filepath,
            "output_directory": output_dir,
            "elapsed_time_seconds": elapsed_time,
            "method_used": "Anti-Content in request header",
            "anti_content_length": len(anti_content)
        }
        
        report_file = os.path.join(output_dir, "crawl_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告: {report_file}")
        print(f"\n🎯 任务完成！Excel文档已生成: {excel_filepath}")
        
        # 显示统计信息
        print(f"\n📈 数据统计:")
        print(f"   总岗位数: {total_positions}")
        print(f"   已爬取: {len(processed_data)} 条 ({pages_to_fetch}/{total_pages} 页)")
        print(f"   工作地点分布: {df['工作地点'].nunique()} 个不同地点")
        print(f"   岗位类别: {df['岗位类别'].nunique()} 个不同类别")
        print(f"   爬取用时: {elapsed_time:.2f} 秒")
        
    except Exception as e:
        print(f"❌ Excel导出失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()