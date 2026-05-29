#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动浏览器爬取器 - 无需用户输入
"""

import os
import json
import time
import logging
from datetime import datetime

import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoBrowserPddCrawler:
    """自动浏览器爬取器"""
    
    def __init__(self):
        """初始化"""
        self.base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
        self.website_url = "https://careers.pddglobalhr.com/jobs"
        self.driver = None
        self.session = requests.Session()
        self.output_dir = "output/pdd_auto_browser"
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("🚀 自动浏览器爬取器初始化完成")
    
    def setup_browser(self):
        """设置无头浏览器"""
        try:
            logger.info("🌐 设置无头Chrome浏览器...")
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")
            
            # 安装并启动浏览器
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
    
    def get_anti_content_simple(self):
        """简单方法获取anti_content"""
        logger.info("🔍 尝试获取anti_content参数...")
        
        if not self.driver:
            return None
        
        try:
            # 访问网站
            logger.info(f"🌐 访问: {self.website_url}")
            self.driver.get(self.website_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info("✅ 页面加载完成")
            
            # 等待API请求
            logger.info("⏳ 等待API请求...")
            time.sleep(5)
            
            # 方法1: 从网络请求中提取
            logger.info("📡 尝试从网络请求提取...")
            
            # 执行JavaScript获取所有请求
            script = """
            // 监听所有fetch请求
            const originalFetch = window.fetch;
            window.interceptedData = null;
            
            window.fetch = function(...args) {
                const url = args[0];
                const options = args[1] || {};
                
                if (url && url.includes('/recruit/position/list')) {
                    console.log('捕获到API请求:', url);
                    
                    // 检查请求头
                    if (options.headers && options.headers['Anti-Content']) {
                        window.interceptedData = {
                            type: 'header',
                            anti_content: options.headers['Anti-Content']
                        };
                    }
                    
                    // 检查请求体
                    if (options.body) {
                        try {
                            const body = JSON.parse(options.body);
                            if (body.anti_content) {
                                window.interceptedData = {
                                    type: 'body',
                                    anti_content: body.anti_content
                                };
                            }
                        } catch(e) {}
                    }
                }
                
                return originalFetch.apply(this, args);
            };
            
            // 触发页面加载更多数据
            setTimeout(() => {
                // 尝试滚动触发加载
                window.scrollTo(0, document.body.scrollHeight);
                
                // 尝试查找并点击分页按钮
                const buttons = document.querySelectorAll('[class*="page"], [class*="pagination"] button, button[class*="next"]');
                if (buttons.length > 0) {
                    console.log('找到分页按钮，尝试点击...');
                    buttons[0].click();
                }
            }, 2000);
            
            return '监听器已设置';
            """
            
            self.driver.execute_script(script)
            
            # 等待更多时间让请求发生
            logger.info("⏳ 等待请求发生...")
            time.sleep(8)
            
            # 获取拦截到的数据
            intercepted = self.driver.execute_script("return window.interceptedData;")
            
            if intercepted and intercepted.get("anti_content"):
                anti_content = intercepted["anti_content"]
                logger.info(f"✅ 成功获取anti_content参数 ({intercepted['type']}): {anti_content[:50]}...")
                return anti_content
            
            # 方法2: 从localStorage获取
            logger.info("🔄 尝试从localStorage获取...")
            try:
                localStorage = self.driver.execute_script("return JSON.stringify(window.localStorage);")
                if "anti" in localStorage.lower():
                    logger.info("✅ localStorage中包含anti相关数据")
                    # 这里可以进一步解析
            except:
                pass
            
            # 方法3: 直接尝试调用API
            logger.info("🔄 尝试直接调用API...")
            
            # 获取cookies
            cookies = self.driver.get_cookies()
            cookies_dict = {c['name']: c['value'] for c in cookies}
            
            # 查找_nano_fp
            nano_fp = cookies_dict.get('_nano_fp', '')
            if nano_fp:
                logger.info(f"✅ 找到_nano_fp: {nano_fp[:50]}...")
            
            # 尝试调用API
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Content-Type": "application/json",
                "Origin": "https://careers.pddglobalhr.com",
                "Referer": "https://careers.pddglobalhr.com/jobs",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Cookie": f"_nano_fp={nano_fp}"
            }
            
            payload = {"page": 1, "pageSize": 10}
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    logger.info("✅ API调用成功（可能不需要anti_content）")
                    return ""  # 空字符串表示不需要
                else:
                    error_code = data.get("errorCode")
                    error_msg = data.get("errorMsg", "未知错误")
                    logger.warning(f"⚠️ API错误: {error_code} - {error_msg}")
            
            logger.error("❌ 所有方法都失败")
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取失败: {e}")
            return None
    
    def fetch_data(self, anti_content, max_pages=5):
        """获取数据"""
        all_positions = []
        
        # 准备请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "Origin": "https://careers.pddglobalhr.com",
            "Referer": "https://careers.pddglobalhr.com/jobs",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Cookie": "_nano_fp=Xpm8lpgJn0EjXqdaXo_eBA4AmspK5Wx4Oawm5ox~"
        }
        
        # 添加anti_content到请求头
        if anti_content:
            headers["Anti-Content"] = anti_content
        
        def fetch_page(page):
            payload = {"page": page, "pageSize": 10}
            if anti_content and anti_content != "":
                payload["anti_content"] = anti_content
            
            try:
                logger.info(f"📥 获取第 {page} 页...")
                
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ HTTP错误: {response.status_code}")
                    return None
                
                data = response.json()
                
                if not data.get("success", False):
                    error_code = data.get("errorCode")
                    error_msg = data.get("errorMsg", "未知错误")
                    logger.error(f"❌ API错误: {error_code} - {error_msg}")
                    return None
                
                result = data.get("result", {})
                positions = result.get("list", [])
                total = result.get("total", 0)
                
                logger.info(f"   ✅ 获取 {len(positions)} 条，总计 {total} 条")
                
                return positions, total
                
            except Exception as e:
                logger.error(f"❌ 获取失败: {e}")
                return None
        
        # 获取第一页
        first_result = fetch_page(1)
        if not first_result:
            return []
        
        positions, total = first_result
        all_positions.extend(positions)
        
        # 计算总页数
        total_pages = (int(total) + 9) // 10
        pages_to_fetch = min(total_pages, max_pages)
        
        logger.info(f"📊 总页数: {total_pages}, 爬取: {pages_to_fetch} 页")
        
        # 获取剩余页
        for page in range(2, pages_to_fetch + 1):
            result = fetch_page(page)
            if result:
                page_positions, _ = result
                all_positions.extend(page_positions)
            else:
                logger.warning(f"⚠️ 第 {page} 页失败，跳过")
            
            time.sleep(1)
        
        logger.info(f"✅ 共获取 {len(all_positions)} 条记录")
        return all_positions
    
    def process_and_export(self, positions):
        """处理并导出数据"""
        if not positions:
            logger.warning("⚠️ 没有数据需要导出")
            return None
        
        # 处理数据
        processed = []
        for pos in positions:
            processed.append({
                "岗位ID": pos.get("code", ""),
                "岗位名称": pos.get("name", ""),
                "工作地点": pos.get("workLocation", ""),
                "岗位类别": pos.get("job", ""),
                "更新时间": pos.get("updateTime", ""),
                "更新时间戳": pos.get("updateDate", 0),
                "详情页URL": f"https://careers.pddglobalhr.com/jobs/{pos.get('code', '')}",
                "爬取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # 导出到Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = os.path.join(self.output_dir, f"pdd_positions_{timestamp}.xlsx")
        
        try:
            df = pd.DataFrame(processed)
            
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='所有岗位', index=False)
                
                if '工作地点' in df.columns:
                    location_stats = df['工作地点'].value_counts().reset_index()
                    location_stats.columns = ['工作地点', '岗位数量']
                    location_stats.to_excel(writer, sheet_name='地点分布', index=False)
            
            file_size = os.path.getsize(excel_file)
            logger.info(f"✅ Excel导出成功: {excel_file} ({file_size:,} 字节)")
            
            return excel_file
            
        except Exception as e:
            logger.error(f"❌ 导出失败: {e}")
            return None
    
    def run(self):
        """运行完整流程"""
        print("\n" + "="*60)
        print("🚀 自动浏览器PDD爬取 - 开始执行")
        print("="*60)
        
        start_time = time.time()
        
        try:
            # 1. 设置浏览器
            if not self.setup_browser():
                return False
            
            # 2. 获取anti_content
            print("\n🔍 获取anti_content参数...")
            anti_content = self.get_anti_content_simple()
            
            # 3. 关闭浏览器
            self.close_browser()
            
            if anti_content is None:
                print("❌ 无法获取anti_content")
                return False
            
            print(f"✅ 获取到参数: {'(空，可能不需要)' if anti_content == '' else anti_content[:50] + '...'}")
            
            # 4. 获取数据
            print("\n📥 获取岗位数据...")
            positions = self.fetch_data(anti_content, max_pages=3)  # 先测试3页
            
            if not positions:
                print("❌ 没有获取到数据")
                return False
            
            # 5. 导出数据
            print("\n📤 导出数据到Excel...")
            excel_file = self.process_and_export(positions)
            
            if not excel_file:
                print("❌ 导出失败")
                return False
            
            # 6. 完成报告
            total_time = time.time() - start_time
            
            print("\n" + "="*60)
            print("🎯 任务完成!")
            print("="*60)
            print(f"✅ 状态: 成功")
            print(f"⏱️  用时: {total_time:.2f} 秒")
            print(f"📊 记录数: {len(positions)} 条")
            print(f"📁 Excel文件: {excel_file}")
            print(f"📂 输出目录: {self.output_dir}")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主函数"""
    print("自动浏览器PDD爬取器")
    print("="*60)
    print("自动获取anti_content并爬取数据")
    print("="*60)
    
    crawler = AutoBrowserPddCrawler()
    success = crawler.run()
    
    if success:
        print("\n✅ 任务完成!")
        return 0
    else:
        print("\n❌ 任务失败")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())