#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘API爬取器（真实实现）
基于快手官方API：https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple
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
        logging.FileHandler('logs/ks_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class KsAPICrawler:
    """快手招聘API爬取器（真实实现）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化快手API爬取器
        
        Args:
            config: 配置字典，包含API参数、认证信息等
        """
        self.config = config or {}
        
        # API配置
        self.base_url = self.config.get("base_url", "https://zhaopin.kuaishou.cn")
        self.api_path = self.config.get("api_path", "/recruit/e/api/v1/open/positions/simple")
        self.api_url = f"{self.base_url}{self.api_path}"
        
        # 默认参数
        self.default_params = {
            "pageSize": self.config.get("page_size", 10),
            "positionCategoryCode": self.config.get("position_category_codes", "J0005,J0004,J0013,J0006,J0014"),
            "positionNatureCode": self.config.get("position_nature_code", "C001"),
            "recruitProject": self.config.get("recruit_project", "socialr"),
            "workLocationCode": self.config.get("work_location_code", "domestic")
        }
        
        # 认证信息
        self.cookie = self.config.get("cookie", "")
        self.user_agent = self.config.get("user_agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        self.referer = self.config.get("referer", "https://zhaopin.kuaishou.cn/")
        
        # 请求配置
        self.timeout = self.config.get("timeout", 30)
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay = self.config.get("retry_delay", 5)  # 秒
        
        # 会话管理
        self.session = requests.Session()
        self._setup_session()
        
        # 状态跟踪
        self.total_positions = 0
        self.total_pages = 0
        self.current_page = 0
        self.positions_crawled = 0
        self.start_time = None
        
        logger.info("✅ 快手API爬取器初始化完成")
        logger.info(f"   API地址: {self.api_url}")
        logger.info(f"   默认参数: {self.default_params}")
    
    def _setup_session(self):
        """设置会话配置"""
        headers = {
            "User-Agent": self.user_agent,
            "Referer": self.referer,
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
            "Sec-Fetch-Site": "same-origin"
        }
        
        self.session.headers.update(headers)
        
        if self.cookie:
            self.session.headers.update({"Cookie": self.cookie})
            logger.info("✅ Cookie已设置")
        else:
            logger.warning("⚠️ 未设置Cookie，API可能返回认证错误")
    
    def _make_request(self, params: Dict[str, Any], retry_count: int = 0) -> Optional[Dict[str, Any]]:
        """
        发送API请求
        
        Args:
            params: 请求参数
            retry_count: 当前重试次数
            
        Returns:
            API响应数据，失败返回None
        """
        try:
            logger.info(f"📡 API请求: pageNum={params.get('pageNum', 1)}, pageSize={params.get('pageSize', 10)}")
            
            response = self.session.get(
                self.api_url,
                params=params,
                timeout=self.timeout
            )
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"❌ API请求失败: HTTP {response.status_code}")
                logger.error(f"   响应内容: {response.text[:200]}")
                return None
            
            # 解析响应
            data = response.json()
            
            # 检查API错误码
            if data.get("code") != 0:
                logger.error(f"❌ API业务错误: code={data.get('code')}, message={data.get('message')}")
                return None
            
            logger.info(f"✅ API请求成功: 获取到 {len(data.get('result', {}).get('list', []))} 个岗位")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 网络请求失败: {e}")
            
            # 重试逻辑
            if retry_count < self.max_retries:
                logger.info(f"🔄 重试 {retry_count + 1}/{self.max_retries}，等待 {self.retry_delay}秒...")
                time.sleep(self.retry_delay)
                return self._make_request(params, retry_count + 1)
            else:
                logger.error(f"❌ 达到最大重试次数 {self.max_retries}，放弃请求")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析失败: {e}")
            logger.error(f"   响应内容: {response.text[:500]}")
            return None
            
        except Exception as e:
            logger.error(f"❌ 未知错误: {e}")
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
        params = self.default_params.copy()
        params["pageNum"] = page_num
        
        if page_size:
            params["pageSize"] = page_size
        
        # 发送请求
        response_data = self._make_request(params)
        
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
            max_pages: 最大爬取页数，None表示爬取所有页
            
        Returns:
            所有岗位数据列表
        """
        logger.info("🚀 开始爬取所有岗位数据...")
        self.start_time = datetime.now()
        
        all_positions = []
        current_page = 1
        
        # 先获取第一页，了解总页数
        positions, pagination = self.fetch_positions_page(current_page)
        
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
            time.sleep(2)
            
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
            "detailUrl": f"https://zhaopin.kuaishou.cn/position/{position.get('id', '')}",
            "department": position.get("departmentCode", ""),
            "educationRequirement": position.get("educationLimitCode", ""),
            "workExperience": position.get("workExperienceCode", ""),
            "jobResponsibilities": position.get("description", ""),
            "jobRequirements": position.get("positionDemand", ""),
            "salaryRange": "",  # 快手API未提供薪资信息
            
            # 附加信息
            "company": "快手",
            "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "crawlMode": "api",
            "source": "kuaishou_api",
            
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
    
    def validate_position_data(self, position: Dict[str, Any]) -> bool:
        """
        验证岗位数据完整性
        
        Args:
            position: 标准化后的岗位数据
            
        Returns:
            是否通过验证
        """
        required_fields = [
            "positionId", "positionName", "workLocation", "positionCategory",
            "publishTime", "detailUrl", "department", "educationRequirement",
            "workExperience", "jobResponsibilities", "jobRequirements", "salaryRange"
        ]
        
        missing_fields = []
        for field in required_fields:
            if not position.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            logger.warning(f"⚠️ 岗位 {position.get('positionId')} 缺失字段: {missing_fields}")
            return False
        
        return True
    
    def save_position_data(self, position: Dict[str, Any], output_dir: str = None) -> str:
        """
        保存岗位数据到JSON文件
        
        Args:
            position: 标准化后的岗位数据
            output_dir: 输出目录
            
        Returns:
            保存的文件路径
        """
        if output_dir is None:
            output_dir = self.config.get("output_dir", "output/ks_data")
        
        # 确保目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        position_id = position.get("positionId", "unknown")
        filename = f"ks_position_{position_id}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # 保存数据
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(position, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 保存岗位数据: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ 保存数据失败: {e}")
            return ""
    
    def crawl_and_save(self, max_pages: int = 5, output_dir: str = None) -> Dict[str, Any]:
        """
        完整爬取流程：爬取数据并保存
        
        Args:
            max_pages: 最大爬取页数
            output_dir: 输出目录
            
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
        valid_positions = 0
        
        for i, raw_position in enumerate(all_positions, 1):
            try:
                # 提取标准字段
                standard_position = self.extract_standard_fields(raw_position)
                
                # 验证数据完整性
                if self.validate_position_data(standard_position):
                    valid_positions += 1
                
                # 保存数据
                filepath = self.save_position_data(standard_position, output_dir)
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
            "valid_positions": valid_positions,
            "saved_files": len(saved_files),
            "valid_percentage": valid_positions / len(all_positions) * 100 if all_positions else 0,
            "output_dir": output_dir or self.config.get("output_dir", "output/ks_data"),
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info("=" * 60)
        logger.info(f"🎉 爬取完成!")
        logger.info(f"   • 总岗位数: {stats['total_positions']}")
        logger.info(f"   • 有效岗位: {stats['valid_positions']} ({stats['valid_percentage']:.1f}%)")
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
        "base_url": "https://zhaopin.kuaishou.cn",
        "api_path": "/recruit/e/api/v1/open/positions/simple",
        "page_size": 10,
        "position_category_codes": "J0005,J0004,J0013,J0006,J0014",
        "position_nature_code": "C001",
        "recruit_project": "socialr",
        "work_location_code": "domestic",
        "output_dir": "output/ks_data",
        "timeout": 30,
        "max_retries": 3,
        "retry_delay": 5
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
    print("🚀 快手招聘API爬取器（真实实现）")
    print("=" * 70)
    print("基于快手官方API：https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple")
    print()
    
    # 加载配置
    config = load_config()
    
    # 检查Cookie
    cookie = config.get("KS_COOKIE_PLACEHOLDER", "")
    if not cookie or "accessproxy_session" not in cookie:
        print("⚠️ 警告：未检测到有效的Cookie")
        print("   请从浏览器复制Cookie并更新 config/.env 文件")
        print("   需要的Cookie字段：accessproxy_session, aliyungf_tc, apdid, weblogger_did")
        print()
        print("   或者，你可以：")
        print("   1. 打开浏览器访问 https://zhaopin.kuaishou.cn")
        print("   2. 登录快手招聘网站")
        print("   3. 打开开发者工具（F12）")
        print("   4. 复制 Cookie 值")
        print("   5. 更新 config/.env 中的 KS_COOKIE_PLACEHOLDER")
        print()
        
        # 询问是否继续
        choice = input("是否继续测试（可能返回认证错误）？(y/N): ")
        if choice.lower() != 'y':
            print("退出程序")
            return
    
    # 创建爬取器
    print("🔄 创建快手API爬取器...")
    crawler = KsAPICrawler(config)
    
    # 测试单页爬取
    print()
    print("📡 测试单页爬取...")
    positions, pagination = crawler.fetch_positions_page(1)
    
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
                print(f"   有效岗位: {stats['valid_positions']} ({stats['valid_percentage']:.1f}%)")
                print(f"   保存文件: {stats['saved_files']}")
                print(f"   输出目录: {stats['output_dir']}")
            else:
                print("❌ 爬取失败")
        else:
            print("✅ 测试完成，退出程序")
    else:
        print("❌ 测试失败，无法获取岗位数据")
        print("   可能原因：")
        print("   1. Cookie无效或过期")
        print("   2. 网络连接问题")
        print("   3. API接口变更")
        print("   4. 签名验证失败")
    
    print("=" * 70)


if __name__ == "__main__":
    main()