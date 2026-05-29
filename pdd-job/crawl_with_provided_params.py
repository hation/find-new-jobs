#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于用户提供参数的PDD岗位爬取器
使用用户提供的准确参数进行爬取
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

import requests
import pandas as pd

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PddCrawlerWithProvidedParams:
    """基于用户提供参数的PDD爬取器"""
    
    def __init__(self):
        """初始化爬取器"""
        self.base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
        self.session = requests.Session()
        
        # 设置请求头（基于用户提供的信息）
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
        
        # 基础请求载荷
        self.base_payload = {
            "page": 1,
            "pageSize": 10,
            "anti_content": ""  # 需要用户提供
        }
        
        # 输出目录
        self.output_dir = "output/pdd_data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("✅ PDD爬取器初始化完成（基于用户提供参数）")
        logger.info(f"   API端点: {self.base_url}")
        logger.info(f"   输出目录: {self.output_dir}")
    
    def set_anti_content(self, anti_content_value: str):
        """
        设置anti_content参数
        
        Args:
            anti_content_value: anti_content参数值
        """
        self.base_payload["anti_content"] = anti_content_value
        logger.info(f"📝 设置anti_content参数: {anti_content_value[:50]}...")
    
    def fetch_page(self, page: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """
        获取单页数据
        
        Args:
            page: 页码
            page_size: 每页大小
            
        Returns:
            响应数据，失败返回None
        """
        # 准备请求数据
        payload = self.base_payload.copy()
        payload["page"] = page
        payload["pageSize"] = page_size
        
        logger.info(f"📥 获取第 {page} 页数据 (每页 {page_size} 条)")
        logger.debug(f"   请求载荷: {json.dumps(payload, ensure_ascii=False)}")
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            elapsed_time = time.time() - start_time
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"❌ HTTP错误: {response.status_code}")
                logger.debug(f"   响应内容: {response.text[:200]}")
                return None
            
            # 解析JSON响应
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                logger.error(f"❌ JSON解析失败")
                logger.debug(f"   响应内容: {response.text[:200]}")
                return None
            
            # 检查API响应状态
            if not response_data.get("success", False):
                error_code = response_data.get("errorCode")
                error_msg = response_data.get("errorMsg", "未知错误")
                logger.error(f"❌ API错误: {error_code} - {error_msg}")
                return None
            
            logger.info(f"   ✅ 获取成功，用时: {elapsed_time:.2f}秒")
            
            # 提取数据
            result = response_data.get("result", {})
            data_list = result.get("list", [])
            total = result.get("total", 0)
            
            logger.info(f"   📊 本页数据: {len(data_list)} 条，总计: {total} 条")
            
            return {
                "page": page,
                "page_size": page_size,
                "total": total,
                "data": data_list,
                "raw_response": response_data,
                "elapsed_time": elapsed_time
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"⏰ 请求超时")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 连接错误")
            return None
        except Exception as e:
            logger.error(f"❌ 请求异常: {e}")
            return None
    
    def fetch_all_pages(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        获取所有页数据
        
        Args:
            max_pages: 最大页数
            
        Returns:
            所有数据列表
        """
        all_data = []
        
        # 先获取第一页，了解总数据量
        logger.info("🚀 开始获取所有页数据...")
        
        first_page = self.fetch_page(page=1)
        if not first_page:
            logger.error("❌ 获取第一页失败，无法继续")
            return []
        
        total_items = first_page["total"]
        page_size = first_page["page_size"]
        total_pages = (total_items + page_size - 1) // page_size  # 计算总页数
        
        logger.info(f"📈 数据统计:")
        logger.info(f"   总岗位数: {total_items}")
        logger.info(f"   每页大小: {page_size}")
        logger.info(f"   总页数: {total_pages}")
        logger.info(f"   最大爬取页数: {min(total_pages, max_pages)}")
        
        # 添加第一页数据
        all_data.extend(first_page["data"])
        
        # 获取剩余页
        actual_pages_to_fetch = min(total_pages, max_pages)
        
        for page in range(2, actual_pages_to_fetch + 1):
            logger.info(f"\n📥 获取第 {page}/{actual_pages_to_fetch} 页...")
            
            page_data = self.fetch_page(page=page)
            if page_data:
                all_data.extend(page_data["data"])
            else:
                logger.warning(f"⚠️ 第 {page} 页获取失败，跳过")
            
            # 避免请求过快
            time.sleep(1)
        
        logger.info(f"\n✅ 数据获取完成")
        logger.info(f"   成功获取页数: {actual_pages_to_fetch}")
        logger.info(f"   总数据量: {len(all_data)} 条")
        
        return all_data
    
    def process_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理原始数据
        
        Args:
            raw_data: 原始数据列表
            
        Returns:
            处理后的数据列表
        """
        logger.info("🔧 处理数据...")
        
        processed_data = []
        
        for i, item in enumerate(raw_data):
            # 基础字段映射
            processed_item = {
                "position_id": item.get("code", ""),
                "position_name": item.get("name", ""),
                "work_location": item.get("workLocation", ""),
                "position_category": item.get("job", ""),
                "update_time_str": item.get("updateTime", ""),
                "update_timestamp": item.get("updateDate", 0),
                "detail_url": f"https://careers.pddglobalhr.com/jobs/{item.get('code', '')}",
                "raw_data": json.dumps(item, ensure_ascii=False)
            }
            
            # 添加处理时间
            processed_item["processed_time"] = datetime.now().isoformat()
            processed_item["data_source"] = "pdd_careers_api"
            
            processed_data.append(processed_item)
            
            # 每处理100条记录日志
            if (i + 1) % 100 == 0:
                logger.info(f"   已处理 {i + 1}/{len(raw_data)} 条记录")
        
        logger.info(f"✅ 数据处理完成，共 {len(processed_data)} 条记录")
        
        return processed_data
    
    def export_to_excel(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        导出数据到Excel
        
        Args:
            data: 数据列表
            filename: 文件名
            
        Returns:
            文件路径
        """
        if not data:
            logger.warning("⚠️ 没有数据需要导出")
            return ""
        
        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pdd_positions_{timestamp}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            logger.info(f"📤 导出数据到Excel: {filename}")
            
            # 转换为DataFrame
            df = pd.DataFrame(data)
            
            # 保存到Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='所有岗位', index=False)
                
                # 添加统计信息
                if 'work_location' in df.columns:
                    location_stats = df['work_location'].value_counts().reset_index()
                    location_stats.columns = ['工作地点', '岗位数量']
                    location_stats.to_excel(writer, sheet_name='地点分布', index=False)
                
                if 'position_category' in df.columns:
                    category_stats = df['position_category'].value_counts().reset_index()
                    category_stats.columns = ['岗位类别', '岗位数量']
                    category_stats.to_excel(writer, sheet_name='类别分布', index=False)
            
            file_size = os.path.getsize(filepath)
            logger.info(f"✅ Excel导出成功")
            logger.info(f"   文件: {filepath}")
            logger.info(f"   大小: {file_size:,} 字节")
            logger.info(f"   记录数: {len(data)}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Excel导出失败: {e}")
            return ""
    
    def export_to_json(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        导出数据到JSON
        
        Args:
            data: 数据列表
            filename: 文件名
            
        Returns:
            文件路径
        """
        if not data:
            return ""
        
        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pdd_positions_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            logger.info(f"📤 导出数据到JSON: {filename}")
            
            # 准备导出数据
            export_data = {
                "export_info": {
                    "export_time": datetime.now().isoformat(),
                    "format": "json",
                    "version": "1.0",
                    "total_records": len(data)
                },
                "data": data
            }
            
            # 保存到JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            file_size = os.path.getsize(filepath)
            logger.info(f"✅ JSON导出成功")
            logger.info(f"   文件: {filepath}")
            logger.info(f"   大小: {file_size:,} 字节")
            
            return filepath
            
        except Exception as e:
            logger.error(f"❌ JSON导出失败: {e}")
            return ""
    
    def run_full_crawl(self, anti_content: str, max_pages: int = 10) -> Dict[str, Any]:
        """
        运行完整爬取流程
        
        Args:
            anti_content: anti_content参数值
            max_pages: 最大爬取页数
            
        Returns:
            爬取结果
        """
        print("\n" + "="*60)
        print("🚀 PDD岗位数据爬取 - 开始执行")
        print("="*60)
        
        start_time = time.time()
        
        # 设置anti_content参数
        self.set_anti_content(anti_content)
        
        # 获取数据
        raw_data = self.fetch_all_pages(max_pages=max_pages)
        
        if not raw_data:
            print("\n❌ 爬取失败，没有获取到数据")
            return {"success": False, "error": "没有获取到数据"}
        
        # 处理数据
        processed_data = self.process_data(raw_data)
        
        # 导出数据
        excel_file = self.export_to_excel(processed_data)
        json_file = self.export_to_json(processed_data)
        
        # 计算总用时
        total_time = time.time() - start_time
        
        # 生成结果报告
        result = {
            "success": True,
            "total_time": total_time,
            "total_records": len(processed_data),
            "excel_file": excel_file,
            "json_file": json_file,
            "export_time": datetime.now().isoformat(),
            "anti_content_used": anti_content[:50] + "..." if len(anti_content) > 50 else anti_content
        }
        
        print("\n" + "="*60)
        print("🎯 爬取完成报告")
        print("="*60)
        print(f"✅ 状态: 成功")
        print(f"⏱️ 总用时: {total_time:.2f} 秒")
        print(f"📊 总记录数: {len(processed_data)} 条")
        print(f"📁 Excel文件: {excel_file}")
        print(f"📁 JSON文件: {json_file}")
        print(f"🔑 anti_content: {result['anti_content_used']}")
        print("="*60)
        
        # 保存结果报告
        report_file = os.path.join(self.output_dir, "crawl_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"📄 详细报告已保存: {report_file}")
        
        return result

def main():
    """主函数"""
    print("PDD岗位数据爬取工具")
    print("="*60)
    print("基于用户提供的参数进行爬取")
    print("="*60)
    
    # 创建爬取器
    crawler = PddCrawlerWithProvidedParams()
    
    # 获取用户输入的anti_content参数
    print("\n🔑 请输入anti_content参数:")
    print("提示: 这个参数可以从浏览器开发者工具的Network选项卡中获取")
    print("     查看拼多多招聘网站的API请求，复制anti_content参数值")
    print("     或者如果您有有效的参数值，请直接输入")
    print("-" * 60)
    
    anti_content = input("请输入anti_content参数值: ").strip()
    
    if not anti_content:
        print("\n❌ 错误: anti_content参数不能为空")
        print("\n💡 如何获取anti_content参数:")
        print("1. 打开浏览器，访问 https://careers.pddglobalhr.com/jobs")
        print("2. 按F12打开开发者工具")
        print("3. 转到Network（网络）选项卡")
        print("4. 刷新页面")
        print("5. 找到名为 'list' 的POST请求")
        print("6. 查看Request Payload（请求载荷）")
        print("7. 复制anti_content参数的值")
        return 1
    
    # 获取最大页数
    print("\n📄 请输入最大爬取页数 (默认10):")
    max_pages_input = input("最大页数: ").strip()
    
    try:
        max_pages = int(max_pages_input) if max_pages_input else 10
    except ValueError:
        print(f"⚠️ 输入无效，使用默认值10")
        max_pages = 10
    
    print(f"\n🚀 开始爬取，使用参数:")
    print(f"   anti_content: {anti_content[:50]}...")
    print(f"   最大页数: {max_pages}")
    print("="*60)
    
    # 运行爬取
    result = crawler.run_full_crawl(anti_content=anti_content, max_pages=max_pages)
    
    if result["success"]:
        print("\n✅ 爬取任务完成!")
        print("\n下一步:")
        print(f"1. 打开Excel文件查看数据: {result['excel_file']}")
        print(f"2. 查看详细报告: output/pdd_data/crawl_report.json")
        print(f"3. 数据已保存到: output/pdd_data/")
        return 0
    else:
        print("\n❌ 爬取任务失败")
        print(f"错误: {result.get('error', '未知错误')}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)