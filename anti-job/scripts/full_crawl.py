#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整爬取蚂蚁国际招聘所有岗位
基于已验证的API配置
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path

def main():
    print("="*70)
    print("🚀 完整爬取蚂蚁国际招聘所有岗位")
    print("="*70)
    
    project_root = Path(__file__).parent.parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = project_root / "output" / f"full_crawl_{timestamp}"
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "positions").mkdir(exist_ok=True)
    (output_dir / "pages").mkdir(exist_ok=True)
    
    print(f"📁 输出目录: {output_dir}")
    
    # API配置
    api_url = "https://hrcareersweb.antgroup.com/api/social/position/search?ctoken=bigfish_ctoken_1a9652509k"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json",
        "Origin": "https://talent.antgroup.com",
        "Referer": "https://talent.antgroup.com/",
        "front-user-id": "729d74a1-d280-4486-a5d6-18aa210e4aff43"
    }
    
    cookies = {
        "ctoken": "bigfish_ctoken_1a9652509k",
        "SESSION": "OTEzODQxNjhEMzQ4OTdDOTFFNzAwNzMzMEYyMzMyOEI="
    }
    
    # 请求体模板
    request_body_template = {
        "regions": "",
        "categories": "97,103,143,124,152,146",
        "subCategories": "97,103,143,124,152,146,98,99,100,101,102,403,404,405,406,104,105,106,107,108,109,110,111,172,474,475,476,477,478,479,480,481,482,483,484,529,757,758,759,763,834,846,847,849,144,145,177,446,447,448,125,126,127,128,129,175,445,716,812,824,825,100000015,100000016,101300030,101300031,101300032,101300033,153,154,155,156,179,461,462,463,464,465,466,467,468,469,470,471,472,473,512,513,147,148,149,150,151,178,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426",
        "bgCode": "",
        "socialQrCode": "",
        "pageSize": 10,
        "channel": "group_official_site",
        "language": "zh"
    }
    
    # 类别映射
    category_mapping = {
        "97": "产品类",
        "103": "运营类",
        "143": "数据类",
        "124": "市场拓展",
        "152": "销售类",
        "146": "金融类"
    }
    
    # 先获取第一页，了解总页数
    print(f"\n📡 获取第一页数据...")
    request_body = request_body_template.copy()
    request_body["pageIndex"] = 1
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            cookies=cookies,
            json=request_body,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ 第一页请求失败: {response.status_code}")
            return False
        
        data = response.json()
        
        if data.get("success") is not True:
            print(f"❌ API返回失败: {data.get('errorMsg', '未知错误')}")
            return False
        
        total_count = data.get("totalCount", 0)
        page_size = data.get("pageSize", 10)
        current_page = data.get("currentPage", 1)
        content = data.get("content", [])
        
        print(f"📊 总岗位数: {total_count}")
        print(f"📊 每页数量: {page_size}")
        print(f"📊 当前页码: {current_page}")
        print(f"📊 第一页岗位: {len(content)}个")
        
        if total_count == 0:
            print("⚠️  总岗位数为0，无法继续")
            return False
        
        # 计算总页数
        total_pages = (total_count + page_size - 1) // page_size
        print(f"📊 总页数: {total_pages}")
        
        # 保存第一页
        save_page_data(data, 1, output_dir)
        save_positions(content, 1, output_dir, category_mapping)
        
        # 爬取剩余页面
        positions_saved = len(content)
        failed_pages = 0
        
        print(f"\n🚀 开始爬取剩余页面...")
        
        for page_no in range(2, total_pages + 1):
            print(f"\n📄 处理第 {page_no}/{total_pages} 页")
            
            # 添加延迟
            time.sleep(1)
            
            # 更新页码
            request_body = request_body_template.copy()
            request_body["pageIndex"] = page_no
            
            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    cookies=cookies,
                    json=request_body,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success") is True:
                        content = data.get("content", [])
                        
                        # 保存页面数据
                        save_page_data(data, page_no, output_dir)
                        
                        # 保存岗位数据
                        page_positions = save_positions(content, page_no, output_dir, category_mapping)
                        positions_saved += page_positions
                        
                        print(f"✅ 第{page_no}页: {len(content)}个岗位，累计{positions_saved}/{total_count}")
                    else:
                        print(f"⚠️  第{page_no}页API失败: {data.get('errorMsg', '未知错误')}")
                        failed_pages += 1
                else:
                    print(f"❌ 第{page_no}页HTTP失败: {response.status_code}")
                    failed_pages += 1
                    
            except Exception as e:
                print(f"❌ 第{page_no}页异常: {e}")
                failed_pages += 1
            
            # 显示进度
            progress = (page_no / total_pages) * 100
            print(f"📈 进度: {page_no}/{total_pages}页 ({progress:.1f}%)")
        
        # 生成报告
        generate_report(output_dir, total_count, positions_saved, total_pages, failed_pages, timestamp)
        
        return True
        
    except Exception as e:
        print(f"❌ 爬取过程异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def save_page_data(data, page_no, output_dir):
    """保存整页数据"""
    pages_dir = output_dir / "pages"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ant_page_{page_no}_{timestamp}.json"
    filepath = pages_dir / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath
    except Exception as e:
        print(f"❌ 保存第{page_no}页数据失败: {e}")
        return None

def save_positions(positions, page_no, output_dir, category_mapping):
    """保存岗位数据"""
    positions_dir = output_dir / "positions"
    saved_count = 0
    
    for position in positions:
        try:
            position_id = position.get("id", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ant_page{page_no}_position_{position_id}_{timestamp}.json"
            filepath = positions_dir / filename
            
            # 添加类别名称映射
            categories = position.get("categories", [])
            category_names = []
            for cat in categories:
                cat_str = str(cat)
                category_names.append(category_mapping.get(cat_str, cat_str))
            
            # 添加处理后的字段
            processed_position = position.copy()
            processed_position["category_names"] = category_names
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(processed_position, f, ensure_ascii=False, indent=2)
            
            saved_count += 1
            
        except Exception as e:
            print(f"❌ 保存岗位数据失败: {e}")
    
    return saved_count

def generate_report(output_dir, total_count, positions_saved, total_pages, failed_pages, timestamp):
    """生成爬取报告"""
    report = {
        "project": "蚂蚁国际招聘完整爬取",
        "timestamp": timestamp,
        "stats": {
            "total_positions": total_count,
            "positions_saved": positions_saved,
            "total_pages": total_pages,
            "failed_pages": failed_pages,
            "success_rate": ((total_pages - failed_pages) / total_pages * 100) if total_pages > 0 else 0,
            "output_directory": str(output_dir)
        },
        "category_summary": {
            "main_categories": 6,
            "sub_categories": 108,
            "category_mapping": {
                "97": "产品类",
                "103": "运营类",
                "143": "数据类",
                "124": "市场拓展",
                "152": "销售类",
                "146": "金融类"
            }
        },
        "api_config": {
            "endpoint": "https://hrcareersweb.antgroup.com/api/social/position/search",
            "method": "POST",
            "authentication": "ctoken + Cookie"
        }
    }
    
    report_file = output_dir / "crawl_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 爬取报告已保存到: {report_file}")
    
    # 打印摘要
    print("\n" + "="*70)
    print("📊 爬取完成摘要")
    print("="*70)
    print(f"📄 总页数: {total_pages}")
    print(f"💾 保存岗位: {positions_saved}/{total_count}")
    print(f"❌ 失败页面: {failed_pages}")
    print(f"📁 输出目录: {output_dir}")
    print("="*70)

if __name__ == "__main__":
    print("⚠️  注意: 这将爬取所有381个岗位（39页），可能需要几分钟时间")
    print("     按 Ctrl+C 可以中断爬取")
    print("-"*70)
    
    confirm = input("确认开始完整爬取？(输入 'y' 确认): ").strip().lower()
    
    if confirm == 'y':
        start_time = datetime.now()
        success = main()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n⏱️  总耗时: {duration:.1f}秒")
        
        if success:
            print("\n🎉 爬取完成！")
            print("\n📋 下一步:")
            print("  1. 检查输出目录的文件结构")
            print("  2. 验证数据完整性")
            print("  3. 分析各类别岗位分布")
        else:
            print("\n❌ 爬取失败")
    else:
        print("❌ 用户取消")