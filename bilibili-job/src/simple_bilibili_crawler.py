#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的B站数据爬取器
演示如何基于夸克框架快速启动
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src/framework"))

print("=" * 70)
print("🚀 简化的B站数据爬取器")
print("=" * 70)

try:
    # 尝试导入框架
    import framework.smart_crawler_selector as scs
    import framework.data_exporter as de
    import framework.unified_crawler_entry as uce
    
    print("✅ 框架导入成功")
    
    # 演示如何使用框架
    print("\n🔧 可用框架组件:")
    print("1. SmartCrawlerSelector - 智能爬取器选择器")
    print("2. UnifiedCrawlerEntry - 统一爬取器入口")
    print("3. DataExporter - 数据导出框架")
    
    # 创建数据目录
    data_dir = Path("data/bilibili")
    output_dir = Path("output/bilibili")
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 创建目录:")
    print(f"  • 数据目录: {data_dir}")
    print(f"  • 输出目录: {output_dir}")
    
    # 生成模拟数据
    print("\n📊 生成B站岗位模拟数据...")
    
    mock_jobs = [
        {
            "position_id": "B001",
            "title": "后端开发工程师",
            "location": "上海",
            "category": "技术类",
            "publish_time": "2026-05-22",
            "detail_url": "https://jobs.bilibili.com/position/001",
            "department": "技术中心",
            "education_requirement": "本科及以上",
            "experience_requirement": "3年以上",
            "responsibilities": "负责B站后端服务开发与维护",
            "requirements": "熟悉Go/Python，有大规模系统经验",
            "salary_range": "30-50K"
        },
        {
            "position_id": "B002",
            "title": "产品经理",
            "location": "北京",
            "category": "产品类",
            "publish_time": "2026-05-21",
            "detail_url": "https://jobs.bilibili.com/position/002",
            "department": "产品部",
            "education_requirement": "本科及以上",
            "experience_requirement": "2年以上",
            "responsibilities": "负责B站产品功能规划与设计",
            "requirements": "有互联网产品经验，熟悉用户研究",
            "salary_range": "25-40K"
        },
        {
            "position_id": "B003",
            "title": "内容运营",
            "location": "广州",
            "category": "运营类",
            "publish_time": "2026-05-20",
            "detail_url": "https://jobs.bilibili.com/position/003",
            "department": "内容运营部",
            "education_requirement": "本科及以上",
            "experience_requirement": "1年以上",
            "responsibilities": "负责B站内容运营和社区管理",
            "requirements": "熟悉B站社区文化，有内容创作经验",
            "salary_range": "15-25K"
        }
    ]
    
    print(f"✅ 生成{len(mock_jobs)}个岗位数据")
    
    # 保存数据
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = data_dir / f"bilibili_jobs_{timestamp}.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(mock_jobs, f, ensure_ascii=False, indent=2)
    
    print(f"💾 数据保存到: {json_file}")
    
    # 导出数据
    print("\n📤 导出数据...")
    
    # 创建数据导出器
    exporter = de.DataExporter()
    
    # 导出数据
    result = exporter.export_data(
        data=mock_jobs,
        format="all",  # 导出所有格式
        company_name="bilibili",
        additional_info={
            "crawled_at": timestamp,
            "total_jobs": len(mock_jobs)
        }
    )
    
    if result.get("success"):
        print(f"✅ 导出成功: {result.get('message', '')}")
        for format, filepath in result.get("files", {}).items():
            if filepath and os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"  • {format.upper()}文件: {filepath} ({file_size:,} bytes)")
    else:
        print(f"❌ 导出失败: {result.get('error', '未知错误')}")
    
    print("\n🎯 项目启动完成！")
    print("\n📚 下一步:")
    print("1. 配置B站API认证信息 (config/api_auth.json)")
    print("2. 实现真实的B站API爬取逻辑")
    print("3. 添加浏览器爬取作为备选方案")
    print("4. 设置定时任务自动爬取")
    
    # 显示文件结构
    print("\n📁 生成的文件结构:")
    if json_file.exists():
        file_size = json_file.stat().st_size
        print(f"  • {json_file.name} ({file_size:,} bytes)")
    
    # 检查导出的文件
    if result.get("files"):
        for format, filepath in result.get("files", {}).items():
            if filepath:
                try:
                    if os.path.exists(filepath):
                        file_size = os.path.getsize(filepath)
                        print(f"  • {format.upper()}文件: {os.path.basename(filepath)} ({file_size:,} bytes)")
                except Exception as e:
                    print(f"  • {format.upper()}文件: 检查失败 ({e})")
    
except ImportError as e:
    print(f"❌ 导入框架失败: {e}")
    print("\n🔧 解决方案:")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 检查Python路径配置")
    print("3. 重新启动项目")

except Exception as e:
    print(f"❌ 运行出错: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("🎉 简化的B站爬取器演示完成！")
print("=" * 70)