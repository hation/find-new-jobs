#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
立即运行PDD爬取任务
解决anti_content参数问题，提供完整功能
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import requests
import pandas as pd

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImmediatePddCrawler:
    """立即可用的PDD爬取器"""
    
    def __init__(self, anti_content: str = None):
        """
        初始化立即爬取器
        
        Args:
            anti_content: anti_content参数值（必须提供）
        """
        if not anti_content:
            raise ValueError("必须提供anti_content参数")
        
        self.anti_content = anti_content
        self.base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
        
        # 请求头
        self.headers = {
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
        
        # 输出目录
        self.output_dir = "output/immediate_crawl"
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("🚀 立即爬取器初始化完成")
        logger.info(f"   使用anti_content: {self.anti_content[:50]}...")
        logger.info(f"   输出目录: {self.output_dir}")
    
    def fetch_single_page(self, page: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """获取单页数据"""
        payload = {
            "page": page,
            "pageSize": page_size,
            "anti_content": self.anti_content
        }
        
        try:
            logger.info(f"📥 获取第 {page} 页 (size={page_size})")
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"❌ HTTP错误: {response.status_code}")
                return None
            
            data = response.json()
            
            if not data.get("success", False):
                error_code = data.get("errorCode")
                error_msg = data.get("errorMsg", "未知错误")
                logger.error(f"❌ API错误: {error_code} - {error_msg}")
                return None
            
            result = data.get("result", {})
            positions = result.get("list", [])
            total = result.get("total", 0)
            
            logger.info(f"   ✅ 成功获取 {len(positions)} 条数据，总计 {total} 条")
            
            if positions:
                # 显示第一条数据示例
                first = positions[0]
                logger.info(f"   📋 示例: {first.get('name', 'N/A')} - {first.get('workLocation', 'N/A')}")
            
            return {
                "page": page,
                "page_size": page_size,
                "total": total,
                "positions": positions,
                "raw_data": data
            }
            
        except Exception as e:
            logger.error(f"❌ 获取第 {page} 页失败: {e}")
            return None
    
    def fetch_all_pages(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """获取所有页数据"""
        all_positions = []
        
        # 先获取第一页了解总数据量
        first_page = self.fetch_single_page(page=1)
        if not first_page:
            logger.error("❌ 获取第一页失败，无法继续")
            return []
        
        total_positions = first_page["total"]
        page_size = first_page["page_size"]
        total_pages = (total_positions + page_size - 1) // page_size
        
        logger.info(f"📊 数据统计:")
        logger.info(f"   总岗位数: {total_positions}")
        logger.info(f"   每页大小: {page_size}")
        logger.info(f"   总页数: {total_pages}")
        logger.info(f"   实际爬取: {min(total_pages, max_pages)} 页")
        
        # 添加第一页数据
        all_positions.extend(first_page["positions"])
        
        # 获取剩余页
        pages_to_fetch = min(total_pages, max_pages)
        
        for page in range(2, pages_to_fetch + 1):
            logger.info(f"\n📥 获取第 {page}/{pages_to_fetch} 页...")
            
            page_data = self.fetch_single_page(page=page)
            if page_data:
                all_positions.extend(page_data["positions"])
            else:
                logger.warning(f"⚠️ 第 {page} 页获取失败，跳过")
            
            # 避免请求过快
            time.sleep(1)
        
        logger.info(f"\n✅ 数据获取完成，共 {len(all_positions)} 条记录")
        return all_positions
    
    def process_positions(self, positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理数据"""
        processed = []
        
        for pos in positions:
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
            processed.append(processed_pos)
        
        return processed
    
    def export_to_excel(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """导出到Excel"""
        if not data:
            logger.warning("⚠️ 没有数据需要导出")
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pdd_positions_{timestamp}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            logger.info(f"📤 导出 {len(data)} 条记录到Excel...")
            
            df = pd.DataFrame(data)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
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
                
                # 时间统计
                if '爬取时间' in df.columns:
                    time_stats = pd.DataFrame({
                        '统计项': ['总记录数', '唯一岗位ID数', '开始爬取时间', '结束爬取时间'],
                        '数值': [len(df), df['岗位ID'].nunique(), df['爬取时间'].min(), df['爬取时间'].max()]
                    })
                    time_stats.to_excel(writer, sheet_name='数据摘要', index=False)
            
            file_size = os.path.getsize(filepath)
            logger.info(f"✅ Excel导出成功")
            logger.info(f"   文件: {filepath}")
            logger.info(f"   大小: {file_size:,} 字节")
            logger.info(f"   工作表: 所有岗位、地点分布、类别分布、数据摘要")
            
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Excel导出失败: {e}")
            return ""
    
    def export_to_json(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """导出到JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pdd_positions_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            export_data = {
                "export_info": {
                    "export_time": datetime.now().isoformat(),
                    "total_records": len(data),
                    "format": "json",
                    "version": "1.0"
                },
                "data": data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ JSON导出成功: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ JSON导出失败: {e}")
            return ""
    
    def run_complete_crawl(self, max_pages: int = 10) -> Dict[str, Any]:
        """运行完整爬取"""
        print("\n" + "="*60)
        print("🚀 PDD岗位数据完整爬取 - 开始执行")
        print("="*60)
        
        start_time = time.time()
        
        # 1. 获取数据
        logger.info("📥 阶段1: 获取岗位列表数据...")
        raw_positions = self.fetch_all_pages(max_pages=max_pages)
        
        if not raw_positions:
            return {
                "success": False,
                "error": "没有获取到任何数据",
                "execution_time": time.time() - start_time
            }
        
        # 2. 处理数据
        logger.info("🔧 阶段2: 处理数据...")
        processed_data = self.process_positions(raw_positions)
        
        # 3. 导出数据
        logger.info("📤 阶段3: 导出数据...")
        excel_file = self.export_to_excel(processed_data)
        json_file = self.export_to_json(processed_data)
        
        # 4. 生成报告
        total_time = time.time() - start_time
        
        result = {
            "success": True,
            "execution_time": total_time,
            "total_records": len(processed_data),
            "excel_file": excel_file,
            "json_file": json_file,
            "export_time": datetime.now().isoformat(),
            "output_directory": self.output_dir
        }
        
        # 显示结果
        print("\n" + "="*60)
        print("🎯 爬取完成报告")
        print("="*60)
        print(f"✅ 状态: 成功")
        print(f"⏱️  用时: {total_time:.2f} 秒")
        print(f"📊 记录数: {len(processed_data)} 条")
        print(f"📁 Excel文件: {excel_file}")
        print(f"📁 JSON文件: {json_file}")
        print(f"📂 输出目录: {self.output_dir}")
        print("="*60)
        
        # 保存详细报告
        report_file = os.path.join(self.output_dir, "crawl_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"📄 详细报告: {report_file}")
        
        return result

def get_anti_content_from_user():
    """从用户获取anti_content参数"""
    print("\n" + "="*60)
    print("🔑 需要anti_content参数")
    print("="*60)
    print("这个参数是访问PDD招聘API的关键。")
    print("\n💡 如何获取:")
    print("1. 打开浏览器，访问 https://careers.pddglobalhr.com/jobs")
    print("2. 按F12打开开发者工具")
    print("3. 转到Network（网络）选项卡")
    print("4. 刷新页面")
    print("5. 找到名为 'list' 的POST请求")
    print("6. 点击该请求，查看Request Payload（请求载荷）")
    print("7. 复制 'anti_content' 参数的值")
    print("\n📝 示例anti_content值可能类似:")
    print("   'Xp8lqgJ...' (一长串字符)")
    print("="*60)
    
    anti_content = input("\n请输入anti_content参数值: ").strip()
    
    if not anti_content:
        print("\n❌ 错误: anti_content参数不能为空")
        print("\n⚠️ 如果没有这个参数，无法访问API。")
        print("   您可以:")
        print("   1. 按照上述步骤获取参数")
        print("   2. 使用浏览器自动化方案（需要额外开发）")
        print("   3. 提供测试用的有效参数")
        return None
    
    return anti_content

def main():
    """主函数"""
    print("PDD岗位数据完整爬取工具")
    print("="*60)
    print("提供完整功能: 爬取 + 处理 + 导出Excel")
    print("="*60)
    
    # 获取anti_content参数
    anti_content = get_anti_content_from_user()
    if not anti_content:
        return 1
    
    # 获取爬取页数
    print("\n📄 请输入爬取页数 (默认10，建议1-20):")
    max_pages_input = input("最大页数: ").strip()
    
    try:
        max_pages = int(max_pages_input) if max_pages_input else 10
        if max_pages < 1:
            max_pages = 10
    except ValueError:
        print("⚠️ 输入无效，使用默认值10")
        max_pages = 10
    
    # 创建爬取器并运行
    try:
        crawler = ImmediatePddCrawler(anti_content=anti_content)
        result = crawler.run_complete_crawl(max_pages=max_pages)
        
        if result["success"]:
            print("\n✅ 任务完成!")
            print("\n📋 下一步:")
            print(f"1. 打开Excel文件查看数据: {result['excel_file']}")
            print(f"2. 文件包含多个工作表: 所有岗位、地点分布、类别分布、数据摘要")
            print(f"3. 查看详细报告: {result['output_directory']}/crawl_report.json")
            print(f"4. 所有文件保存在: {result['output_directory']}/")
            return 0
        else:
            print(f"\n❌ 任务失败: {result.get('error', '未知错误')}")
            return 1
            
    except Exception as e:
        print(f"\n❌ 爬取器创建失败: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)