#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蚂蚁国际招聘API爬取器
基于已确认的API接口和数据结构
版本: v1.0.0
创建时间: 2026-05-22
"""

import json
import requests
import sys
import time
from datetime import datetime
from pathlib import Path
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / 'logs' / 'ant_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AntJobCrawler:
    """蚂蚁国际招聘爬取器"""
    
    def __init__(self, config_path=None):
        """初始化爬取器"""
        self.project_root = project_root
        self.config = self.load_config(config_path)
        self.session = requests.Session()
        self.setup_session()
        
        # 输出目录
        self.output_dir = project_root / "output" / "json"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 统计信息
        self.stats = {
            "total_positions": 0,
            "successful_pages": 0,
            "failed_pages": 0,
            "start_time": datetime.now(),
            "positions_saved": 0
        }
        
        logger.info("🚀 蚂蚁国际招聘爬取器初始化完成")
    
    def load_config(self, config_path=None):
        """加载配置文件"""
        if config_path is None:
            config_path = project_root / "config" / "api_auth.json"
        
        if not config_path.exists():
            logger.error(f"❌ 配置文件不存在: {config_path}")
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"✅ 加载配置文件: {config_path}")
            return config
        except Exception as e:
            logger.error(f"❌ 加载配置文件失败: {e}")
            raise
    
    def setup_session(self):
        """设置会话"""
        # 设置请求头
        headers = self.config.get("authentication", {}).get("headers", {})
        self.session.headers.update(headers)
        
        # 设置Cookie
        cookies = self.config.get("authentication", {}).get("cookies", {})
        for name, value in cookies.items():
            self.session.cookies.set(name, value)
        
        logger.info(f"📋 设置请求头: {len(headers)}个")
        logger.info(f"🍪 设置Cookie: {len(cookies)}个")
    
    def build_request_body(self, page_no=1, page_size=10):
        """构建请求体"""
        # 获取筛选参数
        page_urls = self.config.get("page_urls", {})
        list_page = page_urls.get("list_page", "")
        
        # 从URL中提取categories参数
        categories = ""
        if "categories=" in list_page:
            # 提取categories参数值
            start = list_page.find("categories=") + len("categories=")
            end = list_page.find("&", start)
            if end == -1:
                end = len(list_page)
            categories = list_page[start:end]
        
        request_body = {
            "pageNo": page_no,
            "pageSize": page_size,
            "categories": categories,
            "regions": ""  # 空表示所有地区
        }
        
        logger.debug(f"📦 构建请求体: {json.dumps(request_body, ensure_ascii=False)}")
        return request_body
    
    def get_api_endpoint(self):
        """获取API端点"""
        api_endpoints = self.config.get("api_endpoints", {})
        full_url = api_endpoints.get("full_url", "")
        
        if not full_url:
            logger.error("❌ API端点未配置")
            raise ValueError("API端点未配置")
        
        return full_url
    
    def fetch_page(self, page_no=1, page_size=10):
        """获取单页数据"""
        api_url = self.get_api_endpoint()
        request_body = self.build_request_body(page_no, page_size)
        
        logger.info(f"📡 获取第{page_no}页数据 (每页{page_size}条)")
        
        try:
            response = self.session.post(
                api_url,
                json=request_body,
                timeout=30
            )
            
            logger.info(f"📥 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # 验证响应结构
                if self.validate_response(data):
                    logger.info(f"✅ 第{page_no}页数据获取成功")
                    self.stats["successful_pages"] += 1
                    return data
                else:
                    logger.warning(f"⚠️  第{page_no}页响应结构验证失败")
                    return None
            else:
                logger.error(f"❌ 第{page_no}页请求失败，状态码: {response.status_code}")
                logger.error(f"📝 响应文本: {response.text[:200]}...")
                self.stats["failed_pages"] += 1
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ 第{page_no}页请求超时")
            self.stats["failed_pages"] += 1
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ 第{page_no}页连接错误")
            self.stats["failed_pages"] += 1
            return None
        except json.JSONDecodeError:
            logger.error(f"❌ 第{page_no}页响应不是有效的JSON格式")
            self.stats["failed_pages"] += 1
            return None
        except Exception as e:
            logger.error(f"❌ 第{page_no}页请求异常: {e}")
            self.stats["failed_pages"] += 1
            return None
    
    def validate_response(self, data):
        """验证响应数据"""
        if not isinstance(data, dict):
            logger.error("响应数据不是字典类型")
            return False
        
        # 检查成功状态
        success = data.get("success")
        if success is not True:
            logger.error(f"API返回失败状态: {success}")
            return False
        
        # 检查错误代码
        error_code = data.get("errorCode")
        if error_code != "success":
            logger.error(f"API返回错误代码: {error_code}")
            return False
        
        # 检查数据字段
        content = data.get("content")
        if not isinstance(content, list):
            logger.error(f"content字段不是列表类型: {type(content)}")
            return False
        
        # 检查分页信息
        required_fields = ["totalCount", "pageSize", "currentPage"]
        for field in required_fields:
            if field not in data:
                logger.warning(f"缺少分页字段: {field}")
        
        logger.info(f"📊 验证通过: {len(content)}个岗位，总{data.get('totalCount', 'N/A')}个")
        return True
    
    def save_positions(self, positions, page_no):
        """保存岗位数据"""
        if not positions:
            logger.warning(f"第{page_no}页无岗位数据可保存")
            return
        
        saved_count = 0
        
        for position in positions:
            try:
                # 生成文件名
                position_id = position.get("id", "unknown")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ant_page{page_no}_position_{position_id}_{timestamp}.json"
                filepath = self.output_dir / filename
                
                # 保存单个岗位数据
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(position, f, ensure_ascii=False, indent=2)
                
                saved_count += 1
                self.stats["positions_saved"] += 1
                
                logger.debug(f"💾 保存岗位 {position_id} 到 {filename}")
                
            except Exception as e:
                logger.error(f"❌ 保存岗位数据失败: {e}")
        
        logger.info(f"💾 第{page_no}页保存了 {saved_count}/{len(positions)} 个岗位")
    
    def save_page_data(self, data, page_no):
        """保存整页数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ant_page_{page_no}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📁 保存第{page_no}页完整数据到: {filename}")
            return filepath
        except Exception as e:
            logger.error(f"❌ 保存第{page_no}页数据失败: {e}")
            return None
    
    def calculate_total_pages(self, total_count, page_size):
        """计算总页数"""
        if total_count <= 0 or page_size <= 0:
            return 0
        
        total_pages = (total_count + page_size - 1) // page_size
        logger.info(f"📊 总岗位数: {total_count}, 页大小: {page_size}, 总页数: {total_pages}")
        return total_pages
    
    def crawl_all_pages(self, start_page=1, max_pages=None):
        """爬取所有页面"""
        logger.info("="*70)
        logger.info("🚀 开始爬取蚂蚁国际招聘所有岗位")
        logger.info("="*70)
        
        # 先获取第一页，了解总页数
        first_page_data = self.fetch_page(start_page)
        if not first_page_data:
            logger.error("❌ 获取第一页数据失败，无法继续")
            return False
        
        total_count = first_page_data.get("totalCount", 0)
        page_size = first_page_data.get("pageSize", 10)
        
        if total_count == 0:
            logger.warning("⚠️  总岗位数为0，可能API配置有误")
            return False
        
        # 保存第一页数据
        self.save_page_data(first_page_data, start_page)
        positions = first_page_data.get("content", [])
        self.save_positions(positions, start_page)
        
        # 计算总页数
        total_pages = self.calculate_total_pages(total_count, page_size)
        
        if max_pages and max_pages < total_pages:
            total_pages = max_pages
            logger.info(f"📌 限制最大爬取页数: {max_pages}")
        
        # 爬取剩余页面
        for page_no in range(start_page + 1, total_pages + 1):
            logger.info(f"\n📄 处理第 {page_no}/{total_pages} 页")
            
            # 添加延迟，避免请求过快
            if page_no > start_page:
                time.sleep(1)  # 1秒延迟
            
            page_data = self.fetch_page(page_no, page_size)
            if page_data:
                self.save_page_data(page_data, page_no)
                positions = page_data.get("content", [])
                self.save_positions(positions, page_no)
            else:
                logger.warning(f"⚠️  第{page_no}页获取失败，跳过")
            
            # 显示进度
            progress = (page_no / total_pages) * 100
            logger.info(f"📈 进度: {page_no}/{total_pages}页 ({progress:.1f}%)")
        
        return True
    
    def generate_report(self):
        """生成爬取报告"""
        end_time = datetime.now()
        duration = (end_time - self.stats["start_time"]).total_seconds()
        
        report = {
            "project": "蚂蚁国际招聘数据爬取",
            "start_time": self.stats["start_time"].isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "stats": self.stats,
            "output_directory": str(self.output_dir),
            "config_file": "config/api_auth.json"
        }
        
        # 保存报告
        report_dir = project_root / "output" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"crawl_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 爬取报告已保存到: {report_file}")
        
        # 打印摘要
        print("\n" + "="*70)
        print("📊 爬取完成摘要")
        print("="*70)
        print(f"⏱️  耗时: {duration:.1f}秒")
        print(f"📄 成功页面: {self.stats['successful_pages']}")
        print(f"❌ 失败页面: {self.stats['failed_pages']}")
        print(f"💾 保存岗位: {self.stats['positions_saved']}")
        print(f"📁 输出目录: {self.output_dir}")
        print("="*70)
        
        return report
    
    def test_connection(self):
        """测试API连接"""
        logger.info("🔗 测试API连接...")
        
        test_data = self.fetch_page(1, 5)  # 只获取5条测试
        if test_data:
            logger.info("✅ API连接测试成功")
            
            # 显示测试结果
            content = test_data.get("content", [])
            if content:
                logger.info(f"📋 测试获取到 {len(content)} 个岗位")
                logger.info("🔍 第一个岗位信息:")
                first_position = content[0]
                logger.info(f"  • ID: {first_position.get('id')}")
                logger.info(f"  • 名称: {first_position.get('name')}")
                logger.info(f"  • 地点: {first_position.get('workLocations')}")
                logger.info(f"  • 部门: {first_position.get('department')}")
            
            return True
        else:
            logger.error("❌ API连接测试失败")
            return False

