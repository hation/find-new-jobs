#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘爬取器示例
基于夸克完整架构的智能爬取器框架
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src/framework"))

from framework.smart_crawler_selector import SmartCrawlerSelector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KsAPICrawler:
    """快手API爬取器（示例）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.base_url = self.config.get("api_base_url", "https://job.ksyun.com/api")
        self.api_key = self.config.get("api_key", "")
        self.api_secret = self.config.get("api_secret", "")
        
    def fetch_positions(self, page: int = 1, page_size: int = 10) -> List[Dict[str, Any]]:
        """从API获取岗位列表"""
        logger.info(f"📡 API模式：获取第{page}页，每页{page_size}条")
        
        # 这里应该是实际的API调用
        # 示例数据
        positions = [
            {
                "positionId": f"KS2024001_{page}_{i}",
                "positionName": "后端开发工程师",
                "workLocation": "北京",
                "positionCategory": "技术类",
                "publishTime": "2024-03-15 10:00:00",
                "detailUrl": f"https://job.ksyun.com/position/KS2024001_{page}_{i}"
            }
            for i in range(1, min(page_size, 5) + 1)
        ]
        
        logger.info(f"✅ API模式：获取到 {len(positions)} 个岗位")
        return positions
    
    def fetch_position_detail(self, position_id: str) -> Dict[str, Any]:
        """获取岗位详情"""
        logger.info(f"📡 API模式：获取岗位详情 {position_id}")
        
        # 这里应该是实际的API调用获取详情
        detail = {
            "positionId": position_id,
            "department": "快手主站技术部",
            "educationRequirement": "本科及以上",
            "workExperience": "应届生",
            "jobResponsibilities": "1. 负责快手主站后端系统开发\n2. 参与系统架构设计和性能优化\n3. 编写高质量、可维护的代码",
            "jobRequirements": "1. 熟悉Java/Python/Go至少一种语言\n2. 了解分布式系统原理\n3. 有良好的算法和数据结构基础",
            "salaryRange": "面议"
        }
        
        logger.info(f"✅ API模式：获取到岗位详情 {position_id}")
        return detail


class KsBrowserCrawler:
    """快手浏览器爬取器（示例）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.base_url = self.config.get("website_url", "https://job.ksyun.com")
        
    def fetch_positions(self, page: int = 1, page_size: int = 10) -> List[Dict[str, Any]]:
        """从网页获取岗位列表"""
        logger.info(f"🌐 浏览器模式：获取第{page}页，每页{page_size}条")
        
        # 这里应该是实际的浏览器爬取
        # 示例数据
        positions = [
            {
                "positionId": f"KS2024002_{page}_{i}",
                "positionName": "前端开发工程师",
                "workLocation": "上海",
                "positionCategory": "技术类",
                "publishTime": "2024-03-16 14:00:00",
                "detailUrl": f"https://job.ksyun.com/position/KS2024002_{page}_{i}"
            }
            for i in range(1, min(page_size, 5) + 1)
        ]
        
        logger.info(f"✅ 浏览器模式：获取到 {len(positions)} 个岗位")
        return positions
    
    def fetch_position_detail(self, position_id: str) -> Dict[str, Any]:
        """获取岗位详情"""
        logger.info(f"🌐 浏览器模式：获取岗位详情 {position_id}")
        
        # 这里应该是实际的浏览器爬取获取详情
        detail = {
            "positionId": position_id,
            "department": "快手前端技术部",
            "educationRequirement": "本科及以上",
            "workExperience": "1-3年",
            "jobResponsibilities": "1. 负责快手前端页面开发\n2. 优化前端性能体验\n3. 参与前端组件库建设",
            "jobRequirements": "1. 熟悉React/Vue等前端框架\n2. 掌握HTML5/CSS3/JavaScript\n3. 有移动端开发经验者优先",
            "salaryRange": "20-40k"
        }
        
        logger.info(f"✅ 浏览器模式：获取到岗位详情 {position_id}")
        return detail


