#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速PDD爬取器 - 最简单的实现
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime

def main():
    print("🚀 快速PDD爬取器")
    print("="*60)
    
    # 使用您提供的anti_content（作为请求头）
    anti_content = "0aqWfxUkM_VegaLQeEi6XnDAVD1OIVUYtueGzwqpFKt5IJyiknd5jfd5bHj4-fpySTqFxfYnKHyFolYimTqFbKkKOxSXE_eaG8sYvTQ8n0wYlGwqlYvaOYuyOUpvcCwJlYpxnd9aOGnYnVOKngZPS1fTFl5k7k-PEcsI7iRz7kQdItRIkL2VKkoeSfMEF-RueDjVMAWp7IQ9-29adiePvG2y40Wy0dWEsT2OD9VfYvNluFrOydCjlZuYiZnwuTmPNdE_yuZfYnrzugildFrEjT2QDnKTYAzJi0gwON92274ginp5YtZ7ZKyPV1qGEPtyHJq0sqYPV1dg5TqbjQA6gyuubOGogJ0tyYNgNcYdCnHLUIPzU-2sZkwLvM1QvEstvkkRE11IkSsBDzLqESLtxMJnurYRLUbr9P09g5AATFS21GCX"
    
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
        "Sec-Ch-Ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=1, i",
        "Cookie": "_nano_fp=Xpm8lpgJn0EjXqdaXo_eBA4AmspK5Wx4Oawm5ox~",
        "Anti-Content": anti_content  # 关键：在请求头中
    }
    
    # 简单的请求载荷
    payload = {
        "page": 1,
        "pageSize": 10
    }
    
    # 创建输出目录
    output_dir = "output/pdd_quick"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n🔍 测试API连接...")
    print(f"   请求头Anti-Content: {anti_content[:50]}...")
    print(f"   Cookie: {headers['Cookie'][:50]}...")
    
    try:
        # 测试请求
        response = requests.post(
            base_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return
        
        # 解析响应
        data = response.json()
        print(f"   响应键: {list(data.keys())}")
        
        if not data.get("success", False):
            error_code = data.get("errorCode")
            error_msg = data.get("errorMsg", "未知错误")
            print(f"❌ API错误: {error_code} - {error_msg}")
            return
        
        # 成功获取数据
        result = data.get("result", {})
        positions = result.get("list", [])
        total = result.get("total", 0)
        
        print(f"✅ 成功获取 {len(positions)} 条数据，总计 {total} 条")
        
        if positions:
            first = positions[0]
            print(f"📋 示例: {first.get('name', 'N/A')} - {first.get('workLocation', 'N/A')}")
        
        # 处理数据
        processed_data = []
        for pos in positions:
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
        
        # 导出到Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = os.path.join(output_dir, f"pdd_positions_{timestamp}.xlsx")
        
        df = pd.DataFrame(processed_data)
        df.to_excel(excel_file, sheet_name='所有岗位', index=False)
        
        file_size = os.path.getsize(excel_file)
        print(f"\n✅ Excel导出成功!")
        print(f"   文件: {excel_file}")
        print(f"   大小: {file_size:,} 字节")
        print(f"   记录数: {len(processed_data)} 条")
        
        # 显示数据预览
        print(f"\n📋 数据预览:")
        for i, row in df.head(3).iterrows():
            print(f"   {i+1}. {row['岗位名称']} - {row['工作地点']}")
        
        print(f"\n🎯 任务完成！Excel文档已生成: {excel_file}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()