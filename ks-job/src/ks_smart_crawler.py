#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘智能爬取器
基于夸克项目的经验，实现实时签名获取和完整数据爬取
"""

import sys
import os
import json
import time
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlencode

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ks_smart_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class KsSmartCrawler:
    """快手招聘智能爬取器（实时签名获取）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化智能爬取器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # API配置
        self.base_url = "https://zhaopin.kuaishou.cn"
        self.api_path = "/recruit/e/api/v1/open/positions/simple"
        self.api_url = f"{self.base_url}{self.api_path}"
        
        # 基础认证信息（你提供的）
        self.base_cookie = "aliyungf_tc=62d111759197e609997a914760f88ccc44c00ef73b2f542817802af91250a937; accessproxy_session=01b7eac0ccce9f49aa335ac52039ec8a825379cdb3EAIiE3poYW9waW4ua3VhaXNob3UuY24KJGJiODA2NjMzLTVmODgtNGI5Yy1iM2QyLTBlMjEwZmI1NGEzZioVEhFVTkFVVEhPUklaRURfVVNFUgoAGLHJ1Of+Mw==; apdid=1e615e70-2858-4116-bd0e-5e461bd10eb4cc68ec35bc432b6780dc98e63f48cce7:1779186916:1; weblogger_did=web_754734862580340E"
        self.base_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
        
        # 实时签名（需要从浏览器获取）
        self.current_sign = ""
        self.current_signtimestamp = ""
        
        # 请求配置
        self.timeout = self.config.get("timeout", 30)
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay = self.config.get("retry_delay", 5)  # 秒
        
        # 爬取配置
        self.page_size = self.config.get("page_size", 10)
        self.max_pages = self.config.get("max_pages", 10)
        self.delay_between_pages = self.config.get("delay_between_pages", 2)  # 秒
        
        # 输出配置
        self.output_dir = self.config.get("output_dir", "output/ks_data")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 状态跟踪
        self.total_positions = 0
        self.total_pages = 0
        self.current_page = 0
        self.positions_crawled = 0
        self.start_time = None
        
        # 会话管理
        self.session = requests.Session()
        self._setup_session()
        
        logger.info("✅ 快手智能爬取器初始化完成")
        logger.info(f"   API地址: {self.api_url}")
        logger.info(f"   基础Cookie已设置")
    
    def _setup_session(self):
        """设置基础会话配置"""
        base_headers = {
            "User-Agent": self.base_user_agent,
            "Referer": "https://zhaopin.kuaishou.cn/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"macOS\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cookie": self.base_cookie
        }
        
        self.session.headers.update(base_headers)
        logger.info("✅ 基础会话配置完成")
    
    def _get_real_time_signature(self) -> Tuple[str, str]:
        """
        获取实时签名（模拟实现）
        实际应用中需要从浏览器实时获取
        
        Returns:
            (sign, signtimestamp)
        """
        # 这里应该实现从浏览器获取实时签名的逻辑
        # 目前返回空值，需要你提供实时签名
        
        current_time = int(time.time() * 1000)
        logger.warning(f"⚠️ 需要实时签名，当前时间戳: {current_time}")
        logger.warning(f"   请从浏览器获取最新的 sign 和 signtimestamp")
        
        return "", ""
    
    def _make_request_with_retry(self, params: Dict[str, Any], use_signature: bool = True) -> Optional[Dict[str, Any]]:
        """
        发送带重试的API请求
        
        Args:
            params: 请求参数
            use_signature: 是否使用签名
            
        Returns:
            API响应数据
        """
        for retry in range(self.max_retries):
            try:
                # 如果需要签名，获取实时签名
                headers = {}
                if use_signature:
                    sign, signtimestamp = self._get_real_time_signature()
                    if sign and signtimestamp:
                        headers["sign"] = sign
                        headers["signtimestamp"] = signtimestamp
                        logger.info(f"📝 使用签名: {signtimestamp}")
                    else:
                        logger.warning("⚠️ 未获取到实时签名，尝试无签名请求")
                
                logger.info(f"📡 API请求: pageNum={params.get('pageNum', 1)}, pageSize={params.get('pageSize', 10)}")
                
                # 发送请求
                response = self.session.get(
                    self.api_url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
                
                # 检查响应状态
                if response.status_code != 200:
                    logger.error(f"❌ API请求失败: HTTP {response.status_code}")
                    logger.error(f"   响应内容: {response.text[:200]}")
                    
                    if retry < self.max_retries - 1:
                        logger.info(f"🔄 重试 {retry + 1}/{self.max_retries}，等待 {self.retry_delay}秒...")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return None
                
                # 解析响应
                data = response.json()
                
                # 检查API错误码
                if data.get("code") != 0:
                    error_code = data.get("code")
                    error_msg = data.get("message")
                    
                    logger.error(f"❌ API业务错误: code={error_code}, message={error_msg}")
                    
                    # 如果是签名错误，尝试刷新签名
                    if error_code == -1 and "系统错误" in error_msg and use_signature:
                        logger.info("🔄 检测到签名错误，尝试刷新签名...")
                        if retry < self.max_retries - 1:
                            time.sleep(self.retry_delay)
                            continue
                    
                    return None
                
                logger.info(f"✅ API请求成功: 获取到 {len(data.get('result', {}).get('list', []))} 个岗位")
                return data
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ 网络请求失败: {e}")
                if retry < self.max_retries - 1:
                    logger.info(f"🔄 重试 {retry + 1}/{self.max_retries}，等待 {self.retry_delay}秒...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"❌ 达到最大重试次数 {self.max_retries}，放弃请求")
                    return None
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON解析失败: {e}")
                if response:
                    logger.error(f"   响应内容: {response.text[:500]}")
                return None
                
            except Exception as e:
                logger.error(f"❌ 未知错误: {e}")
                return None
        
        return None
    
    def fetch_positions_page(self, page_num: int = 1, page_size: int = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        获取单页岗位数据
        
        Args:
            page_num: 页码
            page_size: 每页数量
            
        Returns:
            (岗位列表, 分页信息)
        """
        # 构建请求参数
        params = {
            "pageNum": page_num,
            "pageSize": page_size or self.page_size,
            "positionCategoryCode": "J0005,J0004,J0013,J0006,J0014",
            "positionNatureCode": "C001",
            "recruitProject": "socialr",
            "workLocationCode": "domestic"
        }
        
        # 发送请求（先尝试带签名，失败则尝试无签名）
        response_data = self._make_request_with_retry(params, use_signature=True)
        
        if not response_data:
            logger.warning("⚠️ 带签名请求失败，尝试无签名请求...")
            response_data = self._make_request_with_retry(params, use_signature=False)
        
        if not response_data:
            return [], {}
        
        # 提取数据
        result = response_data.get("result", {})
        positions = result.get("list", [])
        pagination = {
            "total": result.get("total", 0),
            "pageNum": result.get("pageNum", page_num),
            "pageSize": result.get("pageSize", params["pageSize"]),
            "pages": result.get("pages", 0),
            "hasNextPage": result.get("hasNextPage", False)
        }
        
        # 更新状态
        if page_num == 1:
            self.total_positions = pagination["total"]
            self.total_pages = pagination["pages"]
            logger.info(f"📊 发现 {self.total_positions} 个岗位，共 {self.total_pages} 页")
        
        self.current_page = page_num
        self.positions_crawled += len(positions)
        
        return positions, pagination
    
    def fetch_all_positions(self, max_pages: int = None) -> List[Dict[str, Any]]:
        """
        获取所有岗位数据（自动分页）
        
        Args:
            max_pages: 最大爬取页数
            
        Returns:
            所有岗位数据列表
        """
        logger.info("🚀 开始爬取所有岗位数据...")
        self.start_time = datetime.now()
        
        all_positions = []
        
        # 先获取第一页，了解总页数
        positions, pagination = self.fetch_positions_page(1)
        
        if not positions:
            logger.error("❌ 第一页数据获取失败，终止爬取")
            return []
        
        all_positions.extend(positions)
        
        # 计算实际要爬取的页数
        if max_pages is None:
            max_pages = pagination.get("pages", 1)
        else:
            max_pages = min(max_pages, pagination.get("pages", 1))
        
        logger.info(f"📄 计划爬取 {max_pages} 页数据")
        
        # 爬取剩余页
        for page_num in range(2, max_pages + 1):
            # 避免请求过快
            time.sleep(self.delay_between_pages)
            
            # 显示进度
            progress = (page_num - 1) / max_pages * 100
            logger.info(f"📊 进度: {page_num-1}/{max_pages}页 ({progress:.1f}%)")
            
            positions, _ = self.fetch_positions_page(page_num)
            
            if not positions:
                logger.warning(f"❌ 第 {page_num} 页数据获取失败，跳过")
                continue
            
            all_positions.extend(positions)
        
        # 统计信息
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        logger.info("=" * 60)
        logger.info(f"📊 爬取完成统计:")
        logger.info(f"   • 总用时: {elapsed_time:.2f}秒")
        logger.info(f"   • 爬取页数: {max_pages}页")
        logger.info(f"   • 获取岗位: {len(all_positions)}个")
        if self.total_positions > 0:
            logger.info(f"   • 成功率: {len(all_positions)/self.total_positions*100:.1f}%")
        logger.info("=" * 60)
        
        return all_positions
    
    def extract_standard_fields(self, position: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取标准字段（12个核心字段）
        
        Args:
            position: 原始API数据
            
        Returns:
            标准化后的岗位数据
        """
        # 基础字段映射
        standard_data = {
            # 12个核心字段
            "positionId": str(position.get("id", "")),
            "positionName": position.get("name", ""),
            "workLocation": position.get("workLocationCode", ""),
            "positionCategory": position.get("positionCategoryCode", ""),
            "publishTime": position.get("updateTime", ""),
            "detailUrl": f"{self.base_url}/position/{position.get('id', '')}",
            "department": position.get("departmentCode", ""),
            "educationRequirement": position.get("educationLimitCode", ""),
            "workExperience": position.get("workExperienceCode", ""),
            "jobResponsibilities": position.get("description", ""),
            "jobRequirements": position.get("positionDemand", ""),
            "salaryRange": "",  # 快手API未提供薪资信息
            
            # 附加信息
            "company": "快手",
            "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "crawlMode": "smart",
            "source": "kuaishou_smart",
            
            # 原始数据（保留供参考）
            "rawData": {
                "levels": position.get("levels", []),
                "workLocationsCode": position.get("workLocationsCode", []),
                "recruitProjectCode": position.get("recruitProjectCode", ""),
                "positionNatureCode": position.get("positionNatureCode", ""),
                "channelCode": position.get("channelCode", "")
            }
        }
        
        return standard_data
    
    def save_position_data(self, position: Dict[str, Any]) -> str:
        """
        保存岗位数据到JSON文件
        
        Args:
            position: 标准化后的岗位数据
            
        Returns:
            保存的文件路径
        """
        # 确保目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        position_id = position.get("positionId", "unknown")
        filename = f"ks_position_{position_id}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # 保存数据
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(position, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 保存岗位数据: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ 保存数据失败: {e}")
            return ""
    
    def crawl_and_save(self, max_pages: int = 5) -> Dict[str, Any]:
        """
        完整爬取流程：爬取数据并保存
        
        Args:
            max_pages: 最大爬取页数
            
        Returns:
            爬取统计信息
        """
        logger.info(f"🚀 开始完整爬取流程（最大 {max_pages} 页）")
        
        # 获取所有数据
        all_positions = self.fetch_all_positions(max_pages)
        
        if not all_positions:
            logger.error("❌ 未获取到任何岗位数据")
            return {"success": False, "message": "未获取到数据"}
        
        # 处理并保存每个岗位
        saved_files = []
        
        for i, raw_position in enumerate(all_positions, 1):
            try:
                # 提取标准字段
                standard_position = self.extract_standard_fields(raw_position)
                
                # 保存数据
                filepath = self.save_position_data(standard_position)
                if filepath:
                    saved_files.append(filepath)
                
                # 显示进度
                if i % 10 == 0 or i == len(all_positions):
                    progress = i / len(all_positions) * 100
                    logger.info(f"📊 处理进度: {i}/{len(all_positions)} ({progress:.1f}%)")
                    
            except Exception as e:
                logger.error(f"❌ 处理岗位失败: {e}")
                continue
        
        # 返回统计信息
        stats = {
            "success": True,
            "total_positions": len(all_positions),
            "saved_files": len(saved_files),
            "output_dir": self.output_dir,
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "crawl_mode": "smart"
        }
        
        logger.info("=" * 60)
        logger.info(f"🎉 爬取完成!")
        logger.info(f"   • 总岗位数: {stats['total_positions']}")
        logger.info(f"   • 保存文件: {stats['saved_files']}")
        logger.info(f"   • 输出目录: {stats['output_dir']}")
        logger.info("=" * 60)
        
        return stats


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config", ".env"
    )
    
    config = {
        "timeout": 30,
        "max_retries": 3,
        "retry_delay": 5,
        "page_size": 10,
        "max_pages": 5,
        "delay_between_pages": 2,
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


def main():
    """主函数"""
    print("=" * 70)
    print("🚀 快手招聘智能爬取器")
    print("=" * 70)
    print("基于夸克项目的经验，实现实时签名获取")
    print("需要从浏览器获取实时签名参数")
    print()
    
    # 加载配置
    config = load_config()
    
    # 创建爬取器
    print("🔄 创建快手智能爬取器...")
    crawler = KsSmartCrawler(config)
    
    # 测试单页爬取
    print()
    print("📡 测试单页爬取...")
    positions, pagination = crawler.fetch_positions_page(1, 5)  # 只取5条测试
    
    if positions:
        print(f"✅ 测试成功！获取到 {len(positions)} 个岗位")
        print(f"   总岗位数: {pagination.get('total', 0)}")
        print(f"   总页数: {pagination.get('pages', 0)}")
        print()
        
        # 显示前几个岗位
        print("📋 岗位示例:")
        for i, position in enumerate(positions[:3], 1):
            print(f"  {i}. {position.get('name', '未知岗位')} - {position.get('workLocationCode', '未知地点')}")
        
        print()
        
        # 询问是否进行完整爬取
        choice = input("是否进行完整爬取？(y/N): ")
        if choice.lower() == 'y':
            max_pages = input("请输入最大爬取页数（默认5）: ")
            max_pages = int(max_pages) if max_pages.strip() else 5
            
            print()
            print("🚀 开始完整爬取...")
            stats = crawler.crawl_and_save(max_pages=max_pages)
            
            if stats["success"]:
                print()
                print("🎉 爬取完成！")
                print(f"   总岗位数: {stats['total_positions']}")
                print(f"   保存文件: {stats['saved_files']}")
                print(f"   输出目录: {stats['output_dir']}")
            else:
                print("❌ 爬取失败")
        else:
            print("✅ 测试完成，退出程序")
    else:
        print("❌ 测试失败，无法获取岗位数据")
        print("   需要从浏览器获取实时签名参数")
        print()
        print("💡 解决方案:")
        print("   1. 打开浏览器访问 https://zhaopin.kuaishou.cn")
        print("   2. 打开开发者工具 (F12)")
        print("   3. 找到API请求，复制最新的 sign 和 signtimestamp")
        print("   4. 更新爬取器的 _get_real_time_signature 方法")
    
    print("=" * 70)


if __name__ == "__main__":
    main()