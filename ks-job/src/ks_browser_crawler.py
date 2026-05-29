#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘浏览器自动化爬取器
基于Playwright的浏览器自动化，解决签名验证问题
"""

import sys
import os
import json
import time
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlencode, urljoin

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ks_browser_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class KsBrowserCrawler:
    """快手招聘浏览器自动化爬取器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化浏览器爬取器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 网站配置
        self.base_url = self.config.get("base_url", "https://zhaopin.kuaishou.cn")
        self.api_url = urljoin(self.base_url, "/recruit/e/api/v1/open/positions/simple")
        
        # 浏览器配置
        self.headless = self.config.get("headless", True)
        self.browser_type = self.config.get("browser_type", "chromium")
        self.timeout = self.config.get("timeout", 30000)  # 毫秒
        self.viewport = self.config.get("viewport", {"width": 1920, "height": 1080})
        
        # 爬取配置
        self.page_size = self.config.get("page_size", 10)
        self.max_pages = self.config.get("max_pages", 10)
        self.delay_between_requests = self.config.get("delay_between_requests", 2000)  # 毫秒
        
        # 输出配置
        self.output_dir = self.config.get("output_dir", "output/ks_data")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 状态跟踪
        self.total_positions = 0
        self.total_pages = 0
        self.current_page = 0
        self.positions_crawled = 0
        self.start_time = None
        
        # 浏览器实例
        self.browser = None
        self.context = None
        self.page = None
        
        logger.info("✅ 快手浏览器爬取器初始化完成")
        logger.info(f"   网站地址: {self.base_url}")
        logger.info(f"   API地址: {self.api_url}")
        logger.info(f"   浏览器模式: {'无头' if self.headless else '有头'}")
    
    async def _init_browser(self):
        """初始化浏览器"""
        try:
            from playwright.async_api import async_playwright
            
            logger.info("🔄 启动浏览器...")
            playwright = await async_playwright().start()
            
            # 启动浏览器
            self.browser = await playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )
            
            # 创建上下文
            self.context = await self.browser.new_context(
                viewport=self.viewport,
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
                locale="zh-CN",
                timezone_id="Asia/Shanghai"
            )
            
            # 创建页面
            self.page = await self.context.new_page()
            
            # 设置请求拦截，捕获API请求
            await self._setup_request_interception()
            
            logger.info("✅ 浏览器启动成功")
            return True
            
        except ImportError:
            logger.error("❌ 未安装Playwright，请运行: pip install playwright")
            logger.error("   然后运行: python -m playwright install")
            return False
            
        except Exception as e:
            logger.error(f"❌ 浏览器启动失败: {e}")
            return False
    
    async def _setup_request_interception(self):
        """设置请求拦截，捕获API请求"""
        async def handle_request(route, request):
            # 记录API请求
            if "positions/simple" in request.url:
                logger.info(f"📡 捕获API请求: {request.url}")
                logger.info(f"   请求头: {request.headers}")
            
            # 继续请求
            await route.continue_()
        
        # 启用请求拦截
        await self.page.route("**/*", handle_request)
    
    async def _get_api_response(self, page_num: int = 1) -> Optional[Dict[str, Any]]:
        """
        通过浏览器获取API响应
        
        Args:
            page_num: 页码
            
        Returns:
            API响应数据
        """
        try:
            # 构建API请求URL
            params = {
                "pageNum": page_num,
                "pageSize": self.page_size,
                "positionCategoryCode": "J0005,J0004,J0013,J0006,J0014",
                "positionNatureCode": "C001",
                "recruitProject": "socialr",
                "workLocationCode": "domestic"
            }
            
            api_url = f"{self.api_url}?{urlencode(params)}"
            logger.info(f"📡 请求API: pageNum={page_num}, pageSize={self.page_size}")
            
            # 使用浏览器发送请求
            response = await self.page.goto(api_url, wait_until="networkidle")
            
            if not response or response.status != 200:
                logger.error(f"❌ API请求失败: 状态码 {response.status if response else '无响应'}")
                return None
            
            # 获取响应内容
            content = await response.text()
            
            try:
                data = json.loads(content)
                
                # 检查API错误码
                if data.get("code") != 0:
                    logger.error(f"❌ API业务错误: code={data.get('code')}, message={data.get('message')}")
                    return None
                
                logger.info(f"✅ API请求成功: 获取到 {len(data.get('result', {}).get('list', []))} 个岗位")
                return data
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON解析失败: {e}")
                logger.error(f"   响应内容: {content[:500]}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 获取API响应失败: {e}")
            return None
    
    async def fetch_positions_page(self, page_num: int = 1) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        获取单页岗位数据
        
        Args:
            page_num: 页码
            
        Returns:
            (岗位列表, 分页信息)
        """
        # 确保浏览器已初始化
        if not self.page:
            if not await self._init_browser():
                return [], {}
        
        # 先访问首页获取Cookie
        if page_num == 1:
            logger.info("🌐 访问首页获取Cookie...")
            await self.page.goto(self.base_url, wait_until="networkidle")
            await asyncio.sleep(3)  # 等待页面加载
        
        # 获取API数据
        response_data = await self._get_api_response(page_num)
        
        if not response_data:
            return [], {}
        
        # 提取数据
        result = response_data.get("result", {})
        positions = result.get("list", [])
        pagination = {
            "total": result.get("total", 0),
            "pageNum": result.get("pageNum", page_num),
            "pageSize": result.get("pageSize", self.page_size),
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
    
    async def fetch_all_positions(self, max_pages: int = None) -> List[Dict[str, Any]]:
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
        positions, pagination = await self.fetch_positions_page(1)
        
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
            await asyncio.sleep(self.delay_between_requests / 1000)
            
            # 显示进度
            progress = (page_num - 1) / max_pages * 100
            logger.info(f"📊 进度: {page_num-1}/{max_pages}页 ({progress:.1f}%)")
            
            positions, _ = await self.fetch_positions_page(page_num)
            
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
            "crawlMode": "browser",
            "source": "kuaishou_browser",
            
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
            "publishTime", "detailUrl"
        ]
        
        missing_fields = []
        for field in required_fields:
            if not position.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            logger.warning(f"⚠️ 岗位 {position.get('positionId')} 缺失关键字段: {missing_fields}")
            return False
        
        return True
    
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
    
    async def crawl_and_save(self, max_pages: int = 5) -> Dict[str, Any]:
        """
        完整爬取流程：爬取数据并保存
        
        Args:
            max_pages: 最大爬取页数
            
        Returns:
            爬取统计信息
        """
        logger.info(f"🚀 开始完整爬取流程（最大 {max_pages} 页）")
        
        # 获取所有数据
        all_positions = await self.fetch_all_positions(max_pages)
        
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
        
        # 关闭浏览器
        await self._close_browser()
        
        # 返回统计信息
        stats = {
            "success": True,
            "total_positions": len(all_positions),
            "valid_positions": valid_positions,
            "saved_files": len(saved_files),
            "valid_percentage": valid_positions / len(all_positions) * 100 if all_positions else 0,
            "output_dir": self.output_dir,
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "crawl_mode": "browser"
        }
        
        logger.info("=" * 60)
        logger.info(f"🎉 爬取完成!")
        logger.info(f"   • 总岗位数: {stats['total_positions']}")
        logger.info(f"   • 有效岗位: {stats['valid_positions']} ({stats['valid_percentage']:.1f}%)")
        logger.info(f"   • 保存文件: {stats['saved_files']}")
        logger.info(f"   • 输出目录: {stats['output_dir']}")
        logger.info("=" * 60)
        
        return stats
    
    async def _close_browser(self):
        """关闭浏览器"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("✅ 浏览器已关闭")
        except Exception as e:
            logger.error(f"❌ 关闭浏览器失败: {e}")


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config", ".env"
    )
    
    config = {
        "base_url": "https://zhaopin.kuaishou.cn",
        "headless": False,  # 显示浏览器窗口，便于调试
        "browser_type": "chromium",
        "timeout": 30000,
        "viewport": {"width": 1920, "height": 1080},
        "page_size": 10,
        "max_pages": 5,
        "delay_between_requests": 2000,
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


async def main_async():
    """异步主函数"""
    print("=" * 70)
    print("🚀 快手招聘浏览器自动化爬取器")
    print("=" * 70)
    print("基于Playwright的浏览器自动化，解决签名验证问题")
    print()
    
    # 加载配置
    config = load_config()
    
    # 创建爬取器
    print("🔄 创建快手浏览器爬取器...")
    crawler = KsBrowserCrawler(config)
    
    # 测试单页爬取
    print()
    print("📡 测试单页爬取...")
    positions, pagination = await crawler.fetch_positions_page(1)
    
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
            stats = await crawler.crawl_and_save(max_pages=max_pages)
            
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
        print("   1. 网络连接问题")
        print("   2. 网站反爬虫机制")
        print("   3. 浏览器启动失败")
        print("   4. API接口变更")
    
    print("=" * 70)


def main():
    """主函数"""
    # 运行异步主函数
    asyncio.run(main_async())


if __name__ == "__main__":
    main()