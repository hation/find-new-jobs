#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单浏览器自动化爬取 - 维持会话获取多页数据
"""

import os
import json
import time
import logging
from datetime import datetime

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleBrowserCrawler:
    """简单浏览器爬取器"""
    
    def __init__(self, headless=False):
        """
        初始化
        
        Args:
            headless: 是否无头模式（默认False，显示浏览器）
        """
        self.website_url = "https://careers.pddglobalhr.com/jobs"
        self.headless = headless
        self.driver = None
        
        # 输出目录
        self.output_dir = "output/pdd_browser_simple"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 数据存储
        self.all_positions = []
        
        logger.info("🚀 简单浏览器爬取器初始化")
        logger.info(f"   显示浏览器: {'否' if headless else '是'}")
    
    def setup_browser(self):
        """设置浏览器（显示窗口）"""
        try:
            logger.info("🌐 设置Chrome浏览器...")
            
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # 基本参数
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1400,900")
            
            # 排除自动化标志
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 用户代理
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")
            
            # 禁用自动化特征
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # 安装并启动
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 隐藏webdriver属性
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ 浏览器设置完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 浏览器设置失败: {e}")
            return False
    
    def close_browser(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✅ 浏览器已关闭")
            except Exception as e:
                logger.error(f"❌ 关闭浏览器失败: {e}")
    
    def navigate_and_wait(self):
        """导航到网站并等待加载"""
        try:
            logger.info(f"🌐 访问网站: {self.website_url}")
            self.driver.get(self.website_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 等待更多内容
            time.sleep(5)
            
            logger.info("✅ 页面加载完成")
            
            # 显示页面标题
            title = self.driver.title
            logger.info(f"   页面标题: {title}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 访问网站失败: {e}")
            return False
    
    def extract_visible_positions(self):
        """提取页面可见的岗位数据"""
        logger.info("🔍 提取页面可见的岗位数据...")
        
        try:
            # 查找岗位列表容器
            containers = self.driver.find_elements(By.CSS_SELECTOR, 
                "[class*='job'], [class*='position'], [class*='list'], [class*='item'], [class*='card']")
            
            positions = []
            
            for container in containers[:50]:  # 检查前50个元素
                try:
                    # 尝试提取文本
                    text = container.text.strip()
                    if text and len(text) > 20:  # 有足够内容
                        # 尝试解析
                        lines = text.split('\n')
                        if len(lines) >= 2:
                            position = {
                                "visible_text": text,
                                "line_count": len(lines),
                                "first_line": lines[0] if lines else "",
                                "second_line": lines[1] if len(lines) > 1 else ""
                            }
                            positions.append(position)
                            
                            if len(positions) <= 3:  # 只显示前3个
                                logger.info(f"   找到岗位: {lines[0][:50]}...")
                except:
                    continue
            
            logger.info(f"✅ 找到 {len(positions)} 个可能的岗位元素")
            return positions
            
        except Exception as e:
            logger.error(f"❌ 提取数据失败: {e}")
            return []
    
    def scroll_and_load_more(self, max_scrolls=10):
        """滚动页面加载更多数据"""
        logger.info(f"📜 滚动页面加载更多数据 (最多{max_scrolls}次)...")
        
        previous_height = self.driver.execute_script("return document.body.scrollHeight")
        positions_count = 0
        
        for i in range(max_scrolls):
            logger.info(f"   滚动 {i+1}/{max_scrolls}...")
            
            # 滚动到底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # 等待加载
            
            # 检查新内容
            current_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if current_height == previous_height:
                logger.info("   没有更多内容，停止滚动")
                break
            
            previous_height = current_height
            
            # 提取当前可见数据
            positions = self.extract_visible_positions()
            if positions:
                positions_count = len(positions)
                logger.info(f"   当前可见岗位: {positions_count} 个")
            
            # 短暂延迟
            time.sleep(2)
        
        logger.info(f"✅ 滚动完成，最后可见岗位: {positions_count} 个")
        return positions_count
    
    def take_screenshot(self, name="page_screenshot"):
        """截取页面截图"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            self.driver.save_screenshot(filepath)
            logger.info(f"📸 截图保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ 截图失败: {e}")
            return None
    
    def get_page_source(self):
        """获取页面源代码"""
        try:
            source = self.driver.page_source
            
            # 保存源代码
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"page_source_{timestamp}.html"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(source)
            
            logger.info(f"📄 页面源代码保存: {filepath}")
            
            # 分析源代码中的API相关信息
            self.analyze_source_for_api(source)
            
            return source
            
        except Exception as e:
            logger.error(f"❌ 获取源代码失败: {e}")
            return None
    
    def analyze_source_for_api(self, source):
        """分析源代码中的API信息"""
        logger.info("🔍 分析源代码中的API信息...")
        
        # 查找可能的API端点
        import re
        
        # 查找API URL模式
        api_patterns = [
            r'/api/[^\s"\']+',
            r'/recruit/[^\s"\']+',
            r'position/[^\s"\']+',
            r'list[^\s"\']*',
            r'anti[_\s-]*content',
            r'pageSize[^\s"\']*'
        ]
        
        found_items = []
        
        for pattern in api_patterns:
            matches = re.findall(pattern, source, re.IGNORECASE)
            if matches:
                for match in matches[:5]:  # 只取前5个
                    if match not in found_items:
                        found_items.append(match)
        
        if found_items:
            logger.info("✅ 找到API相关信息:")
            for item in found_items[:10]:  # 只显示前10个
                logger.info(f"   • {item}")
        
        # 查找JavaScript中的相关代码
        js_pattern = r'<script[^>]*>([\s\S]*?)</script>'
        js_matches = re.findall(js_pattern, source)
        
        if js_matches:
            logger.info(f"✅ 找到 {len(js_matches)} 个script标签")
            
            # 查找包含anti_content的script
            for i, js in enumerate(js_matches[:3]):  # 只检查前3个
                if 'anti' in js.lower() or 'content' in js.lower():
                    logger.info(f"   📋 Script {i+1} 可能包含anti_content相关代码")
                    # 提取相关行
                    lines = js.split('\n')
                    for line in lines:
                        if 'anti' in line.lower():
                            logger.info(f"      {line.strip()[:100]}...")
    
    def export_visible_data(self):
        """导出可见数据到Excel"""
        logger.info("📤 导出可见数据到Excel...")
        
        # 获取页面标题
        title = self.driver.title if self.driver else "PDD招聘"
        
        # 获取当前URL
        url = self.driver.current_url if self.driver else self.website_url
        
        # 获取页面文本
        page_text = self.driver.find_element(By.TAG_NAME, 'body').text if self.driver else ""
        
        # 创建数据
        data = {
            "页面标题": [title],
            "页面URL": [url],
            "爬取时间": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "浏览器模式": ["Selenium自动化"],
            "数据状态": ["页面可见数据"],
            "页面文本长度": [len(page_text)]
        }
        
        # 添加更多信息
        try:
            # 获取所有链接
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            data["链接数量"] = [len(links)]
            
            # 获取所有图片
            images = self.driver.find_elements(By.TAG_NAME, 'img')
            data["图片数量"] = [len(images)]
            
        except:
            data["链接数量"] = ["无法获取"]
            data["图片数量"] = ["无法获取"]
        
        # 导出到Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"pdd_browser_data_{timestamp}.xlsx"
        excel_filepath = os.path.join(self.output_dir, excel_filename)
        
        try:
            df = pd.DataFrame(data)
            df.to_excel(excel_filepath, index=False)
            
            file_size = os.path.getsize(excel_filepath)
            logger.info(f"✅ Excel导出成功!")
            logger.info(f"   文件: {excel_filepath}")
            logger.info(f"   大小: {file_size:,} 字节")
            logger.info(f"   数据: {len(data)} 个字段")
            
            return excel_filepath
            
        except Exception as e:
            logger.error(f"❌ Excel导出失败: {e}")
            return None
    
    def run(self):
        """运行完整流程"""
        print("\n" + "="*70)
        print("🚀 简单浏览器自动化PDD爬取 - 开始执行")
        print("="*70)
        
        start_time = time.time()
        
        try:
            # 1. 设置浏览器
            print("\n🌐 阶段1: 设置浏览器...")
            if not self.setup_browser():
                print("❌ 浏览器设置失败")
                return False
            
            # 2. 导航到网站
            print("\n🌐 阶段2: 访问网站...")
            if not self.navigate_and_wait():
                print("❌ 访问网站失败")
                self.close_browser()
                return False
            
            # 3. 截取初始截图
            print("\n📸 阶段3: 截取初始页面...")
            screenshot1 = self.take_screenshot("initial_page")
            if screenshot1:
                print(f"✅ 截图保存: {screenshot1}")
            
            # 4. 获取页面源代码
            print("\n📄 阶段4: 分析页面源代码...")
            source = self.get_page_source()
            
            # 5. 滚动加载更多
            print("\n📜 阶段5: 滚动加载更多内容...")
            positions_count = self.scroll_and_load_more(max_scrolls=5)
            
            # 6. 截取滚动后截图
            print("\n📸 阶段6: 截取滚动后页面...")
            screenshot2 = self.take_screenshot("scrolled_page")
            if screenshot2:
                print(f"✅ 截图保存: {screenshot2}")
            
            # 7. 导出数据
            print("\n📤 阶段7: 导出数据...")
            excel_file = self.export_visible_data()
            
            # 8. 关闭浏览器
            print("\n🌐 阶段8: 关闭浏览器...")
            self.close_browser()
            
            # 9. 生成报告
            total_time = time.time() - start_time
            
            print("\n" + "="*70)
            print("🎯 浏览器自动化完成报告")
            print("="*70)
            print(f"✅ 状态: 成功")
            print(f"⏱️  用时: {total_time:.2f} 秒")
            
            if excel_file:
                print(f"📁 Excel文件: {excel_file}")
            
            if screenshot1:
                print(f"📸 初始截图: {screenshot1}")
            
            if screenshot2:
                print(f"📸 滚动后截图: {screenshot2}")
            
            print(f"📂 输出目录: {self.output_dir}")
            print("="*70)
            
            print(f"\n📋 收集的信息:")
            print(f"   1. 页面源代码 (包含可能的API信息)")
            print(f"   2. 页面截图 (可视化验证)")
            print(f"   3. Excel数据文件 (元数据)")
            print(f"   4. 页面分析结果")
            
            print(f"\n💡 下一步:")
            print(f"   1. 分析页面源代码中的API信息")
            print(f"   2. 查找anti_content的生成逻辑")
            print(f"   3. 基于分析实现自动化API调用")
            
            return True
            
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 确保浏览器被关闭
            self.close_browser()
            
            return False

def main():
    """主函数"""
    print("简单浏览器自动化PDD数据收集工具")
    print("="*70)
    print("使用Selenium收集页面信息，分析API结构")
    print("="*70)
    
    # 配置参数
    headless = False  # 显示浏览器窗口，方便调试
    
    print(f"\n🚀 配置参数:")
    print(f"   显示浏览器窗口: {'是' if not headless else '否'}")
    print(f"   注意: 浏览器窗口将显示，请勿关闭")
    print("="*70)
    
    # 创建爬取器并运行
    crawler = SimpleBrowserCrawler(headless=headless)
    success = crawler.run()
    
    if success:
        print("\n✅ 浏览器数据收集完成!")
        print("\n📋 输出文件在: output/pdd_browser_simple/")
        print("   包含: 页面源代码、截图、Excel数据")
        return 0
    else:
        print("\n❌ 数据收集失败")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())