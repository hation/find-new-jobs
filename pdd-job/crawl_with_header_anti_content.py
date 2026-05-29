#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在请求头中使用Anti-Content的PDD爬取器
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime

def main():
    print("🚀 PDD爬取器 - 在请求头中使用Anti-Content")
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
        "Anti-Content": anti_content  # 在请求头中添加
    }
    
    # 创建输出目录
    output_dir = "output/pdd_header_approach"
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
            print(f"   请求头Anti-Content: {anti_content[:50]}...")
            print(f"   请求载荷: {json.dumps(payload, ensure_ascii=False)}")
            
            response = requests.post(
                base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ HTTP错误: {response.status_code}")
                if response.text:
                    print(f"   错误响应: {response.text[:200]}")
                return None
            
            # 解析响应
            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"❌ JSON解析失败")
                print(f"   响应内容: {response.text[:200]}")
                return None
            
            print(f"   响应键: {list(data.keys())}")
            
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
    
    # 测试第一页
    first_page = fetch_page(1)
    
    if not first_page:
        print("❌ 获取第一页失败")
        print("\n💡 可能的原因:")
        print("1. anti_content参数已过期")
        print("2. 需要在请求体中使用anti_content")
        print("3. 需要其他认证参数")
        print("\n🔄 尝试在请求体中使用anti_content...")
        
        # 尝试在请求体中使用
        payload_with_anti = {
            "page": 1,
            "pageSize": 10,
            "anti_content": anti_content
        }
        
        # 移除请求头中的Anti-Content
        headers_without_anti = headers.copy()
        headers_without_anti.pop("Anti-Content", None)
        
        print(f"   在请求体中使用anti_content")
        response = requests.post(base_url, headers=headers_without_anti, json=payload_with_anti, timeout=30)
        print(f"   状态码: {response.status_code}")
        if response.text:
            print(f"   响应: {response.text[:200]}")
        
        return
    
    # 成功获取第一页
    total_positions = first_page["total"]
    page_size = first_page["page_size"]
    total_pages = (total_positions + page_size - 1) // page_size
    
    print(f"\n📊 数据统计:")
    print(f"   总岗位数: {total_positions}")
    print(f"   每页大小: {page_size}")
    print(f"   总页数: {total_pages}")
    
    # 收集所有数据
    all_positions = first_page["positions"]
    
    # 获取更多页（先爬取3页）
    pages_to_fetch = min(total_pages, 3)
    
    for page in range(2, pages_to_fetch + 1):
        print(f"\n📥 获取第 {page}/{pages_to_fetch} 页...")
        
        page_data = fetch_page(page)
        if page_data:
            all_positions.extend(page_data["positions"])
        else:
            print(f"⚠️ 第 {page} 页获取失败，跳过")
        
        time.sleep(1)
    
    print(f"\n✅ 数据获取完成，共 {len(all_positions)} 条记录")
    
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
        
        # 保存到Excel
        df.to_excel(excel_filepath, sheet_name='所有岗位', index=False)
        
        file_size = os.path.getsize(excel_filepath)
        print(f"✅ Excel导出成功！")
        print(f"\n📊 导出结果:")
        print(f"   文件: {excel_filepath}")
        print(f"   大小: {file_size:,} 字节")
        print(f"   记录数: {len(processed_data)} 条")
        
        # 显示数据预览
        print(f"\n📋 数据预览 (前3条):")
        for i, row in df.head(3).iterrows():
            print(f"   {i+1}. {row['岗位名称']} - {row['工作地点']}")
        
        # 导出到JSON
        json_filename = f"pdd_positions_{timestamp}.json"
        json_filepath = os.path.join(output_dir, json_filename)
        
        export_data = {
            "export_info": {
                "export_time": datetime.now().isoformat(),
                "total_records": len(processed_data),
                "format": "json",
                "version": "1.0"
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
            "excel_file": excel_filepath,
            "json_file": json_filepath,
            "output_directory": output_dir,
            "method_used": "Anti-Content in header"
        }
        
        report_file = os.path.join(output_dir, "crawl_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告: {report_file}")
        print(f"\n🎯 任务完成！Excel文档已生成: {excel_filepath}")
        
    except Exception as e:
        print(f"❌ Excel导出失败: {e}")

if __name__ == "__main__":
    main()