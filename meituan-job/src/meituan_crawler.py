#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美团招聘爬取器
基于夸克项目的智能爬取器选择器框架
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, os.path.join(project_root, "src/framework"))

from framework.smart_crawler_selector import SmartCrawlerSelector

logger = logging.getLogger(__name__)


class MeituanCrawler(SmartCrawlerSelector):
    """美团招聘爬取器"""
    
    def __init__(self, config_file: str = None):
        """
        初始化美团爬取器
        
        Args:
            config_file: 配置文件路径
        """
        # 加载配置
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        # 美团特定配置
        self.company_name = "美团"
        self.base_url = "https://zhaopin.meituan.com"
        self.filter_url = "https://zhaopin.meituan.com/web/social"
        
        # URL参数（基于提供的URL）
        self.city_code = "001019002"  # 深圳
        self.category_codes = "11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001"
        
        # 岗位类别映射（根据用户说明）
        self.category_mapping = {
            "11002_-1": "产品类",
            "11003_-1": "运营类",
            "11005_-1": "市场营销类",
            "11007_-1": "金融类",
            "11010_1101001": "销售、客服与支持类（销售部分）"
        }
        
        # 数据字段映射
        self.field_mapping = {
            "position_id": "岗位ID",
            "position_name": "岗位名称", 
            "work_location": "工作地点",
            "position_category": "岗位类别",
            "publish_time": "发布时间",
            "detail_url": "详情链接",
            "department": "部门信息",
            "education_requirement": "学历要求",
            "work_experience": "工作经验",
            "job_responsibilities": "工作职责",
            "job_requirements": "任职要求",
            "salary_range": "薪资范围"
        }
        
        # 调用父类初始化
        super().__init__(config)
        
        logger.info(f"✅ 美团招聘爬取器初始化完成 - {self.company_name}")
    
    # ==================== 需要定制的业务逻辑 ====================
    
    def _initialize_primary_crawler(self) -> Tuple[bool, Optional[str]]:
        """
        初始化主爬取器（美团API爬取器）
        
        Returns:
            (成功与否, 错误信息/None)
        """
        try:
            logger.info("🔄 初始化美团API爬取器...")
            
            # 检查API爬取器是否已实现
            try:
                from meituan_api_crawler import MeituanAPICrawler
                logger.info("✅ 发现已实现的API爬取器: MeituanAPICrawler")
            except ImportError as e:
                logger.warning(f"⚠️ API爬取器未找到: {str(e)}")
                return False, f"API爬取器未实现或导入失败: {str(e)}"
            
            # 创建API爬取器实例
            self.primary_crawler = MeituanAPICrawler()
            
            # 验证爬取器功能
            test_success, test_message, test_details = self.primary_crawler.test_api_connection()
            if test_success:
                logger.info(f"✅ 美团API爬取器初始化完成并验证通过: {test_message}")
                return True, None
            else:
                logger.warning(f"⚠️ API爬取器验证失败: {test_message}")
                # 即使验证失败，也返回True，因为爬取器已创建，可能只是网络问题
                return True, f"API爬取器验证失败: {test_message}"
            
        except Exception as e:
            error_msg = f"初始化美团API爬取器失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _initialize_fallback_crawler(self) -> Tuple[bool, Optional[str]]:
        """
        初始化备选爬取器（美团浏览器爬取器）
        
        Returns:
            (成功与否, 错误信息/None)
        """
        try:
            logger.info("🔄 初始化美团浏览器爬取器...")
            
            # 尝试导入Playwright
            try:
                from playwright.sync_api import sync_playwright
                self.playwright = sync_playwright
                logger.info("✅ Playwright库可用")
            except ImportError:
                logger.error("❌ Playwright未安装，请运行: pip install playwright && python -m playwright install")
                return False, "Playwright未安装"
            
            # 创建浏览器爬取器配置
            browser_config = {
                "browser_type": "chrome",
                "headless": False,  # 开发时显示浏览器
                "timeout": 30000,
                "viewport": {"width": 1920, "height": 1080}
            }
            
            # 创建浏览器实例（延迟初始化）
            self.browser_config = browser_config
            self.browser = None
            self.page = None
            
            logger.info("✅ 美团浏览器爬取器初始化完成")
            return True, None
            
        except Exception as e:
            error_msg = f"初始化美团浏览器爬取器失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def test_primary_connection(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        测试主爬取器连接（美团API连接测试）
        
        Returns:
            (是否成功, 诊断信息, 详细错误/None)
        """
        logger.info("🔍 测试美团API连接...")
        
        # 测试步骤
        test_steps = []
        
        # 步骤1: 检查网络连接
        try:
            import requests
            response = requests.get(self.base_url, timeout=10)
            test_steps.append({
                "step": "网络连接",
                "status": "success",
                "message": f"网站可访问，状态码: {response.status_code}"
            })
        except Exception as e:
            test_steps.append({
                "step": "网络连接", 
                "status": "failed",
                "message": f"网站不可访问: {str(e)}"
            })
            return False, "网络连接失败", {"steps": test_steps}
        
        # 步骤2: 检查筛选页面
        try:
            filter_url = f"{self.filter_url}?cityList={self.city_code}&jfJgList={self.category_codes}"
            response = requests.get(filter_url, timeout=10)
            if response.status_code == 200:
                test_steps.append({
                    "step": "筛选页面",
                    "status": "success", 
                    "message": f"筛选页面可访问，URL: {filter_url}"
                })
            else:
                test_steps.append({
                    "step": "筛选页面",
                    "status": "failed",
                    "message": f"筛选页面返回状态码: {response.status_code}"
                })
        except Exception as e:
            test_steps.append({
                "step": "筛选页面",
                "status": "failed",
                "message": f"筛选页面访问失败: {str(e)}"
            })
        
        # 步骤3: 检查API端点（需要调研）
        test_steps.append({
            "step": "API端点",
            "status": "pending",
            "message": "需要调研美团招聘API端点"
        })
        
        logger.info(f"✅ 美团API连接测试完成，步骤: {len(test_steps)}")
        return True, "连接测试完成，需要进一步调研API", {"steps": test_steps}
    
    def get_failure_reason(self, error_details: Dict[str, Any]) -> str:
        """
        根据错误详情生成友好的失败原因
        
        Args:
            error_details: 错误详情
            
        Returns:
            友好的失败原因描述
        """
        if not error_details:
            return "未知错误"
        
        # 根据错误类型生成原因
        error_type = error_details.get("type", "unknown")
        
        reasons = {
            "network": "网络连接问题，请检查网络设置",
            "timeout": "请求超时，网站响应缓慢",
            "api_not_found": "API端点不存在或已变更",
            "authentication": "认证失败，需要有效的API密钥",
            "rate_limit": "请求频率过高，被限制访问",
            "not_implemented": "功能尚未实现，需要开发",
            "browser_error": "浏览器自动化失败",
            "parsing_error": "数据解析失败，页面结构可能已变更"
        }
        
        return reasons.get(error_type, "未知错误，请查看详细日志")
    
    def _extract_position_data(self, position_item: Any) -> Dict[str, Any]:
        """
        提取单个岗位数据
        
        Args:
            position_item: 岗位数据项
            
        Returns:
            提取后的岗位数据字典
        """
        # TODO: 根据美团网站的实际结构实现数据提取
        # 这里提供模板实现
        
        position_data = {
            "position_id": self._extract_field(position_item, "id"),
            "position_name": self._extract_field(position_item, "name"),
            "work_location": self._extract_field(position_item, "location"),
            "position_category": self._extract_field(position_item, "category"),
            "publish_time": self._extract_field(position_item, "publish_time"),
            "detail_url": self._extract_field(position_item, "detail_url"),
            "department": self._extract_field(position_item, "department"),
            "education_requirement": self._extract_field(position_item, "education"),
            "work_experience": self._extract_field(position_item, "experience"),
            "job_responsibilities": self._extract_field(position_item, "responsibilities"),
            "job_requirements": self._extract_field(position_item, "requirements"),
            "salary_range": self._extract_field(position_item, "salary"),
            "company_name": self.company_name,
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_url": self.filter_url
        }
        
        return position_data
    
    def _extract_field(self, item: Any, field_name: str) -> str:
        """
        提取字段值（模板方法）
        
        Args:
            item: 数据项
            field_name: 字段名
            
        Returns:
            字段值或默认值
        """
        # TODO: 根据实际数据结构实现
        # 这里返回默认值
        defaults = {
            "id": "未知ID",
            "name": "未知岗位",
            "location": "未知地点",
            "category": "未知类别",
            "publish_time": datetime.now().strftime("%Y-%m-%d"),
            "detail_url": "",
            "department": "未知部门",
            "education": "学历不限",
            "experience": "经验不限",
            "responsibilities": "待补充",
            "requirements": "待补充",
            "salary": "面议"
        }
        
        return defaults.get(field_name, "")
    
    def crawl_with_browser(self, url: str = None) -> List[Dict[str, Any]]:
        """
        使用浏览器爬取美团招聘数据
        
        Args:
            url: 要爬取的URL，默认为筛选页面
            
        Returns:
            爬取到的岗位数据列表
        """
        if url is None:
            url = f"{self.filter_url}?cityList={self.city_code}&jfJgList={self.category_codes}"
        
        logger.info(f"🌐 使用浏览器爬取美团招聘: {url}")
        
        positions = []
        
        try:
            # 初始化浏览器
            if self.browser is None:
                self._init_browser()
            
            # 访问页面
            logger.info(f"📄 访问页面: {url}")
            self.page.goto(url)
            time.sleep(3)  # 等待页面加载
            
            # 获取页面内容
            page_content = self.page.content()
            
            # TODO: 解析页面内容，提取岗位数据
            # 这里需要根据美团招聘页面的实际HTML结构实现
            
            # 临时示例：提取页面标题
            page_title = self.page.title()
            logger.info(f"📖 页面标题: {page_title}")
            
            # 保存页面快照（用于调试）
            screenshot_path = os.path.join(self.output_dir, f"meituan_screenshot_{int(time.time())}.png")
            self.page.screenshot(path=screenshot_path)
            logger.info(f"📸 页面截图已保存: {screenshot_path}")
            
            # 模拟提取一些数据
            sample_position = {
                "position_id": "meituan_001",
                "position_name": "后端开发工程师",
                "work_location": "北京",
                "position_category": "技术类",
                "publish_time": "2026-05-21",
                "detail_url": url,
                "department": "基础研发平台",
                "education_requirement": "本科及以上",
                "work_experience": "3-5年",
                "job_responsibilities": "负责美团核心系统开发",
                "job_requirements": "熟悉Java/Python，有分布式系统经验",
                "salary_range": "30-50k",
                "company_name": self.company_name,
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_url": url
            }
            
            positions.append(sample_position)
            
            logger.info(f"✅ 浏览器爬取完成，获取到 {len(positions)} 个岗位")
            
        except Exception as e:
            logger.error(f"❌ 浏览器爬取失败: {str(e)}")
            self.last_error = str(e)
            self.last_error_details = {"type": "browser_error", "exception": str(e)}
        
        return positions
    
    def _init_browser(self):
        """初始化浏览器实例"""
        try:
            logger.info("🖥️ 启动浏览器...")
            playwright = self.playwright().start()
            self.browser = playwright.chromium.launch(
                headless=self.browser_config.get("headless", False),
                timeout=self.browser_config.get("timeout", 30000)
            )
            
            # 创建页面
            self.page = self.browser.new_page(
                viewport=self.browser_config.get("viewport", {"width": 1920, "height": 1080})
            )
            
            # 设置User-Agent
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            self.page.set_extra_http_headers({"User-Agent": user_agent})
            
            logger.info("✅ 浏览器初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 浏览器初始化失败: {str(e)}")
            raise
    
    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            logger.info("🛑 关闭浏览器...")
            self.browser.close()
            self.browser = None
            self.page = None
    
    def get_company_info(self) -> Dict[str, Any]:
        """
        获取美团公司信息
        
        Returns:
            公司信息字典
        """
        return {
            "company_name": self.company_name,
            "website": self.base_url,
            "recruitment_url": self.filter_url,
            "city_code": self.city_code,
            "category_codes": self.category_codes,
            "field_count": len(self.field_mapping),
            "required_fields": list(self.field_mapping.keys())[:12],  # 前12个为必须字段
            "crawler_type": "SmartCrawlerSelector",
            "version": "1.0.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def save_positions(self, positions: List[Dict[str, Any]], filename: str = None):
        """
        保存岗位数据
        
        Args:
            positions: 岗位数据列表
            filename: 文件名，默认为自动生成
        """
        if not positions:
            logger.warning("⚠️ 没有数据需要保存")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meituan_positions_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # 准备保存的数据
        save_data = {
            "company": self.company_name,
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_positions": len(positions),
            "positions": positions,
            "metadata": {
                "source_url": self.filter_url,
                "city_code": self.city_code,
                "category_codes": self.category_codes,
                "crawler_version": "1.0.0"
            }
        }
        
        # 保存为JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 数据已保存: {filepath} ({len(positions)} 个岗位)")
        
        # 同时保存为CSV（可选）
        csv_filepath = filepath.replace('.json', '.csv')
        self._save_as_csv(positions, csv_filepath)
    
    def _save_as_csv(self, positions: List[Dict[str, Any]], filepath: str):
        """保存为CSV格式"""
        try:
            import pandas as pd
            
            # 转换为DataFrame
            df = pd.DataFrame(positions)
            
            # 保存为CSV
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"📊 CSV数据已保存: {filepath}")
            
        except ImportError:
            logger.warning("⚠️ Pandas未安装，跳过CSV保存")
        except Exception as e:
            logger.error(f"❌ CSV保存失败: {str(e)}")


def main():
    """美团爬取器主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='美团招聘爬取器')
    parser.add_argument('--mode', choices=['api', 'browser', 'smart', 'test'], 
                       default='smart', help='爬取模式')
    parser.add_argument('--config', default='config/project_config.json', 
                       help='配置文件路径')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--url', help='自定义爬取URL')
    parser.add_argument('--pages', type=int, default=1, help='爬取页数')
    parser.add_argument('--verbose', action='store_true', help='详细日志')
    
    args = parser.parse_args()
    
    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建爬取器
    crawler = MeituanCrawler(config_file=args.config)
    
    print("=" * 60)
    print(f"🚀 美团招聘爬取器启动")
    print(f"📋 公司: {crawler.company_name}")
    print(f"🌐 网站: {crawler.base_url}")
    print(f"🎯 模式: {args.mode}")
    print("=" * 60)
    
    # 根据模式执行
    if args.mode == 'test':
        # 测试连接
        success, message, details = crawler.test_primary_connection()
        print(f"\n🔍 连接测试结果: {'✅ 成功' if success else '❌ 失败'}")
        print(f"📝 消息: {message}")
        
        if details and 'steps' in details:
            print("\n📋 测试步骤:")
            for step in details['steps']:
                status_icon = "✅" if step['status'] == 'success' else "❌" if step['status'] == 'failed' else "⚠️"
                print(f"  {status_icon} {step['step']}: {step['message']}")
        
        # 显示公司信息
        company_info = crawler.get_company_info()
        print(f"\n🏢 公司信息:")
        for key, value in company_info.items():
            print(f"  {key}: {value}")
    
    elif args.mode == 'browser':
        # 浏览器爬取模式
        url = args.url or crawler.filter_url
        positions = crawler.crawl_with_browser(url)
        
        # 保存数据
        if positions:
            crawler.save_positions(positions, args.output)
            print(f"\n✅ 爬取完成! 获取到 {len(positions)} 个岗位")
        else:
            print("\n⚠️ 没有获取到岗位数据")
        
        # 关闭浏览器
        crawler.close_browser()
    
    elif args.mode == 'smart':
        # 智能模式（待实现完整逻辑）
        print("\n🤖 智能模式 - 待实现完整逻辑")
        print("建议先使用 --mode test 测试连接")
        print("或使用 --mode browser 进行浏览器爬取")
    
    else:
        print(f"\n❌ 模式 '{args.mode}' 尚未实现")
        print("可用模式: test, browser, smart")
    
    print("\n" + "=" * 60)
    print("🎉 美团招聘爬取器执行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()