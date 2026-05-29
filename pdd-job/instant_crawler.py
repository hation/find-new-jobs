#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
即时PDD爬取器 - 命令行参数版本
用法: python3 instant_crawler.py "您的anti_content参数"
"""

import os
import sys
import json
import time
import requests
import pandas as pd
from datetime import datetime

def print_usage():
    """打印使用说明"""
    print("🚀 即时PDD爬取器 - 命令行版本")
    print("="*70)
    print("\n📋 使用方法:")
    print("   1. 获取最新的anti_content参数:")
    print("      - 访问 https://careers.pddglobalhr.com/jobs")
    print("      - 按F12 → Network → 刷新页面")
    print("      - 找到'list'请求 → Headers → Request Headers")
    print("      - 复制'Anti-Content'头部的值")
    print("\n   2. 立即运行爬取器:")
    print("      python3 instant_crawler.py \"您的anti_content参数\"")
    print("\n💡 示例:")
    print('      python3 instant_crawler.py "0aqWfxUkM_VegaLQeEi6XnDAVD1OIVUYtueGzwqpFKt5IJyikn..."')
    print("\n⚡ 注意: 参数有效期极短，获取后请立即运行!")
    print("="*70)

def main(anti_content):
    """主函数"""
    print(f"\n🚀 开始即时爬取")
    print(f"   参数长度: {len(anti_content)} 字符")
    print(f"   参数: {anti_content[:50]}...")
    print(f"   开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
    
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
    output_dir = "output/pdd_instant"
    os.makedirs(output_dir, exist_ok=True)
    
    # 测试参数有效性
    print(f"\n🔍 测试参数有效性...")
    
    test_payload = {
        "job": "",
        "page": 1,
        "pageSize": 10,
        "name": "",
        "workLocationList": [],
        "anti_content": anti_content
    }
    
    try:
        response = requests.post(base_url, headers=headers, json=test_payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HTTP错误: {response.status_code}")
            if response.text:
                print(f"   错误信息: {response.text[:200]}")
            return False
        
        data = response.json()
        
        if not data.get("success", False):
            error_code = data.get("errorCode")
            error_msg = data.get("errorMsg", "未知错误")
            print(f"❌ API错误: {error_code} - {error_msg}")
            return False
        
        # 成功获取数据
        result = data.get("result", {})
        positions = result.get("list", [])
        total = result.get("total", 0)
        
        print(f"✅ 参数有效!")
        print(f"   获取数据: {len(positions)} 条")
        print(f"   总岗位数: {total} 条")
        
        if positions:
            first = positions[0]
            print(f"   示例: {first.get('name', 'N/A')} - {first.get('workLocation', 'N/A')}")
        
        # 开始爬取所有数据
        print(f"\n🚀 开始爬取所有数据...")
        start_time = time.time()
        
        all_positions = []
        current_page = 1
        max_pages = min((total + 9) // 10, 20)  # 最多20页
        
        print(f"   预计总页数: {(total + 9) // 10}")
        print(f"   实际爬取: {max_pages} 页")
        
        while current_page <= max_pages:
            print(f"\n📄 获取第{current_page}/{max_pages}页...")
            
            payload = {
                "job": "",
                "page": current_page,
                "pageSize": 10,
                "name": "",
                "workLocationList": [],
                "anti_content": anti_content
            }
            
            try:
                response = requests.post(base_url, headers=headers, json=payload, timeout=30)
                
                if response.status_code != 200:
                    print(f"   ❌ HTTP错误: {response.status_code}")
                    break
                
                data = response.json()
                
                if not data.get("success", False):
                    error_code = data.get("errorCode")
                    error_msg = data.get("errorMsg", "未知错误")
                    print(f"   ❌ API错误: {error_code} - {error_msg}")
                    break
                
                page_positions = data.get("result", {}).get("list", [])
                
                if not page_positions:
                    print(f"   ✅ 没有更多数据，爬取完成")
                    break
                
                all_positions.extend(page_positions)
                print(f"   ✅ 成功: {len(page_positions)} 条，累计 {len(all_positions)} 条")
                
                current_page += 1
                
                # 页间延迟
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ 获取失败: {e}")
                break
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ 数据获取完成!")
        print(f"   共获取 {len(all_positions)} 条记录")
        print(f"   用时: {elapsed_time:.2f} 秒")
        
        if not all_positions:
            print("❌ 没有获取到数据")
            return False
        
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
        excel_filename = f"pdd_instant_{timestamp}.xlsx"
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
                
                # 爬取信息
                info_data = {
                    '信息项': ['爬取时间', '参数获取时间', '总记录数', '请求页数', '爬取用时', '参数状态'],
                    '数值': [
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        '即时获取',
                        len(df),
                        current_page - 1,
                        f"{elapsed_time:.2f}秒",
                        '✅ 有效'
                    ]
                }
                info_df = pd.DataFrame(info_data)
                info_df.to_excel(writer, sheet_name='爬取信息', index=False)
            
            file_size = os.path.getsize(excel_filepath)
            print(f"✅ Excel导出成功!")
            print(f"\n📊 导出结果:")
            print(f"   文件: {excel_filepath}")
            print(f"   大小: {file_size:,} 字节")
            print(f"   记录数: {len(processed_data)} 条")
            print(f"   工作表: 所有岗位、地点分布、类别分布、爬取信息")
            
            # 显示数据预览
            print(f"\n📋 数据预览 (前5条):")
            for i, row in df.head(5).iterrows():
                print(f"   {i+1}. {row['岗位名称']} - {row['工作地点']}")
            
            # 生成报告
            report = {
                "success": True,
                "export_time": datetime.now().isoformat(),
                "total_records": len(processed_data),
                "pages_crawled": current_page - 1,
                "excel_file": excel_filepath,
                "output_directory": output_dir,
                "elapsed_time_seconds": elapsed_time,
                "anti_content_info": {
                    "length": len(anti_content),
                    "first_50_chars": anti_content[:50],
                    "status": "valid"
                }
            }
            
            report_file = os.path.join(output_dir, f"instant_report_{timestamp}.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"\n📄 详细报告: {report_file}")
            print(f"\n🎯 任务完成！Excel文档已生成: {excel_filepath}")
            
            return True
            
        except Exception as e:
            print(f"❌ Excel导出失败: {e}")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)
    
    # 获取参数
    anti_content = sys.argv[1].strip()
    
    if not anti_content:
        print("❌ 错误: 参数不能为空")
        print_usage()
        sys.exit(1)
    
    if len(anti_content) < 100:
        print(f"⚠️ 警告: 参数长度只有 {len(anti_content)} 字符")
        print("   正常参数应该有400+字符")
        print("   继续吗? (y/n)")
        
        # 在实际环境中这里会有input()，但当前环境无法交互
        # 所以直接继续
        print("   自动继续...")
    
    # 运行主函数
    success = main(anti_content)
    
    if success:
        print(f"\n✅ 即时爬取完成!")
        sys.exit(0)
    else:
        print(f"\n❌ 即时爬取失败")
        sys.exit(1)