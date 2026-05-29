#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能爬取器选择器
默认使用API方案，自动切换到浏览器方案作为备选
"""

import logging
import time
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# 导入API爬取器
try:
    from api_crawler import ApiCrawler
    API_CRAWLER_AVAILABLE = True
except ImportError:
    API_CRAWLER_AVAILABLE = False
    logger.warning("API爬取器不可用，将使用浏览器模式")

# 导入浏览器爬取器
try:
    from browser_crawler import QuarkCampusScraper
    BROWSER_CRAWLER_AVAILABLE = True
except ImportError:
    BROWSER_CRAWLER_AVAILABLE = False
    logger.warning("浏览器爬取器不可用")


class CrawlerSelector:
    """智能爬取器选择器（API优先，浏览器备选）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化智能选择器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 爬取器实例
        self.api_crawler = None
        self.browser_crawler = None
        
        # 状态跟踪
        self.current_mode = "unknown"  # api, browser, mixed
        self.positions_extracted = 0
        self.start_time = None
        
        # 性能统计
        self.api_success_count = 0
        self.api_failure_count = 0
        self.browser_success_count = 0
        self.browser_failure_count = 0
        
        # 输出配置
        self.output_dir = self.config.get("output_dir", "output/positions")
        
        # 初始化爬取器
        self._initialize_crawlers()
        
        logger.info("智能爬取器选择器初始化完成")
        logger.info(f"API爬取器可用: {API_CRAWLER_AVAILABLE}")
        logger.info(f"浏览器爬取器可用: {BROWSER_CRAWLER_AVAILABLE}")
        logger.info(f"默认模式: {'api' if API_CRAWLER_AVAILABLE else 'browser'}")
    
    def _initialize_crawlers(self) -> None:
        """初始化所有可用的爬取器"""
        # 初始化API爬取器
        if API_CRAWLER_AVAILABLE:
            try:
                self.api_crawler = ApiCrawler()
                logger.info("API爬取器初始化成功")
            except Exception as e:
                logger.warning(f"API爬取器初始化失败: {str(e)}")
        
        # 初始化浏览器爬取器
        if BROWSER_CRAWLER_AVAILABLE:
            try:
                self.browser_crawler = QuarkCampusScraper(self.config)
                logger.info("浏览器爬取器初始化成功")
            except Exception as e:
                logger.warning(f"浏览器爬取器初始化失败: {str(e)}")
    
    def _test_api_availability(self) -> Tuple[bool, Optional[str]]:
        """
        测试API可用性
        
        Returns:
            (是否可用, 错误信息/None)
        """
        if not self.api_crawler:
            return False, "API爬取器未初始化"
        
        try:
            # 测试获取认证信息
            logger.info("测试API可用性...")
            
            # 尝试获取CSRF令牌（模拟）
            success = self.api_crawler.fetch_from_browser(max_wait=5)
            
            if success and self.api_crawler.csrf_token:
                logger.info("API可用性测试通过")
                return True, None
            else:
                return False, "无法获取认证信息"
                
        except Exception as e:
            return False, f"API测试失败: {str(e)}"
    
    def _test_browser_availability(self) -> Tuple[bool, Optional[str]]:
        """
        测试浏览器可用性
        
        Returns:
            (是否可用, 错误信息/None)
        """
        if not self.browser_crawler:
            return False, "浏览器爬取器未初始化"
        
        try:
            # 这里可以添加浏览器可用性测试
            # 例如检查浏览器服务状态、网络连接等
            
            logger.info("浏览器可用性测试通过（假设可用）")
            return True, None
            
        except Exception as e:
            return False, f"浏览器测试失败: {str(e)}"
    
    def select_crawler_mode(self) -> str:
        """
        智能选择爬取模式
        
        Returns:
            选择的模式: "api", "browser", "mixed", "none"
        """
        logger.info("正在智能选择爬取模式...")
        
        # 检查API可用性
        api_available, api_error = self._test_api_availability()
        
        # 检查浏览器可用性
        browser_available, browser_error = self._test_browser_availability()
        
        # 记录可用性状态
        logger.info(f"API可用: {api_available} ({api_error if not api_available else '正常'})")
        logger.info(f"浏览器可用: {browser_available} ({browser_error if not browser_available else '正常'})")
        
        # 决策逻辑
        if api_available:
            self.current_mode = "api"
            logger.info("✅ 选择API模式（优先）")
            return "api"
        
        elif browser_available:
            self.current_mode = "browser"
            logger.info("⚠️ 选择浏览器模式（API不可用）")
            return "browser"
        
        elif api_available and browser_available:
            # 混合模式：API获取列表，浏览器获取详情
            self.current_mode = "mixed"
            logger.info("🔄 选择混合模式（API+浏览器）")
            return "mixed"
        
        else:
            self.current_mode = "none"
            logger.error("❌ 没有可用的爬取模式")
            return "none"
    
    def crawl_via_api(self) -> Optional[Dict[str, Any]]:
        """
        通过API模式爬取数据
        
        Returns:
            爬取结果，失败返回None
        """
        if not self.api_crawler:
            logger.error("API爬取器不可用")
            return None
        
        try:
            logger.info("开始API模式爬取...")
            self.api_success_count += 1
            
            result = self.api_crawler.run(self.output_dir)
            
            if result.get("success"):
                self.positions_extracted = result.get("positions_extracted", 0)
                logger.info(f"API模式成功: {self.positions_extracted} 个岗位")
            else:
                self.api_failure_count += 1
                logger.warning(f"API模式失败: {result.get('error', '未知错误')}")
            
            return result
            
        except Exception as e:
            self.api_failure_count += 1
            logger.error(f"API模式异常: {str(e)}")
            return None
    
    def crawl_via_browser(self) -> Optional[Dict[str, Any]]:
        """
        通过浏览器模式爬取数据
        
        Returns:
            爬取结果，失败返回None
        """
        if not self.browser_crawler:
            logger.error("浏览器爬取器不可用")
            return None
        
        try:
            logger.info("开始浏览器模式爬取...")
            self.browser_success_count += 1
            
            # 调用现有的浏览器爬取器
            result = self.browser_crawler.scrape_positions()
            
            if result and result.get("total_positions_found", 0) > 0:
                self.positions_extracted = result.get("total_positions_found", 0)
                logger.info(f"浏览器模式成功: {self.positions_extracted} 个岗位")
            else:
                self.browser_failure_count += 1
                logger.warning("浏览器模式失败或没有获取到数据")
            
            return result
            
        except Exception as e:
            self.browser_failure_count += 1
            logger.error(f"浏览器模式异常: {str(e)}")
            return None
    
    def crawl_via_mixed(self) -> Optional[Dict[str, Any]]:
        """
        通过混合模式爬取数据（API获取列表，浏览器获取详情）
        
        Returns:
            爬取结果，失败返回None
        """
        logger.info("开始混合模式爬取...")
        
        # 这里可以实现更复杂的混合逻辑
        # 例如：API获取岗位列表，浏览器获取详情页数据
        
        # 临时实现：先尝试API，失败则切换到浏览器
        api_result = self.crawl_via_api()
        
        if api_result and api_result.get("success"):
            logger.info("混合模式：API部分成功，使用API结果")
            return api_result
        else:
            logger.info("混合模式：API失败，切换到浏览器")
            return self.crawl_via_browser()
    
    def smart_crawl(self) -> Dict[str, Any]:
        """
        智能爬取：自动选择最佳模式并执行
        
        Returns:
            爬取结果统计
        """
        self.start_time = time.time()
        
        logger.info("=" * 60)
        logger.info("开始智能爬取")
        logger.info("=" * 60)
        
        try:
            # 1. 智能选择模式
            mode = self.select_crawler_mode()
            
            if mode == "none":
                return {
                    "success": False,
                    "error": "没有可用的爬取模式",
                    "mode": "none",
                    "positions_extracted": 0
                }
            
            # 2. 根据模式执行爬取
            result = None
            
            if mode == "api":
                result = self.crawl_via_api()
            elif mode == "browser":
                result = self.crawl_via_browser()
            elif mode == "mixed":
                result = self.crawl_via_mixed()
            
            # 3. 处理结果
            end_time = time.time()
            elapsed_time = end_time - self.start_time
            
            if result and result.get("success"):
                final_result = {
                    "success": True,
                    "mode": mode,
                    "positions_extracted": result.get("positions_extracted", 0),
                    "elapsed_time_seconds": elapsed_time,
                    "completion_percentage": result.get("completion_percentage", 0),
                    "save_path": result.get("save_path", ""),
                    "performance_stats": {
                        "api_success": self.api_success_count,
                        "api_failure": self.api_failure_count,
                        "browser_success": self.browser_success_count,
                        "browser_failure": self.browser_failure_count
                    },
                    "raw_result": result
                }
                
                logger.info("=" * 60)
                logger.info(f"智能爬取完成 ({mode}模式)")
                logger.info(f"获取岗位: {final_result['positions_extracted']} 个")
                logger.info(f"耗时: {elapsed_time:.2f} 秒")
                logger.info("=" * 60)
                
                return final_result
            else:
                return {
                    "success": False,
                    "error": result.get("error", "爬取失败") if result else "未知错误",
                    "mode": mode,
                    "positions_extracted": self.positions_extracted,
                    "elapsed_time_seconds": elapsed_time,
                    "performance_stats": {
                        "api_success": self.api_success_count,
                        "api_failure": self.api_failure_count,
                        "browser_success": self.browser_success_count,
                        "browser_failure": self.browser_failure_count
                    }
                }
                
        except Exception as e:
            elapsed_time = time.time() - self.start_time
            logger.error(f"智能爬取异常: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "mode": self.current_mode,
                "positions_extracted": self.positions_extracted,
                "elapsed_time_seconds": elapsed_time,
                "performance_stats": {
                    "api_success": self.api_success_count,
                    "api_failure": self.api_failure_count,
                    "browser_success": self.browser_success_count,
                    "browser_failure": self.browser_failure_count
                }
            }
    
    def force_mode(self, mode: str) -> Optional[Dict[str, Any]]:
        """
        强制使用指定模式爬取
        
        Args:
            mode: 强制模式 ("api", "browser", "mixed")
            
        Returns:
            爬取结果
        """
        logger.info(f"强制使用 {mode} 模式爬取")
        
        self.start_time = time.time()
        self.current_mode = mode
        
        if mode == "api":
            return self.crawl_via_api()
        elif mode == "browser":
            return self.crawl_via_browser()
        elif mode == "mixed":
            return self.crawl_via_mixed()
        else:
            logger.error(f"不支持的模式: {mode}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取当前状态
        
        Returns:
            状态信息
        """
        return {
            "current_mode": self.current_mode,
            "positions_extracted": self.positions_extracted,
            "api_available": bool(self.api_crawler),
            "browser_available": bool(self.browser_crawler),
            "performance_stats": {
                "api_success": self.api_success_count,
                "api_failure": self.api_failure_count,
                "browser_success": self.browser_success_count,
                "browser_failure": self.browser_failure_count
            },
            "output_dir": self.output_dir
        }


def test_crawler_selector():
    """测试智能爬取器选择器"""
    import sys
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/crawler_selector.log", encoding='utf-8')
        ]
    )
    
    try:
        # 创建配置
        config = {
            "output_dir": "output/positions",
            "max_positions": 92,
            "categories": ["产品类", "运营类", "数据类", "市场拓展", "销售类", "游戏类", "金融类"]
        }
        
        # 创建智能选择器
        selector = CrawlerSelector(config)
        
        # 显示状态
        status = selector.get_status()
        print(f"\n📊 当前状态:")
        print(f"   当前模式: {status['current_mode']}")
        print(f"   API可用: {status['api_available']}")
        print(f"   浏览器可用: {status['browser_available']}")
        print(f"   已获取岗位: {status['positions_extracted']}")
        
        # 执行智能爬取
        print(f"\n🚀 开始智能爬取...")
        result = selector.smart_crawl()
        
        if result["success"]:
            print(f"\n✅ 智能爬取成功!")
            print(f"   模式: {result['mode']}")
            print(f"   获取岗位: {result['positions_extracted']}")
            print(f"   完成比例: {result.get('completion_percentage', 0):.1f}%")
            print(f"   耗时: {result['elapsed_time_seconds']:.2f} 秒")
            
            if result.get('save_path'):
                print(f"   保存路径: {result['save_path']}")
        else:
            print(f"\n❌ 智能爬取失败: {result.get('error', '未知错误')}")
        
        return result
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    test_crawler_selector()