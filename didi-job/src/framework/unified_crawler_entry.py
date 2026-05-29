#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一爬取器入口框架模板
- 命令行参数解析
- 模式选择逻辑
- 状态查询功能
- 数据导出功能

通用组件，可用于任何公司招聘爬取
"""

import argparse
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class UnifiedCrawlerEntry:
    """统一爬取器入口框架"""
    
    def __init__(self, company_name: str = "公司名称"):
        """
        初始化统一入口
        
        Args:
            company_name: 公司名称，用于显示和文件命名
        """
        self.company_name = company_name
        self.version = "1.0.0"
        self.description = f"{company_name}招聘爬取器 - 统一入口"
        self.author = "AI助手"
        self.created_date = datetime.now().strftime("%Y-%m-%d")
        
        # 默认配置
        self.default_config = {
            "mode": "optimized",      # 默认模式
            "start_page": 1,          # 起始页码
            "end_page": 10,           # 结束页码
            "output_format": "excel", # 输出格式
            "config_path": "config/api_auth.json",  # 配置文件路径
            "auto_switch": False      # 是否自动切换
        }
        
        # 输出目录
        self.output_dir = f"output/{company_name.lower().replace(' ', '_')}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 状态跟踪
        self.current_mode = None
        self.start_time = None
        self.data_extracted = 0
        
    def parse_arguments(self, args: List[str] = None) -> argparse.Namespace:
        """
        解析命令行参数
        
        Args:
            args: 命令行参数列表，None表示使用sys.argv
            
        Returns:
            解析后的参数对象
        """
        parser = argparse.ArgumentParser(
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f"""
示例用法:
  {sys.argv[0]} --mode optimized          # 使用优化模式
  {sys.argv[0]} --mode api --start 1 --end 5  # API模式爬取前5页
  {sys.argv[0]} --mode status             # 查看状态
  {sys.argv[0]} --mode export --format excel  # 导出数据到Excel
  
支持的模式:
  • api        : 纯API模式
  • browser    : 纯浏览器模式  
  • smart      : 智能模式（API优先）
  • optimized  : 优化模式（失败后询问用户，推荐）
  • status     : 查看项目状态
  • export     : 导出已爬取的数据
  • check      : 检查数据完整性
"""
        )
        
        # 模式选择
        parser.add_argument(
            "--mode", 
            choices=["api", "browser", "smart", "optimized", "status", "export", "check"],
            default=self.default_config["mode"],
            help=f"运行模式（默认: {self.default_config['mode']}）"
        )
        
        # 分页参数
        parser.add_argument(
            "--start", 
            type=int,
            default=self.default_config["start_page"],
            help=f"起始页码（默认: {self.default_config['start_page']}）"
        )
        
        parser.add_argument(
            "--end", 
            type=int,
            default=self.default_config["end_page"],
            help=f"结束页码（默认: {self.default_config['end_page']}）"
        )
        
        # 输出格式
        parser.add_argument(
            "--format",
            choices=["excel", "csv", "json", "all"],
            default=self.default_config["output_format"],
            help=f"输出格式（默认: {self.default_config['output_format']}）"
        )
        
        # 配置文件
        parser.add_argument(
            "--config",
            default=self.default_config["config_path"],
            help=f"配置文件路径（默认: {self.default_config['config_path']}）"
        )
        
        # 自动切换
        parser.add_argument(
            "--auto-switch",
            action="store_true",
            default=self.default_config["auto_switch"],
            help="失败时自动切换到浏览器（谨慎使用）"
        )
        
        # 其他选项
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            default=False,
            help="显示详细日志"
        )
        
        parser.add_argument(
            "--quiet", "-q",
            action="store_true",
            default=False,
            help="静默模式，只输出关键信息"
        )
        
        # 版本信息
        parser.add_argument(
            "--version", "-V",
            action="version",
            version=f"%(prog)s {self.version} ({self.created_date})"
        )
        
        return parser.parse_args(args)
    
    def show_banner(self):
        """显示启动横幅"""
        banner = f"""
