#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站智能爬取器
基于夸克框架的SmartCrawlerSelector实现
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src/framework"))

try:
    from framework.smart_crawler_selector import SmartCrawlerSelector
    from framework.data_exporter import DataExporter
    from bilibili_api_crawler import BilibiliAPICrawler
except ImportError as e:
    print(f"❌ 导入框架失败: {e}")
    print("请确保已安装所有依赖")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BilibiliSmartCrawler(SmartCrawlerSelector):
    """B站智能爬取器（继承自夸克框架）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化B站智能爬取器
        
        Args:
            config: 配置字典
        """
        if config is None:
            config = {
                "company_name": "bilibili",
                "output_dir": "output/bilibili",
                "data_dir": "data/bilibili",
                "log_dir": "logs/bilibili",
                "max_pages": 50,
                "page_size": 10
            }
        
        super().__init__(config)
        
        # B站特定配置
        self.company_name = "bilibili"
        self.base_url = "https://jobs.bilibili.com"
        
        # 子爬取器实例
        self.api_crawler = None
        self.browser_crawler = None
        
        # 数据统计
        self.total_jobs_crawled = 0
        self.last_crawl_time = None
        
        logger.info(f"🚀 初始化B站智能爬取器: {self.company_name}")
        logger.info(f"📊 配置: {json.dumps(config, ensure_ascii=False)}")
    
    def _initialize_primary_crawler(self) -> Tuple[bool, Optional[str]]:
        """
        初始化主爬取器（API爬取器）
        
        Returns:
            (成功与否, 错误信息/None)
        """
        logger.info("🎯 初始化B站API爬取器")
        
        try:
            # 创建API爬取器实例
            self.api_crawler = BilibiliAPICrawler("config/api_auth.json")
            
            # 测试连接
            logger.info("🔗 测试API连接...")
            success, test_data, error = self.api_crawler.crawl_page(1)
            
            if success:
                logger.info(f"✅ API连接测试成功，获取{len(test_data)}条测试数据")
                self.primary_crawler = self.api_crawler
                self.current_mode = "api"
                return True, None
            else:
                error_msg = f"API连接测试失败: {error}"
                logger.error(f"❌ {error_msg}")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"初始化API爬取器失败: {e}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def _initialize_fallback_crawler(self) -> Tuple[bool, Optional[str]]:
        """
        初始化备选爬取器（浏览器爬取器）
        
        Returns:
            (成功与否, 错误信息/None)
        """
        logger.info("🔄 初始化B站浏览器爬取器")
        
        try:
            # TODO: 实现浏览器爬取器
            # 这里可以集成Playwright或Selenium
            
            logger.warning("⚠️ 浏览器爬取器暂未实现，使用模拟数据")
            
            # 创建简单的模拟爬取器
            self.browser_crawler = {
                "name": "B站浏览器爬取器（模拟）",
                "type": "browser",
                "status": "simulated"
            }
            
            self.fallback_crawler = self.browser_crawler
            return True, None
            
        except Exception as e:
            error_msg = f"初始化浏览器爬取器失败: {e}"
            logger.error(f"❌ {error_msg}")
            return False, error_msg
    
    def test_primary_connection(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        测试主爬取器连接
        
        Returns:
            (是否成功, 诊断信息, 详细错误/None)
        """
        logger.info("🔍 测试主爬取器连接")
        
        if not self.primary_crawler:
            return False, "主爬取器未初始化", {"step": "initialize"}
        
        try:
            # 测试爬取第一页
            success, test_data, error = self.api_crawler.crawl_page(1)
            
            if success:
                test_info = {
                    "step": "connection_test",
                    "data_count": len(test_data),
                    "sample_titles": [job.get("title") for job in test_data[:3]] if test_data else []
                }
                
                if test_data:
                    return True, f"连接成功，获取{len(test_data)}条测试数据", test_info
                else:
                    return True, "连接成功但未获取到数据", test_info
            else:
                error_details = {
                    "step": "connection_test",
                    "error": error,
                    "crawler_type": "api"
                }
                return False, f"连接测试失败: {error}", error_details
                
        except Exception as e:
            error_details = {
                "step": "exception",
                "error": str(e),
                "exception_type": type(e).__name__
            }
            return False, f"连接测试异常: {e}", error_details
    
    def crawl_with_primary(self) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        使用主爬取器爬取数据
        
        Returns:
            (是否成功, 爬取的数据, 错误信息)
        """
        logger.info("🚀 使用API爬取器爬取数据")
        
        if not self.primary_crawler:
            return False, None, "主爬取器未初始化"
        
        try:
            # 获取配置中的最大页数
            max_pages = self.config.get("max_pages", 10)
            
            # 爬取所有页数据
            all_data = self.api_crawler.crawl_all_pages(max_pages=max_pages)
            
            if not all_data:
                return False, None, "未爬取到任何数据"
            
            # 更新统计
            self.total_jobs_crawled = len(all_data)
            self.last_crawl_time = datetime.now()
            self.data_extracted = len(all_data)
            
            # 准备结果
            result = {
                "company": self.company_name,
                "crawl_mode": "api",
                "total_jobs": len(all_data),
                "crawl_time": self.last_crawl_time.isoformat(),
                "data": all_data
            }
            
            logger.info(f"✅ API爬取完成，共获取{len(all_data)}条数据")
            return True, result, None
            
        except Exception as e:
            error_msg = f"API爬取失败: {e}"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
    
    def crawl_with_fallback(self) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        使用备选爬取器爬取数据
        
        Returns:
            (是否成功, 爬取的数据, 错误信息)
        """
        logger.info("🔄 使用备选爬取器爬取数据")
        
        # TODO: 实现真实的浏览器爬取
        # 这里返回模拟数据
        
        mock_data = [
            {
                "position_id": "B999",
                "title": "模拟岗位 - 后端开发工程师",
                "location": "上海",
                "category": "技术类",
                "publish_time": "2026-05-22 00:00:00",
                "detail_url": "https://jobs.bilibili.com/position/999",
                "description": "这是模拟数据，实际应使用浏览器爬取真实数据",
                "position_type": "全职",
                "is_hot": 0,
                "recruit_type": 0,
                "source": "bilibili_browser_simulated"
            }
        ]
        
        result = {
            "company": self.company_name,
            "crawl_mode": "browser_simulated",
            "total_jobs": len(mock_data),
            "crawl_time": datetime.now().isoformat(),
            "data": mock_data,
            "note": "这是模拟数据，浏览器爬取器暂未实现"
        }
        
        logger.warning("⚠️ 返回模拟数据，浏览器爬取器未实现")
        return True, result, None
    
    def export_data(self, data: Dict[str, Any], format: str = "all") -> str:
        """
        导出数据
        
        Args:
            data: 爬取的数据
            format: 导出格式
            
        Returns:
            导出文件路径
        """
        if not data or "data" not in data:
            logger.warning("⚠️ 没有数据需要导出")
            return ""
        
        job_data = data["data"]
        if not job_data:
            logger.warning("⚠️ 数据为空")
            return ""
        
        logger.info(f"📤 导出数据，格式: {format}")
        
        # 使用数据导出框架
        exporter = DataExporter()
        
        # 准备导出参数
        company_name = data.get("company", "bilibili")
        crawl_time = data.get("crawl_time", datetime.now().isoformat())
        
        # 导出数据
        result = exporter.export_data(
            data=job_data,
            format=format,
            company_name=company_name,
            additional_info={
                "crawled_at": crawl_time,
                "crawl_mode": data.get("crawl_mode", "unknown"),
                "total_jobs": len(job_data)
            }
        )
        
        if result.get("success"):
            logger.info(f"✅ 导出成功: {result.get('message', '')}")
            
            # 返回第一个文件路径
            files = result.get("files", {})
            if files:
                for filepath in files.values():
                    if filepath and os.path.exists(filepath):
                        return filepath
            
            return ""
        else:
            logger.error(f"❌ 导出失败: {result.get('error', '未知错误')}")
            return ""
    
    def smart_crawl(self) -> Dict[str, Any]:
        """
        智能爬取：先试API，失败后询问是否切换
        
        Returns:
            爬取结果
        """
        logger.info("🧠 开始智能爬取")
        
        # 1. 尝试主爬取器
        success, result, error = self.crawl_with_primary()
        
        if success:
            logger.info("✅ 主爬取器成功，返回数据")
            return result
        
        # 2. 主爬取器失败，生成友好错误信息
        error_details = {
            "step": "primary_failed",
            "error": error,
            "crawler_type": "api"
        }
        friendly_reason = self.get_failure_reason(error_details)
        
        logger.warning(f"⚠️ 主爬取器失败: {friendly_reason}")
        
        # 3. 询问用户是否切换到备选方案
        user_choice = self.ask_user_for_switch(friendly_reason)
        
        if user_choice == True:  # 用户同意切换
            logger.info("🔄 用户同意切换到备选方案")
            
            # 尝试备选爬取器
            fallback_success, fallback_result, fallback_error = self.crawl_with_fallback()
            
            if fallback_success:
                logger.info("✅ 备选爬取器成功")
                return fallback_result
            else:
                logger.error(f"❌ 备选爬取器也失败: {fallback_error}")
                return {
                    "company": self.company_name,
                    "success": False,
                    "error": f"所有爬取方案都失败: {error}, {fallback_error}",
                    "crawl_time": datetime.now().isoformat()
                }
        
        elif user_choice == "retry":  # 用户选择重试
            logger.info("🔄 用户选择重试")
            # 这里可以添加重试逻辑
            return {
                "company": self.company_name,
                "success": False,
                "error": "用户选择重试，但重试逻辑未实现",
                "crawl_time": datetime.now().isoformat()
            }
        
        else:  # 用户不同意切换
            logger.info("👋 用户取消爬取")
            return {
                "company": self.company_name,
                "success": False,
                "error": "用户取消爬取",
                "crawl_time": datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取爬取器状态
        
        Returns:
            状态信息
        """
        base_status = super().get_status()
        
        # 添加B站特定状态
        bilibili_status = {
            "company": self.company_name,
            "base_url": self.base_url,
            "total_jobs_crawled": self.total_jobs_crawled,
            "last_crawl_time": self.last_crawl_time.isoformat() if self.last_crawl_time else None,
            "current_mode": self.current_mode,
            "api_crawler_ready": self.primary_crawler is not None,
            "browser_crawler_ready": self.fallback_crawler is not None
        }
        
        base_status.update(bilibili_status)
        return base_status


def main():
    """主函数"""
    print("=" * 70)
    print("🚀 B站智能爬取器（基于夸克框架）")
    print("=" * 70)
    
    try:
        # 创建智能爬取器
        crawler = BilibiliSmartCrawler()
        
        # 显示状态
        status = crawler.get_status()
        print(f"📊 公司: {status.get('company')}")
        print(f"🌐 网站: {status.get('base_url')}")
        print(f"🎯 当前模式: {status.get('current_mode')}")
        print(f"📈 已爬取: {status.get('total_jobs_crawled')}条")
        print(f"🕐 最后爬取: {status.get('last_crawl_time')}")
        print()
        
        # 测试连接
        print("🔍 测试连接...")
        success, diagnosis, details = crawler.test_primary_connection()
        
        if success:
            print(f"✅ 连接测试成功: {diagnosis}")
            if details and "sample_titles" in details:
                print("📋 样本数据:")
                for i, title in enumerate(details["sample_titles"], 1):
                    print(f"  {i}. {title}")
            print()
            
            # 开始智能爬取
            print("🚀 开始智能爬取...")
            result = crawler.smart_crawl()
            
            if result.get("success", False):
                data = result.get("data", [])
                print(f"✅ 爬取成功，共获取{len(data)}条数据")
                print()
                
                # 显示前几条数据
                if data:
                    print("📋 爬取的数据样本:")
                    for i, job in enumerate(data[:5], 1):
                        print(f"  {i}. {job.get('title')} - {job.get('location')}")
                        print(f"     类别: {job.get('category')}")
                        print(f"     时间: {job.get('publish_time')}")
                        print()
                
                # 导出数据
                print("📤 导出数据...")
                export_path = crawler.export_data(result, "all")
                
                if export_path:
                    print(f"✅ 数据已导出到: {export_path}")
                else:
                    print("⚠️ 数据导出失败")
            
            else:
                print(f"❌ 爬取失败: {result.get('error', '未知错误')}")
        
        else:
            print(f"❌ 连接测试失败: {diagnosis}")
            print("🔧 详细错误:")
            if details:
                for key, value in details.items():
                    print(f"  • {key}: {value}")
    
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 B站智能爬取器演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()