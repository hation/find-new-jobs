#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站API爬取器
基于B站官方招聘API实现数据爬取
"""

import os
import sys
import json
import time
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src/framework"))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BilibiliAPICrawler:
    """B站API爬取器"""
    
    def __init__(self, config_path: str = "config/api_auth.json"):
        """
        初始化B站API爬取器
        
        Args:
            config_path: API配置文件路径
        """
        self.config = self._load_config(config_path)
        self.base_url = self.config.get("base_url", "https://jobs.bilibili.com")
        self.api_endpoint = self.config.get("api_endpoint", "/api/srs/position/positionList")
        self.api_url = f"{self.base_url}{self.api_endpoint}"
        
        # 请求配置
        self.headers = self.config.get("request_headers", {})
        self.default_params = self.config.get("default_params", {})
        self.field_mapping = self.config.get("field_mapping", {})
        
        # 分页配置
        self.page_size = self.default_params.get("pageSize", 10)
        self.max_pages = 50  # 安全限制，避免无限爬取
        
        # 数据存储
        self.data_dir = Path("data/bilibili/raw")
        self.output_dir = Path("output/bilibili")
        self.log_dir = Path("logs/bilibili")
        
        # 创建目录
        for directory in [self.data_dir, self.output_dir, self.log_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 会话管理
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 状态跟踪
        self.total_crawled = 0
        self.last_crawl_time = None
        
        logger.info(f"🚀 初始化B站API爬取器")
        logger.info(f"🌐 API地址: {self.api_url}")
        logger.info(f"📊 每页数量: {self.page_size}")
        logger.info(f"📁 数据目录: {self.data_dir}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            bilibili_config = config.get("bilibili", {})
            if not bilibili_config:
                raise ValueError("配置文件中缺少bilibili配置")
            
            logger.info("✅ 加载B站API配置成功")
            return bilibili_config
            
        except FileNotFoundError:
            logger.error(f"❌ 配置文件不存在: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ 配置文件格式错误: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 加载配置失败: {e}")
            raise
    
    def _prepare_request_headers(self) -> Dict[str, str]:
        """准备请求头"""
        # 使用调试脚本中成功的headers配置
        headers = {
            "authority": "jobs.bilibili.com",
            "method": "POST",
            "path": self.api_endpoint,
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "cookie": "CURRENT_FNVAL=4048; buvid3=5D4FF9D2-A1C1-DCAD-8082-AB4C544E714000840infoc; b_nut=1771296600; _uuid=423969C4-C232-C364-3AFF-2AC10F1ADFF2C01646infoc; buvid_fp=6672304e623983edfd6286c07cb4dd77; buvid4=DE2608B1-2645-F0C8-D0B6-D11118FC8FFB02410-026021710-JsiGD1Ff0mxSW/UEw4D/Cw%3D%3D; CURRENT_QUALITY=0; rpdid=|(kY)lRkJl))0J'u~~~klu)|); bsource=search_baidu",
            "lunar-id": f"lunar-{int(time.time() * 1000)}-7446043945710",
            "origin": "https://jobs.bilibili.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "x-appkey": "ops.ehr-api.auth",
            "x-channel": "social",
            "x-csrf": "9741c476-d601-4c6d-8996-6a3912e0c0da",
            "x-usertype": "2"
        }
        
        return headers
    
    def _prepare_request_data(self, page_num: int) -> Dict[str, Any]:
        """准备请求数据"""
        request_data = self.default_params.copy()
        request_data["pageNum"] = page_num
        
        logger.debug(f"📋 第{page_num}页请求参数: {json.dumps(request_data, ensure_ascii=False)}")
        return request_data
    
    def crawl_page(self, page_num: int) -> Tuple[bool, Optional[List[Dict[str, Any]]], Optional[str]]:
        """
        爬取单页数据
        
        Args:
            page_num: 页码（从1开始）
            
        Returns:
            (是否成功, 数据列表, 错误信息)
        """
        logger.info(f"📄 开始爬取第{page_num}页数据")
        
        try:
            # 准备请求
            headers = self._prepare_request_headers()
            request_data = self._prepare_request_data(page_num)
            
            # 发送请求
            start_time = time.time()
            response = self.session.post(
                self.api_url,
                headers=headers,
                json=request_data,
                timeout=30
            )
            request_time = time.time() - start_time
            
            logger.info(f"🌐 请求完成，状态码: {response.status_code}, 耗时: {request_time:.2f}s")
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"HTTP错误: {response.status_code}"
                logger.error(f"❌ {error_msg}")
                return False, None, error_msg
            
            # 解析响应
            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                error_msg = f"JSON解析失败: {e}"
                logger.error(f"❌ {error_msg}")
                logger.debug(f"原始响应: {response.text[:500]}")
                return False, None, error_msg
            
            # 检查API响应码
            if response_data.get("code") != 0:
                error_msg = f"API错误: {response_data.get('message', '未知错误')}"
                logger.error(f"❌ {error_msg}")
                return False, None, error_msg
            
            # 提取数据
            data_list = response_data.get("data", {}).get("list", [])
            if not data_list:
                logger.warning(f"⚠️ 第{page_num}页没有数据")
                return True, [], None
            
            # 转换数据格式
            converted_data = self._convert_data_format(data_list)
            
            # 保存原始数据
            self._save_raw_data(page_num, response_data)
            
            logger.info(f"✅ 第{page_num}页爬取成功，获取{len(converted_data)}条数据")
            return True, converted_data, None
            
        except requests.exceptions.Timeout:
            error_msg = "请求超时"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
        except requests.exceptions.ConnectionError:
            error_msg = "连接错误"
            logger.error(f"❌ {error_msg}")
            return False, None, error_msg
        except Exception as e:
            error_msg = f"未知错误: {e}"
            logger.error(f"❌ {error_msg}")
            import traceback
            logger.debug(traceback.format_exc())
            return False, None, error_msg
    
    def _convert_data_format(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        转换数据格式：B站格式 → 标准格式
        
        Args:
            raw_data: B站原始数据
            
        Returns:
            标准化后的数据
        """
        converted_list = []
        
        for item in raw_data:
            converted_item = {}
            
            # 字段映射
            for std_field, bili_field in self.field_mapping.items():
                if bili_field in item:
                    converted_item[std_field] = item[bili_field]
                else:
                    converted_item[std_field] = None
            
            # 添加额外信息
            converted_item.update({
                "source": "bilibili",
                "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "detail_url": f"https://jobs.bilibili.com/position/{item.get('id')}",
                "raw_data": item  # 保留原始数据用于调试
            })
            
            # 数据清洗
            converted_item = self._clean_data(converted_item)
            converted_list.append(converted_item)
        
        return converted_list
    
    def _clean_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """数据清洗"""
        # 清洗发布时间格式
        if item.get("publish_time"):
            publish_time = item["publish_time"]
            # 尝试标准化时间格式
            try:
                # 移除可能的时区信息
                if "T" in publish_time:
                    publish_time = publish_time.replace("T", " ")
                item["publish_time"] = publish_time
            except:
                pass
        
        # 清洗岗位描述（移除多余换行）
        if item.get("description"):
            description = item["description"]
            # 合并连续的空行
            lines = [line.strip() for line in description.split("\n") if line.strip()]
            item["description"] = "\n".join(lines)
        
        return item
    
    def _save_raw_data(self, page_num: int, response_data: Dict[str, Any]) -> None:
        """保存原始数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bilibili_page_{page_num}_{timestamp}.json"
        filepath = self.data_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)
            logger.debug(f"💾 保存原始数据到: {filepath}")
        except Exception as e:
            logger.error(f"❌ 保存原始数据失败: {e}")
    
    def crawl_all_pages(self, max_pages: int = None) -> List[Dict[str, Any]]:
        """
        爬取所有页数据
        
        Args:
            max_pages: 最大爬取页数
            
        Returns:
            所有爬取的数据
        """
        max_pages = max_pages or self.max_pages
        all_data = []
        
        logger.info(f"🚀 开始爬取B站招聘数据，最多{max_pages}页")
        
        for page_num in range(1, max_pages + 1):
            logger.info(f"📖 处理第{page_num}/{max_pages}页")
            
            # 爬取单页
            success, page_data, error = self.crawl_page(page_num)
            
            if not success:
                logger.error(f"❌ 第{page_num}页爬取失败: {error}")
                # 如果连续失败，可能没有更多数据
                if page_num > 1 and len(all_data) > 0:
                    logger.info("📊 可能已爬取所有可用数据")
                    break
                continue
            
            if not page_data:
                logger.info("📊 没有更多数据，停止爬取")
                break
            
            # 添加到总数据
            all_data.extend(page_data)
            self.total_crawled += len(page_data)
            
            # 实时保存进度
            self._save_progress(page_num, all_data)
            
            # 控制请求频率（避免被封）
            if page_num < max_pages:
                wait_time = 2  # 2秒间隔
                logger.info(f"⏳ 等待{wait_time}秒后继续...")
                time.sleep(wait_time)
        
        logger.info(f"🎉 爬取完成，共获取{len(all_data)}条数据")
        return all_data
    
    def _save_progress(self, current_page: int, all_data: List[Dict[str, Any]]) -> None:
        """保存进度"""
        if not all_data:
            return
        
        # 每5页或最后保存一次进度
        if current_page % 5 == 0 or len(all_data) % 50 == 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            progress_file = self.output_dir / f"bilibili_progress_{timestamp}.json"
            
            try:
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "current_page": current_page,
                        "total_data": len(all_data),
                        "last_crawl_time": datetime.now().isoformat(),
                        "sample_data": all_data[:5]  # 保存前5条作为样本
                    }, f, ensure_ascii=False, indent=2)
                logger.info(f"📊 保存进度到: {progress_file}")
            except Exception as e:
                logger.error(f"❌ 保存进度失败: {e}")
    
    def save_final_data(self, data: List[Dict[str, Any]]) -> str:
        """
        保存最终数据
        
        Args:
            data: 要保存的数据
            
        Returns:
            保存的文件路径
        """
        if not data:
            logger.warning("⚠️ 没有数据需要保存")
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bilibili_jobs_{timestamp}.json"
        filepath = self.output_dir / filename
        
        try:
            # 准备保存的数据
            save_data = {
                "metadata": {
                    "source": "bilibili",
                    "crawled_at": datetime.now().isoformat(),
                    "total_jobs": len(data),
                    "page_size": self.page_size
                },
                "data": data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 保存最终数据到: {filepath}")
            logger.info(f"📊 数据统计: {len(data)}条记录")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ 保存数据失败: {e}")
            return ""
    
    def get_status(self) -> Dict[str, Any]:
        """获取爬取器状态"""
        return {
            "company": "bilibili",
            "api_url": self.api_url,
            "page_size": self.page_size,
            "total_crawled": self.total_crawled,
            "last_crawl_time": self.last_crawl_time,
            "data_dir": str(self.data_dir),
            "output_dir": str(self.output_dir)
        }


def main():
    """主函数"""
    print("=" * 70)
    print("🚀 B站API数据爬取器")
    print("=" * 70)
    
    try:
        # 创建爬取器实例
        crawler = BilibiliAPICrawler("config/api_auth.json")
        
        # 显示状态
        status = crawler.get_status()
        print(f"📊 公司: {status.get('company')}")
        print(f"🌐 API地址: {status.get('api_url')}")
        print(f"📊 每页数量: {status.get('page_size')}")
        print(f"📁 数据目录: {status.get('data_dir')}")
        print(f"📁 输出目录: {status.get('output_dir')}")
        print()
        
        # 开始爬取
        print("🔍 开始爬取B站招聘数据...")
        print("📝 配置信息:")
        print(f"  • 请求方法: POST")
        print(f"  • 认证方式: Headers + Cookie")
        print(f"  • 分页参数: pageNum")
        print(f"  • 每页数量: {crawler.page_size}")
        print()
        
        # 爬取数据（先测试1页）
        print("🧪 测试爬取第1页数据...")
        success, page_data, error = crawler.crawl_page(1)
        
        if success:
            print(f"✅ 测试成功，获取{len(page_data)}条数据")
            print()
            
            # 显示数据样本
            if page_data:
                print("📋 数据样本（前3条）:")
                for i, job in enumerate(page_data[:3], 1):
                    print(f"  {i}. {job.get('title')} - {job.get('location')}")
                    print(f"     类别: {job.get('category')}")
                    print(f"     发布时间: {job.get('publish_time')}")
                    print()
            
            # 询问是否爬取更多
            print("❓ 是否爬取更多数据？")
            print("  1. 继续爬取所有页")
            print("  2. 只保存当前页")
            print("  3. 退出")
            
            choice = input("请输入选择 (1/2/3): ").strip()
            
            if choice == "1":
                print("🚀 开始爬取所有页数据...")
                all_data = crawler.crawl_all_pages(max_pages=5)  # 先测试5页
                
                if all_data:
                    # 保存数据
                    save_path = crawler.save_final_data(all_data)
                    if save_path:
                        print(f"✅ 数据已保存到: {save_path}")
                    
                    # 显示统计信息
                    print()
                    print("📊 数据统计:")
                    print(f"  • 总记录数: {len(all_data)}")
                    print(f"  • 数据文件: {save_path}")
                    
            elif choice == "2":
                save_path = crawler.save_final_data(page_data)
                if save_path:
                    print(f"✅ 数据已保存到: {save_path}")
            else:
                print("👋 退出程序")
        
        else:
            print(f"❌ 测试失败: {error}")
            print()
            print("🔧 可能的原因:")
            print("  1. 网络连接问题")
            print("  2. API认证信息过期")
            print("  3. B站网站改版")
            print("  4. 反爬虫机制")
    
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 B站API爬取器演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()