class KsJobCrawler(SmartCrawlerSelector):
    """快手招聘爬取器（基于智能选择器框架）"""
    
    def __init__(self):
        # 读取配置
        config = self._load_config()
        super().__init__(config)
        
        # 设置公司名称
        self.company_name = "快手"
        
        logger.info(f"🚀 初始化快手招聘爬取器")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config", ".env"
        )
        
        config = {
            "company_name": "快手",
            "website_url": "https://job.ksyun.com",
            "api_base_url": "https://job.ksyun.com/api",
            "output_dir": "output/ks_data"
        }
        
        # 尝试读取环境配置文件
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                config[key.strip()] = value.strip()
            except Exception as e:
                logger.warning(f"读取配置文件失败: {e}")
        
        return config
    
    def _initialize_primary_crawler(self):
        """初始化主爬取器（API）"""
        logger.info("🔄 初始化主爬取器（API模式）")
        return KsAPICrawler(self.config)
    
    def _initialize_fallback_crawler(self):
        """初始化备选爬取器（浏览器）"""
        logger.info("🔄 初始化备选爬取器（浏览器模式）")
        return KsBrowserCrawler(self.config)
    
    def _extract_position_data(self, position: Dict[str, Any]) -> Dict[str, Any]:
        """提取岗位数据（统一数据格式）"""
        # 基础字段
        data = {
            "positionId": position.get("positionId", ""),
            "positionName": position.get("positionName", ""),
            "workLocation": position.get("workLocation", ""),
            "positionCategory": position.get("positionCategory", ""),
            "publishTime": position.get("publishTime", ""),
            "detailUrl": position.get("detailUrl", ""),
            "department": position.get("department", ""),
            "educationRequirement": position.get("educationRequirement", ""),
            "workExperience": position.get("workExperience", ""),
            "jobResponsibilities": position.get("jobResponsibilities", ""),
            "jobRequirements": position.get("jobRequirements", ""),
            "salaryRange": position.get("salaryRange", ""),
            "company": self.company_name,
            "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "crawlMode": self.current_mode
        }
        
        return data
    
    def _save_position_data(self, data: Dict[str, Any]):
        """保存岗位数据"""
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ks_position_{data['positionId']}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # 保存数据
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 保存岗位数据: {filepath}")
        return filepath
    
    def crawl_positions(self, max_pages: int = 2, items_per_page: int = 5) -> List[Dict[str, Any]]:
        """爬取岗位数据"""
        logger.info(f"🚀 开始爬取快手招聘数据（{max_pages}页，每页{items_per_page}条）")
        
        all_positions = []
        self.start_time = datetime.now()
        
        for page in range(1, max_pages + 1):
            logger.info(f"📄 处理第 {page}/{max_pages} 页")
            
            try:
                # 获取岗位列表
                if self.current_mode == "api" and self.primary_crawler:
                    positions = self.primary_crawler.fetch_positions(page, items_per_page)
                elif self.fallback_crawler:
                    positions = self.fallback_crawler.fetch_positions(page, items_per_page)
                else:
                    logger.error("没有可用的爬取器")
                    break
                
                # 处理每个岗位
                for position in positions:
                    try:
                        # 获取岗位详情
                        if self.current_mode == "api" and self.primary_crawler:
                            detail = self.primary_crawler.fetch_position_detail(position["positionId"])
                        elif self.fallback_crawler:
                            detail = self.fallback_crawler.fetch_position_detail(position["positionId"])
                        else:
                            detail = {}
                        
                        # 合并数据
                        position.update(detail)
                        
                        # 提取统一格式数据
                        data = self._extract_position_data(position)
                        
                        # 保存数据
                        self._save_position_data(data)
                        
                        # 添加到结果列表
                        all_positions.append(data)
                        
                        self.data_extracted += 1
                        logger.info(f"✅ 成功提取岗位: {data['positionName']} ({data['positionId']})")
                        
                    except Exception as e:
                        logger.error(f"❌ 处理岗位失败 {position.get('positionId', 'unknown')}: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"❌ 处理第{page}页失败: {e}")
                # 尝试切换到备选模式
                if self.current_mode == "api":
                    logger.info("🔄 尝试切换到浏览器模式")
                    self.current_mode = "browser"
                continue
        
        # 统计信息
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        logger.info(f"📊 爬取完成统计:")
        logger.info(f"   • 总用时: {elapsed_time:.2f}秒")
        logger.info(f"   • 提取岗位: {self.data_extracted}个")
        logger.info(f"   • 爬取模式: {self.current_mode}")
        logger.info(f"   • 数据保存到: {self.output_dir}")
        
        return all_positions


def main():
    """主函数"""
    print("=" * 70)
    print("🚀 快手招聘数据爬取器")
    print("=" * 70)
    print("基于夸克完整架构的智能爬取器框架")
    print()
    
    # 创建爬取器
    crawler = KsJobCrawler()
    
    # 运行爬取
    print("📡 开始爬取数据...")
    print()
    
    try:
        # 先尝试API模式
        crawler.current_mode = "api"
        crawler.primary_crawler = crawler._initialize_primary_crawler()
        
        # 爬取数据
        positions = crawler.crawl_positions(max_pages=2, items_per_page=3)
        
        print()
        print("📊 爬取结果:")
        print(f"   • 成功爬取 {len(positions)} 个岗位")
        print(f"   • 使用模式: {crawler.current_mode}")
        print(f"   • 数据保存到: {crawler.output_dir}")
        print()
        
        # 显示前几个岗位
        if positions:
            print("📋 爬取的岗位示例:")
            for i, position in enumerate(positions[:3], 1):
                print(f"  {i}. {position['positionName']} - {position['workLocation']}")
        
        print()
        print("✅ 爬取完成！")
        
    except Exception as e:
        print(f"❌ 爬取失败: {e}")
        print("🔄 尝试切换到浏览器模式...")
        
        try:
            crawler.current_mode = "browser"
            crawler.fallback_crawler = crawler._initialize_fallback_crawler()
            
            positions = crawler.crawl_positions(max_pages=1, items_per_page=2)
            
            print(f"✅ 浏览器模式成功爬取 {len(positions)} 个岗位")
            
        except Exception as e2:
            print(f"❌ 浏览器模式也失败: {e2}")
            print("💡 请检查网络连接或网站配置")
    
    print("=" * 70)


if __name__ == "__main__":
    main()