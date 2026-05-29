#!/usr/bin/env python3
# 🏗️ 夸克爬取器 - 插件管理器
# 版本: 1.0
# 创建时间: 2026-05-19
# 基于记忆系统原则: 插件化架构，防止脚本膨胀

import os
import sys
import importlib
import inspect
from typing import Dict, List, Optional, Type, Any
from dataclasses import dataclass
from enum import Enum

# 导入核心接口
from .interfaces import (
    IExtractionStrategy, IPluginRegistry, StrategyType,
    StrategyError, PluginError
)


@dataclass
class PluginInfo:
    """插件信息"""
    name: str
    strategy_type: StrategyType
    plugin_class: Type[IExtractionStrategy]
    version: str
    description: str
    author: str
    enabled: bool = True
    initialized: bool = False
    instance: Optional[IExtractionStrategy] = None


class PluginManager(IPluginRegistry):
    """插件管理器 - 负责插件的注册、加载和管理"""
    
    def __init__(self, plugins_dir: str = None):
        """
        初始化插件管理器
        
        Args:
            plugins_dir: 插件目录路径，默认为当前目录下的plugins/
        """
        self.plugins_dir = plugins_dir or os.path.join(os.path.dirname(__file__), "..", "plugins")
        self._strategies: Dict[StrategyType, PluginInfo] = {}
        self._initialized = False
        
        # 确保插件目录存在
        os.makedirs(self.plugins_dir, exist_ok=True)
        
        # 插件状态跟踪
        self.load_errors: List[str] = []
        self.validation_errors: List[str] = []
        
        print(f"🧩 插件管理器初始化完成")
        print(f"📁 插件目录: {self.plugins_dir}")
    
    def initialize(self) -> bool:
        """初始化插件管理器"""
        if self._initialized:
            return True
        
        try:
            # 1. 扫描插件目录
            self._scan_plugin_directory()
            
            # 2. 加载发现的所有插件
            self._load_discovered_plugins()
            
            # 3. 验证插件完整性
            validation_result = self.validate_plugins()
            
            if validation_result["errors"]:
                print(f"⚠️  插件验证发现错误: {validation_result['errors']}")
                self.validation_errors = validation_result["errors"]
            else:
                print(f"✅ 所有插件验证通过")
            
            self._initialized = True
            print(f"🧩 插件管理器初始化完成，加载了 {len(self._strategies)} 个插件")
            return True
            
        except Exception as e:
            print(f"❌ 插件管理器初始化失败: {e}")
            self.load_errors.append(f"初始化失败: {e}")
            return False
    
    def _scan_plugin_directory(self) -> List[str]:
        """扫描插件目录，发现可用插件"""
        discovered_plugins = []
        
        if not os.path.exists(self.plugins_dir):
            print(f"⚠️  插件目录不存在: {self.plugins_dir}")
            return discovered_plugins
        
        # 遍历插件子目录
        for item in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, item)
            
            # 只处理目录
            if not os.path.isdir(plugin_path):
                continue
            
            # 检查是否有 __init__.py 文件
            init_file = os.path.join(plugin_path, "__init__.py")
            if not os.path.exists(init_file):
                print(f"⚠️  插件目录缺少 __init__.py: {item}")
                continue
            
            discovered_plugins.append(item)
            print(f"🔍 发现插件: {item}")
        
        return discovered_plugins
    
    def _load_discovered_plugins(self) -> None:
        """加载发现的插件"""
        plugin_dirs = self._scan_plugin_directory()
        
        for plugin_dir in plugin_dirs:
            try:
                self._load_single_plugin(plugin_dir)
            except Exception as e:
                error_msg = f"加载插件 {plugin_dir} 失败: {e}"
                print(f"❌ {error_msg}")
                self.load_errors.append(error_msg)
    
    def _load_single_plugin(self, plugin_dir: str) -> bool:
        """加载单个插件"""
        plugin_full_path = os.path.join(self.plugins_dir, plugin_dir)
        
        # 动态导入插件模块
        module_name = f"quark_crawler.plugins.{plugin_dir}"
        
        try:
            # 将插件目录添加到Python路径
            if plugin_full_path not in sys.path:
                sys.path.insert(0, plugin_full_path)
            
            # 导入插件模块
            plugin_module = importlib.import_module(f"quark_crawler.plugins.{plugin_dir}")
            
            # 查找插件注册函数
            if not hasattr(plugin_module, "register_plugin"):
                raise PluginError(f"插件 {plugin_dir} 缺少 register_plugin 函数")
            
            # 调用注册函数
            register_func = plugin_module.register_plugin
            plugin_info = register_func(self)
            
            if not plugin_info:
                raise PluginError(f"插件 {plugin_dir} 注册失败")
            
            print(f"✅ 加载插件: {plugin_dir}")
            return True
            
        except ImportError as e:
            raise PluginError(f"导入插件模块失败: {e}")
        except Exception as e:
            raise PluginError(f"加载插件失败: {e}")
    
    def register_strategy(self, strategy: IExtractionStrategy) -> bool:
        """
        注册策略插件
        
        Args:
            strategy: 策略插件实例
            
        Returns:
            bool: 注册是否成功
        """
        try:
            # 验证策略类型
            strategy_type = strategy.get_strategy_type()
            strategy_name = strategy.get_strategy_name()
            
            if strategy_type in self._strategies:
                print(f"⚠️  策略 {strategy_type} 已存在，将被替换")
            
            # 创建插件信息
            plugin_info = PluginInfo(
                name=strategy_name,
                strategy_type=strategy_type,
                plugin_class=type(strategy),
                version="1.0",  # 可以从策略中获取
                description=f"{strategy_name} 提取策略",
                author="System",
                enabled=True,
                initialized=False,
                instance=strategy
            )
            
            # 存储策略
            self._strategies[strategy_type] = plugin_info
            
            print(f"✅ 注册策略: {strategy_name} ({strategy_type})")
            return True
            
        except Exception as e:
            print(f"❌ 注册策略失败: {e}")
            return False
    
    def get_strategy(self, strategy_type: StrategyType) -> Optional[IExtractionStrategy]:
        """
        获取策略插件
        
        Args:
            strategy_type: 策略类型
            
        Returns:
            Optional[IExtractionStrategy]: 策略实例，如果不存在则返回None
        """
        if strategy_type not in self._strategies:
            print(f"⚠️  策略 {strategy_type} 未注册")
            return None
        
        plugin_info = self._strategies[strategy_type]
        
        # 如果还没有实例，创建新实例
        if plugin_info.instance is None:
            try:
                plugin_info.instance = plugin_info.plugin_class()
                plugin_info.initialized = True
            except Exception as e:
                print(f"❌ 创建策略实例失败: {e}")
                return None
        
        return plugin_info.instance
    
    def list_strategies(self) -> List[Dict[str, Any]]:
        """列出所有可用策略"""
        strategies_info = []
        
        for strategy_type, plugin_info in self._strategies.items():
            strategies_info.append({
                "name": plugin_info.name,
                "type": strategy_type.value,
                "version": plugin_info.version,
                "description": plugin_info.description,
                "enabled": plugin_info.enabled,
                "initialized": plugin_info.initialized,
                "author": plugin_info.author
            })
        
        return strategies_info
    
    def validate_plugins(self) -> Dict[str, List[str]]:
        """验证所有插件"""
        errors = []
        warnings = []
        
        # 检查是否有插件
        if not self._strategies:
            warnings.append("没有注册任何插件")
        
        # 验证每个插件
        for strategy_type, plugin_info in self._strategies.items():
            # 检查插件实例
            if plugin_info.instance is None:
                errors.append(f"插件 {plugin_info.name} 没有实例")
                continue
            
            # 验证插件方法
            try:
                # 检查必需方法
                required_methods = [
                    "get_strategy_type",
                    "get_strategy_name", 
                    "initialize",
                    "validate_environment",
                    "extract_list_page",
                    "extract_position_detail",
                    "save_position_data"
                ]
                
                for method_name in required_methods:
                    if not hasattr(plugin_info.instance, method_name):
                        errors.append(f"插件 {plugin_info.name} 缺少方法 {method_name}")
                    
                    method = getattr(plugin_info.instance, method_name)
                    if not callable(method):
                        errors.append(f"插件 {plugin_info.name} 的 {method_name} 不可调用")
                
                # 验证策略类型
                plugin_type = plugin_info.instance.get_strategy_type()
                if plugin_type != strategy_type:
                    errors.append(f"插件 {plugin_info.name} 类型不匹配: 注册为 {strategy_type}, 实际为 {plugin_type}")
                
            except Exception as e:
                errors.append(f"验证插件 {plugin_info.name} 失败: {e}")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "total_plugins": len(self._strategies),
            "valid_plugins": len(self._strategies) - len(errors)
        }
    
    def enable_strategy(self, strategy_type: StrategyType) -> bool:
        """启用策略"""
        if strategy_type not in self._strategies:
            print(f"⚠️  策略 {strategy_type} 未注册")
            return False
        
        self._strategies[strategy_type].enabled = True
        print(f"✅ 启用策略: {strategy_type}")
        return True
    
    def disable_strategy(self, strategy_type: StrategyType) -> bool:
        """禁用策略"""
        if strategy_type not in self._strategies:
            print(f"⚠️  策略 {strategy_type} 未注册")
            return False
        
        self._strategies[strategy_type].enabled = True
        print(f"✅ 禁用策略: {strategy_type}")
        return True
    
    def get_available_strategies(self) -> List[StrategyType]:
        """获取所有可用策略类型"""
        return list(self._strategies.keys())
    
    def get_strategy_info(self, strategy_type: StrategyType) -> Optional[Dict[str, Any]]:
        """获取策略详细信息"""
        if strategy_type not in self._strategies:
            return None
        
        plugin_info = self._strategies[strategy_type]
        return {
            "name": plugin_info.name,
            "type": plugin_info.strategy_type.value,
            "version": plugin_info.version,
            "description": plugin_info.description,
            "enabled": plugin_info.enabled,
            "initialized": plugin_info.initialized,
            "author": plugin_info.author,
            "class_name": plugin_info.plugin_class.__name__
        }
    
    def cleanup(self) -> None:
        """清理所有插件资源"""
        print("🧹 清理插件资源...")
        
        for strategy_type, plugin_info in self._strategies.items():
            if plugin_info.instance and hasattr(plugin_info.instance, "cleanup"):
                try:
                    plugin_info.instance.cleanup()
                    print(f"✅ 清理插件: {plugin_info.name}")
                except Exception as e:
                    print(f"⚠️  清理插件 {plugin_info.name} 失败: {e}")
        
        self._strategies.clear()
        self._initialized = False
        print("✅ 插件资源清理完成")


