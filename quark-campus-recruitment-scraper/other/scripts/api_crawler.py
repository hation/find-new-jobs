#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
夸克校园招聘API爬取器
基于已验证的API方案实现，默认使用API接口，支持切换到浏览器模式
"""

import json
import time
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class ApiCrawler:
    """夸克校园招聘API爬取器（基于已验证的API方案）"""
    
    def __init__(self, config_path: str = None):
        """
        初始化API爬取器
        
        Args:
            config_path: 配置文件路径
        """
        # 已验证的API信息
        self.api_url = "https://talent.quark.cn/position/search"
        self.base_url = "https://talent.quark.cn/off-campus/position-list?lang=zh"
        
        # 已验证的核心参数（基于历史测试）
        self.base_params = {
            "channel": "group_official_site",
            "language": "zh",
            "batchId": "",
            "categories": "97,103,143,152,124,146,492",  # 7个筛选类别ID
            "deptCodes": [],
            "key": "",
            "pageIndex": 1,     # 页码，从1开始
            "pageSize": 10,     # 每页数量，最大可能为20
            "regions": ""
        }
        
        # 认证信息（需要从浏览器获取）
        self.csrf_token = None
        self.cookies = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://talent.quark.cn",
            "Referer": self.base_url
        }
        
        # 状态跟踪
        self.total_positions = 92  # 目标岗位数
        self.positions_extracted = 0
        
        logger.info("API爬取器初始化完成，基于已验证的API方案")
        logger.info(f"API地址: {self.api_url}")
        logger.info(f"筛选类别ID: {self.base_params['categories']}")
    
    def set_csrf_token(self, csrf_token: str) -> bool:
        """
        设置CSRF令牌（用户手动提供）
        
        Args:
            csrf_token: CSRF令牌字符串
            
        Returns:
            是否设置成功
        """
        if not csrf_token or not isinstance(csrf_token, str):
            logger.error("❌ 无效的CSRF令牌格式")
            return False
        
        self.csrf_token = csrf_token
        logger.info(f"✅ 已设置CSRF令牌: {csrf_token[:8]}...{csrf_token[-8:]}")
        logger.info(f"   完整令牌长度: {len(csrf_token)} 字符")
        
        # 验证令牌格式（UUID格式）
        import re
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        if re.match(uuid_pattern, csrf_token.lower()):
            logger.info("✅ CSRF令牌格式验证通过（UUID格式）")
        else:
            logger.warning("⚠️ CSRF令牌格式非标准UUID，可能无法使用")
        
        return True
        
    def fetch_from_browser(self, max_wait: int = 30) -> bool:
        """
        从浏览器获取必要的认证信息（CSRF令牌和Cookies）
        
        Args:
            max_wait: 最大等待时间（秒）
            
        Returns:
            是否成功获取认证信息
        """
        logger.info("正在从浏览器获取认证信息...")
        
        # 尝试多种方式获取CSRF令牌
        csrf_token = None
        
        # 方式1：从URL查询参数获取（如用户提供的示例）
        # 用户提供的示例：https://talent.quark.cn/position/search?_csrf=c6ea8927-62fd-42ab-9eab-d1f3da836dfc
        
        # 方式2：从页面meta标签获取
        # 方式3：从隐藏表单字段获取
        # 方式4：从JavaScript变量获取
        # 方式5：从Cookie获取
        
        # 由于这是一个占位实现，我们暂时返回示例token
        # 在实际环境中，应该实现上述方法之一
        
        # 提供清晰的错误信息
        logger.warning("⚠️ fetch_from_browser() 方法未实现")
        logger.warning("   需要实现从浏览器获取真实的CSRF令牌")
        logger.warning("   用户提供的示例URL: https://talent.quark.cn/position/search?_csrf=...")
        
        # 返回False表示获取失败
        self.csrf_token = None
        self.cookies = None
        return False
    
    def fetch_page(self, page: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """
        获取单页数据
        
        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            解析后的API响应数据，失败返回None
        """
        if not self.csrf_token:
            logger.error("❌ 没有有效的CSRF令牌")
            logger.error("   请先使用 set_csrf_token() 方法设置CSRF令牌")
            logger.error("   或者从浏览器页面URL中获取，例如：")
            logger.error("   https://talent.quark.cn/position/search?_csrf=c6ea8927-62fd-42ab-9eab-d1f3da836dfc")
            return None
        
        # 构建请求参数
        params = self.base_params.copy()
        params.update({
            "pageIndex": page,
            "pageSize": page_size
        })
        
        # 构建完整URL（包含CSRF令牌）
        full_url = f"{self.api_url}?_csrf={self.csrf_token}"
        
        try:
            logger.info(f"正在获取第 {page} 页数据 (每页 {page_size} 条)")
            
            # 发送POST请求
            response = requests.post(
                full_url,
                headers=self.headers,
                cookies=self.cookies,
                json=params,
                timeout=30
            )
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"API请求失败，状态码: {response.status_code}")
                return None
            
            # 解析响应
            result = response.json()
            
            # 检查API响应状态
            if result.get("code") != 0:
                logger.error(f"API返回错误: {result.get('message', '未知错误')}")
                return None
            
            # 记录成功
            data = result.get("data", {})
            positions = data.get("list", [])
            total = data.get("total", 0)
            
            logger.info(f"成功获取第 {page} 页数据: {len(positions)} 个岗位，总计 {total} 个岗位")
            
            return {
                "page": page,
                "total": total,
                "positions": positions,
                "raw_data": result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            return None
    
    def fetch_all_pages(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        获取所有页面的数据
        
        Args:
            max_pages: 最大页数
            
        Returns:
            所有岗位数据列表
        """
        all_positions = []
        current_page = 1
        
        logger.info(f"开始获取所有页面数据，最多 {max_pages} 页")
        
        while current_page <= max_pages:
            # 获取当前页数据
            page_result = self.fetch_page(current_page)
            
            if not page_result:
                logger.warning(f"第 {current_page} 页获取失败，停止获取")
                break
            
            # 提取岗位数据
            positions = page_result.get("positions", [])
            if not positions:
                logger.info(f"第 {current_page} 页没有数据，停止获取")
                break
            
            # 添加到总列表
            all_positions.extend(positions)
            self.positions_extracted += len(positions)
            
            logger.info(f"已获取 {self.positions_extracted} 个岗位，当前页: {current_page}")
            
            # 检查是否已经获取完所有数据
            total_in_page = page_result.get("total", 0)
            if total_in_page <= self.positions_extracted:
                logger.info(f"已获取所有 {total_in_page} 个岗位数据")
                break
            
            # 继续下一页
            current_page += 1
            
            # 添加延迟避免触发反爬虫
            time.sleep(1)
        
        logger.info(f"获取完成，总计 {len(all_positions)} 个岗位")
        return all_positions
    
    def parse_position(self, raw_position: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析原始岗位数据为标准格式
        
        Args:
            raw_position: 原始API返回的岗位数据
            
        Returns:
            标准化的岗位数据（12个字段）
        """
        # 这里需要根据API实际返回的字段进行解析
        # 基于我们之前的了解，预期字段包括：
        
        position = {
            # 基础字段（5个）
            "position_id": raw_position.get("positionId", ""),
            "position_name": raw_position.get("title", ""),
            "position_category": raw_position.get("category", ""),
            "work_location": raw_position.get("location", ""),
            "update_time": raw_position.get("updateTime", ""),
            
            # 部门信息（1个）
            "department": raw_position.get("department", ""),
            
            # 学历要求（1个）
            "education_requirement": raw_position.get("education", ""),
            
            # 工作经验（1个）
            "work_experience": raw_position.get("experience", ""),
            
            # 岗位描述（1个）
            "position_description": raw_position.get("description", ""),
            
            # 岗位要求（1个）
            "position_requirements": raw_position.get("requirements", ""),
            
            # 其他信息（1个）
            "other_info": raw_position.get("other", ""),
            
            # 元数据（1个）
            "source": "api",
            "extract_time": datetime.now().isoformat(),
            "page_url": f"https://talent.quark.cn/off-campus/position-detail?lang=zh&positionId={raw_position.get('positionId', '')}"
        }
        
        # 清理数据
        for key, value in position.items():
            if isinstance(value, str):
                position[key] = value.strip()
        
        return position
    
    def save_positions(self, positions: List[Dict[str, Any]], output_dir: str = "output/positions") -> str:
        """
        保存岗位数据到文件
        
        Args:
            positions: 岗位数据列表
            output_dir: 输出目录
            
        Returns:
            保存的文件路径
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quark_api_positions_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # 准备保存的数据
        save_data = {
            "metadata": {
                "source": "api",
                "extract_time": datetime.now().isoformat(),
                "total_positions": len(positions),
                "api_url": self.api_url,
                "categories": self.base_params["categories"]
            },
            "positions": positions
        }
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到: {filepath} ({len(positions)} 个岗位)")
        return filepath
    
    def run(self, output_dir: str = "output/positions") -> Dict[str, Any]:
        """
        运行API爬取器的主方法
        
        Args:
            output_dir: 输出目录
            
        Returns:
            运行结果统计
        """
        logger.info("=" * 60)
        logger.info("开始执行夸克校园招聘API爬取")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # 1. 获取认证信息
            if not self.fetch_from_browser():
                return {
                    "success": False,
                    "error": "无法获取认证信息",
                    "positions_extracted": 0
                }
            
            # 2. 获取所有页面数据
            raw_positions = self.fetch_all_pages(max_pages=10)
            
            if not raw_positions:
                return {
                    "success": False,
                    "error": "没有获取到任何岗位数据",
                    "positions_extracted": 0
                }
            
            # 3. 解析数据为标准格式
            parsed_positions = []
            for raw_pos in raw_positions:
                parsed_pos = self.parse_position(raw_pos)
                if parsed_pos.get("position_id"):  # 确保有有效的ID
                    parsed_positions.append(parsed_pos)
            
            # 4. 保存数据
            save_path = self.save_positions(parsed_positions, output_dir)
            
            # 5. 统计结果
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            result = {
                "success": True,
                "positions_extracted": len(parsed_positions),
                "total_positions_target": self.total_positions,
                "elapsed_time_seconds": elapsed_time,
                "save_path": save_path,
                "api_url": self.api_url,
                "categories": self.base_params["categories"],
                "completion_percentage": (len(parsed_positions) / self.total_positions) * 100
            }
            
            logger.info("=" * 60)
            logger.info("API爬取完成!")
            logger.info(f"获取岗位数: {len(parsed_positions)}/{self.total_positions}")
            logger.info(f"完成比例: {result['completion_percentage']:.1f}%")
            logger.info(f"耗时: {elapsed_time:.2f} 秒")
            logger.info(f"保存路径: {save_path}")
            logger.info("=" * 60)
            
            return result
            
        except Exception as e:
            logger.error(f"API爬取失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "positions_extracted": self.positions_extracted
            }


def test_api_crawler():
    """测试API爬取器"""
    import sys
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/api_crawler.log", encoding='utf-8')
        ]
    )
    
    try:
        # 创建API爬取器
        crawler = ApiCrawler()
        
        # 运行爬取
        result = crawler.run()
        
        if result["success"]:
            print(f"\n✅ API爬取成功!")
            print(f"   获取岗位数: {result['positions_extracted']}/{result['total_positions_target']}")
            print(f"   完成比例: {result['completion_percentage']:.1f}%")
            print(f"   耗时: {result['elapsed_time_seconds']:.2f} 秒")
            print(f"   保存路径: {result['save_path']}")
        else:
            print(f"\n❌ API爬取失败: {result.get('error', '未知错误')}")
        
        return result
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    test_api_crawler()