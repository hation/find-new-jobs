#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
夸克校园招聘爬取器 - 统一入口
API优先，浏览器备选的智能爬取系统
符合插件规范
"""

import sys
import os
import json
import argparse
from datetime import datetime

def print_banner():
    """打印横幅"""
    print("=" * 70)
    print("🚀 夸克校园招聘爬取器 - 统一入口")
    print("📊 API优先，浏览器备选的智能爬取系统")
    print("📋 符合插件规范 v2.1")
    print("=" * 70)
    print()

def check_environment():
    """检查环境"""
    print("🔍 环境检查:")
    
    # 检查必要的目录
    required_dirs = ["scripts", "output", "config"]
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ {dir_name}/ 目录存在")
        else:
            print(f"   ❌ {dir_name}/ 目录缺失")
            os.makedirs(dir_name, exist_ok=True)
            print(f"   ✅ 已创建 {dir_name}/ 目录")
    
    # 检查必要的文件
    required_files = [
        "ARCHITECTURE.md",
        "CHECKLIST.md",
        "LESSONS_LEARNED.md",
        "memory_checkpoints.json",
        "scripts/api_crawler_final.py",
        "scripts/crawler_selector.py"
    ]
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"   ✅ {file_name} 存在")
        else:
            print(f"   ⚠️  {file_name} 缺失")
    
    print()

def load_config():
    """加载配置"""
    config_file = "config/crawler_config.json"
    
    default_config = {
        "crawler_mode": "api_priority",  # api_priority, browser_only
        "start_page": 1,
        "end_page": 10,
        "page_size": 10,
        "output_format": "excel",  # excel, csv, json, all
        "data_fields": 15,
        "categories": "97,103,143,124,152,492,146",
        "enable_logging": True,
        "enable_backup": True,
        "retry_count": 3,
        "retry_delay": 2,
        "timeout_seconds": 30
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # 合并配置
            config = {**default_config, **user_config}
            print(f"✅ 已加载配置文件: {config_file}")
            return config
        except Exception as e:
            print(f"⚠️  配置文件加载失败: {e}")
            print("✅ 使用默认配置")
            return default_config
    else:
        print(f"⚠️  配置文件不存在: {config_file}")
        print("✅ 使用默认配置")
        
        # 创建示例配置文件
        os.makedirs("config", exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump({
                "description": "夸克校园招聘爬取器配置文件",
                "last_updated": datetime.now().isoformat(),
                "config": default_config
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已创建示例配置文件: {config_file}")
        return default_config

def show_status():
    """显示当前状态"""
    print("📊 当前状态:")
    
    # 读取记忆检查点
    if os.path.exists("memory_checkpoints.json"):
        with open("memory_checkpoints.json", 'r', encoding='utf-8') as f:
            memory = json.load(f)
        
        project_info = memory.get("project_info", {})
        current_state = memory.get("current_state", {})
        data_status = memory.get("data_status", {})
        api_status = memory.get("api_system_status", {})
        
        print(f"   项目名称: {project_info.get('name', '未知')}")
        print(f"   目标岗位: {project_info.get('target_positions', 0)} 个")
        print(f"   当前进度: {project_info.get('current_positions', 0)} 个 ({project_info.get('progress_percentage', 0)}%)")
        print(f"   当前模式: {current_state.get('current_crawler_mode', '未知')}")
        print(f"   API状态: {api_status.get('status', '未知')}")
        print(f"   数据质量: {current_state.get('data_quality', '未知')}")
        print(f"   最近操作: {current_state.get('last_action', '无记录')}")
        print(f"   最近时间: {current_state.get('last_action_time', '无记录')}")
    else:
        print("   ❌ memory_checkpoints.json 不存在")
    
    print()

def crawl_with_api(config):
    """使用API模式爬取"""
    print("🔄 启动API模式爬取...")
    
    try:
        # 导入API爬取器
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from scripts.api_crawler_final import QuarkApiCrawlerFinal
        
        # 创建爬取器
        crawler_config = {
            "output_dir": f"output/api_crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_page": config.get("start_page", 1),
            "page_size": config.get("page_size", 10)
        }
        
        crawler = QuarkApiCrawlerFinal(crawler_config)
        
        # 显示状态
        status = crawler.get_status()
        print(f"   📊 API爬取器状态:")
        print(f"      当前页面: 第 {status['current_page']} 页")
        print(f"      总页数: {status['total_pages']} 页")
        print(f"      目标岗位: {status['target_positions']} 个")
        print(f"      输出目录: {status['output_dir']}")
        print(f"      CSRF令牌: {status['csrf_token']}")
        print(f"      Cookie数量: {status['has_valid_cookies']}")
        
        # 开始爬取
        start_page = config.get("start_page", 1)
        end_page = config.get("end_page", 10)
        
        print(f"\n   🚀 开始爬取: 第 {start_page} 页到第 {end_page} 页")
        
        result = crawler.crawl_all(start_page=start_page, end_page=end_page)
        
        if result.get("success"):
            print(f"\n   ✅ API爬取完成!")
            print(f"      获取岗位: {result['total_positions_extracted']} 个")
            print(f"      目标岗位: {result['target_positions']} 个")
            print(f"      完成比例: {result['completion_percentage']:.1f}%")
            print(f"      成功页数: {result['successful_pages']} 页")
            print(f"      总耗时: {result['elapsed_time_seconds']:.2f} 秒")
            
            # 是否导出Excel
            if config.get("output_format") in ["excel", "all"]:
                print(f"\n   📊 导出Excel文件...")
                try:
                    from merge_to_excel import merge_to_excel
                    excel_file = merge_to_excel()
                    if excel_file:
                        print(f"   ✅ Excel导出成功: {excel_file}")
                except ImportError:
                    print("   ⚠️  Excel导出模块未找到，请手动运行 merge_to_excel.py")
            
            return True, result
        else:
            print(f"\n   ❌ API爬取失败")
            return False, result
    
    except ImportError as e:
        print(f"   ❌ API爬取器导入失败: {e}")
        return False, {"error": str(e)}
    except Exception as e:
        print(f"   ❌ API爬取异常: {e}")
        return False, {"error": str(e)}

def smart_crawl_with_interaction(config):
    """智能爬取（带用户交互，失败后询问）"""
    print("🧠 启动智能爬取模式（带用户交互）...")
    print("📋 特点: API优先，失败后告知原因并询问是否切换到浏览器")
    
    try:
        # 导入优化的智能选择器
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from scripts.crawler_selector_optimized import QuarkCrawlerSelectorOptimized
        
        # 创建优化选择器
        selector = QuarkCrawlerSelectorOptimized(config)
        
        # 显示状态
        status = selector.get_status()
        print(f"\n📊 选择器状态:")
        print(f"   当前模式: {status.get('current_mode', '未知')}")
        print(f"   API爬取器: {'✅ 已初始化' if status.get('api_crawler_initialized') else '❌ 未初始化'}")
        print(f"   浏览器爬取器: {'✅ 已初始化' if status.get('browser_crawler_initialized') else '❌ 未初始化'}")
        print(f"   输出目录: {status.get('output_dir', '未知')}")
        
        # 执行智能爬取（带用户交互）
        result = selector.smart_crawl_with_user_interaction()
        
        if result.get("success"):
            print(f"\n   ✅ 智能爬取完成!")
            print(f"      模式: {result.get('mode', '未知')}")
            print(f"      获取岗位: {result.get('positions_extracted', 0)} 个")
            print(f"      完成比例: {result.get('completion_percentage', 0):.1f}%")
            print(f"      耗时: {result.get('elapsed_time_seconds', 0):.2f} 秒")
            print(f"      用户交互: {result.get('user_interaction', '无')}")
            
            # 导出数据
            if config.get("output_format") in ["excel", "all"]:
                print(f"\n   📊 导出数据文件...")
                try:
                    from merge_to_excel import merge_to_excel
                    excel_file = merge_to_excel()
                    if excel_file:
                        print(f"   ✅ Excel导出成功: {excel_file}")
                except ImportError:
                    print("   ⚠️  Excel导出模块未找到")
            
            return True, result
        else:
            print(f"\n   ❌ 智能爬取失败")
            print(f"      错误: {result.get('error', '未知错误')}")
            print(f"      模式: {result.get('mode', '未知')}")
            print(f"      用户决策: {result.get('user_decision', '未知')}")
            
            return False, result
    
    except ImportError as e:
        print(f"   ❌ 优化选择器导入失败: {e}")
        print(f"   💡 请确保 scripts/crawler_selector_optimized.py 存在")
        return False, {"error": str(e)}
    except Exception as e:
        print(f"   ❌ 智能爬取异常: {e}")
        return False, {"error": str(e)}

def export_data(format_type="excel"):
    """导出数据"""
    print(f"📤 导出数据 ({format_type.upper()})...")
    
    if format_type == "excel":
        try:
            from merge_to_excel import merge_to_excel
            excel_file = merge_to_excel()
            if excel_file:
                print(f"✅ Excel导出成功: {excel_file}")
                return True
            else:
                print("❌ Excel导出失败")
                return False
        except ImportError:
            print("❌ Excel导出模块未找到")
            return False
    elif format_type == "csv":
        # 这里可以添加CSV导出逻辑
        print("⚠️  CSV导出功能待实现")
        return False
    else:
        print(f"❌ 不支持的导出格式: {format_type}")
        return False

def update_checklist():
    """更新检查清单"""
    print("📋 更新检查清单...")
    
    try:
        # 检查CHECKLIST.md
        if os.path.exists("CHECKLIST.md"):
            with open("CHECKLIST.md", 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含API相关内容
            api_keywords = ["API模式", "CSRF", "Cookie", "pageIndex", "totalCount"]
            missing_keywords = [kw for kw in api_keywords if kw not in content]
            
            if missing_keywords:
                print(f"   ⚠️  检查清单缺少API相关检查项: {missing_keywords}")
                print("   💡 建议运行 check_plugin_compliance.py 进行检查")
            else:
                print("   ✅ 检查清单包含完整的API检查项")
        else:
            print("   ❌ CHECKLIST.md 不存在")
        
        return True
    except Exception as e:
        print(f"   ❌ 更新检查清单失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="夸克校园招聘爬取器 - 统一入口")
    parser.add_argument("--mode", choices=["api", "browser", "smart", "optimized", "status", "export", "check"], 
                       default="optimized", help="运行模式 (optimized推荐: 失败后询问)")
    parser.add_argument("--start", type=int, default=1, help="起始页码")
    parser.add_argument("--end", type=int, default=10, help="结束页码")
    parser.add_argument("--format", choices=["excel", "csv", "json", "all"], 
                       default="excel", help="输出格式")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--auto-switch", action="store_true", 
                       help="失败时自动切换到浏览器 (谨慎使用)")
    
    args = parser.parse_args()
    
    # 打印横幅
    print_banner()
    
    # 检查环境
    check_environment()
    
    # 加载配置
    if args.config and os.path.exists(args.config):
        print(f"📁 使用指定配置文件: {args.config}")
        # 这里可以添加加载指定配置文件的逻辑
        config = load_config()  # 暂时还是使用默认加载
    else:
        config = load_config()
    
    # 更新配置参数
    config["start_page"] = args.start
    config["end_page"] = args.end
    config["output_format"] = args.format
    
    # 根据模式执行
    if args.mode == "status":
        show_status()
    
    elif args.mode == "api":
        print(f"🎯 模式: API爬取 (第{args.start}页到第{args.end}页)")
        success, result = crawl_with_api(config)
        
        if success:
            print(f"\n✅ API爬取任务完成!")
        else:
            print(f"\n❌ API爬取任务失败")
            sys.exit(1)
    
    elif args.mode == "smart":
        print(f"🎯 模式: 智能爬取 (第{args.start}页到第{args.end}页)")
        print(f"💡 注意: 此模式会自动切换，使用 --mode optimized 获得更好的交互体验")
        success, result = smart_crawl(config)
        
        if success:
            print(f"\n✅ 智能爬取任务完成!")
        else:
            print(f"\n❌ 智能爬取任务失败")
            sys.exit(1)
    
    elif args.mode == "optimized":
        print(f"🎯 模式: 优化智能爬取 (第{args.start}页到第{args.end}页)")
        print(f"📋 特点: API优先，失败后告知原因并询问是否切换到浏览器")
        
        if args.auto_switch:
            print(f"⚠️  警告: 启用了自动切换，失败时将自动切换到浏览器")
            print(f"💡 建议: 首次使用时不要使用 --auto-switch，以便了解失败原因")
        
        success, result = smart_crawl_with_interaction(config)
        
        if success:
            print(f"\n✅ 优化智能爬取任务完成!")
        else:
            print(f"\n❌ 优化智能爬取任务失败")
            if not args.auto_switch:
                print(f"💡 建议: 检查失败原因，或使用 --auto-switch 自动切换")
            sys.exit(1)
    
    elif args.mode == "export":
        print(f"🎯 模式: 数据导出 ({args.format})")
        success = export_data(args.format)
        
        if success:
            print(f"\n✅ 数据导出完成!")
        else:
            print(f"\n❌ 数据导出失败")
            sys.exit(1)
    
    elif args.mode == "check":
        print(f"🎯 模式: 规范检查")
        
        # 运行规范检查
        if os.path.exists("check_plugin_compliance.py"):
            os.system("python3 check_plugin_compliance.py")
        else:
            print("❌ check_plugin_compliance.py 不存在")
            update_checklist()
    
    else:
        print(f"❌ 未知模式: {args.mode}")
        parser.print_help()
        sys.exit(1)
    
    # 更新检查清单
    print()
    update_checklist()
    
    # 显示最终状态
    print()
    show_status()
    
    print("=" * 70)
    print("🎉 夸克爬取器执行完成!")
    print("📁 输出目录: output/")
    print("📋 检查清单: CHECKLIST.md")
    print("🧠 记忆状态: memory_checkpoints.json")
    print("=" * 70)

if __name__ == "__main__":
    main()