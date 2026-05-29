#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能爬取器选择器框架模板
- 失败后告知原因
- 询问是否切换到备选方案
- 支持用户决策和重试

通用组件，可用于任何公司招聘爬取
"""

import logging
import time
import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class SmartCrawlerSelector:
    """智能爬取器选择器框架（通用模板）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化智能选择器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 爬取器实例（由具体业务实现）
        self.primary_crawler = None  # 主爬取器（如API）
        self.fallback_crawler = None  # 备选爬取器（如浏览器）
        
        # 状态跟踪
        self.current_mode = "unknown"
        self.data_extracted = 0
        self.start_time = None
        self.last_error = None
        self.last_error_details = None
        
        # 输出配置
        self.output_dir = self.config.get("output_dir", "output/crawl_data")
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("✅ 智能爬取器选择器初始化完成")
    
    # ==================== 需要业务定制的部分 ====================
    
    def _initialize_primary_crawler(self) -> Tuple[bool, Optional[str]]:
        """
        初始化主爬取器（如API爬取器）
        
        Returns:
            (成功与否, 错误信息/None)
        
        Note: 需要由具体业务实现
        """
        # TODO: 实现具体的主爬取器初始化
        # 例如：from api_crawler import ApiCrawler
        #       self.primary_crawler = ApiCrawler()
        return False, "未实现: 请定制主爬取器初始化逻辑"
    
    def _initialize_fallback_crawler(self) -> Tuple[bool, Optional[str]]:
        """
        初始化备选爬取器（如浏览器爬取器）
        
        Returns:
            (成功与否, 错误信息/None)
        
        Note: 需要由具体业务实现
        """
        # TODO: 实现具体的备选爬取器初始化
        # 例如：from browser_crawler import BrowserCrawler
        #       self.fallback_crawler = BrowserCrawler()
        return False, "未实现: 请备案选爬取器初始化逻辑"
    
    def test_primary_connection(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        测试主爬取器连接（如API连接测试）
        
        Returns:
            (是否成功, 诊断信息, 详细错误/None)
        
        Note: 需要由具体业务实现
        """
        # TODO: 实现具体的连接测试逻辑
        # 例如：测试API端点、认证信息、数据获取
        return False, "未实现: 请定制主爬取器连接测试", {"step": "not_implemented"}
    
    def get_failure_reason(self, error_details: Dict[str, Any]) -> str:
        """
        根据错误详情生成友好的失败原因
        
        Args:
            error_details: 错误详情
            
        Returns:
            友好的失败原因描述
        
        Note: 可以由业务定制，也可以使用默认实现
        """
        step = error_details.get("step", "unknown")
        
        # 默认的错误原因映射
        reasons = {
            "initialize": "爬取器初始化失败",
            "auth_validation": "认证信息无效",
            "connection_test": "连接测试失败",
            "data_fetch": "数据获取失败",
            "data_analysis": "数据解析异常",
            "exception": "测试过程中出现异常",
            "not_implemented": "功能未实现"
        }
        
        base_reason = reasons.get(step, "连接失败")
        
        # 添加具体信息
        if "error" in error_details:
            base_reason += f" ({error_details['error']})"
        elif "status" in error_details:
            base_reason += f" (状态: {error_details['status']})"
        
        return base_reason
    
    # ==================== 通用框架部分（无需修改） ====================
    
    def ask_user_for_switch(self, primary_reason: str) -> bool:
        """
        询问用户是否切换到备选方案
        
        Args:
            primary_reason: 主方案失败原因
            
        Returns:
            True: 用户同意切换
            False: 用户不同意切换
            "retry": 用户选择重试
        """
        print("\n" + "=" * 60)
        print("⚠️  主方案失败")
        print("=" * 60)
        print(f"❌ 失败原因: {primary_reason}")
        print()
        print("📋 详细诊断:")
        print(f"   • 主爬取器: {'已初始化' if self.primary_crawler else '未初始化'}")
        print(f"   • 备选爬取器: {'已初始化' if self.fallback_crawler else '未初始化'}")
        print(f"   • 当前模式: {self.current_mode}")
        print(f"   • 输出目录: {self.output_dir}")
        print()
        print("💡 建议解决方案:")
        print("   1. 检查网络连接")
        print("   2. 验证认证信息是否有效")
        print("   3. 检查配置文件")
        print("   4. 切换到备选方案（需要用户操作）")
        print()
        print("🔄 是否切换到备选方案继续爬取？")
        print("   - 输入 'y' 或 'yes' 切换到备选方案")
        print("   - 输入 'n' 或 'no' 放弃爬取")
        print("   - 输入 'r' 或 'retry' 重试主方案")
        print()
        
        # 读取用户输入
        while True:
            try:
                user_input = input("请选择 (y/n/r): ").strip().lower()
                
                if user_input in ['y', 'yes']:
                    print("✅ 用户选择切换到备选方案")
                    return True
                elif user_input in ['n', 'no']:
                    print("❌ 用户选择放弃爬取")
                    return False
                elif user_input in ['r', 'retry']:
                    print("🔄 用户选择重试主方案")
                    return "retry"
                else:
                    print("❓ 请输入 y/n/r")
            except KeyboardInterrupt:
                print("\n❌ 用户取消操作")
                return False
            except Exception as e:
                print(f"❌ 输入错误: {e}")
                return False
    
    def crawl_with_primary(self) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        使用主方案爬取
        
        Returns:
            (是否成功, 结果数据, 失败原因/None)
        """
        logger.info("🚀 开始主方案爬取")
        self.current_mode = "primary"
        
        try:
            # 1. 测试连接
            success, message, error_details = self.test_primary_connection()
            
            if not success:
                reason = self.get_failure_reason(error_details or {})
                logger.error(f"❌ 主方案连接失败: {reason}")
                return False, None, reason
            
            logger.info(f"✅ {message}")
            
            # 2. 检查是否有具体的爬取逻辑
            if not self.primary_crawler:
                reason = "主爬取器未初始化"
                logger.error(f"❌ {reason}")
                return False, None, reason
            
            # 3. 这里应该调用具体的主爬取器逻辑
            # 例如: result = self.primary_crawler.crawl_all()
            # 由于是模板，这里返回模拟结果
            
            result = {
                "success": True,
                "data_extracted": 100,  # 模拟数据
                "completion_percentage": 100.0,
                "output_directory": self.output_dir
            }
            
            self.data_extracted = result.get("data_extracted", 0)
            logger.info(f"✅ 主方案爬取成功: {self.data_extracted}条数据")
            return True, result, None
            
        except Exception as e:
            reason = f"主方案爬取异常: {e}"
            logger.error(f"❌ {reason}")
            return False, None, reason
    
    def crawl_with_fallback(self) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        使用备选方案爬取
        
        Returns:
            (是否成功, 结果数据, 失败原因/None)
        """
        logger.info("🚀 开始备选方案爬取")
        self.current_mode = "fallback"
        
        # 初始化备选爬取器
        init_success, error = self._initialize_fallback_crawler()
        if not init_success:
            reason = f"备选爬取器初始化失败: {error}"
            logger.error(f"❌ {reason}")
            return False, None, reason
        
        try:
            # 这里应该调用具体的备选爬取器逻辑
            # 例如: result = self.fallback_crawler.scrape_data()
            # 由于是模板，这里返回模拟结果
            
            result = {
                "success": True,
                "data_extracted": 80,  # 模拟数据
                "completion_percentage": 80.0,
                "message": "备选方案需要手动执行",
                "requires_user_action": True
            }
            
            return True, result, None
            
        except Exception as e:
            reason = f"备选方案爬取异常: {e}"
            logger.error(f"❌ {reason}")
            return False, None, reason
    
    def smart_crawl_with_user_interaction(self) -> Dict[str, Any]:
        """
        智能爬取（带用户交互）
        
        Returns:
            爬取结果
        """
        self.start_time = time.time()
        
        print("\n" + "=" * 60)
        print("🧠 智能爬取系统（带用户交互）")
        print("=" * 60)
        print("📊 模式: 主方案优先，失败后询问用户")
        print()
        
        # 1. 优先尝试主方案
        print("1️⃣ 尝试主方案...")
        primary_success, primary_result, primary_reason = self.crawl_with_primary()
        
        if primary_success:
            print("✅ 主方案成功!")
            elapsed_time = time.time() - self.start_time
            
            return {
                "success": True,
                "mode": "primary",
                "data_extracted": primary_result.get("data_extracted", 0),
                "completion_percentage": primary_result.get("completion_percentage", 0),
                "elapsed_time_seconds": elapsed_time,
                "output_directory": primary_result.get("output_directory", ""),
                "data_quality": "verified",
                "user_interaction": "none"
            }
        
        # 2. 主方案失败，询问用户
        print(f"\n2️⃣ 主方案失败: {primary_reason}")
        
        user_choice = self.ask_user_for_switch(primary_reason)
        
        if user_choice == "retry":
            # 用户选择重试主方案
            print("\n🔄 重试主方案...")
            primary_success, primary_result, primary_reason = self.crawl_with_primary()
            
            if primary_success:
                elapsed_time = time.time() - self.start_time
                return {
                    "success": True,
                    "mode": "primary_retry",
                    "data_extracted": primary_result.get("data_extracted", 0),
                    "completion_percentage": primary_result.get("completion_percentage", 0),
                    "elapsed_time_seconds": elapsed_time,
                    "output_directory": primary_result.get("output_directory", ""),
                    "data_quality": "verified",
                    "user_interaction": "retry_primary"
                }
        
        if user_choice is True:
            # 3. 用户同意切换到备选方案
            print("\n3️⃣ 切换到备选方案...")
            fallback_success, fallback_result, fallback_reason = self.crawl_with_fallback()
            
            elapsed_time = time.time() - self.start_time
            
            if fallback_success:
                return {
                    "success": True,
                    "mode": "fallback",
                    "data_extracted": fallback_result.get("data_extracted", 0),
                    "completion_percentage": fallback_result.get("completion_percentage", 0),
                    "elapsed_time_seconds": elapsed_time,
                    "user_interaction": "switch_to_fallback",
                    "note": fallback_result.get("message", "")
                }
            else:
                return {
                    "success": False,
                    "mode": "fallback",
                    "error": fallback_reason or "备选方案失败",
                    "elapsed_time_seconds": elapsed_time,
                    "user_interaction": "switch_to_fallback_failed"
                }
        else:
            # 4. 用户不同意切换或放弃
            elapsed_time = time.time() - self.start_time
            
            return {
                "success": False,
                "mode": "primary",
                "error": primary_reason or "主方案失败",
                "elapsed_time_seconds": elapsed_time,
                "user_interaction": "user_rejected_switch"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取当前状态
        
        Returns:
            状态字典
        """
        return {
            "current_mode": self.current_mode,
            "data_extracted": self.data_extracted,
            "primary_crawler_initialized": self.primary_crawler is not None,
            "fallback_crawler_initialized": self.fallback_crawler is not None,
            "output_dir": self.output_dir,
            "last_error": self.last_error,
            "config_keys": list(self.config.keys()) if self.config else []
        }


# ==================== 模板使用示例 ====================

class ExampleSmartCrawler(SmartCrawlerSelector):
    """
    智能爬取器使用示例
    演示如何定制通用框架
    """
    
    def _initialize_primary_crawler(self) -> Tuple[bool, Optional[str]]:
        """示例：实现API爬取器初始化"""
        try:
            # 示例代码，实际使用时需要导入具体实现
            # from company_api_crawler import CompanyApiCrawler
            # self.primary_crawler = CompanyApiCrawler(self.config)
            
            # 这里只是示例，实际应该返回成功
            self.primary_crawler = {"name": "API爬取器示例"}
            return True, None
        except Exception as e:
            return False, f"API爬取器初始化失败: {e}"
    
    def _initialize_fallback_crawler(self) -> Tuple[bool, Optional[str]]:
        """示例：实现浏览器爬取器初始化"""
        try:
            # 示例代码，实际使用时需要导入具体实现
            # from company_browser_crawler import CompanyBrowserCrawler
            # self.fallback_crawler = CompanyBrowserCrawler(self.config)
            
            # 这里只是示例，实际应该返回成功
            self.fallback_crawler = {"name": "浏览器爬取器示例"}
            return True, None
        except Exception as e:
            return False, f"浏览器爬取器初始化失败: {e}"
    
    def test_primary_connection(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """示例：实现API连接测试"""
        try:
            # 这里应该实现实际的连接测试逻辑
            # 例如：测试API端点、验证认证信息、获取数据
            
            # 模拟测试逻辑
            time.sleep(0.5)  # 模拟网络延迟
            
            # 模拟成功或失败
            test_success = True  # 可以改为False测试失败情况
            
            if test_success:
                return True, "API连接测试成功", {"status_code": 200, "response_time": 0.5}
            else:
                return False, "API连接测试失败", {
                    "step": "connection_test",
                    "status": 403,
                    "error": "认证失败"
                }
        except Exception as e:
            return False, f"连接测试异常: {e}", {"step": "exception", "error": str(e)}
    
    def get_failure_reason(self, error_details: Dict[str, Any]) -> str:
        """示例：扩展错误原因映射"""
        # 可以先调用父类的默认实现
        base_reason = super().get_failure_reason(error_details)
        
        # 根据具体业务定制错误原因
        if error_details.get("status") == 403:
            return f"认证被拒绝: {base_reason}"
        elif error_details.get("status") == 404:
            return f"API端点不存在: {base_reason}"
        elif "timeout" in str(error_details.get("error", "")).lower():
            return f"请求超时: {base_reason}"
        
        return base_reason


def demo_usage():
    """演示如何使用智能爬取器模板"""
    print("🚀 智能爬取器模板演示")
    print("=" * 50)
    
    # 1. 创建配置
    config = {
        "output_dir": "output/demo_crawl",
        "api_endpoint": "https://example.com/api",
        "authentication": {"api_key": "demo_key"}
    }
    
    # 2. 创建智能爬取器实例
    crawler = ExampleSmartCrawler(config)
    
    # 3. 查看状态
    status = crawler.get_status()
    print(f"📊 初始状态:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # 4. 进行智能爬取
    print(f"\n🧠 开始智能爬取...")
    result = crawler.smart_crawl_with_user_interaction()
    
    # 5. 显示结果
    print(f"\n📋 爬取结果:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    return result


if __name__ == "__main__":
    """
    运行演示:
    1. 尝试主方案（API）
    2. 如果失败，询问用户是否切换到备选方案
    3. 根据用户选择执行相应操作
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    demo_result = demo_usage()
    
    if demo_result.get("success"):
        print(f"\n🎉 演示完成！模式: {demo_result.get('mode')}")
    else:
        print(f"\n❌ 演示失败！原因: {demo_result.get('error')}")