def main():
    """主函数"""
    print("="*70)
    print("🚀 蚂蚁国际招聘API爬取器")
    print("="*70)
    
    try:
        # 初始化爬取器
        crawler = AntJobCrawler()
        
        # 测试连接
        print("\n1. 🔗 测试API连接...")
        if not crawler.test_connection():
            print("❌ API连接测试失败，请检查配置")
            return
        
        # 询问用户
        print("\n2. 📋 选择爬取模式:")
        print("   1) 测试模式 (只爬取前3页)")
        print("   2) 完整模式 (爬取所有页面)")
        print("   3) 自定义模式 (指定页数)")
        
        choice = input("\n请选择模式 (1-3): ").strip()
        
        if choice == "1":
            # 测试模式
            print("\n🎯 开始测试模式 (爬取前3页)...")
            success = crawler.crawl_all_pages(start_page=1, max_pages=3)
        elif choice == "2":
            # 完整模式
            print("\n🎯 开始完整模式 (爬取所有页面)...")
            success = crawler.crawl_all_pages(start_page=1)
        elif choice == "3":
            # 自定义模式
            try:
                start_page = int(input("起始页码 (默认1): ") or "1")
                max_pages = int(input("最大页数 (默认10): ") or "10")
                print(f"\n🎯 开始自定义模式 (从第{start_page}页开始，最多{max_pages}页)...")
                success = crawler.crawl_all_pages(start_page=start_page, max_pages=max_pages)
            except ValueError:
                print("❌ 输入无效，使用默认设置")
                success = crawler.crawl_all_pages(start_page=1, max_pages=10)
        else:
            print("❌ 无效选择，使用测试模式")
            success = crawler.crawl_all_pages(start_page=1, max_pages=3)
        
        # 生成报告
        if success:
            crawler.generate_report()
            print("\n✅ 爬取完成！")
        else:
            print("\n❌ 爬取过程中出现错误")
        
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        logger.exception("程序异常")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())