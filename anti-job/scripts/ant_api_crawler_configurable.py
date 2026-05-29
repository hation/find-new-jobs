#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蚂蚁国际招聘API爬取器（可配置版）
基于夸克项目API爬取器规范实现
版本: v1.0.0
创建时间: 2026-05-22
"""

import json
import time
import logging
import requests
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / 'logs' / 'ant_api_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AntApiCrawlerConfigurable:
    """蚂蚁国际招聘API爬取器（可配置版）"""
    
    def __init__(self, config_path: str = None):
        """
        初始化API爬取器（基于夸克项目规范）
        
        Args:
            config_path: 配置文件路径，默认使用 config/ant_api_auth.json
        """
        # 加载配置文件
        self.config_path = config_path or str(project_root / "config" / "ant_api_auth.json")
        self.config = self._load_config()
        
        if not self.config:
            raise ValueError(f"无法加载配置文件: {self.config_path}")
        
        # 从配置中获取认证信息
        self.api_url = self.config.get("api_endpoints", {}).get("full_url", "")
        self.cookies = self.config.get("authentication", {}).get("cookies", {})
        self.headers = self.config.get("authentication", {}).get("headers", {})
        
        # 获取参数配置
        self.parameters = self.config.get("parameters", {})
        self.validation = self.config.get("validation", {})
        self.data_mapping = self.config.get("data_mapping", {})
        self.response_structure = self.config.get("response_structure", {})
        
        # 创建会话
        self.session = requests.Session()
        self._setup_session()
        
        # 输出目录（基于夸克项目规范）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = project_root / "output" / f"ant_api_crawl_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        (self.output_dir / "positions").mkdir(exist_ok=True)
        (self.output_dir / "pages").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        
        # 状态跟踪（基于夸克项目规范）
        self.positions_extracted = 0
        self.current_page = 1
        self.total_pages = 0
        self.max_positions = self.validation.get("expected_total_positions", 0)
        self.start_time = datetime.now()
        
        # 检查点文件（用于断点续传）
        self.checkpoint_file = self.output_dir / "checkpoint.json"
        
        logger.info("="*70)
        logger.info("🚀 蚂蚁国际API爬取器（可配置版）初始化完成")
        logger.info(f"   配置文件: {self.config_path}")
        logger.info(f"   API端点: {self.api_url}")
        logger.info(f"   Cookie数量: {len(self.cookies)} 个")
        logger.info(f"   请求头数量: {len(self.headers)} 个")
        logger.info(f"   输出目录: {self.output_dir}")
        logger.info(f"   检查点文件: {self.checkpoint_file}")
        logger.info("="*70)
    
    def _load_config(self) -> Optional[Dict[str, Any]]:
        """加载配置文件"""
        config_path = Path(self.config_path)
        
        if not config_path.exists():
            logger.error(f"❌ 配置文件不存在: {config_path}")
            
            # 创建示例配置文件
            if config_path.name == "ant_api_auth.json":
                config_path.parent.mkdir(parents=True, exist_ok=True)
                
                example_config = {
                    "description": "蚂蚁国际招聘API认证配置文件",
                    "last_updated": datetime.now().isoformat(),
                    "status": "example",
                    "authentication": {
                        "ctoken": "YOUR_CTOKEN_HERE",
                        "cookies": {
                            "SESSION": "YOUR_SESSION_TOKEN_HERE",
                            "ctoken": "YOUR_CTOKEN_HERE"
                        },
                        "headers": {
                            "User-Agent": "Mozilla/5.0 ...",
                            "Content-Type": "application/json;charset=UTF-8"
                        }
                    },
                    "api_endpoints": {
                        "full_url": "https://hrcareersweb.antgroup.com/api/social/position/search?ctoken=YOUR_CTOKEN_HERE",
                        "method": "POST"
                    },
                    "parameters": {
                        "pagination": {
                            "page_param": "pageNo",
                            "size_param": "pageSize",
                            "default_page_size": 10
                        },
                        "categories": {
                            "all_categories": "98,99,100,101,102,403,404,405,406,104,105,106,107,108,109,110,111,172,474,475,476,477,478,479,480,481,482,483,484,529,757,758,759,763,834,846,847,849,144,145,177,446,447,448,125,126,127,128,129,175,445,716,812,824,825,100000015,100000016,101300030,101300031,101300032,101300033,153,154,155,156,179,461,462,463,464,465,466,467,468,469,470,471,472,473,512,513,147,148,149,150,151,178,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426"
                        }
                    }
                }
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(example_config, f, ensure_ascii=False, indent=2)
                
                logger.warning(f"已创建示例配置文件: {config_path}")
                logger.warning("请编辑此文件，填入实际的认证信息")
            
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"✅ 配置文件加载成功: {config_path}")
            return config
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            return None
    
    def _setup_session(self):
        """设置会话（基于夸克项目规范）"""
        # 设置请求头
        if self.headers:
            self.session.headers.update(self.headers)
        
        # 设置Cookie
        if self.cookies:
            for name, value in self.cookies.items():
                self.session.cookies.set(name, value)
        
        logger.info(f"📋 设置请求头: {len(self.headers)}个")
        logger.info(f"🍪 设置Cookie: {len(self.cookies)}个")
    
    def validate_auth(self) -> bool:
        """验证认证信息是否有效（基于夸克项目规范）"""
        logger.info("🔍 验证API认证信息...")
        
        # 检查必要的认证信息
        if not self.api_url:
            logger.error("❌ API端点为空")
            return False
        
        if not self.cookies:
            logger.error("❌ Cookie为空")
            return False
        
        # 检查关键的Cookie
        required_cookies = ["SESSION", "ctoken"]
        for cookie in required_cookies:
            if cookie not in self.cookies:
                logger.warning(f"⚠️  Cookie中缺少 {cookie}")
        
        # 测试API连接
        test_result = self.fetch_page(page_no=1, page_size=1)
        
        if test_result and self._validate_response(test_result):
            logger.info("✅ API认证验证成功")
            return True
        else:
            logger.error("❌ API认证验证失败")
            return False
    
    def fetch_page(self, page_no: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """获取单页数据（基于夸克项目规范）"""
        # 构建请求体
        request_body = self._build_request_body(page_no, page_size)
        
        logger.info(f"📡 获取第{page_no}页数据 (每页{page_size}条)")
        logger.debug(f"📦 请求体: {json.dumps(request_body, ensure_ascii=False)}")
        
        try:
            response = self.session.post(
                self.api_url,
                json=request_body,
                timeout=30
            )
            
            logger.info(f"📥 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # 验证响应结构
                if self._validate_response(data):
                    logger.info(f"✅ 第{page_no}页数据获取成功")
                    return data
                else:
                    logger.warning(f"⚠️  第{page_no}页响应结构验证失败")
                    return None
            else:
                logger.error(f"❌ 第{page_no}页请求失败，状态码: {response.status_code}")
                logger.error(f"📝 响应文本: {response.text[:200]}...")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ 第{page_no}页请求超时")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ 第{page_no}页连接错误")
            return None
        except json.JSONDecodeError:
            logger.error(f"❌ 第{page_no}页响应不是有效的JSON格式")
            logger.error(f"📝 响应文本: {response.text[:200]}...")
            return None
        except Exception as e:
            logger.error(f"❌ 第{page_no}页请求异常: {e}")
            return None
    
    def _build_request_body(self, page_no: int, page_size: int) -> Dict[str, Any]:
        """构建请求体（基于实际请求体确认）"""
        # 获取筛选参数
        categories_config = self.parameters.get("categories", {})
        
        request_body = {
            "regions": categories_config.get("regions", ""),
            "categories": categories_config.get("main_categories", ""),
            "subCategories": categories_config.get("sub_categories", ""),
            "bgCode": categories_config.get("bg_code", ""),
            "socialQrCode": categories_config.get("social_qrcode", ""),
            "pageIndex": page_no,
            "pageSize": page_size,
            "channel": categories_config.get("channel", "group_official_site"),
            "language": categories_config.get("language", "zh")
        }
        
        logger.debug(f"📦 构建请求体: {json.dumps(request_body, ensure_ascii=False)}")
        return request_body
    
    def _validate_response(self, data: Dict[str, Any]) -> bool:
        """验证响应数据（基于夸克项目规范）"""
        if not isinstance(data, dict):
            logger.error("响应数据不是字典类型")
            return False
        
        # 检查成功状态
        success = data.get(self.response_structure.get("success_field", "success"))
        if success is not True:
            logger.error(f"API返回失败状态: {success}")
            return False
        
        # 检查错误代码
        error_code = data.get(self.response_structure.get("error_code_field", "errorCode"))
        success_value = self.response_structure.get("error_code_success_value", "success")
        if error_code != success_value:
            logger.error(f"API返回错误代码: {error_code}")
            return False
        
        # 检查数据字段
        data_field = self.response_structure.get("data_field", "content")
        content = data.get(data_field)
        if not isinstance(content, list):
            logger.error(f"{data_field}字段不是列表类型: {type(content)}")
            return False
        
        # 检查分页信息
        required_fields = [
            self.response_structure.get("total_field", "totalCount"),
            self.response_structure.get("page_size_field", "pageSize"),
            self.response_structure.get("page_field", "currentPage")
        ]
        
        for field in required_fields:
            if field not in data:
                logger.warning(f"缺少分页字段: {field}")
        
        total_count = data.get(self.response_structure.get("total_field", "totalCount"), 0)
        logger.info(f"📊 验证通过: {len(content)}个岗位，总{total_count}个")
        return True
    
    def save_positions(self, positions: List[Dict[str, Any]], page_no: int):
        """保存岗位数据（基于夸克项目规范）"""
        if not positions:
            logger.warning(f"第{page_no}页无岗位数据可保存")
            return
        
        saved_count = 0
        positions_dir = self.output_dir / "positions"
        
        for position in positions:
            try:
                # 生成文件名（基于夸克项目规范）
                position_id = position.get("id", "unknown")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ant_page{page_no}_position_{position_id}_{timestamp}.json"
                filepath = positions_dir / filename
                
                # 保存单个岗位数据
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(position, f, ensure_ascii=False, indent=2)
                
                saved_count += 1
                self.positions_extracted += 1
                
                logger.debug(f"💾 保存岗位 {position_id} 到 {filename}")
                
            except Exception as e:
                logger.error(f"❌ 保存岗位数据失败: {e}")
        
        logger.info(f"💾 第{page_no}页保存了 {saved_count}/{len(positions)} 个岗位")
    
    def save_page_data(self, data: Dict[str, Any], page_no: int) -> Optional[Path]:
        """保存整页数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ant_page_{page_no}_{timestamp}.json"
        pages_dir = self.output_dir / "pages"
        filepath = pages_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📁 保存第{page_no}页完整数据到: {filename}")
            return filepath
        except Exception as e:
            logger.error(f"❌ 保存第{page_no}页数据失败: {e}")
            return None
    
    def save_checkpoint(self, page_no: int, total_pages: int):
        """保存检查点（基于夸克项目规范）"""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "current_page": page_no,
            "total_pages": total_pages,
            "positions_extracted": self.positions_extracted,
            "output_directory": str(self.output_dir),
            "config_file": self.config_path
        }
        
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📝 保存检查点到: {self.checkpoint_file}")
        except Exception as e:
            logger.error(f"❌ 保存检查点失败: {e}")
    
    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """加载检查点（支持断点续传）"""
        if not self.checkpoint_file.exists():
            logger.info("没有找到检查点文件，从头开始爬取")
            return None
        
        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            
            logger.info(f"📝 加载检查点: 第{checkpoint.get('current_page', 1)}页")
            return checkpoint
        except Exception as e:
            logger.error(f"❌ 加载检查点失败: {e}")
            return None
    
    def calculate_total_pages(self, total_count: int, page_size: int) -> int:
        """计算总页数"""
        if total_count <= 0 or page_size <= 0:
            return 0
        
        total_pages = (total_count + page_size - 1) // page_size
        logger.info(f"📊 总岗位数: {total_count}, 页大小: {page_size}, 总页数: {total_pages}")
        return total_pages
    
    def crawl_all_pages(self, start_page: int = 1, max_pages: int = None) -> bool:
        """爬取所有页面（基于夸克项目规范）"""
        logger.info("="*70)
        logger.info("🚀 开始爬取蚂蚁国际招聘所有岗位")
        logger.info("="*70)
        
        # 检查断点续传
        checkpoint = self.load_checkpoint()
        if checkpoint:
            start_page = checkpoint.get("current_page", 1) + 1
            logger.info(f"🔄 从断点继续: 第{start_page}页开始")
        
        # 先获取第一页，了解总页数
        first_page_data = self.fetch_page(start_page)
        if not first_page_data:
            logger.error("❌ 获取第一页数据失败，无法继续")
            return False
        
        total_count = first_page_data.get(
            self.response_structure.get("total_field", "totalCount"), 0
        )
        page_size = first_page_data.get(
            self.response_structure.get("page_size_field", "pageSize"), 10
        )
        
        if total_count == 0:
            logger.warning("⚠️  总岗位数为0，可能API配置有误")
            return False
        
        # 保存第一页数据
        self.save_page_data(first_page_data, start_page)
        data_field = self.response_structure.get("data_field", "content")
        positions = first_page_data.get(data_field, [])
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
                positions = page_data.get(data_field, [])
                self.save_positions(positions, page_no)
                
                # 保存检查点
                self.save_checkpoint(page_no, total_pages)
            else:
                logger.warning(f"⚠️  第{page_no}页获取失败，跳过")
            
            # 显示进度
            progress = (page_no / total_pages) * 100
            logger.info(f"📈 进度: {page_no}/{total_pages}页 ({progress:.1f}%)")
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """获取爬取器状态（基于夸克项目规范）"""
        return {
            "type": "ant_api_configurable",
            "config_file": self.config_path,
            "api_url": self.api_url,
            "positions_extracted": self.positions_extracted,
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "output_directory": str(self.output_dir),
            "checkpoint_file": str(self.checkpoint_file),
            "start_time": self.start_time.isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds()
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """生成爬取报告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report = {
            "project": "蚂蚁国际招聘数据爬取",
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "stats": {
                "positions_extracted": self.positions_extracted,
                "output_directory": str(self.output_dir),
                "config_file": self.config_path
            }
        }
        
        # 保存报告
        report_file = self.output_dir / "reports" / f"crawl_report_{end_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 爬取报告已保存到: {report_file}")
        
        # 打印摘要
        print("\n" + "="*70)
        print("📊 爬取完成摘要")
        print("="*70)
        print(f"⏱️  耗时: {duration:.1f}秒")
        print(f"💾 保存岗位: {self.positions_extracted}")
        print(f"📁 输出目录: {self.output_dir}")
        print("="*70)
        
        return report


def main():
    """主函数"""
    print("="*70)
    print("🚀 蚂蚁国际招聘API爬取器（可配置版）")
    print("="*70)
    
    try:
        # 初始化爬取器
        crawler = AntApiCrawlerConfigurable()
        
        # 测试连接
        print("\n1. 🔗 测试API连接...")
        if not crawler.validate_auth():
            print("❌ API连接测试失败，请检查配置")
            return 1
        
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