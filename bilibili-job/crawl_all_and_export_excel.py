#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬取所有B站招聘数据并导出为Excel文件
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src/framework"))

print("=" * 80)
print("🚀 B站招聘数据完整爬取 + Excel导出")
print("=" * 80)

try:
    from src.bilibili_api_crawler import BilibiliAPICrawler
    
    print("✅ 导入爬取器成功")
    
    # 创建爬取器实例
    print("🔧 创建B站API爬取器...")
    crawler = BilibiliAPICrawler("config/api_auth.json")
    
    # 显示状态
    status = crawler.get_status()
    print(f"📊 公司: {status.get('company')}")
    print(f"🌐 API地址: {status.get('api_url')}")
    print(f"📊 每页数量: {status.get('page_size')}")
    print()
    
    # 1. 先获取总页数
    print("🔍 获取总页数信息...")
    success, first_page_data, error = crawler.crawl_page(1)
    
    if not success:
        print(f"❌ 获取第一页失败: {error}")
        sys.exit(1)
    
    # 读取原始数据文件获取总页数
    raw_files = list(Path("data/bilibili/raw").glob("bilibili_page_1_*.json"))
    if raw_files:
        with open(raw_files[-1], 'r', encoding='utf-8') as f:
            first_page_response = json.load(f)
        
        total_pages = first_page_response.get("data", {}).get("pages", 0)
        total_jobs = first_page_response.get("data", {}).get("total", 0)
        
        print(f"📊 数据统计:")
        print(f"  • 总页数: {total_pages}页")
        print(f"  • 总岗位数: {total_jobs}个")
        print(f"  • 每页数量: {status.get('page_size')}")
        print()
    else:
        print("⚠️ 无法获取总页数，使用默认值33页")
        total_pages = 33
        total_jobs = 327
    
    # 2. 爬取所有数据
    print(f"🚀 开始爬取所有{total_pages}页数据...")
    print("📝 爬取配置:")
    print(f"  • 目标页数: {total_pages}页")
    print(f"  • 预计数据: {total_jobs}条")
    print(f"  • 请求间隔: 2秒")
    print(f"  • 预计时间: {total_pages * 2}秒")
    print()
    
    all_data = crawler.crawl_all_pages(max_pages=total_pages)
    
    if not all_data:
        print("❌ 未爬取到任何数据")
        sys.exit(1)
    
    print(f"✅ 爬取完成，共获取{len(all_data)}条数据")
    print()
    
    # 3. 数据统计和分析
    print("📊 详细数据统计:")
    print(f"  • 实际爬取: {len(all_data)}条")
    print(f"  • 数据来源: B站招聘官网")
    print(f"  • 爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 工作地点分析
    locations = {}
    for job in all_data:
        location = job.get('location', '未知')
        locations[location] = locations.get(location, 0) + 1
    
    print("📍 工作地点分布:")
    for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / len(all_data)) * 100
        print(f"  • {location}: {count}个岗位 ({percentage:.1f}%)")
    
    print()
    
    # 岗位类别分析
    categories = {}
    for job in all_data:
        category = job.get('category', '未知')
        categories[category] = categories.get(category, 0) + 1
    
    print("🏷️ 岗位类别分布:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / len(all_data)) * 100
        print(f"  • {category}: {count}个岗位 ({percentage:.1f}%)")
    
    print()
    
    # 4. 保存原始JSON数据
    print("💾 保存JSON数据...")
    json_save_path = crawler.save_final_data(all_data)
    
    if json_save_path:
        print(f"✅ JSON数据已保存到: {json_save_path}")
        
        # 显示JSON文件信息
        import os
        json_size = os.path.getsize(json_save_path)
        print(f"📁 JSON文件大小: {json_size:,} 字节")
    else:
        print("❌ JSON数据保存失败")
    
    print()
    
    # 5. 导出为Excel文件
    print("📤 导出为Excel文件...")
    
    # 准备数据用于Excel导出
    excel_data = []
    for job in all_data:
        excel_row = {
            "岗位ID": job.get('position_id', ''),
            "岗位标题": job.get('title', ''),
            "工作地点": job.get('location', ''),
            "岗位类别": job.get('category', ''),
            "发布时间": job.get('publish_time', ''),
            "岗位类型": job.get('position_type', ''),
            "是否热招": "是" if job.get('is_hot') == 1 else "否",
            "详情链接": job.get('detail_url', ''),
            "爬取时间": job.get('crawled_at', '')
        }
        
        # 添加描述的前100个字符（避免Excel单元格过长）
        description = job.get('description', '')
        if description:
            excel_row["岗位描述(摘要)"] = description[:200] + "..." if len(description) > 200 else description
        
        excel_data.append(excel_row)
    
    # 创建DataFrame
    df = pd.DataFrame(excel_data)
    
    # 生成Excel文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"bilibili_jobs_{timestamp}.xlsx"
    excel_path = Path("output/bilibili") / excel_filename
    
    # 确保输出目录存在
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 导出到Excel
    try:
        # 使用pandas的ExcelWriter
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # 写入主数据表
            df.to_excel(writer, sheet_name='岗位数据', index=False)
            
            # 创建工作地点统计表
            location_df = pd.DataFrame([
                {"工作地点": loc, "岗位数量": count, "占比(%)": (count/len(all_data))*100}
                for loc, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)
            ])
            location_df.to_excel(writer, sheet_name='地点分布', index=False)
            
            # 创建岗位类别统计表
            category_df = pd.DataFrame([
                {"岗位类别": cat, "岗位数量": count, "占比(%)": (count/len(all_data))*100}
                for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)
            ])
            category_df.to_excel(writer, sheet_name='类别分布', index=False)
            
            # 创建元数据表
            metadata_df = pd.DataFrame([
                {"项目": "B站招聘数据爬取", "值": ""},
                {"项目": "爬取时间", "值": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                {"项目": "总岗位数", "值": len(all_data)},
                {"项目": "数据来源", "值": "https://jobs.bilibili.com"},
                {"项目": "API端点", "值": status.get('api_url')},
                {"项目": "JSON数据文件", "值": json_save_path if json_save_path else "未保存"},
                {"项目": "生成工具", "值": "B站招聘数据爬取器 v1.0"},
                {"项目": "备注", "值": "基于夸克项目框架开发"}
            ])
            metadata_df.to_excel(writer, sheet_name='元数据', index=False)
        
        print(f"✅ Excel文件已生成: {excel_path}")
        print(f"📁 Excel文件大小: {excel_path.stat().st_size:,} 字节")
        print(f"📊 Excel工作表:")
        print(f"  • 岗位数据: {len(df)}行 x {len(df.columns)}列")
        print(f"  • 地点分布: {len(location_df)}行")
        print(f"  • 类别分布: {len(category_df)}行")
        print(f"  • 元数据: {len(metadata_df)}行")
        
        # 显示Excel文件中的样本数据
        print()
        print("📋 Excel数据样本（前3行）:")
        print(df.head(3).to_string(index=False))
        
    except Exception as e:
        print(f"❌ Excel导出失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 尝试简单的CSV导出作为备选
        print("🔄 尝试导出为CSV文件...")
        csv_path = excel_path.with_suffix('.csv')
        try:
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"✅ CSV文件已生成: {csv_path}")
        except Exception as csv_error:
            print(f"❌ CSV导出也失败: {csv_error}")
    
    print()
    
    # 6. 生成报告
    print("📈 生成数据报告...")
    report_content = f"""
# B站招聘数据爬取报告

## 📅 报告时间
{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

## 📊 数据概览
- **总爬取页数**: {total_pages}页
- **总岗位数**: {len(all_data)}条
- **数据完整性**: {len(all_data)/total_jobs*100:.1f}% (已爬取/总数)
- **爬取耗时**: 约{total_pages * 2}秒

## 📍 主要工作地点
{chr(10).join(f'- **{loc}**: {count}个岗位 ({count/len(all_data)*100:.1f}%)' for loc, count in list(sorted(locations.items(), key=lambda x: x[1], reverse=True))[:5])}

## 🏷️ 主要岗位类别
{chr(10).join(f'- **{cat}**: {count}个岗位 ({count/len(all_data)*100:.1f}%)' for cat, count in list(sorted(categories.items(), key=lambda x: x[1], reverse=True))[:5])}

## 📁 生成文件
- **Excel文件**: {excel_path.name} ({excel_path.stat().st_size:,} 字节)
- **JSON文件**: {Path(json_save_path).name if json_save_path else "未生成"} ({json_size:,} 字节)
- **原始数据**: {len(list(Path('data/bilibili/raw').glob('*.json')))}个文件

## 🔧 技术信息
- **数据源**: B站招聘官网 (https://jobs.bilibili.com)
- **API端点**: {status.get('api_url')}
- **爬取工具**: B站招聘数据爬取器 v1.0
- **框架**: 基于夸克项目框架

## 📝 备注
1. 数据爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
2. 数据可能因网站更新而变化
3. 建议定期爬取以保持数据最新
"""
    
    report_path = Path("output/bilibili") / f"bilibili_report_{timestamp}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 报告已生成: {report_path}")
    
    print()
    print("📁 最终生成的文件清单:")
    print(f"  📂 {excel_path.name} - Excel数据文件")
    print(f"  📂 {Path(json_save_path).name if json_save_path else 'bilibili_jobs_*.json'} - JSON数据文件")
    print(f"  📂 {report_path.name} - 数据报告")
    print(f"  📂 data/bilibili/raw/*.json - {len(list(Path('data/bilibili/raw').glob('*.json')))}个原始数据文件")
    
    print()
    print("🎉 所有任务完成！")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("🔧 请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"❌ 程序运行出错: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ B站招聘数据完整爬取 + Excel导出完成！")
print("=" * 80)