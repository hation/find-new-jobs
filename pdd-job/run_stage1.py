#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段1运行脚本 - 测试PDD基础API爬取
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from crawler.pdd_crawler import PddCrawlerSelector, main

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/pdd_stage1.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查配置文件
    config_files = [
        "config/.env",
        "config/api_auth.json",
        "config/project_config.json"
    ]
    
    for file_path in config_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path} 存在")
        else:
            print(f"   ⚠️  {file_path} 不存在")
    
    # 检查输出目录
    output_dirs = [
        "output",
        "logs",
        "data"
    ]
    
    for dir_path in output_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"   ✅ 目录已创建: {dir_path}")
    
    print("✅ 环境检查完成")


def test_api_connection():
    """测试API连接"""
    print("\n🔐 测试API连接...")
    
    try:
        from crawler.pdd_crawler import PddCrawlerSelector
        
        selector = PddCrawlerSelector()
        success, message, details = selector.test_api_connection()
        
        if success:
            print(f"   ✅ {message}")
            
            # 显示详细信息
            if details and "total_positions" in details:
                print(f"   📊 总岗位数: {details['total_positions']}")
            
            if details and "sample_data" in details and details["sample_data"]:
                sample = details["sample_data"]
                print(f"   📋 样本数据:")
                print(f"      岗位ID: {sample.get('position_id', 'N/A')}")
                print(f"      岗位名称: {sample.get('position_name', 'N/A')}")
                print(f"      工作地点: {sample.get('work_location', 'N/A')}")
                print(f"      岗位类别: {sample.get('position_category', 'N/A')}")
            
            return True, message
        else:
            print(f"   ❌ {message}")
            
            # 显示错误详情
            if details:
                print(f"   🔍 错误详情:")
                for key, value in details.items():
                    print(f"      {key}: {value}")
            
            return False, message
            
    except Exception as e:
        error_msg = f"API连接测试异常: {e}"
        print(f"   ❌ {error_msg}")
        return False, error_msg


