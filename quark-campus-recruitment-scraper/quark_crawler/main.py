#!/usr/bin/env python3
# 🏗️ 夸克爬取器 - 主程序入口
# 版本: 2.0 (插件化架构)
# 创建时间: 2026-05-19
# 基于记忆系统: 使用标准化接口和防错机制

import os
import sys
import json
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入核心组件
from core.interfaces import (
    StrategyType, PositionData, PageState, ExecutionContext,
    IExtractionStrategy, create_position_data_from_dict
)
from core.plugin_manager import PluginManager, create_default_plugin_manager
from core.browser_manager import OpenClawBrowserManager
from plugins.utils.data_manager import StandardDataManager


class QuarkCrawler:
    """夸克爬取器主类 - 基于插件化架构"""
    
    def __init__(self, config_path: str = None):
        """
        初始化夸克爬取器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "..", "config", "quark_config.json"
        )
        
        # 核心组件
        self.plugin_manager: Optional[PluginManager] = None
        self.browser_manager: Optional[OpenClawBrowserManager] = None
        self.data_manager: Optional[StandardDataManager] = None
        self.current_strategy: Optional[IExtractionStrategy] = None
        
        # 配置
        self.config: Dict[str, Any] = self._load_config()
        self.output_dir = self.config.get("output_dir", "output")
        
        # 状态跟踪
        self.execution_context: Optional[ExecutionContext] = None
        self.current_page_state: Optional[PageState] = None
        self.positions_extracted: List[PositionData] = []
        
        # 性能统计
        self.start_time: Optional[float] = None
        self.positions_per_hour: float = 0.0
        self.error_count: int = 0
        
        print("=" * 60)
        print("🏗️  夸克校园招聘爬取器 - 插件化架构版")
        print(f"📁 项目路径: {os.path.dirname(os.path.dirname(__file__))}")
        print(f"⚙️  配置文件: {self.config_path}")
        print("=" * 60)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "project_name": "夸克校园招聘爬取器",
            "target_positions": 92,
            "filter_categories": [
                "产品类", "运营类", "数据类", 
                "市场拓展", "销售类", "游戏类", "金融类"
            ],
            "output_dir": "output",
            "default_strategy": "direct_url",
            "browser_profile": "openclaw",
            "timeout_ms": 30000,
            "max_retries": 3,
            "retry_delay_ms": 1000,
            "save_interval": 5,
            "validate_before_action": True,
            "create_backups": True
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # 合并配置
                default_config.update(user_config)
                print(f"✅ 加载配置文件: {self.config_path}")
                
            except Exception as e:
                print(f"⚠️  配置文件加载失败，使用默认配置: {e}")
        else:
            print(f"⚠️  配置文件不存在，使用默认配置: {self.config_path}")
            
            # 创建配置目录
            config_dir = os.path.dirname(self.config_path)
            os.makedirs(config_dir, exist_ok=True)
            
            # 保存默认配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print(f"📄 创建默认配置文件: {self.config_path}")
        
        return default_config
    
    def initialize(self) -> bool:
        """初始化所有组件"""
        print("\n🧠 初始化夸克爬取器...")
        
        try:
            # 1. 初始化插件管理器
            print("1. 初始化插件管理器...")
            self.plugin_manager = create_default_plugin_manager()
            
            if not self.plugin_manager.initialize():
                print("❌ 插件管理器初始化失败")
                return False
            
            # 列出可用插件
            strategies = self.plugin_manager.list_strategies()
            print(f"   ✅ 加载了 {len(strategies)} 个插件:")
            for strategy in strategies:
                print(f"     • {strategy['name']} ({strategy['type']})")
            
            # 2. 初始化浏览器管理器
            print("2. 初始化浏览器管理器...")
            self.browser_manager = OpenClawBrowserManager(
                profile=self.config.get("browser_profile", "openclaw")
            )
            
            if not self.browser_manager.initialize():
                print("❌ 浏览器管理器初始化失败")
                return False
            
            # 3. 初始化数据管理器
            print("3. 初始化数据管理器...")
            self.data_manager = StandardDataManager()
            
            output_dir = self.config.get("output_dir", "output")
            if not self.data_manager.initialize(output_dir):
                print("❌ 数据管理器初始化失败")
                return False
            
            # 4. 选择策略
            print("4. 选择提取策略...")
            strategy_type_str = self.config.get("default_strategy", "direct_url")
            
            try:
                strategy_type = StrategyType(strategy_type_str)
            except ValueError:
                print(f"⚠️  未知策略类型: {strategy_type_str}，使用默认策略")
                strategy_type = StrategyType.DIRECT_URL
            
            self.current_strategy = self.plugin_manager.get_strategy(strategy_type)
            
            if not self.current_strategy:
                print(f"❌ 无法获取策略: {strategy_type}")
                return False
            
            print(f"   ✅ 选择策略: {self.current_strategy.get_strategy_name()} ({strategy_type})")
            
            # 5. 初始化执行上下文
            print("5. 初始化执行上下文...")
            self.execution_context = ExecutionContext(
                strategy_type=strategy_type,
                browser_profile=self.config.get("browser_profile", "openclaw"),
                current_page=1,
                current_position_index=0,
                retry_count=0,
                timeout_ms=self.config.get("timeout_ms", 30000),
                positions_completed=0,
                positions_failed=0,
                start_time=datetime.now().isoformat(),
                last_update_time=datetime.now().isoformat()
            )
            
            # 6. 初始化策略
            print("6. 初始化策略...")
            if not self.current_strategy.initialize(self.execution_context):
                print("❌ 策略初始化失败")
                return False
            
            # 7. 验证环境
            print("7. 验证环境...")
            environment_issues = self.current_strategy.validate_environment()
            
            if environment_issues:
                print(f"⚠️  环境验证发现问题:")
                for issue in environment_issues:
                    print(f"    • {issue}")
                
                # 严重问题阻止执行
                critical_issues = [i for i in environment_issues if "必须" in i or "无法" in i]
                if critical_issues:
                    print("❌ 发现严重问题，无法继续执行")
                    return False
            else:
                print("   ✅ 环境验证通过")
            
            self.start_time = time.time()
            print("✅ 夸克爬取器初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def validate_page_state(self) -> bool:
        """验证页面状态"""
        if not self.current_strategy:
            print("❌ 未选择策略")
            return False
        
        expected_categories = self.config.get("filter_categories", [])
        
        print("\n🔍 验证页面状态...")
        print(f"   期望筛选类别: {expected_categories}")
        print(f"   期望数量: {len(expected_categories)}个")
        
        # 验证筛选状态
        is_valid = self.current_strategy.validate_page_state(expected_categories)
        
        if is_valid:
            print("   ✅ 页面状态验证通过")
        else:
            print("   ❌ 页面状态验证失败")
            
            # 尝试重新应用筛选
            print("   🔄 尝试重新应用筛选...")
            # 这里需要实现重新应用筛选的逻辑
        
        return is_valid
    
    def extract_single_page(self, page_number: int) -> List[PositionData]:
        """提取单个页面"""
        if not self.current_strategy:
            print("❌ 未选择策略")
            return []
        
        print(f"\n📄 开始提取第 {page_number} 页...")
        
        try:
            # 1. 提取列表页
            print(f"   1. 提取列表页...")
            position_ids = self.current_strategy.extract_list_page(page_number)
            
            if not position_ids:
                print("   ⚠️  列表页提取失败或没有找到岗位")
                return []
            
            print(f"   ✅ 找到 {len(position_ids)} 个岗位")
            
            # 2. 批量提取详情
            print(f"   2. 批量提取岗位详情...")
            positions = []
            
            for i, position_id in enumerate(position_ids):
                print(f"     [{i+1}/{len(position_ids)}] 提取岗位: {position_id}")
                
                try:
                    position_data = self.current_strategy.extract_position_detail(
                        position_id, page_number, i + 1
                    )
                    
                    # 验证数据完整性
                    missing_fields = position_data.validate()
                    if missing_fields:
                        print(f"       ⚠️  数据不完整，缺失字段: {missing_fields}")
                    else:
                        print(f"       ✅ 数据完整 (12个字段)")
                    
                    positions.append(position_data)
                    
                    # 更新进度
                    if self.execution_context:
                        self.execution_context.positions_completed += 1
                        self.execution_context.last_update_time = datetime.now().isoformat()
                    
                    # 定期保存
                    if len(positions) % self.config.get("save_interval", 5) == 0:
                        self._save_current_progress(positions, page_number)
                        
                except Exception as e:
                    print(f"       ❌ 提取失败: {position_id} - {e}")
                    
                    if self.execution_context:
                        self.execution_context.positions_failed += 1
                    
                    self.error_count += 1
            
            # 3. 保存页面数据
            if positions:
                print(f"   3. 保存页面数据...")
                self._save_current_progress(positions, page_number)
            
            print(f"   📊 第 {page_number} 页提取完成: {len(positions)}/{len(position_ids)} 个岗位")
            return positions
            
        except Exception as e:
            print(f"❌ 提取第 {page_number} 页失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _save_current_progress(self, positions: List[PositionData], page_number: int) -> None:
        """保存当前进度"""
        if not self.data_manager or not positions:
            return
        
        try:
            # 保存页面数据
            page_file = self.data_manager.save_page_data(page_number, positions)
            print(f"       📄 保存页面数据: {page_file}")
            
            # 更新全局数据
            self.positions_extracted.extend(positions)
            
            # 保存完整数据
            if len(self.positions_extracted) >= 10:  # 每10个岗位保存一次完整数据
                full_file = self.data_manager.save_full_data(self.positions_extracted)
                print(f"       📊 保存完整数据: {full_file}")
            
            # 生成报告
            report_file = self.data_manager.generate_report(self.positions_extracted)
            print(f"       📈 生成报告: {report_file}")
            
        except Exception as e:
            print(f"       ⚠️  保存进度失败: {e}")
    
    def run(self, start_page: int = 1, end_page: int = 10) -> bool:
        """运行爬取器"""
        if not self.initialize():
            print("❌ 初始化失败，无法运行")
            return False
        
        print("\n" + "=" * 60)
        print("🚀 开始执行夸克招聘爬取任务")
        print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📄 目标页面: {start_page} - {end_page}")
        print(f"🎯 目标岗位: {self.config.get('target_positions', 92)}")
        print("=" * 60)
        
        try:
            # 验证初始状态
            if not self.validate_page_state():
                print("⚠️  初始页面状态验证失败，可能影响提取结果")
                # 根据配置决定是否继续
                if self.config.get("validate_before_action", True):
                    user_input = input("❓ 是否继续? (y/n): ")
                    if user_input.lower() != 'y':
                        print("⏹️  用户取消执行")
                        return False
            
            total_positions = 0
            
            for page_num in range(start_page, end_page + 1):
                print(f"\n{'='*40}")
                print(f"📖 处理第 {page_num}/{end_page} 页")
                print(f"{'='*40}")
                
                # 更新当前页面状态
                if self.execution_context:
                    self.execution_context.current_page = page_num
                    self.execution_context.current_position_index = 0
                
                # 提取页面
                page_positions = self.extract_single_page(page_num)
                total_positions += len(page_positions)
                
                # 计算进度
                progress = (total_positions / self.config.get('target_positions', 92)) * 100
                print(f"📊 总进度: {total_positions}/{self.config.get('target_positions', 92)} ({progress:.1f}%)")
                
                # 计算性能
                elapsed_hours = (time.time() - self.start_time) / 3600 if self.start_time else 1
                self.positions_per_hour = total_positions / elapsed_hours if elapsed_hours > 0 else 0
                print(f"⏱️  性能: {self.positions_per_hour:.1f} 岗位/小时")
                
                # 检查是否达到目标
                if total_positions >= self.config.get('target_positions', 92):
                    print("🎯 已达到目标岗位数量")
                    break
                
                # 添加延迟，避免请求过快
                if page_num < end_page:
                    delay_seconds = 2
                    print(f"⏳ 等待 {delay_seconds} 秒后继续...")
                    time.sleep(delay_seconds)
            
            # 最终保存和报告
            print("\n" + "=" * 60)
            print("✅ 任务执行完成")
            print("=" * 60)
            
            self._generate_final_report(total_positions)
            self.cleanup()
            
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️  用户中断执行")
            self._save_interrupted_progress()
            return False
        except Exception as e:
            print(f"\n❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()
            self._save_interrupted_progress()
            return False
    
    def _generate_final_report(self, total_positions: int) -> None:
        """生成最终报告"""
        if not self.data_manager or not self.positions_extracted:
            return
        
        try:
            print("\n📊 生成最终报告...")
            
            # 保存完整数据
            full_file = self.data_manager.save_full_data(self.positions_extracted)
            print(f"   📄 完整数据: {full_file}")
            
            # 生成详细报告
            report_file = self.data_manager.generate_report(self.positions_extracted)
            print(f"   📈 详细报告: {report_file}")
            
            # 生成统计信息
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            hours = elapsed_time / 3600
            
            stats = {
                "total_positions": total_positions,
                "target_positions": self.config.get('target_positions', 92),
                "completion_rate": (total_positions / self.config.get('target_positions', 92)) * 100,
                "execution_time_hours": hours,
                "positions_per_hour": self.positions_per_hour,
                "error_count": self.error_count,
                "error_rate": (self.error_count / max(total_positions + self.error_count, 1)) * 100,
                "start_time": self.execution_context.start_time if self.execution_context else "",
                "end_time": datetime.now().isoformat(),
                "strategy_used": self.execution_context.strategy_type.value if self.execution_context else "",
                "filter_categories": self.config.get('filter_categories', [])
            }
            
            # 保存统计信息
            stats_file = os.path.join(self.output_dir, "final_stats.json")
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            print(f"   📊 统计数据: {stats_file}")
            
            # 打印摘要
            print("\n📋 执行摘要:")
            print(f"   总岗位数: {stats['total_positions']}/{stats['target_positions']}")
            print(f"   完成率: {stats['completion_rate']:.1f}%")
            print(f"   执行时间: {stats['execution_time_hours']:.2f} 小时")
            print(f"   处理速度: {stats['positions_per_hour']:.1f} 岗位/小时")
            print(f"   错误数量: {stats['error_count']} ({stats['error_rate']:.1f}%)")
            
        except Exception as e:
            print(f"   ⚠️  生成报告失败: {e}")
    
    def _save_interrupted_progress(self) -> None:
        """保存中断时的进度"""
        print("\n💾 保存中断进度...")
        
        if self.positions_extracted:
            try:
                # 创建中断备份目录
                interrupt_dir = os.path.join(self.output_dir, "interrupted_backups")
                os.makedirs(interrupt_dir, exist_ok=True)
                
                # 保存当前数据
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(interrupt_dir, f"interrupted_{timestamp}.json")
                
                data_to_save = [asdict(pos) for pos in self.positions_extracted]
                
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "positions": data_to_save,
                        "total_count": len(self.positions_extracted),
                        "interrupted_at": datetime.now().isoformat(),
                        "context": asdict(self.execution_context) if self.execution_context else {}
                    }, f, ensure_ascii=False, indent=2)
                
                print(f"   ✅ 中断进度已保存: {backup_file}")
                
            except Exception as e:
                print(f"   ❌ 保存中断进度失败: {e}")
    
    def cleanup(self) -> None:
        """清理资源"""
        print("\n🧹 清理资源...")
        
        try:
            # 清理策略
            if self.current_strategy and hasattr(self.current_strategy, "cleanup"):
                self.current_strategy.cleanup()
                print("   ✅ 清理策略资源")
            
            # 清理浏览器
            if self.browser_manager and hasattr(self.browser_manager, "cleanup"):
                self.browser_manager.cleanup()
                print("   ✅ 清理浏览器资源")
            
            # 清理插件管理器
            if self.plugin_manager and hasattr(self.plugin_manager, "cleanup"):
                self.plugin_manager.cleanup()
                print("   ✅ 清理插件资源")
            
            print("✅ 资源清理完成")
            
        except Exception as e:
            print(f"⚠️  清理资源时出错: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="夸克校园招聘爬取器 - 插件化架构版")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--strategy", help="提取策略 (click_based, direct_url, hybrid)")
    parser.add_argument("--start-page", type=int, default=1, help="起始页码")
    parser.add_argument("--end-page", type=int, default=10, help="结束页码")
    parser.add_argument("--output-dir", help="输出目录")
    parser.add_argument("--validate-only", action="store_true", help="仅验证，不执行")
    parser.add_argument("--list-plugins", action="store_true", help="列出可用插件")
    
    args = parser.parse_args()
    
    # 创建爬取器实例
    crawler = QuarkCrawler(config_path=args.config)
    
    # 列出插件
    if args.list_plugins:
        print("🔌 可用插件:")
        
        # 这里需要先初始化插件管理器
        crawler.plugin_manager = create_default_plugin_manager()
        if crawler.plugin_manager.initialize():
            plugins = crawler.plugin_manager.list_strategies()
            for plugin in plugins:
                print(f"  • {plugin['name']} ({plugin['type']}) - {plugin['description']}")
        else:
            print("❌ 无法加载插件列表")
        
        return
    
    # 仅验证
    if args.validate_only:
        if crawler.initialize():
            print("✅ 系统验证通过")
            crawler.validate_page_state()
        else:
            print("❌ 系统验证失败")
        return
    
    # 运行爬取器
    success = crawler.run(
        start_page=args.start_page,
        end_page=args.end_page
    )
    
    if success:
        print("\n🎉 夸克爬取任务完成!")
        sys.exit(0)
    else:
        print("\n💀 夸克爬取任务失败")
        sys.exit(1)


if __name__ == "__main__":
    main()