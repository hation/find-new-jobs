#!/usr/bin/env python3
# 🏗️ 夸克爬取器 - 浏览器管理器
# 版本: 1.0
# 创建时间: 2026-05-19
# 基于教训: 使用 profile="openclaw" 最稳定

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# 导入核心接口
from .interfaces import IBrowserManager, BrowserError


class BrowserAction(Enum):
    """浏览器操作类型"""
    NAVIGATE = "navigate"
    CLICK = "click"
    EXECUTE_SCRIPT = "execute_script"
    SNAPSHOT = "snapshot"
    SWITCH_TAB = "switch_tab"
    CLOSE_TAB = "close_tab"


@dataclass
class BrowserTab:
    """浏览器标签页信息"""
    tab_id: str
    url: str
    title: str
    created_at: float
    last_accessed: float
    is_active: bool = False
    
    def update_access(self) -> None:
        """更新访问时间"""
        self.last_accessed = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "tab_id": self.tab_id,
            "url": self.url,
            "title": self.title,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "is_active": self.is_active,
            "age_seconds": time.time() - self.created_at
        }


class OpenClawBrowserManager(IBrowserManager):
    """OpenClaw浏览器管理器 - 通过工具调用控制浏览器"""
    
    def __init__(self, profile: str = "openclaw", max_tabs: int = 10):
        """
        初始化浏览器管理器
        
        Args:
            profile: 浏览器配置，默认为 "openclaw"
            max_tabs: 最大标签页数量
        """
        self.profile = profile
        self.max_tabs = max_tabs
        self._initialized = False
        self._current_tab_id: Optional[str] = None
        self._tabs: Dict[str, BrowserTab] = {}
        self._action_history: List[Dict[str, Any]] = []
        
        # 浏览器配置
        self.default_timeout_ms = 30000
        self.retry_count = 3
        self.retry_delay_ms = 1000
        
        print(f"🌐 浏览器管理器初始化 (profile: {profile})")
    
    def initialize(self, profile: str = "openclaw") -> bool:
        """初始化浏览器"""
        if self._initialized:
            print("⚠️  浏览器已经初始化")
            return True
        
        self.profile = profile
        
        try:
            # 检查浏览器服务状态
            from openclaw_tools import browser
            
            # 尝试获取浏览器状态
            status_result = browser(action="status")
            
            if status_result.get("status") != "running":
                print("⚠️  浏览器服务未运行，尝试启动...")
                start_result = browser(action="start", profile=self.profile)
                
                if not start_result.get("success", False):
                    raise BrowserError(f"启动浏览器失败: {start_result}")
                
                print("✅ 浏览器服务启动成功")
            
            # 获取标签页列表
            tabs_result = browser(action="tabs", profile=self.profile)
            tabs = tabs_result.get("tabs", [])
            
            # 初始化标签页跟踪
            for tab in tabs:
                tab_id = tab.get("id")
                if tab_id:
                    self._tabs[tab_id] = BrowserTab(
                        tab_id=tab_id,
                        url=tab.get("url", ""),
                        title=tab.get("title", ""),
                        created_at=time.time(),
                        last_accessed=time.time(),
                        is_active=tab.get("active", False)
                    )
                    
                    if tab.get("active", False):
                        self._current_tab_id = tab_id
            
            self._initialized = True
            print(f"✅ 浏览器管理器初始化完成，发现 {len(self._tabs)} 个标签页")
            
            # 记录初始化操作
            self._record_action(BrowserAction.NAVIGATE, "initialize", True)
            return True
            
        except ImportError:
            print("⚠️  无法导入 browser 工具，将在实际调用时处理")
            self._initialized = True
            return True
        except Exception as e:
            print(f"❌ 浏览器初始化失败: {e}")
            return False
    
    def _call_browser_tool(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        调用浏览器工具
        
        Args:
            action: 浏览器操作
            **kwargs: 工具参数
            
        Returns:
            Dict[str, Any]: 工具调用结果
        """
        try:
            # 动态导入 browser 工具
            from openclaw_tools import browser
            
            # 添加默认参数
            if "profile" not in kwargs:
                kwargs["profile"] = self.profile
            
            if "timeoutMs" not in kwargs and "timeout_ms" not in kwargs:
                kwargs["timeoutMs"] = self.default_timeout_ms
            
            # 调用工具
            result = browser(action=action, **kwargs)
            
            # 记录操作历史
            self._record_action(
                BrowserAction(action),
                f"{action}: {kwargs.get('url', kwargs.get('targetId', 'unknown'))}",
                result.get("success", False)
            )
            
            return result
            
        except ImportError as e:
            raise BrowserError(f"无法导入 browser 工具: {e}")
        except Exception as e:
            raise BrowserError(f"浏览器工具调用失败: {e}")
    
    def _record_action(self, action_type: BrowserAction, description: str, success: bool) -> None:
        """记录浏览器操作历史"""
        action_record = {
            "timestamp": time.time(),
            "action": action_type.value,
            "description": description,
            "success": success,
            "tab_count": len(self._tabs),
            "current_tab": self._current_tab_id
        }
        self._action_history.append(action_record)
        
        # 保持历史记录大小
        if len(self._action_history) > 100:
            self._action_history = self._action_history[-100:]
    
    def navigate(self, url: str, timeout_ms: int = 30000) -> bool:
        """导航到URL"""
        for attempt in range(self.retry_count):
            try:
                result = self._call_browser_tool(
                    action="navigate",
                    url=url,
                    timeoutMs=timeout_ms
                )
                
                if result.get("success", False):
                    # 更新当前标签页信息
                    if self._current_tab_id and self._current_tab_id in self._tabs:
                        self._tabs[self._current_tab_id].url = url
                        self._tabs[self._current_tab_id].update_access()
                    
                    print(f"✅ 导航到: {url}")
                    return True
                else:
                    print(f"⚠️  导航失败 (尝试 {attempt + 1}/{self.retry_count}): {result.get('error', '未知错误')}")
                    
                    if attempt < self.retry_count - 1:
                        time.sleep(self.retry_delay_ms / 1000)
                        continue
                    
                    return False
                    
            except Exception as e:
                print(f"❌ 导航异常 (尝试 {attempt + 1}/{self.retry_count}): {e}")
                
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay_ms / 1000)
                    continue
                
                raise BrowserError(f"导航失败: {e}")
        
        return False
    
    def execute_script(self, javascript: str) -> Any:
        """执行JavaScript"""
        try:
            result = self._call_browser_tool(
                action="act",
                kind="evaluate",
                fn=javascript
            )
            
            if result.get("success", False):
                return result.get("result")
            else:
                raise BrowserError(f"执行脚本失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            raise BrowserError(f"执行脚本异常: {e}")
    
    def take_snapshot(self, refs: str = "aria") -> Dict[str, Any]:
        """获取页面快照"""
        try:
            result = self._call_browser_tool(
                action="snapshot",
                refs=refs,
                interactive=True
            )
            
            if result.get("success", False):
                return result
            else:
                raise BrowserError(f"获取快照失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            raise BrowserError(f"获取快照异常: {e}")
    
    def click_element(self, ref: str, timeout_ms: int = 10000) -> bool:
        """点击元素"""
        try:
            result = self._call_browser_tool(
                action="act",
                kind="click",
                ref=ref,
                timeoutMs=timeout_ms
            )
            
            if result.get("success", False):
                print(f"✅ 点击元素: {ref}")
                return True
            else:
                raise BrowserError(f"点击元素失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            raise BrowserError(f"点击元素异常: {e}")
    
    def switch_to_tab(self, tab_id: str) -> bool:
        """切换到指定标签页"""
        try:
            result = self._call_browser_tool(
                action="focus",
                targetId=tab_id
            )
            
            if result.get("success", False):
                # 更新标签页状态
                for tab in self._tabs.values():
                    tab.is_active = (tab.tab_id == tab_id)
                
                self._current_tab_id = tab_id
                print(f"✅ 切换到标签页: {tab_id}")
                return True
            else:
                raise BrowserError(f"切换标签页失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            raise BrowserError(f"切换标签页异常: {e}")
    
    def close_tab(self, tab_id: str) -> bool:
        """关闭标签页"""
        try:
            result = self._call_browser_tool(
                action="close",
                targetId=tab_id
            )
            
            if result.get("success", False):
                # 从跟踪中移除标签页
                if tab_id in self._tabs:
                    del self._tabs[tab_id]
                
                # 如果关闭的是当前标签页，选择另一个标签页
                if self._current_tab_id == tab_id:
                    self._