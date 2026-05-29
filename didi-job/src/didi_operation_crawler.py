#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
滴滴出行运营岗位数据爬取器
专门针对运营类岗位的爬取（jobType=5）
"""

import os
import sys
import json
import time
import logging
import requests
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src/framework"))

from framework.data_exporter import DataExporter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DidiOperationCrawler:
    """滴滴出行运营岗位爬取器（jobType=5）"""
    
    def __init__(self):
        """初始化运营岗位爬取器"""
        self.company_name = "滴滴出行"
        self.website_url = "https://talent.didiglobal.com"
        
        # API配置 - 使用 jobType=5 获取运营岗位
        self.api_config = {
            "list_endpoint": "https://talent.didiglobal.com/recruit-portal-service/api/job/front/list",
            "detail_endpoint": "https://talent.didiglobal.com/recruit-portal-service/api/job/front/view/{jdId}",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Content-Type": "application/json",
                "Referer": "https://talent.didiglobal.com/social/list/1?jobType=5",
                "Origin": "https://talent.didiglobal.com",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "X-Requested-With": "XMLHttpRequest",
                "pragma": "no-cache",
                "cache-control": "no-cache"
            },
            "cookies": {
                "_OMGID": "ec27041c-eb2d-4492-b532-8ec163593281",
                "SESSION": "1841c93d-6134-4802-9e94-c33567821687",
                "language": "zh_cn"
            },
            "params": {
                "jobType": 5,        # 运营岗位
                "recruitType": 1,    # 常规招聘
                "size": 16           # 每页数量
            }
        }
        
        # 请求会话
        self.session = requests.Session()
        self._setup_session()
        
        # 数据统计
        self.total_positions = 0
        self.crawled_positions = 0
        self.failed_positions = 0
        
        # 输出目录
        self.output_dir = project_root / "output" / "didi_operation_positions"
        self.immediate_dir = self.output_dir / "immediate"
        self.immediate_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ 滴滴运营岗位爬取器初始化完成 (jobType=5)")
    
    def _setup_session(self):
        """设置请求会话"""
        # 设置请求头
        headers = self.api_config.get("headers", {})
        for key, value in headers.items():
            self.session.headers[key] = value
        
        # 设置Cookie
        cookies = self.api_config.get("cookies", {})
        for key, value in cookies.items():
            self.session.cookies.set(key, value)
        
        # 设置超时
        self.session.timeout = 30
        
        logger.info("✅ 请求会话设置完成")
    
    def fetch_all_operation_positions(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        获取所有运营岗位（jobType=5）
        
        Args:
            max_pages: 最大爬取页数
            
        Returns:
            所有运营岗位数据列表
        """
        all_positions = []
        current_page = 1
        
        logger.info(f"🚀 开始获取滴滴运营岗位 (jobType=5)，最大页数: {max_pages}")
        
        try:
            while current_page <= max_pages:
                logger.info(f"📄 正在获取第 {current_page} 页...")
                
                # 构建请求参数
                params = self.api_config["params"].copy()
                params["page"] = current_page
                
                # 发送请求
                response = self.session.get(
                    self.api_config["list_endpoint"],
                    params=params,
                    timeout=30
                )
                
                # 检查响应状态
                response.raise_for_status()
                
                # 解析JSON响应
                result = response.json()
                
                # 检查API响应状态
                if result.get("meta", {}).get("code") != 0:
                    error_msg = result.get("meta", {}).get("message", "API返回错误")
                    logger.error(f"❌ API返回错误: {error_msg}")
                    break
                
                # 提取数据
                data = result.get("data", {})
                positions = data.get("items", [])
                total = data.get("total", 0)
                
                if not positions:
                    logger.info("📭 没有更多数据")
                    break
                
                all_positions.extend(positions)
                self.total_positions = total
                
                logger.info(f"✅ 第 {current_page} 页获取成功: {len(positions)}个运营岗位")
                logger.info(f"📊 累计: {len(all_positions)}/{total} ({len(all_positions)/total*100:.1f}%)")
                
                current_page += 1
                
                # 添加延迟避免请求过快
                time.sleep(0.5)
            
            logger.info(f"🎉 运营岗位获取完成: {len(all_positions)}个岗位")
            return all_positions
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 网络请求失败: {e}")
            return all_positions
        except Exception as e:
            logger.error(f"❌ 获取数据失败: {e}")
            return all_positions
    
    def fetch_position_details(self, positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        获取运营岗位的详细信息
        
        Args:
            positions: 运营岗位列表
            
        Returns:
            包含详细信息的运营岗位列表
        """
        detailed_positions = []
        
        logger.info(f"🔍 开始获取 {len(positions)} 个运营岗位的详细信息...")
        
        for i, position in enumerate(positions, 1):
            jd_id = position.get("jdId")
            job_name = position.get("jobName", "未知岗位")
            jd_no = position.get("jdNo", "")
            
            if not jd_id:
                logger.warning(f"⚠️ 跳过无ID的岗位: {job_name}")
                self.failed_positions += 1
                continue
            
            try:
                # 构建详情API URL
                endpoint = self.api_config["detail_endpoint"].format(jdId=jd_id)
                
                logger.info(f"📥 获取详情 ({i}/{len(positions)}): {job_name} ({jd_no})")
                
                # 发送请求
                response = self.session.get(endpoint, timeout=30)
                response.raise_for_status()
                
                # 解析JSON响应
                result = response.json()
                
                # 检查API响应状态
                if result.get("meta", {}).get("code") != 0:
                    error_msg = result.get("meta", {}).get("message", "API返回错误")
                    logger.warning(f"⚠️ 详情API返回错误: {error_msg}")
                    self.failed_positions += 1
                    continue
                
                # 提取详情数据
                detail_data = result.get("data", {})
                
                # 合并数据
                combined_data = {**position, **detail_data}
                detailed_positions.append(combined_data)
                
                # 实时保存
                self._save_position_immediately(combined_data)
                
                self.crawled_positions += 1
                logger.info(f"✅ 成功获取: {job_name}")
                
                # 添加延迟避免请求过快
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ 详情请求失败: {job_name} - {e}")
                self.failed_positions += 1
            except Exception as e:
                logger.error(f"❌ 详情处理失败: {job_name} - {e}")
                self.failed_positions += 1
        
        logger.info(f"🎉 详细信息获取完成: {self.crawled_positions} 成功, {self.failed_positions} 失败")
        return detailed_positions
    
    def _save_position_immediately(self, position: Dict[str, Any]):
        """立即保存岗位数据到文件"""
        try:
            jd_id = position.get("jdId", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            filename = f"didi_operation_position_{jd_id}_{timestamp}.json"
            filepath = self.immediate_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(position, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"💾 实时保存: {filename}")
            
        except Exception as e:
            logger.error(f"❌ 保存文件失败: {e}")
    
    def export_data(self, positions: List[Dict[str, Any]], format: str = "json"):
        """导出数据"""
        try:
            exporter = DataExporter()
            
            result = exporter.export_data(
                data=positions,
                format=format,
                company_name=f"{self.company_name}运营岗位"
            )
            
            if result.get("success"):
                logger.info(f"✅ 数据导出成功: {format.upper()}格式")
                return result
            else:
                logger.error(f"❌ 数据导出失败: {result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 导出数据失败: {e}")
            return None
    
    def run(self, max_pages: int = 10, start_page: int = 1):
        """
        运行爬取器
        
        Args:
            max_pages: 最大爬取页数
            start_page: 起始页码
        """
        print("=" * 70)
        print(f"🚀 滴滴出行运营岗位数据爬取器 (jobType=5)")
        print("=" * 70)
        print(f"📊 公司: {self.company_name}")
        print(f"🌐 网站: {self.website_url}")
        print(f"📄 爬取页数: {max_pages}")
        print(f"🔢 起始页码: {start_page}")
        print("-" * 70)
        
        # 1. 获取所有运营岗位
        logger.info("📡 开始获取运营岗位列表...")
        positions = self.fetch_all_operation_positions(max_pages=max_pages)
        
        if not positions:
            logger.error("❌ 未获取到任何运营岗位数据")
            return
        
        # 2. 获取详细信息
        logger.info("🔍 开始获取运营岗位详细信息...")
        detailed_positions = self.fetch_position_details(positions)
        
        if not detailed_positions:
            logger.error("❌ 未获取到任何运营岗位详细信息")
            return
        
        # 3. 导出数据
        logger.info("📤 开始导出运营岗位数据...")
        export_result = self.export_data(detailed_positions, format="json")
        
        # 4. 生成报告
        self._generate_report(detailed_positions)
    
    def _generate_report(self, positions: List[Dict[str, Any]]):
        """生成爬取报告"""
        print("\n" + "=" * 70)
        print("📊 滴滴运营岗位爬取报告")
        print("=" * 70)
        print(f"✅ 爬取成功!")
        print(f"📊 总运营岗位数: {self.total_positions}")
        print(f"📥 成功爬取: {self.crawled_positions}")
        print(f"❌ 失败爬取: {self.failed_positions}")
        print(f"📄 爬取页数: {max(1, self.total_positions // 16)}")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if positions:
            print(f"\n📋 爬取的运营岗位示例:")
            for i, pos in enumerate(positions[:10], 1):
                job_name = pos.get("jobName", "未知")
                work_area = pos.get("workArea", "未知")
                dept_name = pos.get("deptName", "未知")
                print(f"{i}. {job_name}")
                print(f"   地点: {work_area}, 部门: {dept_name}")
            
            if len(positions) > 10:
                print(f"... 还有 {len(positions) - 10} 个运营岗位")
        
        print(f"\n📁 数据已保存到:")
        print(f"   {self.output_dir}/immediate/ (实时保存文件)")
        print(f"   {project_root}/output/data_export/ (批量导出文件)")
        
        print(f"\n💡 提示:")
        print(f"• 查看完整数据: 查看 {self.output_dir}/ 目录")
        print(f"• 配置API认证: 编辑配置文件")
        print(f"• 基于夸克项目的防错机制，确保数据完整性和稳定性")
        print("=" * 70)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="滴滴出行运营岗位数据爬取器")
    parser.add_argument("--pages", type=int, default=10, help="最大爬取页数")
    parser.add_argument("--start", type=int, default=1, help="起始页码")
    parser.add_argument("--format", type=str, default="json", choices=["json", "excel"], help="导出格式")
    
    args = parser.parse_args()
    
    # 创建爬取器
    crawler = DidiOperationCrawler()
    
    # 运行爬取
    crawler.run(max_pages=args.pages, start_page=args.start)

if __name__ == "__main__":
    main()