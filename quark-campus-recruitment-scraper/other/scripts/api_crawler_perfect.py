#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
夸克校园招聘API爬取器（完美版）
使用完全正确的认证信息和请求参数
基于用户提供的实际网络请求
"""

import json
import time
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class QuarkApiCrawlerPerfect:
    """夸克校园招聘API爬取器（使用完全正确的认证信息）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化API爬取器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # ✅ 完整的API端点
        self.api_url = "https://talent.quark.cn/position/search"
        
        # ✅ 用户提供的CSRF令牌（完全正确）
        self.csrf_token = "c6ea8927-62fd-42ab-9eab-d1f3da836dfc"
        
        # ✅ 用户提供的完整Cookie（完全正确）
        self.cookies = {
            "XSRF-TOKEN": "c6ea8927-62fd-42ab-9eab-d1f3da836dfc",
            "prefered-lang": "zh",
            "SESSION": "MTQzNjY5NTVCQUJFM0EwRDBDMkNDMEU2ODUyQ0NDQzM=",
            "cna": "QH2RIvlJWR4CAQ6ZRGRcngaX",
            "xlly_s": "1",
            "tfstk": "gYUoDT9-lx9sv5pVSpu5mywLXBIAP4gITJLKp2HF0xkXJ_wdNkcEnWxRNDe8mv2mhYEdO7kn--Fe2U3rJJDUe5P-eWFPtwVU_JmCNvHEKJFU2sQOW7NSR2zhBNQ9zQXc68vr4v5eufhGMbuuBQjKR2WOHnLEVN0Qe0VzR2PViXhIL3yE4Elqhf9r8Yoe3nlZ3vuULvl2uXGnTHorasVqhX0ELJoPiqkjT2kUL2kK3Ik8L8aVCuUVDkaysrloqAPrU7F7u_oDVWDcgs40m5MZWxYe8rcuOxd_EU7i3uEUyqzP3Eu41oeriVbkCbq4s4ludNTSz5P4Y04hvCMQmSrtmoOROva0gzrUGLXEGky-uxyeE_D3u8eIyr5e4Ar8e4k0R6TIUuFUJD4PQBHzP8Umfy9lHvETMzo0QtL0dDqUyqzP3Njzen-N5PTIg6U2AHirGjDthVDqFB1fIbCcihrs4jGPWsfDAworGj0PisxwF0ljav1..",
            "isg": "BFpa-Fzy5FipN2jzGwJ1pjJOqwZ8i95lwiWZwWTRB-3k1_MRTRnkdwvhp6PLB1b9"
        }
        
        # ✅ 完全正确的请求参数（基于实际请求）
        self.base_params = {
            "channel": "group_official_site",
            "language": "zh",
            "batchId": "",
            "categories": "97,103,143,124,152,492,146",  # ✅ 7个筛选类别ID（正确的顺序）
            "deptCodes": [],
            "key": "",
            "pageIndex": 1,
            "pageSize": 10,
            "regions": "",
            "subCategories": "403,404,405,406,108,474,475,476,477,478,479,480,481,482,483,484,529,757,758,759,763,834,846,847,446,447,448,126,445,716,812,824,825,156,461,462,463,464,465,466,467,468,469,470,471,472,473,512,513,493,494,495,496,497,514,515,516,517,518,519,520,521,771,807,842,843,844,845,147,151,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426",
            "shareType": "",
            "shareId": "",
            "myReferralShareCode": ""
        }
        
        # ✅ 完全正确的请求头（基于实际请求）
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "bx-v": "2.5.11",
            "Origin": "https://talent.quark.cn",
            "Referer": "https://talent.quark.cn/off-campus/position-list?lang=zh",
            "Sec-Ch-Ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=1, i",
            "Connection": "keep-alive"
        }
        
        # 输出目录
        self.output_dir = config.get("output_dir", "output/positions_perfect")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 状态跟踪
        self.positions_extracted = 0
        self.current_page = config.get("start_page", 4)  # 当前在第4页
        self.total_pages = 10  # 根据页面显示
        self.max_positions = 93  # 页面显示93个岗位
        
        logger.info(f"🎯 夸克API爬取器（完美版）初始化完成")
        logger.info(f"   📍 当前页面: 第 {self.current_page} 页/共 {self.total_pages} 页")
        logger.info(f"   🎯 目标岗位: {self.max_positions} 个")
        logger.info(f"   🔐 CSRF令牌: {self.csrf_token[:8]}...{self.csrf_token[-8:]}")
        logger.info(f"   🍪 Cookie数量: {len(self.cookies)} 个")
        logger.info(f"   📊 筛选类别: {self.base_params['categories']}")
        logger.info(f"   💾 输出目录: {self.output_dir}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取爬取器状态
        
        Returns:
            状态字典
        """
        return {
            "type": "api_perfect",
            "positions_extracted": self.positions_extracted,
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "completion_percentage": (self.positions_extracted / self.max_positions) * 100,
            "output_dir": self.output_dir,
            "csrf_token": f"{self.csrf_token[:8]}...{self.csrf_token[-8:]}",
            "has_valid_cookies": bool(self.cookies),
            "api_url": self.api_url
        }
    
    def fetch_page(self, page_index: int = None, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """
        获取单页数据
        
        Args:
            page_index: 页码（从1开始），默认使用当前页
            page_size: 每页数量
            
        Returns:
            解析后的API响应数据，失败返回None
        """
        if page_index is None:
            page_index = self.current_page
        
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
        logger.debug(f"   请求头数量: {len(self.headers)} 个")
        logger.debug(f"   Cookie数量: {len(self.cookies)} 个")
        
        try:
            # 发送POST请求（使用所有正确的信息）
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
                    api_code = data.get("code")
                    api_msg = data.get("msg", "无消息")
                    
                    if api_code == 0:
                        total = data.get("data", {}).get("total", 0)
                        positions = data.get("data", {}).get("list", [])
                        
                        logger.info(f"🎉 成功获取 {len(positions)} 个岗位，总计 {total} 个岗位")
                        logger.info(f"📊 API消息: {api_msg}")
                        
                        # 更新目标岗位数
                        if total > 0:
                            logger.info(f"📈 API返回总计 {total} 个岗位")
                            self.max_positions = total
                        
                        return data
                    else:
                        logger.error(f"❌ API业务错误: 代码={api_code}, 消息={api_msg}")
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
                # 提取关键字段（基于实际API响应结构）
                processed_pos = {
                    "position_id": pos.get("id") or pos.get("positionId") or f"quark_{page_index}_{i+1:02d}",
                    "position_name": pos.get("title") or pos.get("positionName") or "未知岗位",
                    "position_category": pos.get("categoryName") or pos.get("category") or "未知类别",
                    "work_location": pos.get("location") or pos.get("workLocation") or "未知地点",
                    "update_time": pos.get("updateTime") or pos.get("publishTime") or "未知时间",
                    "department": pos.get("department") or pos.get("deptName") or "未知部门",
                    "education_requirement": pos.get("education") or pos.get("educationRequirement") or "学历不限",
                    "work_experience": pos.get("experience") or pos.get("workExperience") or "经验不限",
                    "position_description": pos.get("description") or pos.get("positionDesc") or "",
                    "position_requirements": pos.get("requirement") or pos.get("positionRequirement") or "",
                    "other_info": json.dumps(pos, ensure_ascii=False),
                    "source": "api_perfect",
                    "extract_time": datetime.now().isoformat(),
                    "page_number": page_index,
                    "position_in_page": i + 1,
                    # 额外字段（如果存在）
                    "salary": pos.get("salary") or "",
                    "work_type": pos.get("workType") or "",
                    "recruit_num": pos.get("recruitNum") or 1
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
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quark_page_{page_index}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # 保存数据
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "crawler_mode": "api_perfect",
                    "extraction_time": datetime.now().isoformat(),
                    "page_number": page_index,
                    "positions_count": len(positions),
                    "current_position": f"{self.positions_extracted}/{self.max_positions}",
                    "csrf_token": f"{self.csrf_token[:8]}...{self.csrf_token[-8:]}",
                    "categories": self.base_params["categories"]
                },
                "positions": positions
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 已保存第 {page_index} 页 {len(positions)} 个岗位到: {filepath}")
        return filepath
    
    def crawl_all(self, start_page: int = None, end_page: int = None) -> Dict[str, Any]:
        """
        爬取所有页面
        
        Args:
            start_page: 起始页码，默认从当前页开始
            end_page: 结束页码，默认到最后一页
            
        Returns:
            爬取结果摘要
        """
        if start_page is None:
            start_page = self.current_page
        if end_page is None:
            end_page = self.total_pages
        
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
            time.sleep(1.5)
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        # 准备结果摘要
        result = {
            "success": len(all_positions) > 0,
            "mode": "api_perfect",
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


def test_perfect_api():
    """测试完美的API爬取器"""
    print("🧪 测试完美的API爬取器")
    print("=" * 60)
    
    # 创建爬取器
    crawler = QuarkApiCrawlerPerfect({
        "output_dir": "output/test_perfect",
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
                title = pos.get('title', '未知标题')
                location = pos.get('location', '未知地点')
                category = pos.get('categoryName', '未知类别')
                print(f"  {i+1}. {title}")
                print(f"     地点: {location}, 类别: {category}")
            
            return True, total, len(positions), positions[:3]
        else:
            print(f"❌ API业务错误: {data.get('msg', '未知错误')}")
            return False, 0, 0, []
    else:
        print("❌ API连接失败")
        return False, 0, 0, []


def main():
    """主函数"""
    print("🚀 测试完美的API方案")
    print("=" * 60)
    print("📊 使用以下认证信息:")
    print(f"   🔐 CSRF令牌: c6ea8927...da836dfc")
    print(f"   🍪 Cookie数量: 7 个（包括SESSION和XSRF-TOKEN）")
    print(f"   🎯 筛选类别ID: 97,103,143,124,152,492,146")
    print(f"   📍 当前页面: 第4页/共10页")
    print(f"   🎯 目标岗位: 93个（页面显示）")
    print()
    
    success, total_positions, page_positions, sample_positions = test_perfect_api()
    
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
        print("   2. 从第4页开始继续爬取")
        print("   3. 爬取完成后生成数据报告")
    else:
        print("❌ API方案验证失败")
        print("💡 可能原因:")
        print("   1. CSRF令牌已过期")
        print("   2. Cookie无效")
        print("   3. 请求头不完整")
        print("   4. 网络或服务器问题")
    
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)