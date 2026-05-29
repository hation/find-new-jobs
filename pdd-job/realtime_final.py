#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时最终PDD爬取器
指导用户获取新参数并立即爬取
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime
import webbrowser
import sys

def print_header():
    """打印标题"""
    print("="*70)
    print("                🚀 PDD实时最终爬取器")
    print("="*70)
    print("\n📋 这个工具将指导您：")
    print("   1. 获取最新的anti_content参数")
    print("   2. 立即使用参数爬取数据")
    print("   3. 导出完整的Excel文档")
    print("\n💡 关键: anti_content参数有效期极短，获取后请立即使用")
    print("="*70)

def print_instructions():
    """打印详细的获取指导"""
    print("\n📖 第一步：获取新的anti_content参数")
    print("-"*70)
    print("\n请按以下步骤操作：")
    print("\n1. 🌐 打开浏览器")
    print("   访问: https://careers.pddglobalhr.com/jobs")
    
    print("\n2. 🔧 打开开发者工具")
    print("   按 F12 键")
    print("   或者: 右键点击页面 → 检查")
    
    print("\n3. 📡 转到Network选项卡")
    print("   点击顶部菜单的 'Network' 或 '网络'")
    
    print("\n4. 🔄 刷新页面")
    print("   按 F5 键刷新页面")
    print("   或者: 点击浏览器刷新按钮")
    
    print("\n5. 🔍 查找API请求")
    print("   在请求列表中查找名为 'list' 的POST请求")
    print("   注意: 请求URL是 /api/recruit/position/list")
    
    print("\n6. 📋 查看请求详情")
    print("   点击该请求")
    print("   查看 'Headers' 或 '标头' 选项卡")
    
    print("\n7. 📝 复制参数")
    print("   在 'Request Headers' 部分")
    print("   找到 'Anti-Content:' 行")
    print("   复制冒号后面的值（长字符串）")
    
    print("\n💡 参数示例:")
    print("   Anti-Content: 0aqWfxUkM_VegaLQeEi6XnDAVD1OIVUYtueGzwqpFKt5IJyikn...")
    print("   （这是一个很长的字符串，通常以'0aqW'开头）")
    print("-"*70)

def open_browser_automatically():
    """自动打开浏览器"""
    print("\n🖱️ 是否自动打开浏览器？")
    choice = input("自动打开浏览器访问拼多多招聘网站? (y/n, 默认y): ").strip().lower() or "y"
    
    if choice == "y":
        print("\n🌐 正在打开浏览器...")
        url = "https://careers.pddglobalhr.com/jobs"
        webbrowser.open(url)
        print(f"✅ 已打开: {url}")
        print("\n📝 请按照上述步骤获取anti_content参数")
        return True
    return False

def get_anti_content_from_user():
    """从用户获取参数"""
    print("\n" + "="*70)
    print("📝 第二步：输入您获取的anti_content参数")
    print("="*70)
    
    print("\n请粘贴您复制的anti_content参数值：")
    print("（直接粘贴，然后按Enter键）")
    print("\n输入示例:")
    print("   0aqWfxUkM_VegaLQeEi6XnDAVD1OIVUYtueGzwqpFKt5IJyiknd5jfd5bHj4-fpySTqFxfYnKHyFolYimTqFbKkKOxSXE_eaG8sYvTQ8n0wYlGwqlYvaOYuyOUpvcCwJlYpxnd9aOGnYnVOKngZPS1fTFl5k7k-PEcsI7iRz7kQdItRIkL2VKkoeSfMEF-RueDjVMAWp7IQ9-29adiePvG2y40Wy0dWEsT2OD9VfYvNluFrOydCjlZuYiZnwuTmPNdE_yuZfYnrzugildFrEjT2QDnKTYAzJi0gwON92274ginp5YtZ7ZKyPV1qGEPtyHJq0sqYPV1dg5TqbjQA6gyuubOGogJ0tyYNgNcYdCnHLUIPzU-2sZkwLvM1QvEstvkkRE11IkSsBDzLqESLtxMJnurYRLUbr9P09g5AATFS21GCX")
    
    anti_content = input("\n请输入anti_content参数: ").strip()
    
    if not anti_content:
        print("\n❌ 错误: 参数不能为空")
        return None
    
    if len(anti_content) < 100:
        print(f"\n⚠️ 警告: 参数长度只有 {len(anti_content)} 字符")
        print("   正常参数应该有400+字符")
        print("   您确定这是正确的参数吗？")
        
        confirm = input("继续使用此参数? (y/n): ").strip().lower()
        if confirm != "y":
            return None
    
    print(f"\n✅ 收到参数: {anti_content[:50]}...")
    print(f"   参数长度: {len(anti_content)} 字符")
    
    return anti_content

