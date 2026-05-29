#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
滴滴招聘爬取器示例
基于夸克完整架构框架
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src/framework"))

from framework.smart_crawler_selector import SmartCrawlerSelector
from framework.unified_crawler_entry import UnifiedCrawlerEntry
from framework.data_exporter import DataExporter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DidiCrawler(SmartCrawlerSelector):
    """滴滴招聘智能爬取器"""
    
    def __init__(self, company_name="滴滴出行", website_url="https://job.didiglobal.com"):
        """
        初始化滴滴招聘爬取器
        
        Args:
            company_name: 公司名称
            website_url: 招聘网站URL
        """
        # 创建配置字典
        config = {
            "company_name": company_name,
            "website_url": website_url,
            "output_dir": "output/didi_positions"
        }
        
        super().__init__(config)
        self.company_name = company_name
        self.website_url = website_url
        
        # 滴滴招聘的API配置
        self.api_endpoint = "https://job.didiglobal.com/api/v1/positions"
        self.api_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/json"
        }
        
        # 数据字段定义
        self.required_fields = [
            "position_id",      # 岗位ID
            "position_name",    # 岗位名称
            "work_location",    # 工作地点
            "position_category", # 岗位类别
            "publish_time",     # 发布时间
            "detail_url",       # 详情链接
            "department",       # 部门信息
            "education",        # 学历要求
            "experience",       # 工作经验
            "responsibilities", # 工作职责
            "requirements",     # 任职要求
            "salary_range"      # 薪资范围
        ]
        
        logger.info(f"初始化滴滴招聘爬取器: {company_name}")
    
    def _initialize_primary_crawler(self):
        """初始化API爬取器（主要爬取方式）"""
        logger.info("初始化API爬取器...")
        
        # 这里应该实现滴滴招聘的API爬取逻辑
        # 由于滴滴招聘的API可能需要认证，这里先返回基础实现
        
        def api_crawler():
            """API爬取函数"""
            try:
                # 这里应该实现滴滴招聘的API调用
                # 示例：获取第一页数据
                response = {
                    "success": True,
                    "data": {
                        "total": 100,
                        "positions": [
                            {
                                "position_id": "DIDI001",
                                "position_name": "高级后端开发工程师",
                                "work_location": "北京",
                                "position_category": "技术类",
                                "publish_time": "2026-05-22",
                                "detail_url": "https://job.didiglobal.com/position/DIDI001"
                            }
                        ]
                    }
                }
                return response
            except Exception as e:
                logger.error(f"API爬取失败: {e}")
                return {"success": False, "error": str(e)}
        
        return api_crawler
    
    def _initialize_fallback_crawler(self):
        """初始化浏览器爬取器（备用爬取方式）"""
        logger.info("初始化浏览器爬取器...")
        
        # 这里应该实现滴滴招聘的浏览器爬取逻辑
        # 使用Playwright或Selenium进行浏览器自动化
        
        def browser_crawler():
            """浏览器爬取函数"""
            try:
                # 这里应该实现浏览器自动化逻辑
                # 示例：模拟浏览器访问
                logger.info("使用浏览器爬取滴滴招聘网站...")
                
                # 返回模拟数据
                return {
                    "success": True,
                    "data": {
                        "total": 50,
                        "positions": [
                            {
                                "position_id": "DIDI002",
                                "position_name": "产品经理",
                                "work_location": "上海",
                                "position_category": "产品类",
                                "publish_time": "2026-05-21",
                                "detail_url": "https://job.didiglobal.com/position/DIDI002"
                            }
                        ]
                    }
                }
            except Exception as e:
                logger.error(f"浏览器爬取失败: {e}")
                return {"success": False, "error": str(e)}
        
        return browser_crawler
    
    def extract_position_details(self, position_id: str) -> Dict[str, Any]:
        """
        提取岗位详细信息
        
        Args:
            position_id: 岗位ID
            
        Returns:
            岗位详细信息字典
        """
        try:
            # 这里应该实现从详情页提取完整信息的逻辑
            # 示例数据
            details = {
                "position_id": position_id,
                "department": "技术部-后端开发组",
                "education": "本科及以上",
                "experience": "3-5年工作经验",
                "responsibilities": "1. 负责滴滴核心业务系统开发\n2. 参与系统架构设计和优化\n3. 保障系统高可用和高性能",
                "requirements": "1. 精通Java/Python/Go等至少一门语言\n2. 熟悉分布式系统设计\n3. 有大型互联网公司经验者优先",
                "salary_range": "30-50k",
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return details
        except Exception as e:
            logger.error(f"提取岗位详情失败 {position_id}: {e}")
            return {"error": str(e)}
    
    def run(self, mode: str = "smart", max_positions: int = 10) -> Dict[str, Any]:
        """
        运行爬取器
        
        Args:
            mode: 爬取模式 (api, browser, smart)
            max_positions: 最大爬取岗位数
            
        Returns:
            爬取结果
        """
        logger.info(f"开始滴滴招聘数据爬取，模式: {mode}, 最大岗位数: {max_positions}")
        
        # 根据模式选择爬取方式
        if mode == "api":
            # 使用API爬取
            result = self._initialize_primary_crawler()
            if not result:
                return {"success": False, "error": "API爬取器初始化失败"}
            
            # 执行API爬取
            api_result = result()
            if not api_result.get("success"):
                return api_result
            
            positions = api_result.get("data", {}).get("positions", [])
            total = api_result.get("data", {}).get("total", 0)
            
        elif mode == "browser":
            # 使用浏览器爬取
            result = self._initialize_fallback_crawler()
            if not result:
                return {"success": False, "error": "浏览器爬取器初始化失败"}
            
            # 执行浏览器爬取
            browser_result = result()
            if not browser_result.get("success"):
                return browser_result
            
            positions = browser_result.get("data", {}).get("positions", [])
            total = browser_result.get("data", {}).get("total", 0)
            
        elif mode == "smart":
            # 智能模式：先尝试API，失败则尝试浏览器
            api_result = self._initialize_primary_crawler()
            if api_result:
                api_data = api_result()
                if api_data.get("success"):
                    positions = api_data.get("data", {}).get("positions", [])
                    total = api_data.get("data", {}).get("total", 0)
                    logger.info("✅ 智能模式：API爬取成功")
                else:
                    logger.warning(f"⚠️ API爬取失败，尝试浏览器爬取: {api_data.get('error')}")
                    # 尝试浏览器
                    browser_result = self._initialize_fallback_crawler()
                    if browser_result:
                        browser_data = browser_result()
                        if browser_data.get("success"):
                            positions = browser_data.get("data", {}).get("positions", [])
                            total = browser_data.get("data", {}).get("total", 0)
                            logger.info("✅ 智能模式：浏览器爬取成功")
                        else:
                            return {"success": False, "error": "API和浏览器爬取都失败"}
                    else:
                        return {"success": False, "error": "浏览器爬取器初始化失败"}
            else:
                return {"success": False, "error": "API爬取器初始化失败"}
        else:
            return {"success": False, "error": f"不支持的爬取模式: {mode}"}
        
        # 限制爬取数量
        if max_positions > 0:
            positions = positions[:max_positions]
        
        # 提取详细信息
        detailed_positions = []
        for pos in positions:
            position_id = pos.get("position_id")
            if position_id:
                details = self.extract_position_details(position_id)
                pos.update(details)
            detailed_positions.append(pos)
            
            # 实时保存（防数据丢失）
            self._save_position_immediately(pos)
            
            # 添加延迟避免请求过快
            time.sleep(0.5)
        
        # 导出数据
        if detailed_positions:
            exporter = DataExporter()
            export_result = exporter.export_data(
                data=detailed_positions,
                format="json",
                company_name="滴滴出行"
            )
            
            if export_result.get("success"):
                logger.info(f"数据导出成功: {export_result.get('file_path')}")
            else:
                logger.error(f"数据导出失败: {export_result.get('error')}")
        
        return {
            "success": True,
            "total_positions": total,
            "crawled_positions": len(detailed_positions),
            "positions": detailed_positions,
            "company": self.company_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _save_position_immediately(self, position: Dict[str, Any]):
        """立即保存单个岗位数据（防数据丢失）"""
        try:
            output_dir = Path(project_root) / "output" / "json" / "immediate"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            position_id = position.get("position_id", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_dir / f"didi_position_{position_id}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(position, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"立即保存岗位数据: {filename}")
        except Exception as e:
            logger.error(f"立即保存数据失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 滴滴招聘数据爬取器")
    print("=" * 60)
    
    # 创建爬取器实例
    crawler = DidiCrawler()
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="滴滴招聘数据爬取器")
    parser.add_argument("--mode", choices=["api", "browser", "smart"], default="smart",
                       help="爬取模式: api(仅API), browser(仅浏览器), smart(智能选择)")
    parser.add_argument("--max", type=int, default=5,
                       help="最大爬取岗位数 (0表示无限制)")
    parser.add_argument("--output", choices=["json", "excel", "csv"], default="json",
                       help="输出格式")
    
    args = parser.parse_args()
    
    # 运行爬取器
    print(f"📊 公司: {crawler.company_name}")
    print(f"🌐 网站: {crawler.website_url}")
    print(f"🔧 模式: {args.mode}")
    print(f"📈 最大岗位数: {args.max}")
    print(f"💾 输出格式: {args.output}")
    print("-" * 60)
    
    result = crawler.run(mode=args.mode, max_positions=args.max)
    
    if result.get("success"):
        print(f"✅ 爬取成功!")
        print(f"📊 总岗位数: {result.get('total_positions', 0)}")
        print(f"📥 已爬取: {result.get('crawled_positions', 0)}")
        print(f"⏰ 时间: {result.get('timestamp')}")
        
        # 显示前几个岗位
        positions = result.get("positions", [])
        if positions:
            print("\n📋 爬取的岗位:")
            for i, pos in enumerate(positions[:3], 1):
                print(f"{i}. {pos.get('position_name', '未知')} - {pos.get('work_location', '未知')}")
            
            if len(positions) > 3:
                print(f"... 还有 {len(positions) - 3} 个岗位")
    else:
        print(f"❌ 爬取失败: {result.get('error', '未知错误')}")
    
    print("\n📁 数据已保存到:")
    print(f"   {Path(project_root) / 'output' / 'json'}")
    print(f"   {Path(project_root) / 'output' / 'json' / 'immediate'}")
    
    print("\n💡 提示:")
    print("• 查看完整数据: 查看 output/json/ 目录")
    print("• 配置API认证: 编辑 config/api_auth.json")
    print("• 查看检查清单: docs/CHECKLIST.md")
    print("• 记录经验教训: docs/LESSONS_LEARNED.md")

if __name__ == "__main__":
    main()