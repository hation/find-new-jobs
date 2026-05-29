#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合PDD爬取器 - 结合多种方法获取更多数据
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime

def test_different_methods(anti_content):
    """测试不同的请求方法"""
    base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
    
    print("\n🔬 测试不同的请求方法...")
    
    # 方法1: 只在请求头中使用Anti-Content
    print("方法1: Anti-Content在请求头中")
    headers1 = {
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
        "Anti-Content": anti_content
    }
    
    payload1 = {"page": 1, "pageSize": 10}
    
    try:
        r1 = requests.post(base_url, headers=headers1, json=payload1, timeout=30)
        print(f"   第1页: 状态码 {r1.status_code}")
        
        if r1.status_code == 200:
            data = r1.json()
            if data.get("success", False):
                print(f"   ✅ 成功: {len(data.get('result', {}).get('list', []))} 条数据")
            else:
                print(f"   ❌ API错误: {data.get('errorCode')} - {data.get('errorMsg')}")
        else:
            print(f"   ❌ HTTP错误: {r1.status_code}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 方法2: 在请求体中使用anti_content
    print("\n方法2: anti_content在请求体中")
    headers2 = headers1.copy()
    headers2.pop("Anti-Content", None)  # 移除请求头中的Anti-Content
    
    payload2 = {
        "job": "",
        "page": 1,
        "pageSize": 10,
        "name": "",
        "workLocationList": [],
        "anti_content": anti_content
    }
    
    try:
        r2 = requests.post(base_url, headers=headers2, json=payload2, timeout=30)
        print(f"   第1页: 状态码 {r2.status_code}")
        
        if r2.status_code == 200:
            data = r2.json()
            if data.get("success", False):
                print(f"   ✅ 成功: {len(data.get('result', {}).get('list', []))} 条数据")
            else:
                print(f"   ❌ API错误: {data.get('errorCode')} - {data.get('errorMsg')}")
        else:
            print(f"   ❌ HTTP错误: {r2.status_code}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 方法3: 两者都用
    print("\n方法3: 请求头和请求体中都使用")
    headers3 = headers1.copy()  # 包含Anti-Content头部
    
    payload3 = payload2.copy()  # 包含anti_content字段
    
    try:
        r3 = requests.post(base_url, headers=headers3, json=payload3, timeout=30)
        print(f"   第1页: 状态码 {r3.status_code}")
        
        if r3.status_code == 200:
            data = r3.json()
            if data.get("success", False):
                print(f"   ✅ 成功: {len(data.get('result', {}).get('list', []))} 条数据")
            else:
                print(f"   ❌ API错误: {data.get('errorCode')} - {data.get('errorMsg')}")
        else:
            print(f"   ❌ HTTP错误: {r3.status_code}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")

def fetch_with_workaround(anti_content, max_pages=5):
    """使用变通方法获取数据"""
    base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
    
    all_positions = []
    
    # 基本请求头（不包含Anti-Content）
    base_headers = {
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
    
    print(f"\n🚀 开始爬取数据 (最多{max_pages}页)...")
    
    for page in range(1, max_pages + 1):
        print(f"\n📥 获取第{page}页...")
        
        # 尝试不同的参数组合
        methods = [
            # 方法A: 完整的参数（像浏览器一样）
            {
                "name": "完整参数",
                "headers": {**base_headers, "Anti-Content": anti_content},
                "payload": {"page": page, "pageSize": 10}
            },
            # 方法B: 请求体中使用
            {
                "name": "请求体参数",
                "headers": base_headers,
                "payload": {
                    "job": "",
                    "page": page,
                    "pageSize": 10,
                    "name": "",
                    "workLocationList": [],
                    "anti_content": anti_content
                }
            },
            # 方法C: 两者都用
            {
                "name": "双重参数",
                "headers": {**base_headers, "Anti-Content": anti_content},
                "payload": {
                    "job": "",
                    "page": page,
                    "pageSize": 10,
                    "name": "",
                    "workLocationList": [],
                    "anti_content": anti_content
                }
            },
            # 方法D: 简单参数
            {
                "name": "简单参数",
                "headers": base_headers,
                "payload": {"page": page, "pageSize": 10, "anti_content": anti_content}
            }
        ]
        
        success = False
        
        for method in methods:
            print(f"   尝试 {method['name']}...")
            
            try:
                response = requests.post(
                    base_url,
                    headers=method["headers"],
                    json=method["payload"],
                    timeout=30
                )
                
                print(f"     状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success", False):
                        positions = data.get("result", {}).get("list", [])
                        total = data.get("result", {}).get("total", 0)
                        
                        print(f"     ✅ 成功: {len(positions)} 条数据")
                        all_positions.extend(positions)
                        success = True
                        break
                    else:
                        error_code = data.get("errorCode")
                        error_msg = data.get("errorMsg", "未知错误")
                        print(f"     ❌ API错误: {error_code} - {error_msg}")
                else:
                    print(f"     ❌ HTTP错误: {response.status_code}")
                    
            except Exception as e:
                print(f"     ❌ 异常: {e}")
            
            # 短暂延迟
            time.sleep(0.5)
        
        if not success:
            print(f"   ⚠️ 第{page}页所有方法都失败，停止爬取")
            break
        
        # 页间延迟
        if page < max_pages:
            time.sleep(1)
    
    return all_positions

def main():
    print("🚀 混合PDD爬取器")
    print("="*60)
    
    # 使用您提供的新参数
    anti_content = "0aqAfx5e-wCEQT1iEMxgWXqnSeiGgAE8iUeK4mY6-kkaiptcKqF5ij4fklUKt0E_FN1lDgSnDzSztNCf_difYNKX_A5_4N3Qjm1tYRK-46tWneQVa7mziCNeXycGPqXpdycYEanGPaXY6dnYmycpdqXGmxX5Xan9VSmPIt730XUv-ezsVLctQ7nHNHXqdMdnidYdn0apdYlY4ofGNLavo0XtyMndT9ttQC6tyTSB2HgB3HB-8OIl2Ed3t_BKqe3e3DS-xIDLx-DtzVbAbpbRhCS3Bw-KqIbKqeM38OIlBmd3AA-LVhkzlCeCt24mBfkEFg-vgh0wUw2HUvlTDK7MSsHvUwV_-fgWMqIULlfE83xCDuKAPzfW8f3H-FRwvy6y_K7X-35MlmonJ6k2TE93AecB4mBUcN1"
    
    print(f"参数长度: {len(anti_content)} 字符")
    print(f"参数: {anti_content[:50]}...")
    
    # 测试不同方法
    test_different_methods(anti_content)
    
    # 询问爬取页数
    print("\n📄 请输入要爬取的页数 (默认5):")
    print("注意: 由于参数有效期限制，可能只能获取前几页")
    
    try:
        max_pages = 5  # 默认值
    except:
        max_pages = 5
    
    print(f"将尝试爬取 {max_pages} 页数据")
    
    # 开始爬取
    start_time = time.time()
    positions = fetch_with_workaround(anti_content, max_pages=max_pages)
    elapsed_time = time.time() - start_time
    
    print(f"\n✅ 数据获取完成!")
    print(f"   共获取 {len(positions)} 条记录")
    print(f"   用时: {elapsed_time:.2f} 秒")
    
    if not positions:
        print("❌ 没有获取到数据")
        return
    
    # 处理数据
    print(f"\n🔧 处理数据...")
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
    
    print(f"✅ 数据处理完成，共 {len(processed_data)} 条记录")
    
    # 导出到Excel
    print(f"\n📤 导出数据到Excel...")
    output_dir = "output/pdd_hybrid"
    os.makedirs(output_dir, exist_ok=True)
    
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
        
        file_size = os.path.getsize(excel_filepath)
        print(f"✅ Excel导出成功!")
        print(f"\n📊 导出结果:")
        print(f"   文件: {excel_filepath}")
        print(f"   大小: {file_size:,} 字节")
        print(f"   记录数: {len(processed_data)} 条")
        print(f"   工作表: 所有岗位、地点分布、类别分布")
        
        # 显示数据预览
        print(f"\n📋 数据预览 (前10条):")
        for i, row in df.head(10).iterrows():
            print(f"   {i+1}. {row['岗位名称']} - {row['工作地点']}")
        
        print(f"\n🎯 任务完成！Excel文档已生成: {excel_filepath}")
        
    except Exception as e:
        print(f"❌ Excel导出失败: {e}")

if __name__ == "__main__":
    main()