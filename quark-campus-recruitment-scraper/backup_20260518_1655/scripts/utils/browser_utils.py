#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器工具模块
封装OpenClaw browser工具调用，实现防反爬策略
"""

import time
import random
import logging
from typing import Optional, Dict, Any, List
import json

logger = logging.getLogger(__name__)


class BrowserUtils:
    """浏览器工具类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化浏览器工具
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.browser_config = config.get('browser', {})
        self.anti_scraping = config.get('anti_scraping', {})
        
    def random_delay(self, min_delay: Optional[float] = None, 
                     max_delay: Optional[float] = None) -> None:
        """
        随机延迟，模拟人类行为
        
        Args:
            min_delay: 最小延迟（秒）
            max_delay: 最大延迟（秒）
        """
        if min_delay is None:
            min_delay = self.anti_scraping.get('delay_min', 1.0)
        if max_delay is None:
            max_delay = self.anti_scraping.get('delay_max', 3.0)
        
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"随机延迟: {delay:.2f}秒")
        time.sleep(delay)
    
    def get_random_user_agent(self) -> str:
        """
        获取随机User-Agent
        
        Returns:
            随机User-Agent字符串
        """
        user_agents = self.browser_config.get('user_agents', [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ])
        return random.choice(user_agents)
    
    def open_browser(self, url: str) -> Dict[str, Any]:
        """
        打开浏览器并访问URL
        
        Args:
            url: 要访问的URL
            
        Returns:
            浏览器响应结果
        """
        logger.info(f"打开浏览器访问: {url}")
        
        # 添加随机延迟
        self.random_delay()
        
        # 这里需要调用OpenClaw的browser工具
        # 由于我们无法直接调用工具，这里返回一个模拟响应
        # 实际使用时需要替换为OpenClaw browser工具调用
        
        return {
            "status": "success",
            "url": url,
            "message": "浏览器已打开"
        }
    
    def take_snapshot(self, target_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取页面快照
        
        Args:
            target_id: 目标元素ID
            
        Returns:
            页面快照结果
        """
        logger.debug("获取页面快照")
        
        # 这里需要调用OpenClaw的browser snapshot工具
        # 实际使用时需要替换为OpenClaw browser工具调用
        
        return {
            "status": "success",
            "message": "快照已获取"
        }
    
    def find_element(self, selector: str, target_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查找页面元素
        
        Args:
            selector: CSS选择器
            target_id: 目标元素ID
            
        Returns:
            元素信息
        """
        logger.debug(f"查找元素: {selector}")
        
        # 这里需要调用OpenClaw的browser工具进行元素查找
        # 实际使用时需要替换为OpenClaw browser工具调用
        
        return {
            "status": "success",
            "selector": selector,
            "found": True,
            "message": "元素已找到"
        }
    
    def click_element(self, ref: str, target_id: Optional[str] = None) -> Dict[str, Any]:
        """
        点击元素
        
        Args:
            ref: 元素引用
            target_id: 目标元素ID
            
        Returns:
            点击结果
        """
        logger.debug(f"点击元素: {ref}")
        
        # 添加点击前的随机延迟
        self.random_delay(0.2, 0.5)
        
        # 这里需要调用OpenClaw的browser工具进行点击
        # 实际使用时需要替换为OpenClaw browser工具调用
        
        return {
            "status": "success",
            "ref": ref,
            "message": "元素已点击"
        }
    
    def get_text_content(self, selector: str, target_id: Optional[str] = None) -> str:
        """
        获取元素的文本内容
        
        Args:
            selector: CSS选择器
            target_id: 目标元素ID
            
        Returns:
            文本内容
        """
        logger.debug(f"获取文本内容: {selector}")
        
        # 这里需要调用OpenClaw的browser工具获取文本
        # 实际使用时需要替换为OpenClaw browser工具调用
        
        # 模拟返回
        return "模拟文本内容"
    
    def scroll_to_bottom(self, target_id: Optional[str] = None) -> Dict[str, Any]:
        """
        滚动到页面底部
        
        Args:
            target_id: 目标元素ID
            
        Returns:
            滚动结果
        """
        logger.debug("滚动到页面底部")
        
        # 这里需要调用OpenClaw的browser工具进行滚动
        # 实际使用时需要替换为OpenClaw browser工具调用
        
        return {
            "status": "success",
            "message": "已滚动到底部"
        }
    
    def simulate_human_behavior(self) -> None:
        """
        模拟人类行为：随机移动和滚动
        """
        if self.anti_scraping.get('random_mouse_moves', True):
            logger.debug("模拟鼠标移动")
            # 这里可以添加模拟鼠标移动的逻辑
        
        if self.anti_scraping.get('random_scrolls', True):
            logger.debug("模拟页面滚动")
            # 这里可以添加模拟滚动的逻辑
    
    def close_browser(self) -> Dict[str, Any]:
        """
        关闭浏览器
        
        Returns:
            关闭结果
        """
        logger.info("关闭浏览器")
        
        # 这里需要调用OpenClaw的browser工具关闭浏览器
        # 实际使用时需要替换为OpenClaw browser工具调用
        
        return {
            "status": "success",
            "message": "浏览器已关闭"
        }
    
    def handle_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """
        处理浏览器操作错误
        
        Args:
            error: 异常对象
            operation: 操作名称
            
        Returns:
            错误处理结果
        """
        logger.error(f"浏览器操作失败 - {operation}: {str(error)}")
        
        return {
            "status": "error",
            "operation": operation,
            "error": str(error),
            "message": f"{operation}失败: {str(error)}"
        }


class RetryHandler:
    """重试处理器"""
    
    def __init__(self, max_retries: int = 3):
        """
        初始化重试处理器
        
        Args:
            max_retries: 最大重试次数
        """
        self.max_retries = max_retries
        
    def execute_with_retry(self, func, *args, **kwargs) -> Any:
        """
        带重试的执行函数
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            Exception: 重试次数用尽后抛出异常
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    logger.info(f"重试第{attempt}次...")
                    # 重试前等待时间指数递增
                    wait_time = min(2 ** attempt, 30)  # 最大30秒
                    time.sleep(wait_time)
                
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                logger.warning(f"第{attempt + 1}次尝试失败: {str(e)}")
                
                # 如果是网络错误，继续重试
                if "network" in str(e).lower() or "timeout" in str(e).lower():
                    continue
                # 其他错误直接抛出
                else:
                    break
        
        raise last_exception or Exception("重试次数用尽")