╔{'═' * 70}╗
║{'🚀 统一爬取器入口框架'.center(68)}║
║{'━' * 70}║
║{'公司:'.ljust(12)} {self.company_name} ║
║{'版本:'.ljust(12)} {self.version} ║
║{'创建:'.ljust(12)} {self.created_date} ║
║{'模式:'.ljust(12)} {self.current_mode or '未选择'} ║
║{'输出:'.ljust(12)} {self.output_dir} ║
╚{'═' * 70}╝
"""
        print(banner)
    
    def run_mode_api(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        API模式运行
        
        Args:
            args: 命令行参数
            
        Returns:
            运行结果
        """
        print("🚀 启动API爬取模式...")
        self.current_mode = "api"
        
        # TODO: 需要业务实现API爬取逻辑
        # 例如：from api_crawler import CompanyApiCrawler
        #       crawler = CompanyApiCrawler(args.config)
        #       result = crawler.crawl_pages(args.start, args.end)
        
        print("⚠️  API模式需要业务实现")
        
        return {
            "success": False,
            "mode": "api",
            "message": "需要业务实现API爬取逻辑",
            "recommendation": "请实现具体的API爬取器"
        }
    
    def run_mode_browser(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        浏览器模式运行
        
        Args:
            args: 命令行参数
            
        Returns:
            运行结果
        """
        print("🌐 启动浏览器爬取模式...")
        self.current_mode = "browser"
        
        # TODO: 需要业务实现浏览器爬取逻辑
        # 例如：from browser_crawler import CompanyBrowserCrawler
        #       crawler = CompanyBrowserCrawler()
        #       result = crawler.scrape_positions(args.start, args.end)
        
        print("⚠️  浏览器模式需要业务实现")
        
        return {
            "success": False,
            "mode": "browser",
            "message": "需要业务实现浏览器爬取逻辑",
            "recommendation": "请实现具体的浏览器爬取器"
        }
    
    def run_mode_smart(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        智能模式运行（API优先）
        
        Args:
            args: 命令行参数
            
        Returns:
            运行结果
        """
        print("🧠 启动智能爬取模式（API优先）...")
        self.current_mode = "smart"
        
        # TODO: 需要业务实现智能选择器
        # 例如：from smart_selector import SmartCrawlerSelector
        #       selector = SmartCrawlerSelector(args.config)
        #       result = selector.smart_crawl(args.start, args.end)
        
        print("⚠️  智能模式需要业务实现")
        
        return {
            "success": False,
            "mode": "smart",
            "message": "需要业务实现智能选择器",
            "recommendation": "请实现具体的智能选择器"
        }
    
    def run_mode_optimized(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        优化模式运行（失败后询问用户）
        
        Args:
            args: 命令行参数
            
        Returns:
            运行结果
        """
        print("🔧 启动优化爬取模式（失败后询问用户）...")
        self.current_mode = "optimized"
        
        # TODO: 需要业务实现优化的智能选择器
        # 例如：from optimized_selector import OptimizedCrawlerSelector
        #       selector = OptimizedCrawlerSelector(args.config)
        #       result = selector.smart_crawl_with_user_interaction()
        
        print("⚠️  优化模式需要业务实现")
        
        return {
            "success": False,
            "mode": "optimized",
            "message": "需要业务实现优化选择器",
            "recommendation": "请实现具体的优化选择器"
        }
    
    def run_mode_status(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        状态查看模式
        
        Args:
            args: 命令行参数
            
        Returns:
            状态信息
        """
        print("📊 查看项目状态...")
        self.current_mode = "status"
        
        # 检查文件系统
        files_exist = {
            "配置文件": os.path.exists(args.config),
            "输出目录": os.path.exists(self.output_dir),
            "爬取脚本": os.path.exists("scripts/"),
            "数据文件": len(os.listdir(self.output_dir)) if os.path.exists(self.output_dir) else 0
        }
        
        # 创建状态报告
        status_report = {
            "company": self.company_name,
            "version": self.version,
            "config_file": args.config,
            "config_exists": files_exist["配置文件"],
            "output_dir": self.output_dir,
            "output_exists": files_exist["输出目录"],
            "data_files_count": files_exist["数据文件"],
            "scripts_dir_exists": files_exist["爬取脚本"],
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system": "统一爬取器框架",
            "status": "框架就绪，需要业务实现"
        }
        
        # 显示状态
        print("\n" + "=" * 50)
        print("📋 项目状态报告")
        print("=" * 50)
        
        for key, value in status_report.items():
            if isinstance(value, bool):
                status = "✅" if value else "❌"
                print(f"  {key}: {status}")
            else:
                print(f"  {key}: {value}")
        
        print("\n🔧 下一步:")
        if not status_report["config_exists"]:
            print("  • 创建配置文件: cp template/config.json config/")
        if not status_report["scripts_dir_exists"]:
            print("  • 创建脚本目录: mkdir scripts/")
        print("  • 实现具体的爬取器逻辑")
        print("  • 测试爬取功能")
        
        return status_report
    
    def run_mode_export(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        数据导出模式
        
        Args:
            args: 命令行参数
            
        Returns:
            导出结果
        """
        print(f"💾 导出数据（格式: {args.format}）...")
        self.current_mode = "export"
        
        # TODO: 需要业务实现数据导出逻辑
        # 例如：from data_exporter import DataExporter
        #       exporter = DataExporter(self.output_dir)
        #       result = exporter.export(args.format)
        
        print("⚠️  数据导出需要业务实现")
        
        return {
            "success": False,
            "mode": "export",
            "format": args.format,
            "message": "需要业务实现数据导出逻辑",
            "recommendation": "请实现具体的数据导出器"
        }
    
    def run_mode_check(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        数据检查模式
        
        Args:
            args: 命令行参数
            
        Returns:
            检查结果
        """
        print("🔍 检查数据完整性...")
        self.current_mode = "check"
        
        # TODO: 需要业务实现数据检查逻辑
        # 例如：from data_checker import DataChecker
        #       checker = DataChecker(self.output_dir)
        #       result = checker.check_integrity()
        
        print("⚠️  数据检查需要业务实现")
        
        return {
            "success": False,
            "mode": "check",
            "message": "需要业务实现数据检查逻辑",
            "recommendation": "请实现具体的数据检查器"
        }
    
    def run(self, args: List[str] = None) -> Dict[str, Any]:
        """
        主运行函数
        
        Args:
            args: 命令行参数列表
            
        Returns:
            运行结果
        """
        self.start_time = time.time()
        
        # 1. 解析参数
        parsed_args = self.parse_arguments(args)
        
        # 2. 显示横幅
        if not parsed_args.quiet:
            self.show_banner()
        
        # 3. 根据模式运行
        mode_handlers = {
            "api": self.run_mode_api,
            "browser": self.run_mode_browser,
            "smart": self.run_mode_smart,
            "optimized": self.run_mode_optimized,
            "status": self.run_mode_status,
            "export": self.run_mode_export,
            "check": self.run_mode_check
        }
        
        if parsed_args.mode not in mode_handlers:
            print(f"❌ 不支持的模式: {parsed_args.mode}")
            return {
                "success": False,
                "error": f"不支持的模式: {parsed_args.mode}",
                "supported_modes": list(mode_handlers.keys())
            }
        
        # 4. 执行对应模式
        try:
            result = mode_handlers[parsed_args.mode](parsed_args)
            elapsed_time = time.time() - self.start_time
            
            # 添加执行时间
            if isinstance(result, dict):
                result["elapsed_time_seconds"] = elapsed_time
            
            # 显示结果摘要
            if not parsed_args.quiet:
                self._show_result_summary(result, elapsed_time)
            
            return result
            
        except KeyboardInterrupt:
            elapsed_time = time.time() - self.start_time
            print(f"\n❌ 用户中断执行 (耗时: {elapsed_time:.1f}秒)")
            return {
                "success": False,
                "error": "用户中断",
                "elapsed_time_seconds": elapsed_time,
                "mode": parsed_args.mode
            }
        except Exception as e:
            elapsed_time = time.time() - self.start_time
            print(f"\n❌ 执行异常: {e} (耗时: {elapsed_time:.1f}秒)")
            return {
                "success": False,
                "error": str(e),
                "elapsed_time_seconds": elapsed_time,
                "mode": parsed_args.mode
            }
    
    def _show_result_summary(self, result: Dict[str, Any], elapsed_time: float):
        """显示结果摘要"""
        print("\n" + "=" * 50)
        print("📋 执行摘要")
        print("=" * 50)
        
        print(f"  模式: {self.current_mode}")
        print(f"  耗时: {elapsed_time:.1f}秒")
        
        if result.get("success"):
            print(f"  状态: ✅ 成功")
            
            # 显示成功相关信息
            for key in ["data_extracted", "completion_percentage", "output_directory"]:
                if key in result:
                    print(f"  {key.replace('_', ' ')}: {result[key]}")
        else:
            print(f"  状态: ❌ 失败")
            
            if "error" in result:
                print(f"  错误: {result['error']}")
            elif "message" in result:
                print(f"  信息: {result['message']}")
        
        # 显示建议
        if "recommendation" in result:
            print(f"\n💡 建议: {result['recommendation']}")
        
        print()


def create_company_crawler(company_name: str, output_file: str = None):
    """
    创建公司特定的爬取器入口文件
    
    Args:
        company_name: 公司名称
        output_file: 输出文件路径，默认为 company_crawler.py
    
    Returns:
        创建的爬取器入口文件路径
    """
    if not output_file:
        safe_name = company_name.lower().replace(' ', '_')
        output_file = f"{safe_name}_crawler.py"
    
    template = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{company_name}招聘爬取器 - 基于统一入口框架
"""

import sys
import os

# 添加父目录到路径，以便导入框架
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# TODO: 导入具体的业务实现
# from scripts.api_crawler import {company_name.replace(' ', '')}ApiCrawler
# from scripts.browser_crawler import {company_name.replace(' ', '')}BrowserCrawler
# from scripts.smart_selector import {company_name.replace(' ', '')}SmartCrawlerSelector

from unified_crawler_entry import UnifiedCrawlerEntry


class {company_name.replace(' ', '')}Crawler(UnifiedCrawlerEntry):
    """{company_name}招聘爬取器"""
    
    def __init__(self):
        """初始化{company_name}爬取器"""
        super().__init__(company_name="{company_name}")
        
        # TODO: 可以在这里添加{company_name}特定的初始化逻辑
        # 例如：设置默认配置、验证环境等
    
    # TODO: 覆盖父类的方法来实现具体的业务逻辑
    # def run_mode_api(self, args):
    #     """实现{company_name}的API爬取逻辑"""
    #     print(f"🚀 {company_name}API爬取模式")
    #     
    #     # 1. 创建API爬取器实例
    #     api_crawler = {company_name.replace(' ', '')}ApiCrawler(args.config)
    #     
    #     # 2. 执行爬取
    #     result = api_crawler.crawl_pages(args.start, args.end)
    #     
    #     # 3. 返回结果
    #     return result
    # 
    # def run_mode_browser(self, args):
    #     """实现{company_name}的浏览器爬取逻辑"""
    #     print(f"🌐 {company_name}浏览器爬取模式")
    #     
    #     # 类似地实现浏览器爬取逻辑
    #     pass
    # 
    # def run_mode_smart(self, args):
    #     """实现{company_name}的智能爬取逻辑"""
    #     print(f"🧠 {company_name}智能爬取模式")
    #     
    #     # 类似地实现智能选择逻辑
    #     pass
    # 
    # def run_mode_optimized(self, args):
    #     """实现{company_name}的优化爬取逻辑"""
    #     print(f"🔧 {company_name}优化爬取模式")
    #     
    #     # 类似地实现优化选择逻辑
    #     pass


def main():
    """主函数"""
    crawler = {company_name.replace(' ', '')}Crawler()
    
    # 运行爬取器
    result = crawler.run()
    
    # 根据结果退出
    if result.get("success"):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(template)
    
    # 设置执行权限
    os.chmod(output_file, 0o755)
    
    print(f"✅ 已创建{company_name}爬取器入口: {output_file}")
    print("下一步:")
    print(f"  1. 实现具体的爬取器逻辑（scripts/目录）")
    print(f"  2. 配置认证信息（config/目录）")
    print(f"  3. 测试: python3 {output_file} --mode status")
    
    return output_file


def demo():
    """演示如何使用统一入口框架"""
    print("🚀 统一入口框架演示")
    print("=" * 50)
    
    # 1. 创建示例公司爬取器
    print("1. 创建示例公司爬取器...")
    crawler_file = create_company_crawler("示例公司", "demo_company_crawler.py")
    
    # 2. 显示帮助信息
    print(f"\n2. 显示帮助信息:")
    print(f"   python3 {crawler_file} --help")
    
    # 3. 演示状态查看
    print(f"\n3. 演示状态查看:")
    print(f"   python3 {crawler_file} --mode status")
    
    # 4. 清理演示文件
    print(f"\n4. 清理演示文件...")
    if os.path.exists("demo_company_crawler.py"):
        os.remove("demo_company_crawler.py")
        print("   ✅ 已清理演示文件")
    
    print("\n🎉 演示完成！")
    print("💡 实际使用时，请创建公司特定的爬取器并实现业务逻辑")


if __name__ == "__main__":
    demo()