#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
立即执行PDD爬取 - 使用新参数
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime

def main():
    print("🚀 立即执行PDD数据爬取")
    print("="*60)
    
    # 使用您提供的新参数
    anti_content = "0aqAfx5e-wCEQT1iEMxgWXqnSeiGgAE8iUeK4mY6-kkaiptcKqF5ij4fklUKt0E_FN1lDgSnDzSztNCf_difYNKX_A5_4N3Qjm1tYRK-46tWneQVa7mziCNeXycGPqXpdycYEanGPaXY6dnYmycpdqXGmxX5Xan9VSmPIt730XUv-ezsVLctQ7nHNHXqdMdnidYdn0apdYlY4ofGNLavo0XtyMndT9ttQC6tyTSB2HgB3HB-8OIl2Ed3t_BKqe3e3DS-xIDLx-DtzVbAbpbRhCS3Bw-KqIbKqeM38OIlBmd3AA-LVhkzlCeCt24mBfkEFg-vgh0wUw2HUvlTDK7MSsHvUwV_-fgWMqIULlfE83xCDuKAPzfW8f3H-FRwvy6y_K7X-35MlmonJ6k2TE93AecB4mBUcN1"
    
    base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
    
    # 关键：Anti-Content作为请求头
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
        "Cookie": "_nano_fp=Xpm8lpgJn0EjXqdaXo_eBA4AmspK5Wx4Oawm5ox~",
        "Anti-Content": anti_content  # 在请求头中
    }
    
    # 创建输出目录
    output_dir = "output/pdd_final_result"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n🔍 使用新参数测试连接...")
    print(f"   参数长度: {len(anti_content)} 字符")
    print(f"   参数前50位: {anti_content[:50]}...")
    
    def fetch_page(page):
        """获取单页数据"""
        payload = {"page": page, "pageSize": 10}
        
        try:
            response = requests.post(base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ 第{page}页HTTP错误: {response.status_code}")
                return None
            
            data = response.json()
            
            if not data.get("success", False):
                error_code = data.get("errorCode")
                error_msg = data.get("errorMsg", "未知错误")
                print(f"❌ 第{page}页API错误: {error_code} - {error_msg}")
                return None
            
            result = data.get("result", {})
            positions = result.get("list", [])
            total = result.get("total", 0)
            
            print(f"   ✅ 第{page}页: 获取 {len(positions)} 条，总计 {total} 条")
            
            if positions and page == 1:
                first = positions[0]
                print(f"   📋 示例: {first.get('name', 'N/A')} - {first.get('workLocation', 'N/A')}")
            
            return positions, total
            
        except Exception as e:
            print(f"❌ 第{page}页失败: {e}")
            return None
    
    # 开始爬取
    start_time = time.time()
    
    # 获取第一页
    print(f"\n📥 获取第1页数据...")
    first_result = fetch_page(1)
    
    if not first_result:
        print("❌ 获取第一页失败，参数可能已过期")
        return
    
    positions, total = first_result
    all_positions = positions
    
    # 计算总页数
    total_pages = (int(total) + 9) // 10
    
    print(f"\n📊 数据统计:")
    print(f"   总岗位数: {total}")
    print(f"   总页数: {total_pages}")
    
    # 决定爬取多少页
    pages_to_fetch = min(total_pages, 5)  # 先爬取5页
    
    print(f"   实际爬取: {pages_to_fetch} 页")
    
    # 获取剩余页
    for page in range(2, pages_to_fetch + 1):
        print(f"\n📥 获取第{page}/{pages_to_fetch}页...")
        
        result = fetch_page(page)
        if result:
            page_positions, _ = result
            all_positions.extend(page_positions)
        else:
            print(f"   ⚠️ 第{page}页失败，跳过")
        
        time.sleep(1)  # 避免请求过快
    
    elapsed_time = time.time() - start_time
    print(f"\n✅ 数据获取完成!")
    print(f"   共获取 {len(all_positions)} 条记录")
    print(f"   用时: {elapsed_time:.2f} 秒")
    
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
                '统计项': ['总记录数', '唯一岗位ID数', '数据源', '爬取时间', '参数有效期'],
                '数值': [len(df), df['岗位ID'].nunique(), '拼多多招聘网站', timestamp, '实时获取']
            })
            time_stats.to_excel(writer, sheet_name='数据摘要', index=False)
        
        file_size = os.path.getsize(excel_filepath)
        print(f"✅ Excel导出成功!")
        print(f"\n📊 导出结果:")
        print(f"   文件: {excel_filepath}")
        print(f"   大小: {file_size:,} 字节")
        print(f"   记录数: {len(processed_data)} 条")
        print(f"   工作表: 所有岗位、地点分布、类别分布、数据摘要")
        
        # 显示数据预览
        print(f"\n📋 数据预览 (前5条):")
        for i, row in df.head(5).iterrows():
            print(f"   {i+1}. {row['岗位名称']} - {row['工作地点']}")
        
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
                "crawl_method": "API with Anti-Content header",
                "anti_content_used": anti_content[:50] + "..."
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
            "anti_content_length": len(anti_content),
            "anti_content_obtained_at": "17:58 GMT+8"
        }
        
        report_file = os.path.join(output_dir, "crawl_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告: {report_file}")
        print(f"\n🎯 任务完成！Excel文档已生成: {excel_filepath}")
        
        # 显示统计信息
        print(f"\n📈 数据统计:")
        print(f"   总岗位数: {total}")
        print(f"   已爬取: {len(processed_data)} 条 ({pages_to_fetch}/{total_pages} 页)")
        print(f"   工作地点分布: {df['工作地点'].nunique()} 个不同地点")
        print(f"   岗位类别: {df['岗位类别'].nunique()} 个不同类别")
        print(f"   爬取用时: {elapsed_time:.2f} 秒")
        print(f"   参数状态: ✅ 有效 (17:58获取)")
        
    except Exception as e:
        print(f"❌ Excel导出失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()