def run_small_test():
    """运行小规模测试（1页）"""
    print("\n🧪 运行小规模测试（1页）...")
    
    try:
        from crawler.pdd_crawler import PddCrawlerSelector
        
        selector = PddCrawlerSelector({
            "output_dir": "output/test_small",
            "log_dir": "logs"
        })
        
        result = selector.run_optimized(max_pages=1)
        
        if result["success"]:
            print(f"   ✅ 测试成功!")
            print(f"      获取岗位: {result['positions_count']} 个")
            print(f"      输出文件: {result['output_file']}")
            print(f"      执行时间: {result['execution_time']:.2f}秒")
            
            # 显示样本数据
            if result["output_file"] and os.path.exists(result["output_file"]):
                with open(result["output_file"], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data:
                        sample = data[0]
                        print(f"\n   📋 样本数据验证:")
                        print(f"      岗位ID: {sample.get('position_id', 'N/A')}")
                        print(f"      岗位名称: {sample.get('position_name', 'N/A')}")
                        print(f"      工作地点: {sample.get('work_location', 'N/A')}")
                        print(f"      岗位类别: {sample.get('position_category', 'N/A')}")
                        print(f"      更新时间: {sample.get('update_time_str', 'N/A')}")
                        print(f"      详情链接: {sample.get('detail_url', 'N/A')}")
            
            return True, result
        else:
            print(f"   ❌ 测试失败: {result['error']}")
            return False, result
            
    except Exception as e:
        error_msg = f"小规模测试异常: {e}"
        print(f"   ❌ {error_msg}")
        return False, {"error": error_msg}


def run_full_crawl(max_pages: int = 10):
    """运行完整爬取"""
    print(f"\n🚀 运行完整爬取（最多 {max_pages} 页）...")
    
    try:
        from crawler.pdd_crawler import PddCrawlerSelector
        
        selector = PddCrawlerSelector({
            "output_dir": "output/full_crawl",
            "log_dir": "logs"
        })
        
        result = selector.run_optimized(max_pages=max_pages)
        
        if result["success"]:
            print(f"   ✅ 完整爬取成功!")
            print(f"      获取岗位: {result['positions_count']} 个")
            print(f"      输出文件: {result['output_file']}")
            print(f"      执行时间: {result['execution_time']:.2f}秒")
            
            # 计算平均速度
            if result["execution_time"] > 0:
                speed = result["positions_count"] / result["execution_time"]
                print(f"      平均速度: {speed:.2f} 岗位/秒")
            
            return True, result
        else:
            print(f"   ❌ 完整爬取失败: {result['error']}")
            return False, result
            
    except Exception as e:
        error_msg = f"完整爬取异常: {e}"
        print(f"   ❌ {error_msg}")
        return False, {"error": error_msg}


def create_summary_report(test_results: dict):
    """创建总结报告"""
    print("\n" + "=" * 60)
    print("阶段1测试总结报告")
    print("=" * 60)
    
    timestamp = os.path.basename(test_results.get("output_file", "")).replace("pdd_positions_", "").replace(".json", "")
    
    report = {
        "project": "拼多多招聘爬取器 - 阶段1",
        "timestamp": timestamp,
        "test_results": test_results,
        "environment": {
            "config_files_exist": all(os.path.exists(f) for f in ["config/.env", "config/api_auth.json"]),
            "output_dirs_created": all(os.path.exists(d) for d in ["output", "logs", "data"]),
            "python_version": sys.version
        },
        "recommendations": []
    }
    
    # 显示结果
    if test_results.get("success"):
        print(f"✅ 阶段1测试成功!")
        print(f"   获取岗位数: {test_results.get('positions_count', 0)}")
        print(f"   执行时间: {test_results.get('execution_time', 0):.2f}秒")
        print(f"   输出文件: {test_results.get('output_file', 'N/A')}")
        print(f"   爬取模式: {test_results.get('mode', 'N/A')}")
        
        report["status"] = "success"
        report["recommendations"].append("阶段1基础API爬取功能验证通过")
        report["recommendations"].append("可以开始阶段2开发（详情页获取）")
        
    else:
        print(f"❌ 阶段1测试失败")
        print(f"   错误信息: {test_results.get('error', '未知错误')}")
        
        report["status"] = "failed"
        report["recommendations"].append("需要检查API连接和认证信息")
        report["recommendations"].append("检查配置文件是否正确")
        report["recommendations"].append("可能需要更新Cookie信息")
    
    # 显示环境状态
    print(f"\n🔧 环境状态:")
    print(f"   配置文件: {'✅ 完整' if report['environment']['config_files_exist'] else '⚠️ 缺失'}")
    print(f"   输出目录: {'✅ 已创建' if report['environment']['output_dirs_created'] else '⚠️ 未创建'}")
    print(f"   Python版本: {report['environment']['python_version'].split()[0]}")
    
    # 显示建议
    print(f"\n💡 建议:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"   {i}. {rec}")
    
    # 保存报告
    report_file = f"output/stage1_report_{timestamp if timestamp else 'unknown'}.json"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 报告已保存: {report_file}")
    print("=" * 60)
    
    return report


def interactive_menu():
    """交互式菜单"""
    print("\n" + "=" * 60)
    print("拼多多招聘爬取器 - 阶段1 测试菜单")
    print("=" * 60)
    print("1. 检查环境配置")
    print("2. 测试API连接")
    print("3. 运行小规模测试（1页）")
    print("4. 运行完整爬取（10页）")
    print("5. 运行完整爬取（自定义页数）")
    print("6. 运行所有测试")
    print("7. 退出")
    print("=" * 60)
    
    while True:
        try:
            choice = input("请选择操作 (1-7): ").strip()
            
            if choice == "1":
                check_environment()
                return True
                
            elif choice == "2":
                success, message = test_api_connection()
                return success
                
            elif choice == "3":
                success, result = run_small_test()
                if success:
                    create_summary_report(result)
                return success
                
            elif choice == "4":
                success, result = run_full_crawl(max_pages=10)
                if success:
                    create_summary_report(result)
                return success
                
            elif choice == "5":
                try:
                    pages = int(input("请输入最大页数: ").strip())
                    if pages <= 0:
                        print("⚠️ 页数必须大于0")
                        continue
                    success, result = run_full_crawl(max_pages=pages)
                    if success:
                        create_summary_report(result)
                    return success
                except ValueError:
                    print("⚠️ 请输入有效的数字")
                    
            elif choice == "6":
                print("\n🔧 运行所有测试...")
                
                # 1. 检查环境
                check_environment()
                
                # 2. 测试API连接
                api_success, api_message = test_api_connection()
                if not api_success:
                    print("❌ API连接测试失败，停止测试")
                    return False
                
                # 3. 小规模测试
                test_success, test_result = run_small_test()
                if not test_success:
                    print("❌ 小规模测试失败，停止测试")
                    return False
                
                # 4. 完整爬取
                full_success, full_result = run_full_crawl(max_pages=5)  # 先测试5页
                
                # 创建报告
                create_summary_report(full_result)
                
                return full_success
                
            elif choice == "7":
                print("👋 退出程序")
                return True
                
            else:
                print("⚠️ 无效的选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n👋 用户中断，退出程序")
            return False
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            return False


def main():
    """主函数"""
    print("拼多多招聘爬取器 - 阶段1 测试工具")
    print("版本: 1.0.0")
    print("描述: 测试基础API爬取功能")
    print("=" * 60)
    
    # 创建必要目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    # 运行交互式菜单
    success = interactive_menu()
    
    if success:
        print("\n✅ 测试完成")
        return 0
    else:
        print("\n❌ 测试失败")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)