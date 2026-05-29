#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时PDD爬取器 - 指导用户获取新参数
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime
import webbrowser
import sys

def print_instructions():
    """打印获取参数的指导"""
    print("="*70)
    print("                    🚀 PDD实时爬取器")
    print("="*70)
    print("\n📋 这个工具将指导您获取最新的anti_content参数并爬取数据")
    print("\n🔍 第一步：获取新的anti_content参数")
    print("   1. 我将自动打开浏览器访问拼多多招聘网站")
    print("   2. 您需要按F12打开开发者工具")
    print("   3. 转到Network（网络）选项卡")
    print("   4. 刷新页面")
    print("   5. 找到名为'list'的POST请求")
    print("   6. 查看Request Headers（请求头）")
    print("   7. 复制'Anti-Content'头部的值")
    print("\n💡 提示：")
    print("   • 参数值类似: '0aqWfxUkM_VegaLQeEi6XnDAVD1OIVUYtueGzwqpFKt5IJyikn...'")
    print("   • 这是一个长字符串，通常以'0aqW'开头")
    print("   • 参数有效期很短，获取后请立即使用")
    
    print("\n" + "="*70)

def open_browser():
    """打开浏览器"""
    print("\n🌐 正在打开浏览器...")
    url = "https://careers.pddglobalhr.com/jobs"
    webbrowser.open(url)
    print(f"✅ 已打开: {url}")
    print("\n📝 请按照上述步骤获取anti_content参数")
    print("   完成后，请将参数值粘贴到下方")

def get_user_input():
    """获取用户输入的参数"""
    print("\n" + "-"*70)
    print("📝 请输入您获取的anti_content参数:")
    print("   (直接粘贴，然后按Enter键)")
    print("-"*70)
    
    anti_content = input("\nAnti-Content参数值: ").strip()
    
    if not anti_content:
        print("\n❌ 错误: 参数不能为空")
        return None
    
    print(f"\n✅ 收到参数: {anti_content[:50]}...")
    return anti_content

def test_connection(anti_content):
    """测试API连接"""
    print("\n🔍 测试API连接...")
    
    base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
    
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
        "Anti-Content": anti_content
    }
    
    payload = {"page": 1, "pageSize": 10}
    
    try:
        response = requests.post(base_url, headers=headers, json=payload, timeout=30)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ HTTP错误: {response.status_code}")
            if response.text:
                print(f"   错误信息: {response.text[:200]}")
            return None
        
        data = response.json()
        
        if not data.get("success", False):
            error_code = data.get("errorCode")
            error_msg = data.get("errorMsg", "未知错误")
            print(f"❌ API错误: {error_code} - {error_msg}")
            return None
        
        print(f"✅ 连接测试成功!")
        return data
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return None

def fetch_all_data(anti_content, max_pages=5):
    """获取所有数据"""
    print(f"\n📥 开始获取数据 (最多{max_pages}页)...")
    
    base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
    
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
        "Anti-Content": anti_content
    }
    
    all_positions = []
    start_time = time.time()
    
    # 获取第一页
    print("   获取第1页...")
    payload = {"page": 1, "pageSize": 10}
    
    try:
        response = requests.post(base_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ 第1页失败: HTTP {response.status_code}")
            return []
        
        data = response.json()
        
        if not data.get("success", False):
            print(f"❌ 第1页API错误")
            return []
        
        result = data.get("result", {})
        positions = result.get("list", [])
        total = result.get("total", 0)
        
        print(f"   ✅ 获取 {len(positions)} 条，总计 {total} 条")
        all_positions.extend(positions)
        
        # 计算总页数
        total_pages = (int(total) + 9) // 10
        pages_to_fetch = min(total_pages, max_pages)
        
        print(f"   📊 总页数: {total_pages}，实际爬取: {pages_to_fetch} 页")
        
        # 获取剩余页
        for page in range(2, pages_to_fetch + 1):
            print(f"   获取第{page}/{pages_to_fetch}页...")
            
            payload = {"page": page, "pageSize": 10}
            response = requests.post(base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    page_positions = data.get("result", {}).get("list", [])
                    all_positions.extend(page_positions)
                    print(f"      ✅ 获取 {len(page_positions)} 条")
                else:
                    print(f"      ⚠️ API错误，跳过")
            else:
                print(f"      ⚠️ HTTP错误，跳过")
            
            time.sleep(1)  # 避免请求过快
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ 数据获取完成!")
        print(f"   共获取 {len(all_positions)} 条记录")
        print(f"   用时: {elapsed_time:.2f} 秒")
        
        return all_positions
        
    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
        return []

def export_to_excel(positions, output_dir="output/pdd_realtime"):
    """导出到Excel"""
    if not positions:
        print("❌ 没有数据需要导出")
        return None
    
    os.makedirs(output_dir, exist_ok=True)
    
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
    
    try:
        df = pd.DataFrame(processed_data)
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
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
        
        file_size = os.path.getsize(excel_file)
        print(f"\n✅ Excel导出成功!")
        print(f"   文件: {excel_file}")
        print(f"   大小: {file_size:,} 字节")
        print(f"   记录数: {len(processed_data)} 条")
        print(f"   工作表: 所有岗位、地点分布、类别分布")
        
        # 显示数据预览
        print(f"\n📋 数据预览 (前3条):")
        for i, row in df.head(3).iterrows():
            print(f"   {i+1}. {row['岗位名称']} - {row['工作地点']}")
        
        return excel_file
        
    except Exception as e:
        print(f"❌ Excel导出失败: {e}")
        return None

def main():
    """主函数"""
    print_instructions()
    
    # 询问是否打开浏览器
    print("\n🖱️ 是否需要我自动打开浏览器？")
    open_browser_choice = input("自动打开浏览器? (y/n, 默认y): ").strip().lower() or "y"
    
    if open_browser_choice == "y":
        open_browser()
    
    # 获取用户输入的参数
    anti_content = get_user_input()
    if not anti_content:
        return
    
    # 测试连接
    test_result = test_connection(anti_content)
    if not test_result:
        print("\n❌ 连接测试失败，参数可能已过期")
        print("💡 请获取新的参数并重试")
        return
    
    # 询问爬取页数
    print("\n📄 请输入要爬取的页数 (默认3):")
    max_pages_input = input("最大页数: ").strip()
    
    try:
        max_pages = int(max_pages_input) if max_pages_input else 3
        if max_pages < 1:
            max_pages = 3
    except ValueError:
        print("⚠️ 输入无效，使用默认值3")
        max_pages = 3
    
    # 获取数据
    positions = fetch_all_data(anti_content, max_pages=max_pages)
    
    if not positions:
        print("\n❌ 没有获取到数据")
        return
    
    # 导出数据
    excel_file = export_to_excel(positions)
    
    if excel_file:
        print("\n" + "="*70)
        print("🎯 任务完成!")
        print("="*70)
        print(f"✅ Excel文档已成功生成: {excel_file}")
        print(f"\n📋 下一步:")
        print(f"   1. 打开Excel文件查看完整数据")
        print(f"   2. 文件保存在: output/pdd_realtime/")
        print(f"   3. 数据包含 {len(positions)} 条岗位记录")
        print("\n💡 提示:")
        print(f"   • 这个anti_content参数可能已过期")
        print(f"   • 下次需要时，请重新获取新参数")
        print("="*70)
    else:
        print("\n❌ 导出失败")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按Enter键退出...")