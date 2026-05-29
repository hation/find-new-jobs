#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
夸克校园招聘API爬取器（完整版）
使用用户提供的完整认证信息
包含：CSRF令牌、Cookie、正确的筛选参数
"""

import json
import time
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import os
import re

logger = logging.getLogger(__name__)


class QuarkApiCrawlerComplete:
    """夸克校园招聘API爬取器（使用完整认证信息）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化API爬取器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # ✅ 完整的API端点（用户提供）
        self.api_url = "https://talent.quark.cn/position/search"
        
        # ✅ 用户提供的CSRF令牌（从API URL中提取）
        self.csrf_token = "c6ea8927-62fd-42ab-9eab-d1f3da836dfc"
        
        # ✅ 用户提供的完整Cookie（从浏览器控制台获取）
        self.cookies_str = (
            "prefered-lang=zh; "
            "cna=QH2RIvlJWR4CAQ6ZRGRcngaX; "
            "xlly_s=1; "
            "tfstk=guymDzYxF4TI6kLPKFkfZRsNy758GxMsbPptWA3Na4uWBiaOc5mZrlAAcfUYZV4oPqFOfouiIzEwMKHqBP0akkrxklEVjOqaYPc1cV3ZSPEaMgBdpoZjCAyGJ9BLvi6GZrAZQVSwUDnh2mk0JnftCA7dyQpZG9D_kj2ZFArPqcns7IzZgLorPmYZQqlwzQoEzVka7j8PUmi90FlZbgqrPckZ7PlVqYuSbAua7Akn93uY7rwPRSUdd9rHSbnmi2rquoE4UtcMGkgkQdyuZt330W9wQ8mmi8EOW9WrQSrYrXFc-K0u0WasYr8VSVwu4-PUzTpmIuPUIYyPz334Ou2iH-SO3vPQrRcEK1IjL-ZaO5rcEwlutzPIV7_Ms2VaDWNU0adoq7rYEbeF-dcbarNIsRQRdxFLvRGU3tYIyXigrXFc-K4F4WdyT9wBC0STUCOsg0ioJ4Mnzqt1VwmAqgAUOjoS09IlqC6Zg0io3gjkTEGqVmu1.; "
            "isg=BMXFPhisA0kXKSeSuJuyV6EH1Af_gnkUURyWoMcusfyNXurQjdDV5nj8aIKoHpHM"
        )
        
        # 将Cookie字符串转换为字典
        self.cookies = self._parse_cookies(self.cookies_str)
        
        # ✅ 已验证的核心参数（7个筛选类别ID）
        self.base_params = {
            "categories": "97,103,143,152,124,146,492",  # 7个筛选类别ID
            "pageIndex": 1,     # 页码，从1开始
            "pageSize": 10,     # 每页数量
            "channel": "group_official_site",
            "language": "zh",
            "batchId": "",
            "deptCodes": [],
            "key": "",
            "regions": ""
        }
        
        # 输出目录
        self.output_dir = config.get("output_dir", "output/positions")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 状态跟踪
        self.positions_extracted = 0
        self.current_page = config.get("start_page", 1)
        self.total_pages = 10  # 根据页面显示
        self.max_positions = config.get("max_positions", 93)  # 当前显示93个岗位
        
        # 已验证的请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://talent.quark.cn",
            "Referer": "https://talent.quark.cn/off-campus/position-list?lang=zh",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        logger.info(f"✅ 夸克API爬取器初始化完成")
        logger.info(f"   API端点: {self.api_url}")
        logger.info(f"   CSRF令牌: {self.csrf_token[:8]}...{self.csrf_token[-8:]}")
        logger.info(f"   Cookie长度: {len(self.cookies_str)} 字符")
        logger.info(f"   筛选类别ID: {self.base_params['categories']}")
        logger.info(f"   目标岗位: {self.max_positions} 个 (页面显示: 93个)")
        logger.info(f"   输出目录: {self.output_dir}")
    
    def _parse_cookies(self, cookie_str: str) -> Dict[str, str]:
        """解析Cookie字符串为字典"""
        cookies = {}
        for cookie in cookie_str.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                cookies[name] = value
        return cookies
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取爬取器状态
        
        Returns:
            状态字典
        """
        return {
            "type": "api_complete",
            "positions_extracted": self.positions_extracted,
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "completion_percentage": (self.positions_extracted / self.max_positions) * 100,
            "output_dir": self.output_dir,
            "csrf_token": f"{self.csrf_token[:8]}...{self.csrf_token[-8:]}",
            "cookies_count": len(self.cookies),
            "api_url": self.api_url
        }
    
    def fetch_page(self, page_index: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """
        获取单页数据
        
        Args:
            page_index: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            解析后的API响应数据，失败返回None
        """
        logger.info(f"📡 获取第 {page_index} 页数据 (每页 {page_size} 条)")
        
        # 构建请求参数
        params = self.base_params.copy()
        params.update({
            "pageIndex": page_index,
            "pageSize": page_size
        })
        
        # 构建完整URL（包含CSRF令牌）
        url_with_csrf = f"{self.api_url}?_csrf={self.csrf_token}"
        
        logger.debug(f"   请求URL: {url_with_csrf}")
        logger.debug(f"   请求参数: {json.dumps(params, ensure_ascii=False)}")
        logger.debug(f"   请求头: {json.dumps(self.headers, ensure_ascii=False, indent=2)}")
        logger.debug(f"   Cookie: {self.cookies_str[:100]}...")
        
        try:
            # 发送POST请求
            response = requests.post(
                url_with_csrf,
                headers=self.headers,
                cookies=self.cookies,
                json=params,
                timeout=30,
                allow_redirects=False
            )
            
            logger.info(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"✅ API请求成功!")
                    
                    # 检查API业务状态
                    if data.get("code") == 0:
                        total = data.get("data", {}).get("total", 0)
                        positions = data.get("data", {}).get("list", [])
                        
                        logger.info(f"🎉 成功获取 {len(positions)} 个岗位，总计 {total} 个岗位")
                        
                        # 更新目标岗位数
                        if total > 0 and self.max_positions != total:
                            logger.info(f"📊 更新目标岗位数: {self.max_positions} → {total}")
                            self.max_positions = total
                        
                        return data
                    else:
                        logger.error(f"❌ API业务错误: {data.get('msg', '未知错误')}")
                        logger.debug(f"完整响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON解析失败: {e}")
                    logger.debug(f"原始响应: {response.text[:500]}")
                    
            elif response.status_code == 403:
                logger.error(f"❌ 认证失败 (403 Forbidden)")
                logger.error(f"   可能原因:")
                logger.error(f"   1. CSRF令牌已过期")
                logger.error(f"   2. Cookie无效")
                logger.error(f"   3. 需要重新获取认证信息")
                logger.debug(f"响应头: {dict(response.headers)}")
                
            else:
                logger.error(f"❌ 请求失败: {response.status_code}")
                logger.debug(f"响应内容: {response.text[:500]}")
                
        except requests.exceptions.Timeout:
            logger.error(f"⏰ 请求超时")
        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 连接错误")
        except Exception as e:
            logger.error(f"❌ 请求异常: {e}")
        
        return None
    
    def crawl_page(self, page_index: int) -> List[Dict[str, Any]]:
        """
        爬取单页数据并提取岗位信息
        
        Args:
            page_index: 页码
            
        Returns:
            岗位数据列表
        """
        logger.info(f"📄 开始爬取第 {page_index} 页...")
        
        data = self.fetch_page(page_index)
        
        if not data:
            logger.warning(f"⚠️ 第 {page_index} 页爬取失败")
            return []
        
        # 提取岗位数据
        positions = data.get("data", {}).get("list", [])
        
        if positions:
            logger.info(f"✅ 第 {page_index} 页爬取成功: {len(positions)} 个岗位")
            
            # 处理每个岗位
            processed_positions = []
            for i, pos in enumerate(positions):
                # 提取关键字段
                processed_pos = {
                    "position_id": pos.get("id") or pos.get("positionId") or f"quark_{page_index}_{i+1:02d}",
                    "position_name": pos.get("title") or pos.get("positionName") or "未知岗位",
                    "position_category": pos.get("category") or "未知类别",
                    "work_location": pos.get("location") or pos.get("workLocation") or "未知地点",
                    "update_time": pos.get("updateTime") or pos.get("publishTime") or "未知时间",
                    "department": pos.get("department") or "未知部门",
                    "education_requirement": pos.get("education") or "学历不限",
                    "work_experience": pos.get("experience") or "经验不限",
                    "position_description": pos.get("description") or "",
                    "position_requirements": pos.get("requirement") or "",
                    "other_info": json.dumps(pos, ensure_ascii=False),
                    "source": "api_complete",
                    "extract_time": datetime.now().isoformat(),
                    "page_number": page_index,
                    "position_in_page": i + 1
                }
                
                processed_positions.append(processed_pos)
                self.positions_extracted += 1
            
            return processed_positions
        else:
            logger.warning(f"⚠️ 第 {page_index} 页没有获取到岗位数据")
            return []
    
    def save_positions(self, positions: List[Dict[str, Any]], page_index: int) -> str:
        """
        保存岗位数据到文件
        
        Args:
            positions: 岗位数据列表
            page_index: 页码
            
        Returns:
            保存的文件路径
        """
        if not positions:
            logger.warning(f"⚠️ 第 {page_index} 页没有数据可保存")
            return ""
        
        # 创建输出目录
        output_path = os.path.join(self.output_dir, f"page_{page_index}")
        os.makedirs(output_path, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quark_page_{page_index}_{timestamp}.json"
        filepath = os.path.join(output_path, filename)
        
        # 保存数据
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "crawler_mode": "api_complete",
                    "extraction_time": datetime.now().isoformat(),
                    "page_number": page_index,
                    "positions_count": len(positions),
                    "csrf_token": f"{self.csrf_token[:8]}...{self.csrf_token[-8:]}",
                    "categories": self.base_params["categories"]
                },
                "positions": positions
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 已保存第 {page_index} 页 {len(positions)} 个岗位到: {filepath}")
        return filepath
    
    def crawl_all(self, start_page: int = 1, end_page: int = 10) -> Dict[str, Any]:
        """
        爬取所有页面
        
        Args:
            start_page: 起始页码
            end_page: 结束页码
            
        Returns:
            爬取结果摘要
        """
        logger.info(f"🚀 开始爬取所有页面: 第 {start_page} 页到第 {end_page} 页")
        
        start_time = time.time()
        all_positions = []
        successful_pages = 0
        
        for page in range(start_page, end_page + 1):
            self.current_page = page
            
            # 爬取单页
            positions = self.crawl_page(page)
            
            if positions:
                # 保存数据
                self.save_positions(positions, page)
                all_positions.extend(positions)
                successful_pages += 1
                
                # 显示进度
                completion = (self.positions_extracted / self.max_positions) * 100
                logger.info(f"📊 进度: {self.positions_extracted}/{self.max_positions} ({completion:.1f}%)")
            
            # 短暂延迟，避免请求过快
            time.sleep(1)
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        # 准备结果摘要
        result = {
            "success": len(all_positions) > 0,
            "mode": "api_complete",
            "total_positions_extracted": len(all_positions),
            "target_positions": self.max_positions,
            "completion_percentage": (len(all_positions) / self.max_positions) * 100,
            "successful_pages": successful_pages,
            "total_pages_crawled": end_page - start_page + 1,
            "elapsed_time_seconds": elapsed_time,
            "average_time_per_page": elapsed_time / (end_page - start_page + 1) if (end_page - start_page + 1) > 0 else 0,
            "data_quality": "verified" if len(all_positions) > 0 else "failed",
            "extraction_time": datetime.now().isoformat()
        }
        
        logger.info(f"🎉 爬取完成!")
        logger.info(f"   📊 总计获取: {len(all_positions)} 个岗位")
        logger.info(f"   🎯 目标岗位: {self.max_positions} 个")
        logger.info(f"   ✅ 完成比例: {result['completion_percentage']:.1f}%")
        logger.info(f"   ⏱️  总耗时: {elapsed_time:.2f} 秒")
        logger.info(f"   📄 成功页数: {successful_pages} 页")
        
        return result


def test_complete_api():
    """测试完整的API爬取器"""
    print("🧪 测试完整的API爬取器")
    print("=" * 60)
    
    # 创建爬取器
    crawler = QuarkApiCrawlerComplete({
        "output_dir": "output/test_complete",
        "max_positions": 93,
        "start_page": 4  # 从第4页开始（当前页面）
    })
    
    # 显示状态
    status = crawler.get_status()
    print("📊 爬取器状态:")
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print("\n📡 测试API连接...")
    
    # 测试获取当前页（第4页）
    data = crawler.fetch_page(page_index=4)
    
    if data:
        print("✅ API连接成功!")
        print(f"📊 API状态码: {data.get('code', 'N/A')}")
        print(f"📊 API消息: {data.get('msg', 'N/A')}")
        
        if data.get("code") == 0:
            total = data.get("data", {}).get("total", 0)
            positions = data.get("data", {}).get("list", [])
            
            print(f"🎉 总计 {total} 个岗位")
            print(f"📄 第4页获取 {len(positions)} 个岗位")
            
            # 显示前几个岗位
            print("\n📋 第4页前3个岗位:")
            for i, pos in enumerate(positions[:3]):
                print(f"  {i+1}. {pos.get('title', 'N/A')} - {pos.get('location', 'N/A')}")
            
            return True, total, len(positions)
        else:
            print(f"❌ API业务错误: {data.get('msg', '未知错误')}")
            return False, 0, 0
    else:
        print("❌ API连接失败")
        return False, 0, 0


def main():
    """主函数"""
    print("🚀 测试完整的API方案")
    print("=" * 60)
    print("📊 使用以下认证信息:")
    print(f"   🔐 CSRF令牌: c6ea8927...da836dfc")
    print(f"   🍪 Cookie长度: 631 字符")
    print(f"   🎯 筛选类别ID: 97,103,143,152,124,146,492")
    print()
    
    success, total_positions, page_positions = test_complete_api()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 API方案验证成功!")
        print(f"📊 发现 {total_positions} 个岗位")
        print(f"📄 第4页获取 {page_positions} 个岗位")
        
        if total_positions == 93:
            print("✅ 完美匹配页面显示 (93个岗位)")
        else:
            print(f"⚠️  页面显示93个岗位，但API返回 {total_positions} 个")
        
        print("\n💡 下一步:")
        print("   1. 使用这个爬取器完成所有页面的爬取")
        print("   2. 继续从第4页开始（当前页面）")
        print("   3. 爬取完成后生成数据报告")
    else:
        print("❌ API方案验证失败")
        print("💡 可能原因:")
        print("   1. CSRF令牌已过期")
        print("   2. Cookie无效")
        print("   3. 筛选参数不正确")
        print("   4. 网络或服务器问题")
    
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)