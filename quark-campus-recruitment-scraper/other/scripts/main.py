#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
夸克校园招聘爬取系统主脚本
使用智能选择器：默认API优先，支持切换到浏览器模式
"""

import sys
import os
import logging
import json
import argparse
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入智能选择器
from scripts.crawler_selector import CrawlerSelector

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    设置日志配置
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径
    """
    # 创建日志目录
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    if not log_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"quark_crawler_{timestamp}.log"
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(log_file), encoding='utf-8')
        ]
    )
    
    logger.info(f"日志配置完成，级别: {log_level}")
    logger.info(f"日志文件: {log_file}")


def load_config(config_path: str = None) -> dict:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    # 默认配置
    default_config = {
        "project": {
            "name": "夸克校园招聘爬取器",
            "version": "2.0",
            "target_positions": 92,
            "categories": [
                "产品类", "运营类", "数据类", "市场拓展", 
                "销售类", "游戏类", "金融类"
            ]
        },
        "crawler": {
            "mode": "auto",  # auto, api, browser, mixed
            "max_pages": 10,
            "page_size": 10,
            "output_dir": "output/positions",
            "backup_dir": "output/backups",
            "retry_times": 3,
            "retry_delay": 2.0
        },
        "api": {
            "enabled": True,
            "url": "https://talent.quark.cn/position/search",
            "categories": "97,103,143,152,124,146,492",
            "timeout": 30
        },
        "browser": {
            "enabled": True,
            "profile": "openclaw",
            "headless": False,
            "timeout": 60
        },
        "quality": {
            "validate_fields": True,
            "required_fields": [
                "position_id", "position_name", "position_category",
                "work_location", "update_time", "department",
                "education_requirement", "work_experience",
                "position_description", "position_requirements"
            ],
            "min_fields_required": 10
        }
    }
    
    # 如果配置文件存在，则尝试加载
    if config_path and os.path.exists(config_path):
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                
            # 深度合并配置
            def deep_merge(base, update):
                for key, value in update.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        deep_merge(base[key], value)
                    else:
                        base[key] = value
                return base
            
            config = deep_merge(default_config, user_config)
            logger.info(f"已加载配置文件: {config_path}")
            
        except Exception as e:
            logger.warning(f"配置文件加载失败，使用默认配置: {str(e)}")
            config = default_config
    else:
        logger.info("使用默认配置")
        config = default_config
    
    return config


def save_result(result: dict, output_dir: str) -> str:
    """
    保存爬取结果
    
    Args:
        result: 爬取结果
        output_dir: 输出目录
        
    Returns:
        保存的文件路径
    """
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quark_crawler_result_{timestamp}.json"
    filepath = output_path / filename
    
    # 保存到文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    logger.info(f"结果已保存到: {filepath}")
    return str(filepath)


def print_summary(result: dict):
    """
    打印结果摘要
    
    Args:
        result: 爬取结果
    """
    print("\n" + "=" * 60)
    print("📊 夸克校园招聘爬取结果摘要")
    print("=" * 60)
    
    if result.get("success"):
        print(f"✅ 状态: 成功")
        print(f"   🎯 模式: {result.get('mode', 'unknown')}")
        print(f"   📋 获取岗位: {result.get('positions_extracted', 0)} 个")
        print(f"   🎯 目标岗位: {result.get('target_positions', 92)} 个")
        
        completion = result.get("completion_percentage", 0)
        if completion >= 95:
            print(f"   📈 完成比例: {completion:.1f}% 🎉")
        elif completion >= 80:
            print(f"   📈 完成比例: {completion:.1f}% 👍")
        else:
            print(f"   📈 完成比例: {completion:.1f}% ⚠️")
        
        print(f"   ⏱️  耗时: {result.get('elapsed_time_seconds', 0):.2f} 秒")
        
        if result.get("save_path"):
            print(f"   💾 保存路径: {result.get('save_path')}")
        
        # 显示性能统计
        stats = result.get("performance_stats", {})
        if stats:
            print(f"   📊 API成功: {stats.get('api_success', 0)} 次")
            print(f"   📊 浏览器成功: {stats.get('browser_success', 0)} 次")
    else:
        print(f"❌ 状态: 失败")
        print(f"   💥 错误: {result.get('error', '未知错误')}")
        print(f"   🎯 模式: {result.get('mode', 'unknown')}")
        print(f"   📋 获取岗位: {result.get('positions_extracted', 0)} 个")
        print(f"   ⏱️  耗时: {result.get('elapsed_time_seconds', 0):.2f} 秒")
    
    print("=" * 60 + "\n")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='夸克校园招聘智能爬取系统')
    parser.add_argument('--mode', choices=['auto', 'api', 'browser', 'mixed'], 
                       default='auto', help='爬取模式 (默认: auto)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='日志级别 (默认: INFO)')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--output', type=str, default='output/positions', 
                       help='输出目录 (默认: output/positions)')
    parser.add_argument('--test', action='store_true', help='测试模式')
    parser.add_argument('--force-browser', action='store_true', 
                       help='强制使用浏览器模式')
    parser.add_argument('--force-api', action='store_true', 
                       help='强制使用API模式')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    
    logger.info("=" * 60)
    logger.info("🚀 夸克校园招聘智能爬取系统启动")
    logger.info("=" * 60)
    logger.info(f"项目根目录: {project_root}")
    logger.info(f"命令行参数: {vars(args)}")
    
    # 加载配置
    config = load_config(args.config)
    
    # 更新输出目录
    if args.output:
        config["crawler"]["output_dir"] = args.output
    
    # 处理强制模式
    if args.force_browser:
        config["crawler"]["mode"] = "browser"
        logger.info("强制使用浏览器模式")
    elif args.force_api:
        config["crawler"]["mode"] = "api"
        logger.info("强制使用API模式")
    
    try:
        # 创建智能选择器
        logger.info("正在初始化智能爬取器选择器...")
        selector = CrawlerSelector(config)
        
        # 显示初始状态
        status = selector.get_status()
        logger.info(f"初始状态: API可用={status['api_available']}, "
                   f"浏览器可用={status['browser_available']}")
        
        # 执行爬取
        result = None
        
        if args.test:
            logger.info("运行测试模式...")
            result = selector.smart_crawl()
        elif config["crawler"]["mode"] == "api":
            logger.info("强制API模式爬取...")
            result = selector.force_mode("api")
        elif config["crawler"]["mode"] == "browser":
            logger.info("强制浏览器模式爬取...")
            result = selector.force_mode("browser")
        elif config["crawler"]["mode"] == "mixed":
            logger.info("强制混合模式爬取...")
            result = selector.force_mode("mixed")
        else:
            logger.info("智能模式爬取...")
            result = selector.smart_crawl()
        
        # 保存结果
        if result:
            # 添加配置信息
            result["config"] = {
                "mode": config["crawler"]["mode"],
                "target_positions": config["project"]["target_positions"],
                "categories": config["project"]["categories"]
            }
            
            # 保存到文件
            save_path = save_result(result, config["crawler"]["output_dir"])
            result["save_path"] = save_path
            
            # 打印摘要
            print_summary(result)
            
            # 返回退出码
            return 0 if result.get("success") else 1
        else:
            logger.error("没有获取到爬取结果")
            return 1
            
    except KeyboardInterrupt:
        logger.warning("用户中断程序")
        return 130
    except Exception as e:
        logger.error(f"程序异常: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())