def test_parameter(anti_content):
    """测试参数有效性"""
    print("\n" + "="*70)
    print("🔍 第三步：测试参数有效性")
    print("="*70)
    
    base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
    
    # 方法1: 在请求体中使用
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
    
    payload = {
        "job": "",
        "page": 1,
        "pageSize": 10,
        "name": "",
        "workLocationList": [],
        "anti_content": anti_content
    }
    
    print("\n🧪 测试API连接...")
    start_time = time.time()
    
    try:
        response = requests.post(base_url, headers=headers, json=payload, timeout=30)
        elapsed = time.time() - start_time
        
        print(f"   响应时间: {elapsed:.2f} 秒")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ HTTP错误: {response.status_code}")
            if response.text:
                print(f"   错误信息: {response.text[:200]}")
            return False, None
        
        data = response.json()
        
        if not data.get("success", False):
            error_code = data.get("errorCode")
            error_msg = data.get("errorMsg", "未知错误")
            print(f"❌ API错误: {error_code} - {error_msg}")
            return False, None
        
        # 成功获取数据
        result = data.get("result", {})
        positions = result.get("list", [])
        total = result.get("total", 0)
        
        print(f"✅ 测试成功!")
        print(f"   获取数据: {len(positions)} 条")
        print(f"   总岗位数: {total} 条")
        
        if positions:
            first = positions[0]
            print(f"   示例: {first.get('name', 'N/A')} - {first.get('workLocation', 'N/A')}")
        
        return True, {"positions": positions, "total": total, "data": data}
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False, None

def fetch_all_pages(anti_content, max_pages=10):
    """获取所有页数据"""
    print(f"\n" + "="*70)
    print(f"📥 第四步：获取数据 (最多{max_pages}页)")
    print("="*70)
    
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
        "Cookie": "_nano_fp=Xpm8lpgJn0EjXqdaXo_eBA4AmspK5Wx4Oawm5ox~"
    }
    
    payload_template = {
        "job": "",
        "page": 1,
        "pageSize": 10,
        "name": "",
        "workLocationList": [],
        "anti_content": anti_content
    }
    
    all_positions = []
    start_time = time.time()
    
    # 先获取第一页了解总数据量
    print(f"\n📄 获取第1页...")
    payload = payload_template.copy()
    payload["page"] = 1
    
    try:
        response = requests.post(base_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ 第1页HTTP错误: {response.status_code}")
            return []
        
        data = response.json()
        
        if not data.get("success", False):
            error_code = data.get("errorCode")
            error_msg = data.get("errorMsg", "未知错误")
            print(f"❌ 第1页API错误: {error_code} - {error_msg}")
            return []
        
        result = data.get("result", {})
        positions = result.get("list", [])
        total = result.get("total", 0)
        
        print(f"   ✅ 成功: {len(positions)} 条，总计 {total} 条")
        all_positions.extend(positions)
        
        # 计算总页数
        total_pages = (int(total) + 9) // 10
        pages_to_fetch = min(total_pages, max_pages)
        
        print(f"\n📊 数据统计:")
        print(f"   总岗位数: {total}")
        print(f"   总页数: {total_pages}")
        print(f"   实际爬取: {pages_to_fetch} 页")
        
        # 获取剩余页
        for page in range(2, pages_to_fetch + 1):
            print(f"\n📄 获取第{page}/{pages_to_fetch}页...")
            
            payload = payload_template.copy()
            payload["page"] = page
            
            try:
                response = requests.post(base_url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        page_positions = data.get("result", {}).get("list", [])
                        all_positions.extend(page_positions)
                        print(f"   ✅ 成功: {len(page_positions)} 条，累计 {len(all_positions)} 条")
                    else:
                        print(f"   ⚠️ API错误，跳过此页")
                else:
                    print(f"   ⚠️ HTTP错误 {response.status_code}，跳过此页")
                    
            except Exception as e:
                print(f"   ⚠️ 异常: {e}，跳过此页")
            
            # 页间延迟
            time.sleep(1)
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ 数据获取完成!")
        print(f"   共获取 {len(all_positions)} 条记录")
        print(f"   用时: {elapsed_time:.2f} 秒")
        
        return all_positions
        
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return []

def export_to_excel(positions, output_dir="output/pdd_realtime_final"):
    """导出到Excel"""
    print(f"\n" + "="*70)
    print("📤 第五步：导出数据到Excel")
    print("="*70)
    
    if not positions:
        print("❌ 没有数据需要导出")
        return None
    
    os.makedirs(output_dir, exist_ok=True)
    
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
                '统计项': ['总记录数', '唯一岗位ID数', '数据源', '爬取方式', '爬取时间'],
                '数值': [len(df), df['岗位ID'].nunique(), '拼多多招聘网站', '实时获取参数', timestamp]
            })
            time_stats.to_excel(writer, sheet_name='数据摘要', index=False)
        
        file_size = os.path.getsize(excel_filepath)
        print(f"\n✅ Excel导出成功!")
        print(f"   文件: {excel_filepath}")
        print(f"   大小: {file_size:,} 字节")
        print(f"   记录数: {len(processed_data)} 条")
        print(f"   工作表: 所有岗位、地点分布、类别分布、数据摘要")
        
        # 显示数据预览
        print(f"\n📋 数据预览 (前10条):")
        for i, row in df.head(10).iterrows():
            print(f"   {i+1}. {row['岗位名称']} - {row['工作地点']}")
        
        return excel_filepath
        
    except Exception as e:
        print(f"❌ Excel导出失败: {e}")
        return None

