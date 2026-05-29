#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终解决方案：PDD招聘数据爬取
"""

import os
import sys
import json
import time
import requests
import pandas as pd
from datetime import datetime

def print_header():
    """打印标题"""
    print("="*70)
    print("                  🚀 PDD招聘数据爬取 - 最终解决方案")
    print("="*70)
    print("\n📋 这个工具将帮助您：")
    print("   1. 获取有效的anti_content参数")
    print("   2. 立即爬取所有岗位数据")
    print("   3. 导出完整的Excel文档")
    print("\n⚡ 关键: anti_content参数有效期极短，获取后请立即运行")
    print("="*70)

def get_anti_content_instruction():
    """获取参数的指导"""
    print("\n📖 第一步：获取anti_content参数")
    print("-"*70)
    print("\n请立即执行以下操作：")
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
    print("   （这是一个很长的字符串，通常以'0aqW'开头，400+字符）")
    print("-"*70)

def validate_anti_content(anti_content):
    """验证参数格式"""
    if not anti_content:
        return False, "参数为空"
    
    if len(anti_content) < 400:
        return False, f"参数长度只有{len(anti_content)}字符，正常应该400+字符"
    
    if not anti_content.startswith('0aqW'):
        return False, "参数不以'0aqW'开头"
    
    return True, "格式正确"

def test_api_connection(anti_content):
    """测试API连接"""
    print(f"\n🔍 测试API连接...")
    
    url = "https://careers.pddglobalhr.com/api/recruit/position/list"
    
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
    
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        elapsed = time.time() - start_time
        
        print(f"   响应时间: {elapsed:.2f} 秒")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ HTTP错误: {response.status_code}")
            if response.text:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                if error_data.get('errorMsg'):
                    print(f"   错误信息: {error_data['errorMsg']}")
                else:
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
        
        print(f"✅ 连接成功!")
        print(f"   获取数据: {len(positions)} 条")
        print(f"   总岗位数: {total} 条")
        
        if positions:
            first = positions[0]
            print(f"   示例: {first.get('name', 'N/A')} - {first.get('workLocation', 'N/A')}")
        
        return True, {"positions": positions, "total": total, "data": data}
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False, None

def crawl_all_data(anti_content, max_pages=50):
    """爬取所有数据"""
    print(f"\n🚀 开始爬取所有数据...")
    
    url = "https://careers.pddglobalhr.com/api/recruit/position/list"
    
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
    
    # 先获取第一页了解总数
    print(f"\n📄 获取第1页...")
    payload = payload_template.copy()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
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
        
        if not positions:
            print(f"❌ 第1页没有数据")
            return []
        
        print(f"   ✅ 成功: {len(positions)} 条")
        all_positions.extend(positions)
        
        # 计算总页数
        total_pages = (total + 9) // 10
        actual_pages = min(total_pages, max_pages)
        
        print(f"\n📊 数据统计:")
        print(f"   总岗位数: {total}")
        print(f"   总页数: {total_pages}")
        print(f"   实际爬取: {actual_pages} 页")
        
        # 获取剩余页
        for page in range(2, actual_pages + 1):
            print(f"\n📄 获取第{page}/{actual_pages}页...")
            
            payload = payload_template.copy()
            payload["page"] = page
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success", False):
                        page_positions = data.get("result", {}).get("list", [])
                        if page_positions:
                            all_positions.extend(page_positions)
                            print(f"   ✅ 成功: {len(page_positions)} 条，累计 {len(all_positions)} 条")
                        else:
                            print(f"   ⚠️ 没有数据，停止爬取")
                            break
                    else:
                        error_code = data.get("errorCode")
                        error_msg = data.get("errorMsg", "未知错误")
                        print(f"   ⚠️ API错误: {error_code} - {error_msg}")
                        print(f"   可能参数已过期，停止爬取")
                        break
                else:
                    print(f"   ⚠️ HTTP错误 {response.status_code}，停止爬取")
                    break
                    
            except Exception as e:
                print(f"   ⚠️ 异常: {e}，停止爬取")
                break
            
            # 页间延迟
            time.sleep(1)
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ 数据获取完成!")
        print(f"   共获取 {len(all_positions)} 条记录")
        print(f"   用时: {elapsed_time:.2f} 秒")
        
        return all_positions
        
    except Exception as e:
        print(f"❌ 爬取失败: {e}")
        return []

def export_to_excel(positions, anti_content):
    """导出到Excel"""
    if not positions:
        print("❌ 没有数据需要导出")
        return None
    
    # 创建输出目录
    output_dir = "output/pdd_final_result"
    os.makedirs(output_dir, exist_ok=True)
    
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
            
            # 爬取信息
            info_data = {
                '信息项': ['爬取时间', '总记录数', '唯一岗位ID数', '参数获取时间', '参数状态', '数据源'],
                '数值': [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    len(df),
                    df['岗位ID'].nunique(),
                    '即时获取',
                    '✅ 有效',
                    '拼多多招聘网站'
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
        
        # 导出到JSON
        json_filename = f"pdd_positions_{timestamp}.json"
        json_filepath = os.path.join(output_dir, json_filename)
        
        export_data = {
            "export_info": {
                "export_time": datetime.now().isoformat(),
                "total_records": len(processed_data),
                "anti_content_length": len(anti_content),
                "anti_content_prefix": anti_content[:10],
                "format": "json",
                "version": "1.0",
                "data_source": "拼多多招聘网站",
                "method": "manual_parameter_fetch"
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
            "anti_content_info": {
                "length": len(anti_content),
                "first_10_chars": anti_content[:10],
                "status": "valid_used"
            }
        }
        
        report_file = os.path.join(output_dir, "final_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告: {report_file}")
        
        return excel_filepath
        
    except Exception as e:
        print(f"❌ Excel导出失败: {e}")
        return None

def main():
    """主函数"""
    print_header()
    
    # 显示指导
    get_anti_content_instruction()
    
    # 在实际环境中，这里会有用户输入
    # 但当前环境无法交互，所以我们需要用户直接提供参数
    
    print(f"\n📝 第二步：输入您获取的anti_content参数")
    print("="*70)
    
    # 这里应该是 input()，但当前环境无法交互
    # 所以显示错误信息
    print("\n❌ 错误: 当前环境无法获取用户输入")
    print("\n💡 请按照以下方式运行:")
    print("   1. 获取新的anti_content参数")
    print("   2. 使用以下命令运行:")
    print('      python3 -c "')
    print('      import sys')
    print('      sys.path.insert(0, \".\")')
    print('      from final_solution import crawl_with_parameter')
    print(f'      crawl_with_parameter(\"您的anti_content参数\")')
    print('      "')
    
    print("\n📋 或者直接修改代码，在第200行添加您的参数")
    print("="*70)

def crawl_with_parameter(anti_content):
    """使用提供的参数爬取数据"""
    print(f"\n🚀 使用提供的参数开始爬取")
    print(f"   参数: {anti_content[:50]}...")
    print(f"   长度: {len(anti_content)} 字符")
    
    # 验证参数
    is_valid, message = validate_anti_content(anti_content)
    if not is_valid:
        print(f"❌ 参数验证失败: {message}")
        return False
    
    print(f"✅ 参数验证通过: {message}")
    
    # 测试API连接
    success, test_data = test_api_connection(anti_content)
    if not success:
        print(f"❌ API测试失败，参数可能已过期")
        return False
    
    # 爬取所有数据
    positions = crawl_all_data(anti_content, max_pages=50)
    
    if not positions:
        print(f"❌ 没有获取到数据")
        return False
    
    # 导出数据
    excel_file = export_to_excel(positions, anti_content)
    
    if not excel_file:
        print(f"❌ 导出失败")
        return False
    
    # 完成报告
    print(f"\n" + "="*70)
    print("🎯 任务完成!")
    print("="*70)
    print(f"✅ Excel文档已成功生成: {excel_file}")
    print(f"📊 数据统计: {len(positions)} 条记录")
    print(f"📁 所有文件保存在: {os.path.dirname(excel_file)}/")
    print(f"\n📋 包含文件:")
    print(f"   1. Excel文档 (.xlsx) - 包含多个工作表")
    print(f"   2. JSON数据 (.json) - 原始数据格式")
    print(f"   3. 详细报告 (.json) - 爬取统计信息")
    print("="*70)
    
    return True

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) == 2:
        # 使用命令行参数
        anti_content = sys.argv[1]
        success = crawl_with_parameter(anti_content)
        sys.exit(0 if success else 1)
    else:
        # 显示指导
        main()