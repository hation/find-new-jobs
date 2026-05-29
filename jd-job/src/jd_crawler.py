#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京东招聘数据爬取器
基于夸克项目的 SmartCrawlerSelector 框架
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src/framework"))

from framework.smart_crawler_selector import SmartCrawlerSelector
from framework.data_exporter import DataExporter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JDJobCrawler(SmartCrawlerSelector):
    """京东招聘数据爬取器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化京东爬取器
        
        Args:
            config_path: 配置文件路径
        """
        super().__init__(config_path)
        self.company_name = "京东"
        self.base_url = "https://zhaopin.jd.com"
        self.api_endpoint = "/web/job/job_list"
        
        # 从环境变量加载配置
        self.load_environment_config()
        
        logger.info(f"初始化京东招聘爬取器: {self.company_name}")
    
    def load_environment_config(self):
        """加载环境配置"""
        # 从配置文件加载API配置
        config_file = project_root / "config" / "api_auth.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.api_config = json.load(f)
        
        # 设置默认请求参数
        self.default_params = {
            "pageIndex": 1,
            "pageSize": 10,
            "workCityJson": "[11,31,44]",  # 北京、上海、广州
            "jobTypeJson": '["CAIXIAO","JINRONGYW","YUNGYUN"]',  # 采销、金融业务、运营
            "jobSearch": "",
            "depTypeJson": "[]"
        }
        
        # 设置请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://zhaopin.jd.com/web/job/job_info_list/3",
            "Origin": "https://zhaopin.jd.com",
            "X-Requested-With": "XMLHttpRequest",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
    
    def _initialize_primary_crawler(self):
        """初始化API爬取器（主要方案）"""
        logger.info("初始化京东API爬取器...")
        
        # 这里可以添加API客户端的初始化逻辑
        # 由于京东API使用简单的HTTP请求，我们使用requests库
        
        return {
            "type": "api",
            "name": "京东招聘API",
            "description": "通过京东招聘官方API获取数据",
            "status": "ready"
        }
    
    def _initialize_fallback_crawler(self):
        """初始化浏览器爬取器（备用方案）"""
        logger.info("初始化京东浏览器爬取器（备用方案）...")
        
        # 这里可以添加浏览器自动化客户端的初始化逻辑
        # 使用Playwright或Selenium作为备用方案
        
        return {
            "type": "browser",
            "name": "京东招聘浏览器爬取",
            "description": "通过浏览器自动化获取数据（当API不可用时）",
            "status": "ready"
        }
    
    def fetch_job_list(self, page: int = 1, page_size: int = 10) -> List[Dict]:
        """
        获取岗位列表
        
        Args:
            page: 页码
            page_size: 每页数量
            
        Returns:
            岗位列表
        """
        logger.info(f"获取第 {page} 页岗位数据，每页 {page_size} 条")
        
        try:
            import requests
            
            # 准备请求参数
            params = self.default_params.copy()
            params["pageIndex"] = page
            params["pageSize"] = page_size
            
            # 发送请求
            url = f"{self.base_url}{self.api_endpoint}"
            
            # 注意：这里需要实际的Cookie信息
            # 在实际使用中，需要从配置文件或环境变量中获取有效的Cookie
            cookies = {
                "JSESSIONID": "01E7E01CBA28A7444D576D166B9572E3.s1",
                "__jda": "176729966.17791859482501284180274.1779185948.1779424595.1779435415.4",
                "__jdb": "176729966.3.17791859482501284180274|4.1779435415"
            }
            
            response = requests.post(
                url,
                data=params,
                headers=self.headers,
                cookies=cookies,
                timeout=30
            )
            
            if response.status_code == 200:
                jobs = response.json()
                logger.info(f"成功获取 {len(jobs)} 个岗位")
                return jobs
            else:
                logger.error(f"API请求失败: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"获取岗位列表失败: {e}")
            return []
    
    def process_job_data(self, raw_jobs: List[Dict]) -> List[Dict]:
        """
        处理原始岗位数据
        
        Args:
            raw_jobs: 原始岗位数据
            
        Returns:
            处理后的岗位数据
        """
        processed_jobs = []
        
        for job in raw_jobs:
            try:
                # 提取关键信息
                processed_job = {
                    "position_id": job.get("id", ""),
                    "position_name": job.get("positionName", ""),
                    "work_location": job.get("workCity", ""),
                    "department": job.get("positionDeptName", ""),
                    "education_requirement": self.extract_education(job.get("qualification", "")),
                    "work_experience": self.extract_experience(job.get("qualification", "")),
                    "position_description": job.get("workContent", ""),
                    "position_requirements": job.get("qualification", ""),
                    "publish_date": job.get("formatPublishTime", ""),
                    "company_info": job.get("positionDeptName", ""),
                    "recruitment_number": job.get("reqNumber", ""),
                    "job_type": job.get("jobType", ""),
                    "is_hot": job.get("isHot", 0),
                    "raw_data": json.dumps(job, ensure_ascii=False)
                }
                
                processed_jobs.append(processed_job)
                
            except Exception as e:
                logger.error(f"处理岗位数据失败: {e}, 岗位数据: {job}")
                continue
        
        return processed_jobs
    
    def extract_education(self, qualification: str) -> str:
        """从任职要求中提取学历要求"""
        education_keywords = ["本科", "硕士", "博士", "大专", "学历", "学位"]
        
        for keyword in education_keywords:
            if keyword in qualification:
                # 提取包含关键词的句子
                lines = qualification.split('\n')
                for line in lines:
                    if keyword in line:
                        return line.strip()
        
        return "未明确"
    
    def extract_experience(self, qualification: str) -> str:
        """从任职要求中提取工作经验要求"""
        experience_keywords = ["经验", "年", "工作经历"]
        
        for keyword in experience_keywords:
            if keyword in qualification:
                lines = qualification.split('\n')
                for line in lines:
                    if keyword in line:
                        return line.strip()
        
        return "未明确"
    
    def crawl_all_jobs(self, max_pages: int = 10) -> List[Dict]:
        """
        爬取所有岗位
        
        Args:
            max_pages: 最大爬取页数
            
        Returns:
            所有岗位数据
        """
        all_jobs = []
        page = 1
        
        logger.info(f"开始爬取京东招聘岗位，最多 {max_pages} 页")
        
        while page <= max_pages:
            logger.info(f"正在爬取第 {page}/{max_pages} 页...")
            
            # 获取当前页数据
            raw_jobs = self.fetch_job_list(page=page)
            
            if not raw_jobs:
                logger.info(f"第 {page} 页没有数据，停止爬取")
                break
            
            # 处理数据
            processed_jobs = self.process_job_data(raw_jobs)
            all_jobs.extend(processed_jobs)
            
            logger.info(f"第 {page} 页处理完成，共 {len(processed_jobs)} 个岗位")
            
            # 检查是否还有更多数据
            if len(raw_jobs) < 10:  # 如果一页不满10个，可能是最后一页
                logger.info(f"第 {page} 页不满10个岗位，可能是最后一页")
                break
            
            # 延迟，避免请求过快
            time.sleep(1.5)
            
            page += 1
        
        logger.info(f"爬取完成，共获取 {len(all_jobs)} 个岗位")
        return all_jobs
    
    def save_jobs_to_file(self, jobs: List[Dict], format: str = "json") -> str:
        """
        保存岗位数据到文件
        
        Args:
            jobs: 岗位数据
            format: 文件格式 (json, csv, excel)
            
        Returns:
            保存的文件路径
        """
        # 创建输出目录
        output_dir = project_root / "output" / "jd_jobs"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            file_path = output_dir / f"jd_jobs_{timestamp}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2)
        
        elif format == "csv":
            import pandas as pd
            file_path = output_dir / f"jd_jobs_{timestamp}.csv"
            df = pd.DataFrame(jobs)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        elif format == "excel":
            # 使用统一格式的Excel导出
            file_path = self._export_to_unified_excel(jobs, output_dir, timestamp)
        
        else:
            raise ValueError(f"不支持的格式: {format}")
        
        logger.info(f"数据已保存到: {file_path}")
        return str(file_path)
    
    def _export_to_unified_excel(self, jobs: List[Dict], output_dir: Path, timestamp: str) -> str:
        """
        导出到统一格式的Excel（匹配anti-job格式）
        
        Args:
            jobs: 岗位数据
            output_dir: 输出目录
            timestamp: 时间戳
            
        Returns:
            文件路径
        """
        import pandas as pd
        from datetime import datetime
        
        # 处理数据为统一格式
        processed_jobs = []
        for i, job in enumerate(jobs):
            processed_job = {
                "序号": i + 1,
                "岗位ID": job.get("position_id", ""),
                "岗位名称": job.get("position_name", ""),
                "岗位类别": job.get("job_type", ""),
                "工作地点": job.get("work_location", ""),
                "发布时间": job.get("publish_date", ""),
                "所属部门": job.get("department", ""),
                "学历要求": self._extract_education(job.get("education_requirement", "")),
                "工作经验": self._extract_experience(job.get("work_experience", "")),
                "岗位要求": job.get("position_requirements", ""),
                "岗位描述": job.get("position_description", ""),
                "岗位标签": self._extract_tags(job),
                "岗位代码": job.get("recruitment_number", ""),
                "是否收藏": "否",
                "数据来源": "京东招聘官网",
                "类别名称": job.get("job_type", "")
            }
            processed_jobs.append(processed_job)
        
        # 创建DataFrame
        df = pd.DataFrame(processed_jobs)
        
        # 生成文件名（统一格式）
        file_path = output_dir / f"jd_international_positions_{timestamp}.xlsx"
        
        # 创建多工作表Excel
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # 1. 所有岗位
            df.to_excel(writer, sheet_name='所有岗位', index=False)
            
            # 2. 地点分布
            if '工作地点' in df.columns:
                location_stats = df['工作地点'].value_counts().reset_index()
                location_stats.columns = ['工作地点', '岗位数量']
                location_stats.to_excel(writer, sheet_name='地点分布', index=False)
            
            # 3. 类别分布
            if '岗位类别' in df.columns:
                category_stats = df['岗位类别'].value_counts().reset_index()
                category_stats.columns = ['岗位类别', '岗位数量']
                category_stats.to_excel(writer, sheet_name='类别分布', index=False)
            
            # 4. 学历分布
            if '学历要求' in df.columns:
                education_stats = df['学历要求'].value_counts().reset_index()
                education_stats.columns = ['学历要求', '岗位数量']
                education_stats.to_excel(writer, sheet_name='学历分布', index=False)
            
            # 5. 部门分布
            if '所属部门' in df.columns:
                department_stats = df['所属部门'].value_counts().reset_index()
                department_stats.columns = ['所属部门', '岗位数量']
                department_stats.to_excel(writer, sheet_name='部门分布', index=False)
            
            # 6. 经验要求
            if '工作经验' in df.columns:
                experience_stats = df['工作经验'].value_counts().reset_index()
                experience_stats.columns = ['工作经验', '岗位数量']
                experience_stats.to_excel(writer, sheet_name='经验要求', index=False)
            
            # 7. 数据摘要
            summary_data = {
                '统计项': [
                    '总岗位数', '数据来源', '公司名称', 
                    'Excel生成时间', '数据质量'
                ],
                '值': [
                    len(df), '京东招聘官网', '京东集团',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    f"完整率: {df.notnull().sum().sum()/(df.shape[0]*df.shape[1])*100:.1f}%"
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='数据摘要', index=False)
        
        # 同时生成简化版CSV
        csv_file_path = output_dir / f"jd_positions_simple_{timestamp}.csv"
        key_columns = ['序号', '岗位名称', '岗位类别', '工作地点', '学历要求', '工作经验', '所属部门']
        available_columns = [col for col in key_columns if col in df.columns]
        if available_columns:
            simple_df = df[available_columns]
            simple_df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
        
        return str(file_path)
    
    def _extract_education(self, education_text: str) -> str:
        """提取学历要求"""
        if not education_text:
            return "学历不限"
        
        education_keywords = {
            "博士": "博士", "硕士": "硕士", "研究生": "硕士",
            "本科": "本科", "大专": "大专", "专科": "大专",
            "高中": "高中", "中专": "中专"
        }
        
        for keyword, level in education_keywords.items():
            if keyword in education_text:
                return level
        
        return "学历不限"
    
    def _extract_experience(self, experience_text: str) -> str:
        """提取工作经验"""
        if not experience_text:
            return "经验不限"
        
        import re
        year_pattern = r'(\d+)[\+-]?\s*年'
        matches = re.findall(year_pattern, experience_text)
        
        if matches:
            years = [int(m) for m in matches]
            if len(years) >= 2:
                return f"{min(years)}-{max(years)}年"
            else:
                return f"{years[0]}+年"
        
        if "不限" in experience_text or "无要求" in experience_text:
            return "经验不限"
        elif "应届" in experience_text:
            return "应届生"
        elif "实习" in experience_text:
            return "实习生"
        
        return "经验不限"
    
    def _extract_tags(self, job: Dict) -> str:
        """提取岗位标签"""
        tags = []
        
        location = job.get("work_location", "")
        if location:
            tags.append(location)
        
        department = job.get("department", "")
        if department:
            tags.append(department)
        
        job_type = job.get("job_type", "")
        if job_type:
            tags.append(job_type)
        
        is_hot = job.get("is_hot", 0)
        if is_hot == 1:
            tags.append("热门岗位")
        
        return ", ".join(tags) if tags else ""
    
    def run(self, max_pages: int = 5, output_format: str = "excel"):
        """
        运行爬虫
        
        Args:
            max_pages: 最大爬取页数
            output_format: 输出格式
        """
        logger.info("=" * 60)
        logger.info("开始运行京东招聘爬虫")
        logger.info(f"公司: {self.company_name}")
        logger.info(f"网站: {self.base_url}")
        logger.info(f"最大页数: {max_pages}")
        logger.info(f"输出格式: {output_format}")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # 爬取数据
            jobs = self.crawl_all_jobs(max_pages=max_pages)
            
            if not jobs:
                logger.warning("没有获取到任何岗位数据")
                return
            
            # 保存数据
            file_path = self.save_jobs_to_file(jobs, format=output_format)
            
            # 统计信息
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info("=" * 60)
            logger.info("爬取完成!")
            logger.info(f"总耗时: {duration:.2f} 秒")
            logger.info(f"获取岗位数: {len(jobs)}")
            logger.info(f"数据文件: {file_path}")
            logger.info("=" * 60)
            
            return file_path
            
        except Exception as e:
            logger.error(f"爬虫运行失败: {e}")
            raise


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="京东招聘数据爬取器")
    parser.add_argument("--pages", type=int, default=5, help="最大爬取页数")
    parser.add_argument("--format", type=str, default="excel", 
                       choices=["json", "csv", "excel"], help="输出格式")
    parser.add_argument("--test", action="store_true", help="测试模式")
    
    args = parser.parse_args()
    
    # 创建爬虫实例
    crawler = JDJobCrawler()
    
    if args.test:
        # 测试模式：只爬取1页
        logger.info("运行测试模式...")
        crawler.run(max_pages=1, output_format=args.format)
    else:
        # 正常模式
        crawler.run(max_pages=args.pages, output_format=args.format)


if __name__ == "__main__":
    main()