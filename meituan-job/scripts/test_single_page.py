#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美团招聘单页爬取测试脚本
按照夸克项目规范：先进行单页测试验证实际功能
核心经验：永远相信页面显示，不是URL参数
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Any, Optional

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from src.meituan_crawler import MeituanCrawler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MeituanSinglePageTester:
    """美团单页测试器"""
    
    def __init__(self):
        self.crawler = MeituanCrawler()
        self.test_results = {
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "company": self.crawler.company_name,
            "city": "深圳",
            "categories": list(self.crawler.category_mapping.values()),
            "tests": {}
        }
    
    def test_page_access(self) -> bool:
        """测试页面访问"""
        print("=" * 60)
        print("🌐 测试1: 页面访问测试")
        print("=" * 60)
        
        try:
            import requests
            
            # 测试URL
            test_url = f"{self.crawler.filter_url}?cityList={self.crawler.city_code}&jfJgList={self.crawler.category_codes}"
            print(f"📄 测试URL: {test_url}")
            
            # 发送请求
            response = requests.get(test_url, timeout=10)
            print(f"📊 响应状态: {response.status_code}")
            print(f"📏 响应大小: {len(response.text)} 字节")
            
            # 检查响应类型
            content_type = response.headers.get('content-type', '')
            print(f"📋 内容类型: {content_type}")
            
            # 分析响应内容
            if response.status_code == 200:
                if 'application/json' in content_type:
                    print("✅ 页面返回JSON格式")
                    try:
                        data = response.json()
                        print(f"📊 JSON结构: {type(data)}")
                        if isinstance(data, dict):
                            print(f"📋 JSON字段: {list(data.keys())}")
                    except:
                        print("⚠️ JSON解析失败，可能是HTML伪装成JSON")
                elif 'text/html' in content_type:
                    print("✅ 页面返回HTML格式")
                    # 检查是否包含岗位信息
                    if '岗位' in response.text or '职位' in response.text:
                        print("✅ 页面包含岗位信息")
                    else:
                        print("⚠️ 页面可能不包含岗位信息")
                else:
                    print(f"⚠️ 未知内容类型: {content_type}")
                
                self.test_results["tests"]["page_access"] = {
                    "status": "success",
                    "url": test_url,
                    "status_code": response.status_code,
                    "content_type": content_type,
                    "size_bytes": len(response.text)
                }
                return True
            else:
                print(f"❌ 页面访问失败: HTTP {response.status_code}")
                self.test_results["tests"]["page_access"] = {
                    "status": "failed",
                    "url": test_url,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
                return False
                
        except Exception as e:
            print(f"❌ 页面访问异常: {str(e)}")
            self.test_results["tests"]["page_access"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def test_browser_launch(self) -> bool:
        """测试浏览器启动"""
        print("\n" + "=" * 60)
        print("🖥️ 测试2: 浏览器启动测试")
        print("=" * 60)
        
        try:
            # 尝试导入Playwright
            from playwright.sync_api import sync_playwright
            
            print("🔧 尝试启动浏览器...")
            
            with sync_playwright() as p:
                # 启动浏览器
                browser = p.chromium.launch(headless=False, timeout=30000)
                print("✅ 浏览器启动成功")
                
                # 创建页面
                page = browser.new_page()
                print("✅ 页面创建成功")
                
                # 设置视口
                page.set_viewport_size({"width": 1920, "height": 1080})
                print("✅ 视口设置成功")
                
                # 设置User-Agent
                user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                page.set_extra_http_headers({"User-Agent": user_agent})
                print("✅ User-Agent设置成功")
                
                # 测试访问美团首页
                test_url = "https://zhaopin.meituan.com"
                print(f"🌐 测试访问: {test_url}")
                
                page.goto(test_url, timeout=30000)
                print(f"✅ 页面加载成功，标题: {page.title()[:50]}...")
                
                # 截图保存
                screenshot_path = "test_browser_screenshot.png"
                page.screenshot(path=screenshot_path)
                print(f"📸 截图保存: {screenshot_path}")
                
                # 关闭浏览器
                browser.close()
                print("🛑 浏览器关闭成功")
                
                self.test_results["tests"]["browser_launch"] = {
                    "status": "success",
                    "screenshot": screenshot_path,
                    "page_title": page.title()
                }
                return True
                
        except ImportError:
            print("❌ Playwright未安装")
            print("💡 请运行: pip install playwright && python -m playwright install")
            self.test_results["tests"]["browser_launch"] = {
                "status": "failed",
                "error": "Playwright未安装"
            }
            return False
            
        except Exception as e:
            print(f"❌ 浏览器启动异常: {str(e)}")
            self.test_results["tests"]["browser_launch"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def test_single_page_crawl(self) -> bool:
        """测试单页爬取"""
        print("\n" + "=" * 60)
        print("🕷️ 测试3: 单页爬取测试")
        print("=" * 60)
        
        try:
            print("🚀 启动单页爬取...")
            
            # 使用爬取器进行单页爬取
            url = f"{self.crawler.filter_url}?cityList={self.crawler.city_code}&jfJgList={self.crawler.category_codes}"
            positions = self.crawler.crawl_with_browser(url)
            
            if positions:
                print(f"✅ 爬取成功，获取到 {len(positions)} 个岗位")
                
                # 显示第一个岗位的详细信息
                if positions:
                    first_position = positions[0]
                    print("\n📋 第一个岗位详情:")
                    for key, value in first_position.items():
                        if value:  # 只显示有值的字段
                            print(f"  {key}: {value}")
                
                # 保存测试数据
                test_filename = f"single_page_test_{int(time.time())}.json"
                self.crawler.save_positions(positions, test_filename)
                
                # 数据质量分析
                quality_report = self.analyze_data_quality(positions)
                print(f"\n📊 数据质量报告:")
                print(f"  总岗位数: {quality_report['total_positions']}")
                print(f"  完整字段数: {quality_report['complete_fields']}")
                print(f"  数据完整度: {quality_report['completeness_rate']:.1f}%")
                
                self.test_results["tests"]["single_page_crawl"] = {
                    "status": "success",
                    "positions_count": len(positions),
                    "data_file": test_filename,
                    "quality_report": quality_report
                }
                return True
            else:
                print("⚠️ 爬取成功但未获取到岗位数据")
                print("💡 可能原因:")
                print("  1. 页面结构已变更")
                print("  2. 筛选条件无结果")
                print("  3. 数据提取逻辑需要调整")
                
                self.test_results["tests"]["single_page_crawl"] = {
                    "status": "partial",
                    "positions_count": 0,
                    "note": "爬取成功但无数据"
                }
                return False
                
        except Exception as e:
            print(f"❌ 单页爬取异常: {str(e)}")
            self.test_results["tests"]["single_page_crawl"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def analyze_data_quality(self, positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析数据质量"""
        if not positions:
            return {
                "total_positions": 0,
                "complete_fields": 0,
                "completeness_rate": 0
            }
        
        # 必填字段列表
        required_fields = list(self.crawler.field_mapping.keys())
        
        # 统计完整度
        complete_count = 0
        field_stats = {}
        
        for position in positions:
            complete_fields = 0
            for field in required_fields:
                if field in position and position[field]:
                    complete_fields += 1
                    field_stats[field] = field_stats.get(field, 0) + 1
            
            if complete_fields == len(required_fields):
                complete_count += 1
        
        # 计算完整度
        completeness_rate = (complete_count / len(positions)) * 100 if positions else 0
        
        # 字段完整度统计
        field_completeness = {}
        for field in required_fields:
            count = field_stats.get(field, 0)
            field_completeness[field] = {
                "count": count,
                "rate": (count / len(positions)) * 100 if positions else 0
            }
        
        return {
            "total_positions": len(positions),
            "complete_positions": complete_count,
            "complete_fields": sum(field_stats.values()),
            "completeness_rate": completeness_rate,
            "field_stats": field_completeness
        }
    
    def test_pagination_logic(self) -> bool:
        """测试分页逻辑（夸克核心经验）"""
        print("\n" + "=" * 60)
        print("📖 测试4: 分页逻辑测试（夸克核心经验）")
        print("=" * 60)
        
        print("🎯 夸克项目核心经验:")
        print("  1. 永远相信页面显示，不是URL参数")
        print("  2. 每次操作前验证筛选状态")
        print("  3. 每个岗位提取后立即保存")
        print("  4. 使用检查清单防止重复犯错")
        
        print("\n🔍 美团分页分析:")
        print("  需要手动访问美团招聘网站，观察:")
        print("  1. 分页控件位置和样式")
        print("  2. 当前页码显示位置")
        print("  3. 总页数显示位置")
        print("  4. 上一页/下一页按钮")
        
        print("\n💡 测试步骤:")
        print("  1. 手动访问: https://zhaopin.meituan.com/web/social")
        print("  2. 应用筛选条件")
        print("  3. 观察分页显示")
        print("  4. 点击下一页，观察URL变化")
        
        # 这里只能提供指导，实际需要手动测试
        self.test_results["tests"]["pagination_logic"] = {
            "status": "manual_test_required",
            "note": "需要手动测试分页逻辑",
            "core_experience": [
                "永远相信页面显示，不是URL参数",
                "验证筛选状态持久性",
                "实时保存提取的数据"
            ]
        }
        
        return True  # 返回True，因为这是指导性测试
    
    def save_test_report(self):
        """保存测试报告"""
        report_file = os.path.join(self.crawler.output_dir, "single_page_test_report.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📋 测试报告已保存: {report_file}")
        return report_file
    
    def generate_summary(self):
        """生成测试总结"""
        print("\n" + "=" * 60)
        print("📊 单页测试总结")
        print("=" * 60)
        
        passed = 0
        total = 0
        
        for test_name, result in self.test_results["tests"].items():
            total += 1
            status = result.get("status", "unknown")
            
            if status == "success":
                passed += 1
                print(f"✅ {test_name}: 通过")
            elif status == "partial":
                print(f"⚠️ {test_name}: 部分通过")
            elif status == "manual_test_required":
                print(f"📝 {test_name}: 需要手动测试")
            else:
                print(f"❌ {test_name}: 失败")
        
        print(f"\n📈 测试通过率: {passed}/{total}")
        
        if passed == total:
            print("\n🎉 所有自动测试通过！")
            print("💡 下一步建议:")
            print("  1. 手动测试分页逻辑")
            print("  2. 验证数据准确性")
            print("  3. 进行多页爬取测试")
        else:
            print(f"\n⚠️ 有 {total - passed} 个测试需要关注")
            print("💡 建议先修复失败的项目")
        
        return passed == total


def main():
    """主函数"""
    print("🚀 美团招聘单页爬取测试")
    print("按照夸克项目规范：先单页测试，验证实际功能")
    print("=" * 60)
    
    tester = MeituanSinglePageTester()
    
    # 运行测试
    tester.test_page_access()
    tester.test_browser_launch()
    tester.test_single_page_crawl()
    tester.test_pagination_logic()
    
    # 保存报告和总结
    report_file = tester.save_test_report()
    all_passed = tester.generate_summary()
    
    print("\n" + "=" * 60)
    print("🎯 按照夸克规范，下一步行动:")
    
    if all_passed:
        print("1. ✅ 单页测试通过，可以进行多页测试")
        print("2. 📝 手动验证分页逻辑（关键！）")
        print("3. 🔧 根据实际页面调整数据提取逻辑")
        print("4. 🚀 开始完整爬取")
    else:
        print("1. 🔧 修复失败的测试项目")
        print("2. 🔍 查看详细错误信息")
        print("3. 📋 参考检查清单逐项排查")
        print("4. 🔄 重新运行单页测试")
    
    print("=" * 60)
    
    # 显示测试报告位置
    print(f"\n📁 测试文件位置: output/crawl_data/")
    print(f"📋 详细报告: {report_file}")
    
    return all_passed


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)