# 工具函数：创建默认插件管理器
def create_default_plugin_manager() -> PluginManager:
    """创建默认插件管理器"""
    manager = PluginManager()
    
    # 自动初始化
    if not manager.initialize():
        print("⚠️  插件管理器初始化失败，将继续使用空管理器")
    
    return manager


# 工具函数：注册插件装饰器
def register_plugin(strategy_type: StrategyType):
    """
    插件注册装饰器
    
    Usage:
        @register_plugin(StrategyType.CLICK_BASED)
        class ClickBasedStrategy(IExtractionStrategy):
            ...
    """
    def decorator(cls):
        # 验证类是否实现了必需接口
        required_methods = [
            "get_strategy_type",
            "get_strategy_name", 
            "initialize",
            "validate_environment",
            "extract_list_page",
            "extract_position_detail",
            "save_position_data"
        ]
        
        for method in required_methods:
            if not hasattr(cls, method):
                raise PluginError(f"插件类 {cls.__name__} 缺少方法 {method}")
        
        # 添加策略类型属性
        cls._strategy_type = strategy_type
        
        # 创建注册函数
        def register_plugin_function(plugin_manager: PluginManager):
            instance = cls()
            plugin_manager.register_strategy(instance)
            return {
                "name": cls.__name__,
                "type": strategy_type,
                "class": cls,
                "instance": instance
            }
        
        # 将注册函数添加到类
        cls.register_plugin = staticmethod(register_plugin_function)
        
        return cls
    
    return decorator


if __name__ == "__main__":
    # 测试插件管理器
    print("🧪 测试插件管理器...")
    
    manager = PluginManager()
    success = manager.initialize()
    
    if success:
        print("✅ 插件管理器测试通过")
        print(f"📊 加载的插件: {manager.list_strategies()}")
    else:
        print("❌ 插件管理器测试失败")
        print(f"❌ 加载错误: {manager.load_errors}")