def generate_report(positions, excel_file, anti_content):
    """生成报告"""
    report_dir = os.path.dirname(excel_file)
    report_file = os.path.join(report_dir, "crawl_report.json")
    
    report = {
        "success": True,
        "export_time": datetime.now().isoformat(),
        "total_records": len(positions),
        "excel_file": excel_file,
        "output_directory": report_dir,
        "anti_content_length": len(anti_content),
        "anti_content_obtained": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "method": "realtime_parameter_fetch"
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report_file

def main():
    """主函数"""
    print_header()
    
    # 打印指导
    print_instructions()
    
    # 自动打开浏览器
    open_browser_automatically()
    
    # 获取参数
    anti_content = get_anti_content_from_user()
    if not anti_content:
        print("\n❌ 未提供参数，程序退出")
        return
    
    # 测试参数
    success, test_data = test_parameter(anti_content)
    if not success:
        print("\n❌ 参数测试失败，请获取新的参数")
        return
    
    # 询问爬取页数
    print("\n📄 请输入要爬取的页数 (默认10，最大50):")
    try:
        max_pages_input = input("最大页数: ").strip()
        max_pages = int(max_pages_input) if max_pages_input else 10
        max_pages = min(max(1, max_pages), 50)  # 限制在1-50页
    except:
        print("⚠️ 输入无效，使用默认值10")
        max_pages = 10
    
    print(f"将爬取最多 {max_pages} 页数据")
    
    # 获取所有数据
    positions = fetch_all_pages(anti_content, max_pages=max_pages)
    
    if not positions:
        print("\n❌ 没有获取到数据")
        return
    
    # 导出数据
    excel_file = export_to_excel(positions)
    
    if not excel_file:
        print("\n❌ 导出失败")
        return
    
    # 生成报告
    report_file = generate_report(positions, excel_file, anti_content)
    
    # 完成报告
    print("\n" + "="*70)
    print("🎯 任务完成!")
    print("="*70)
    print(f"✅ Excel文档已成功生成: {excel_file}")
    print(f"📄 详细报告: {report_file}")
    print(f"📊 数据统计: {len(positions)} 条记录")
    print("\n📋 下一步:")
    print(f"   1. 打开Excel文件查看完整数据")
    print(f"   2. 文件包含多个工作表: 所有岗位、地点分布、类别分布、数据摘要")
    print(f"   3. 所有文件保存在: {os.path.dirname(excel_file)}/")
    print("\n💡 提示:")
    print(f"   • 这个anti_content参数现在可能已过期")
    print(f"   • 下次需要时，请重新获取新参数")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 等待用户查看结果
    print("\n" + "="*70)
    input("按Enter键退出...")