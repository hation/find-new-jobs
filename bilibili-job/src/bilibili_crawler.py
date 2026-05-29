#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili数据爬取器
基于夸克项目完整框架的B站数据爬取实现
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys_path_added = False
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    sys_path_added = True
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))
if str(project_root / "src/framework") not in sys.path:
    sys.path.insert(0, str(project_root / "src/framework"))

try:
    from framework.smart_crawler_selector import SmartCrawlerSelector
    from framework.data_exporter import DataExporter
except ImportError as e:
    print(f"❌ 导入框架失败: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BilibiliCrawler(SmartCrawlerSelector):
    """B站数据爬取器"""
    
    def __init__(self, company_name: str = "bilibili"):
        """
        初始化B站爬取器
        
        Args:
            company_name: 公司名称，默认为"bilibili"
        """
        config = {
            "company_name": company_name,
            "output_dir": f"output/{company_name}",
            "data_dir": f"data/{company_name}",
            "log_dir": f"logs/{company_name}"
        }
        super().__init__(config)
        
        # B站特定配置
        self.base_url = "https://www.bilibili.com"
        self.job_portal_url = "https://jobs.bilibili.com"
        self.api_base_url = "https://api.bilibili.com"
        
        # 数据存储
        self.data_dir = Path("data/bilibili")
        self.output_dir = Path("output/bilibili")
        self.log_dir = Path("logs/bilibili")
        
        # 创建目录
        for directory in [self.data_dir, self.output_dir, self.log_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🚀 初始化B站爬取器: {company_name}")
        logger.info(f"📁 数据目录: {self.data_dir}")
        logger.info(f"📁 输出目录: {self.output_dir}")
    
    def _initialize_primary_crawler(self) -> Dict[str, Any]:
        """
        初始化API爬取器（首选方案）
        
        Returns:
            爬取器配置字典
        """
        logger.info("🎯 初始化B站API爬取器")
        
        # 加载API配置
        api_config = self._load_api_config()
        
        return {
            "name": "B站API爬取器",
            "type": "api",
            "status": "ready" if api_config else "config_required",
            "config": api_config,
            "description": "通过B站官方API获取数据（高效、稳定）"
        }
    
    def _initialize_fallback_crawler(self) -> Dict[str, Any]:
        """
        初始化浏览器爬取器（备选方案）
        
        Returns:
            爬取器配置字典
        """
        logger.info("🔄 初始化B站浏览器爬取器")
        
        # 加载浏览器配置
        browser_config = self._load_browser_config()
        
        return {
            "name": "B站浏览器爬取器",
            "type": "browser",
            "status": "ready" if browser_config else "config_required",
            "config": browser_config,
            "description": "通过浏览器模拟用户操作获取数据（兼容性好）"
        }
    
    def _load_api_config(self) -> Optional[Dict[str, Any]]:
        """加载API配置"""
        config_path = Path("config/api_auth.json")
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 检查B站API配置
                bilibili_config = config.get("bilibili", {})
                if bilibili_config:
                    logger.info("✅ 加载B站API配置成功")
                    return bilibili_config
                else:
                    logger.warning("⚠️ 配置文件中缺少B站API配置")
                    return None
            except Exception as e:
                logger.error(f"❌ 加载API配置失败: {e}")
                return None
        else:
            logger.warning("⚠️ API配置文件不存在: config/api_auth.json")
            return None
    
    def _load_browser_config(self) -> Optional[Dict[str, Any]]:
        """加载浏览器配置"""
        config_path = Path("config/browser_config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info("✅ 加载浏览器配置成功")
                return config
            except Exception as e:
                logger.error(f"❌ 加载浏览器配置失败: {e}")
                return None
        else:
            logger.warning("⚠️ 浏览器配置文件不存在: config/browser_config.json")
            return None
    
    def crawl_jobs(self, max_pages: int = 10, category: str = None) -> List[Dict[str, Any]]:
        """
        爬取B站岗位数据
        
        Args:
            max_pages: 最大爬取页数
            category: 岗位类别（可选）
            
        Returns:
            岗位数据列表
        """
        logger.info(f"📡 开始爬取B站岗位数据，最多{max_pages}页")
        
        # 选择爬取策略
        crawler_info = self.select_crawler()
        logger.info(f"📊 选择爬取策略: {crawler_info.get('name')}")
        
        all_jobs = []
        
        if crawler_info.get("type") == "api":
            # 使用API爬取
            jobs = self._crawl_jobs_via_api(max_pages, category)
        else:
            # 使用浏览器爬取
            jobs = self._crawl_jobs_via_browser(max_pages, category)
        
        # 保存数据
        if jobs:
            self._save_jobs(jobs)
            all_jobs.extend(jobs)
        
        logger.info(f"✅ 爬取完成，共获取{len(all_jobs)}个岗位")
        return all_jobs
    
    def _crawl_jobs_via_api(self, max_pages: int, category: str = None) -> List[Dict[str, Any]]:
        """
        通过API爬取岗位数据
        
        Args:
            max_pages: 最大页数
            category: 岗位类别
            
        Returns:
            岗位数据列表
        """
        logger.info("🌐 使用API模式爬取数据")
        
        # 这里应该实现实际的API请求逻辑
        # 暂时返回模拟数据
        
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
                "salary_range": "30-50K",
                "tags": ["Go", "Python", "微服务", "分布式"]
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
                "salary_range": "25-40K",
                "tags": ["产品设计", "用户研究", "数据分析"]
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
                "salary_range": "15-25K",
                "tags": ["内容运营", "社区管理", "视频制作"]
            }
        ]
        
        return mock_jobs
    
    def _crawl_jobs_via_browser(self, max_pages: int, category: str = None) -> List[Dict[str, Any]]:
        """
        通过浏览器爬取岗位数据
        
        Args:
            max_pages: 最大页数
            category: 岗位类别
            
        Returns:
            岗位数据列表
        """
        logger.info("🌍 使用浏览器模式爬取数据")
        
        # 这里应该实现实际的浏览器自动化逻辑
        # 暂时返回模拟数据
        
        mock_jobs = [
            {
                "position_id": "B004",
                "title": "前端开发工程师",
                "location": "杭州",
                "category": "技术类",
                "publish_time": "2026-05-19",
                "detail_url": "https://jobs.bilibili.com/position/004",
                "department": "前端技术部",
                "education_requirement": "本科及以上",
                "experience_requirement": "2年以上",
                "responsibilities": "负责B站前端页面开发与优化",
                "requirements": "熟悉React/Vue，有性能优化经验",
                "salary_range": "25-40K",
                "tags": ["React", "Vue", "TypeScript", "前端工程化"]
            },
            {
                "position_id": "B005",
                "title": "数据分析师",
                "location": "深圳",
                "category": "数据类",
                "publish_time": "2026-05-18",
                "detail_url": "https://jobs.bilibili.com/position/005",
                "department": "数据分析中心",
                "education_requirement": "硕士及以上",
                "experience_requirement": "3年以上",
                "responsibilities": "负责B站业务数据分析与挖掘",
                "requirements": "熟悉SQL/Python，有数据建模经验",
                "salary_range": "30-50K",
                "tags": ["数据分析", "SQL", "Python", "数据挖掘"]
            }
        ]
        
        return mock_jobs
    
    def _save_jobs(self, jobs: List[Dict[str, Any]]) -> None:
        """
        保存岗位数据
        
        Args:
            jobs: 岗位数据列表
        """
        if not jobs:
            return
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bilibili_jobs_{timestamp}.json"
        filepath = self.data_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 保存数据到: {filepath}")
        except Exception as e:
            logger.error(f"❌ 保存数据失败: {e}")
    
    def export_data(self, format: str = "excel") -> str:
        """
        导出数据
        
        Args:
            format: 导出格式（excel, csv, json）
            
        Returns:
            导出文件路径
        """
        logger.info(f"📤 导出数据，格式: {format}")
        
        # 加载所有数据
        all_jobs = self._load_all_jobs()
        
        if not all_jobs:
            logger.warning("⚠️ 没有数据可导出")
            return ""
        
        # 使用数据导出框架
        exporter = DataExporter()
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "excel":
            filename = f"bilibili_jobs_{timestamp}.xlsx"
            filepath = self.output_dir / filename
            exporter.export_to_excel(all_jobs, str(filepath))
        elif format == "csv":
            filename = f"bilibili_jobs_{timestamp}.csv"
            filepath = self.output_dir / filename
            exporter.export_to_csv(all_jobs, str(filepath))
        else:  # json
            filename = f"bilibili_jobs_{timestamp}.json"
            filepath = self.output_dir / filename
            exporter.export_to_json(all_jobs, str(filepath))
        
        logger.info(f"✅ 数据导出完成: {filepath}")
        return str(filepath)
    
    def _load_all_jobs(self) -> List[Dict[str, Any]]:
        """加载所有保存的岗位数据"""
        all_jobs = []
        
        if not self.data_dir.exists():
            return all_jobs
        
        for filepath in self.data_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    jobs = json.load(f)
                all_jobs.extend(jobs)
                logger.debug(f"📂 加载文件: {filepath.name} ({len(jobs)}条记录)")
            except Exception as e:
                logger.error(f"❌ 加载文件失败 {filepath}: {e}")
        
        logger.info(f"📊 共加载{len(all_jobs)}条岗位记录")
        return all_jobs
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取爬取器状态
        
        Returns:
            状态信息字典
        """
        status = super().get_status()
        
        # 添加B站特定状态
        status.update({
            "company": "bilibili",
            "base_url": self.base_url,
            "job_portal": self.job_portal_url,
            "data_count": len(self._load_all_jobs()),
            "data_dir": str(self.data_dir),
            "output_dir": str(self.output_dir)
        })
        
        return status


def main():
    """主函数"""
    print("=" * 70)
    print("🚀 B站数据爬取器")
    print("=" * 70)
    
    # 创建爬取器实例
    crawler = BilibiliCrawler("bilibili")
    
    # 显示状态
    status = crawler.get_status()
    print(f"📊 公司: {status.get('company')}")
    print(f"🌐 网站: {status.get('base_url')}")
    print(f"📁 数据目录: {status.get('data_dir')}")
    print(f"📁 输出目录: {status.get('output_dir')}")
    print(f"📈 已有数据: {status.get('data_count')}条")
    print()
    
    # 显示爬取器选择
    crawler_info = crawler.select_crawler()
    print(f"🎯 推荐爬取方式: {crawler_info.get('name')}")
    print(f"📝 描述: {crawler_info.get('description')}")
    print()
    
    # 演示爬取
    print("🔍 演示爬取B站岗位数据...")
    jobs = crawler.crawl_jobs(max_pages=2)
    
    if jobs:
        print(f"✅ 爬取完成，共获取{len(jobs)}个岗位")
        print()
        
        # 显示前几个岗位
        print("📋 岗位列表:")
        for i, job in enumerate(jobs[:3], 1):
            print(f"  {i}. {job.get('title')} - {job.get('location')}")
            print(f"     类别: {job.get('category')}")
            print(f"     发布时间: {job.get('publish_time')}")
            print()
        
        # 导出数据
        print("📤 导出数据...")
        export_file = crawler.export_data(format="excel")
        if export_file:
            print(f"✅ 数据已导出到: {export_file}")
    
    print("\n" + "=" * 70)
    print("🎉 B站爬取器演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()