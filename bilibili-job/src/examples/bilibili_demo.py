#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站爬取器演示
展示如何基于夸克框架创建B站数据爬取器
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src/framework"))

print("=" * 70)
print("🚀 B站数据爬取器演示")
print("=" * 70)

try:
    from framework.smart_crawler_selector import SmartCrawlerSelector
    from framework.unified_crawler_entry import UnifiedCrawlerEntry
    from framework.data_exporter import DataExporter
    
    print("✅ 框架导入成功")
    
    # 演示如何创建B站爬取器
    print("\n🔧 创建B站爬取器步骤:")
    print("1. 继承 SmartCrawlerSelector 实现业务逻辑")
    print("2. 配置 UnifiedCrawlerEntry 作为命令行入口")
    print("3. 使用 DataExporter 导出数据")
    
    # 示例代码
    print("\n📝 示例代码:")
    
    demo_code = '''
class BilibiliCrawler(SmartCrawlerSelector):
    """B站数据爬取器"""
    
    def __init__(self, company_name="bilibili"):
        super().__init__(company_name)
        self.base_url = "https://www.bilibili.com"
        
    def _initialize_primary_crawler(self):
        """初始化API爬取器（首选）"""
        print(f"🎯 初始化B站API爬取器: {self.base_url}")
        # 这里实现B站API爬取逻辑
        return {
            "name": "B站API爬取器",
            "type": "api",
            "status": "ready"
        }
    
    def _initialize_fallback_crawler(self):
        """初始化浏览器爬取器（备选）"""
        print("🔄 初始化B站浏览器爬取器")
        # 这里实现浏览器爬取逻辑
        return {
            "name": "B站浏览器爬取器",
            "type": "browser",
            "status": "ready"
        }
    
    def crawl_jobs(self, max_pages=10):
        """爬取B站岗位数据"""
        print(f"📡 开始爬取B站岗位数据，最多{max_pages}页")
        # 这里实现具体的爬取逻辑
        mock_data = [
            {
                "position_id": "B001",
                "title": "后端开发工程师",
                "location": "上海",
                "category": "技术类",
                "publish_time": "2026-05-22",
                "detail_url": "https://www.bilibili.com/job/001"
            },
            {
                "position_id": "B002",
                "title": "产品经理",
                "location": "北京",
                "category": "产品类",
                "publish_time": "2026-05-21",
                "detail_url": "https://www.bilibili.com/job/002"
            }
        ]
        return mock_data
'''
    
    print(demo_code)
    
    print("\n🎯 运行演示:")
    print("```bash")
    print("# 1. 创建B站爬取器实例")
    print("crawler = BilibiliCrawler('bilibili')")
    print("")
    print("# 2. 使用统一入口")
    print("entry = UnifiedCrawlerEntry(company_name='bilibili')")
    print("")
    print("# 3. 爬取数据")
    print("data = crawler.crawl_jobs(max_pages=2)")
    print("")
    print("# 4. 导出数据")
    print("exporter = DataExporter()")
    print("exporter.export_to_excel(data, 'bilibili_jobs.xlsx')")
    print("```")
    
    # 演示命令行使用
    print("\n💻 命令行使用:")
    print("```bash")
    print("# 查看帮助")
    print("python3 -m src.framework.unified_crawler_entry --help")
    print("")
    print("# API模式运行")
    print("python3 -m src.framework.unified_crawler_entry --company bilibili --mode api")
    print("")
    print("# 浏览器模式运行")
    print("python3 -m src.framework.unified_crawler_entry --company bilibili --mode browser")
    print("")
    print("# 智能模式运行")
    print("python3 -m src.framework.unified_crawler_entry --company bilibili --mode smart")
    print("```")
    
except ImportError as e:
    print(f"❌ 框架导入失败: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")

print("\n" + "=" * 70)
print("📚 下一步:")
print("1. 实现 BilibiliCrawler 的具体业务逻辑")
print("2. 配置 B站API认证信息")
print("3. 测试数据爬取功能")
print("4. 优化错误处理和性能")
print("=" * 70)

if __name__ == "__main__":
    # 这里可以添加实际的演示代码
    print("\n🎬 演示完成！")
    print("现在可以基于这个框架开发B站数据爬取功能了。")