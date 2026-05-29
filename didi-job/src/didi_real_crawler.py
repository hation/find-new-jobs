#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
滴滴出行招聘数据爬取器（真实API实现）
基于夸克完整架构框架，针对滴滴招聘API定制
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import urllib.parse

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

class DidiRealCrawler(SmartCrawlerSelector):
    """滴滴出行招聘真实API爬取器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化滴滴招聘爬取器
        
        Args:
            config_path: 配置文件路径
        """
        # 加载滴滴招聘配置
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            # 默认配置
            config = {
                "company_name": "滴滴出行",
                "website_url": "https://talent.didiglobal.com",
                "output_dir": "output/didi_positions",
                "api_config": {
                    "list_endpoint": "https://talent.didiglobal.com/recruit-portal-service/api/job/front/list",
                    "detail_endpoint": "https://talent.didiglobal.com/recruit-portal-service/api/job/front/view/{jdId}",
                    "base_params": {
                        "jobType": 3,      # 社招
                        "recruitType": 1   # 常规招聘
                    },
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                        "Content-Type": "application/json",
                        "Referer": "https://talent.didiglobal.com/social/list/1?jobType=3",
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
                        "SESSION": "1e9fef71-a907-4271-a06b-f4e5fb21d8c3",
                        "language": "zh_cn"
                    }
                }
            }
        
        super().__init__(config)
        self.company_name = config.get("company_name", "滴滴出行")
        self.website_url = config.get("website_url", "https://talent.didiglobal.com")
        self.api_config = config.get("api_config", {})
        
        # 请求会话
        self.session = requests.Session()
        self._setup_session()
        
        # 数据统计
        self.total_positions = 0
        self.crawled_positions = 0
        self.failed_positions = 0
        
        logger.info(f"✅ 滴滴招聘爬取器初始化完成: {self.company_name}")
    
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
        
        # 设置超时和重试
        self.session.timeout = 30
        logger.info("✅ 请求会话设置完成")
    
    def _initialize_primary_crawler(self):
        """初始化API爬取器（主要爬取方式）"""
        logger.info("🚀 初始化滴滴招聘API爬取器")
        
        def api_crawler(page: int = 1, size: int = 16) -> Dict[str, Any]:
            """
            滴滴招聘API爬取函数
            
            Args:
                page: 页码
                size: 每页数量
                
            Returns:
                API响应数据
            """
            try:
                # 构建请求参数
                params = {
                    "jobType": 3,        # 社招
                    "page": page,        # 页码
                    "recruitType": 1,    # 常规招聘
                    "size": size         # 每页数量
                }
                
                # API端点（硬编码确保正确）
                endpoint = "https://talent.didiglobal.com/recruit-portal-service/api/job/front/list"
                
                logger.info(f"📡 请求滴滴招聘API: {endpoint}, 参数: {params}")
                
                # 发送请求
                response = self.session.get(
                    endpoint,
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
                    return {
                        "success": False,
                        "error": error_msg,
                        "data": None
                    }
                
                # 提取数据
                data = result.get("data", {})
                total = data.get("total", 0)
                items = data.get("items", [])
                current_page = data.get("page", page)
                page_size = data.get("size", size)
                
                logger.info(f"✅ API请求成功: 第{current_page}页, 共{total}个岗位, 本页{len(items)}个")
                
                # 记录速率限制信息
                rate_limit = response.headers.get("x-ratelimit-limit-second")
                rate_remaining = response.headers.get("x-ratelimit-remaining-second")
                if rate_limit and rate_remaining:
                    logger.debug(f"📊 速率限制: {rate_remaining}/{rate_limit} 请求/秒")
                
                return {
                    "success": True,
                    "data": {
                        "total": total,
                        "current_page": current_page,
                        "page_size": page_size,
                        "positions": items,
                        "has_more": len(items) > 0 and (current_page * page_size) < total
                    },
                    "meta": {
                        "rate_limit": rate_limit,
                        "rate_remaining": rate_remaining,
                        "response_time": response.elapsed.total_seconds()
                    }
                }
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ 网络请求失败: {e}")
                return {
                    "success": False,
                    "error": f"网络请求失败: {str(e)}",
                    "data": None
                }
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON解析失败: {e}")
                return {
                    "success": False,
                    "error": f"JSON解析失败: {str(e)}",
                    "data": None
                }
            except Exception as e:
                logger.error(f"❌ 未知错误: {e}")
                return {
                    "success": False,
                    "error": f"未知错误: {str(e)}",
                    "data": None
                }
        
        return api_crawler
    
    def _initialize_fallback_crawler(self):
        """初始化浏览器爬取器（备用爬取方式）"""
        logger.info("🌐 初始化滴滴招聘浏览器爬取器（备用方案）")
        
        def browser_crawler():
            """浏览器爬取函数（备用方案）"""
            logger.warning("⚠️ 浏览器爬取器尚未实现，建议使用API模式")
            return {
                "success": False,
                "error": "浏览器爬取器尚未实现",
                "data": None
            }
        
        return browser_crawler
    
    def fetch_position_details(self, jd_id: int) -> Dict[str, Any]:
        """
        获取岗位详细信息
        
        Args:
            jd_id: 岗位ID
            
        Returns:
            岗位详细信息
        """
        try:
            # 构建详情API URL（硬编码确保正确）
            endpoint = f"https://talent.didiglobal.com/recruit-portal-service/api/job/front/view/{jd_id}"
            
            logger.info(f"🔍 获取岗位详情: ID={jd_id}, URL={endpoint}")
            
            # 发送请求
            response = self.session.get(
                endpoint,
                timeout=30
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析JSON响应
            result = response.json()
            
            # 检查API响应状态
            if result.get("meta", {}).get("code") != 0:
                error_msg = result.get("meta", {}).get("message", "API返回错误")
                logger.error(f"❌ 详情API返回错误: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "data": None
                }
            
            # 提取详情数据
            detail_data = result.get("data", {})
            
            # 标准化字段名
            standardized_data = {
                "jobName": detail_data.get("jobName", ""),
                "deptName": detail_data.get("deptName", ""),
                "publishTime": detail_data.get("publishTime", ""),
                "refreshTime": detail_data.get("refreshTime", ""),
                "jdNo": detail_data.get("jdNo", ""),
                "jobDesc": detail_data.get("jobDesc", ""),
                "qualification": detail_data.get("qualification", ""),
                "workArea": detail_data.get("workArea", ""),
                "recruitNum": detail_data.get("recruitNum", 1),
                "jobType": detail_data.get("jobType", ""),
                "recordId": detail_data.get("recordId", ""),
                "jdStatus": detail_data.get("jdStatus", 0)
            }
            
            logger.info(f"✅ 获取岗位详情成功: {standardized_data.get('jobName', '未知')}")
            
            return {
                "success": True,
                "data": standardized_data,
                "meta": {
                    "response_time": response.elapsed.total_seconds(),
                    "jd_id": jd_id
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 详情请求失败: {e}")
            return {
                "success": False,
                "error": f"详情请求失败: {str(e)}",
                "data": None
            }
        except Exception as e:
            logger.error(f"❌ 详情处理失败: {e}")
            return {
                "success": False,
                "error": f"详情处理失败: {str(e)}",
                "data": None
            }
    
    def crawl_all_positions(self, max_pages: int = 10, start_page: int = 1) -> Dict[str, Any]:
        """
        爬取所有岗位数据
        
        Args:
            max_pages: 最大爬取页数
            start_page: 起始页码
            
        Returns:
            爬取结果
        """
        logger.info(f"🚀 开始爬取滴滴招聘数据，最大页数: {max_pages}, 起始页码: {start_page}")
        
        # 初始化API爬取器
        api_crawler = self._initialize_primary_crawler()
        if not api_crawler:
            return {
                "success": False,
                "error": "API爬取器初始化失败",
                "data": None
            }
        
        all_positions = []
        current_page = start_page
        has_more = True
        total_positions = 0
        
        try:
            while has_more and current_page <= (start_page + max_pages - 1):
                logger.info(f"📄 正在爬取第 {current_page} 页...")
                
                # 获取当前页数据
                page_result = api_crawler(page=current_page, size=16)
                
                if not page_result.get("success"):
                    logger.error(f"❌ 第 {current_page} 页爬取失败: {page_result.get('error')}")
                    break
                
                page_data = page_result.get("data", {})
                positions = page_data.get("positions", [])
                total_positions = page_data.get("total", 0)
                has_more = page_data.get("has_more", False)
                
                # 处理本页每个岗位
                for position in positions:
                    position_id = position.get("jdId")
                    if not position_id:
                        logger.warning("⚠️ 跳过无ID的岗位")
                        continue
                    
                    # 获取岗位详情
                    detail_result = self.fetch_position_details(position_id)
                    
                    if detail_result.get("success"):
                        detail_data = detail_result.get("data", {})
                        # 合并列表数据和详情数据
                        combined_data = {**position, **detail_data}
                        all_positions.append(combined_data)
                        
                        # 实时保存
                        self._save_position_immediately(combined_data)
                        
                        self.crawled_positions += 1
                        logger.info(f"✅ 成功爬取: {combined_data.get('jobName', '未知岗位')} (ID: {position_id})")
                    else:
                        self.failed_positions += 1
                        logger.warning(f"⚠️ 详情获取失败: {position.get('jobName', '未知岗位')} (ID: {position_id})")
                        # 仍然保存基础信息
                        all_positions.append(position)
                        self._save_position_immediately(position)
                    
                    # 添加延迟避免请求过快
                    time.sleep(0.1)
                
                # 更新进度
                progress = len(all_positions) / total_positions * 100 if total_positions > 0 else 0
                logger.info(f"📊 进度: {len(all_positions)}/{total_positions} ({progress:.1f}%)")
                
                current_page += 1
                
                # 添加页间延迟
                if has_more:
                    time.sleep(0.5)
            
            # 导出数据
            if all_positions:
                export_result = self._export_data(all_positions)
                if export_result.get("success"):
                    logger.info(f"✅ 数据导出成功: {export_result.get('file_path')}")
                else:
                    logger.error(f"❌ 数据导出失败: {export_result.get('error')}")
            
            return {
                "success": True,
                "data": {
                    "total_positions": total_positions,
                    "crawled_positions": self.crawled_positions,
                    "failed_positions": self.failed_positions,
                    "positions": all_positions,
                    "pages_crawled": current_page - start_page
                },
                "meta": {
                    "company": self.company_name,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "website": self.website_url
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 爬取过程中发生错误: {e}")
            return {
                "success": False,
                "error": f"爬取过程中发生错误: {str(e)}",
                "data": {
                    "total_positions": total_positions,
                    "crawled_positions": self.crawled_positions,
                    "failed_positions": self.failed_positions,
                    "positions": all_positions,
                    "pages_crawled": current_page - start_page
                }
            }
    
    def _save_position_immediately(self, position: Dict[str, Any]):
        """立即保存单个岗位数据（防数据丢失）"""
        try:
            output_dir = Path(project_root) / "output" / "didi_positions" / "immediate"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            position_id = position.get("jdId", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_dir / f"didi_position_{position_id}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(position, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"💾 立即保存岗位数据: {filename}")
        except Exception as e:
            logger.error(f"❌ 立即保存数据失败: {e}")
    
    def _export_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """导出数据"""
        try:
            exporter = DataExporter()
            export_result = exporter.export_data(
                data=data,
                format="json",
                company_name=self.company_name
            )
            
            return export_result
        except Exception as e:
            logger.error(f"❌ 数据导出失败: {e}")
            return {
                "success": False,
                "error": f"数据导出失败: {str(e)}"
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        logger.info("🔍 测试滴滴招聘API连接...")
        
        try:
            # 测试列表API
            api_crawler = self._initialize_primary_crawler()
            if not api_crawler:
                return {
                    "success": False,
                    "error": "API爬取器初始化失败"
                }
            
            test_result = api_crawler(page=1, size=1)
            
            if test_result.get("success"):
                # 测试详情API
                test_position_id = 61620  # 示例岗位ID
                detail_result = self.fetch_position_details(test_position_id)
                
                return {
                    "success": True,
                    "list_api": test_result,
                    "detail_api": detail_result,
                    "session_info": {
                        "cookies_count": len(self.session.cookies),
                        "headers_count": len(self.session.headers)
                    }
                }
            else:
                return {
                    "success": False,
                    "error": test_result.get("error", "API测试失败")
                }
                
        except Exception as e:
            logger.error(f"❌ 连接测试失败: {e}")
            return {
                "success": False,
                "error": f"连接测试失败: {str(e)}"
            }

def main():
    """主函数"""
    print("=" * 70)
    print("🚀 滴滴出行招聘数据爬取器（真实API版）")
    print("=" * 70)
    
    # 创建爬取器实例
    config_path = Path(project_root) / "config" / "didi_api_auth.json"
    crawler = DidiRealCrawler(str(config_path) if config_path.exists() else None)
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="滴滴出行招聘数据爬取器")
    parser.add_argument("--test", action="store_true", help="测试API连接")
    parser.add_argument("--pages", type=int, default=3, help="爬取页数（默认3页）")
    parser.add_argument("--start", type=int, default=1, help="起始页码（默认第1页）")
    parser.add_argument("--output", choices=["json", "excel", "csv", "all"], default="json", help="输出格式")
    
    args = parser.parse_args()
    
    if args.test:
        print("🔍 测试API连接...")
        test_result = crawler.test_connection()
        
        if test_result.get("success"):
            print("✅ API连接测试成功!")
            print(f"📊 列表API: {test_result.get('list_api', {}).get('success', False)}")
            print(f"📊 详情API: {test_result.get('detail_api', {}).get('success', False)}")
            print(f"🍪 Cookie数量: {test_result.get('session_info', {}).get('cookies_count', 0)}")
        else:
            print(f"❌ API连接测试失败: {test_result.get('error', '未知错误')}")
    else:
        print(f"📊 公司: {crawler.company_name}")
        print(f"🌐 网站: {crawler.website_url}")
        print(f"📄 爬取页数: {args.pages}")
        print(f"🔢 起始页码: {args.start}")
        print(f"💾 输出格式: {args.output}")
        print("-" * 70)
        
        # 开始爬取
        result = crawler.crawl_all_positions(max_pages=args.pages, start_page=args.start)
        
        if result.get("success"):
            data = result.get("data", {})
            print(f"✅ 爬取成功!")
            print(f"📊 总岗位数: {data.get('total_positions', 0)}")
            print(f"📥 成功爬取: {data.get('crawled_positions', 0)}")
            print(f"❌ 失败爬取: {data.get('failed_positions', 0)}")
            print(f"📄 爬取页数: {data.get('pages_crawled', 0)}")
            print(f"⏰ 时间: {result.get('meta', {}).get('timestamp', '未知')}")
            
            # 显示前几个岗位
            positions = data.get("positions", [])
            if positions:
                print("\n📋 爬取的岗位示例:")
                for i, pos in enumerate(positions[:5], 1):
                    job_name = pos.get('jobName', '未知岗位')
                    work_area = pos.get('workArea', '未知地点')
                    dept_name = pos.get('deptName', '未知部门')
                    print(f"{i}. {job_name}")
                    print(f"   地点: {work_area}, 部门: {dept_name}")
                
                if len(positions) > 5:
                    print(f"... 还有 {len(positions) - 5} 个岗位")
        else:
            print(f"❌ 爬取失败: {result.get('error', '未知错误')}")
        
        print("\n📁 数据已保存到:")
        print(f"   {Path(project_root) / 'output' / 'didi_positions'}")
        print(f"   {Path(project_root) / 'output' / 'didi_positions' / 'immediate'}")
    
    print("\n💡 提示:")
    print("• 查看完整数据: 查看 output/didi_positions/ 目录")
    print("• 配置API认证: 编辑 config/didi_api_auth.json")
    print("• 查看检查清单: docs/CHECKLIST.md")
    print("• 记录经验教训: docs/LESSONS_LEARNED.md")
    print("• 基于夸克项目的防错机制，确保数据完整性和稳定性")

if __name__ == "__main__":
    main()