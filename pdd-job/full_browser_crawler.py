#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整浏览器自动化PDD爬取器
使用Selenium模拟真实用户，爬取所有数据
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import requests
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

class FullBrowserPddCrawler:
    """完整浏览器自动化爬取器"""
    
    def __init__(self, headless: bool = True):
        """
        初始化
        
        Args:
            headless: 是否使用无头模式（默认True，后台运行）
        """
        self.base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
        self.website_url = "https://careers.pddglobalhr.com/jobs"
        
        # 浏览器配置
        self.headless = headless
        self.driver = None
        
        # 会话
        self.session = requests.Session()
        
        # 输出目录
        self.output_dir = "output/pdd_full_browser"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 数据存储
        self.all_positions = []
        self.current_anti_content = None
        
        logger.info("🚀 完整浏览器爬取器初始化完成")
        logger.info(f"   网站URL: {self.website_url}")
        logger.info(f"   输出目录: {self.output_dir}")
        logger.info(f"   无头模式: {headless}")
    
    def setup_browser(self):
        """设置浏览器"""
        try:
            logger.info("🌐 设置Chrome浏览器...")
            
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # 添加常用参数
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # 排除自动化标志
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 设置用户代理
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")
            
            # 禁用自动化控制特征
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
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
    
    def navigate_to_website(self):
        """导航到网站"""
        try:
            logger.info(f"🌐 访问网站: {self.website_url}")
            self.driver.get(self.website_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 等待更多内容加载
            time.sleep(3)
            
            logger.info("✅ 页面加载完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 访问网站失败: {e}")
            return False
    
    def intercept_network_requests(self):
        """拦截网络请求以获取anti_content"""
        logger.info("📡 设置网络请求拦截器...")
        
        intercept_script = """
        // 保存原始的fetch
        const originalFetch = window.fetch;
        
        // 存储拦截到的anti_content
        window.interceptedAntiContents = [];
        
        // 拦截fetch请求
        window.fetch = function(...args) {
            const url = args[0];
            const options = args[1] || {};
            
            // 检查是否是目标API
            if (url && url.includes('/recruit/position/list')) {
                console.log('🔍 拦截到API请求:', url);
                
                // 检查请求头中的Anti-Content
                if (options.headers && options.headers['Anti-Content']) {
                    const antiContent = options.headers['Anti-Content'];
                    console.log('✅ 找到Anti-Content:', antiContent.substring(0, 50) + '...');
                    window.interceptedAntiContents.push(antiContent);
                    window.lastAntiContent = antiContent;
                }
                
                // 检查请求体中的anti_content
                if (options.body) {
                    try {
                        const body = JSON.parse(options.body);
                        if (body.anti_content) {
                            console.log('✅ 找到请求体中的anti_content:', body.anti_content.substring(0, 50) + '...');
                            window.interceptedAntiContents.push(body.anti_content);
                            window.lastAntiContent = body.anti_content;
                        }
                    } catch(e) {
                        // 解析失败，忽略
                    }
                }
            }
            
            return originalFetch.apply(this, args);
        };
        
        // 保存原始的XMLHttpRequest
        const originalXHROpen = window.XMLHttpRequest.prototype.open;
        const originalXHRSend = window.XMLHttpRequest.prototype.send;
        
        window.XMLHttpRequest.prototype.open = function(method, url, ...args) {
            this._url = url;
            return originalXHROpen.apply(this, [method, url, ...args]);
        };
        
        window.XMLHttpRequest.prototype.send = function(body) {
            // 检查是否是目标API
            if (this._url && this._url.includes('/recruit/position/list')) {
                console.log('🔍 拦截到XHR API请求:', this._url);
                
                // 检查请求体
                if (body) {
                    try {
                        const parsed = JSON.parse(body);
                        if (parsed.anti_content) {
                            console.log('✅ 找到XHR中的anti_content:', parsed.anti_content.substring(0, 50) + '...');
                            window.interceptedAntiContents.push(parsed.anti_content);
                            window.lastAntiContent = parsed.anti_content;
                        }
                    } catch(e) {
                        // 解析失败，忽略
                    }
                }
            }
            
            return originalXHRSend.apply(this, arguments);
        };
        
        console.log('✅ 网络拦截器已设置');
        return '拦截器已设置';
        """
        
        self.driver.execute_script(intercept_script)
        logger.info("✅ 网络拦截器设置完成")
    
    def get_current_anti_content(self):
        """获取当前拦截到的anti_content"""
        try:
            anti_content = self.driver.execute_script("return window.lastAntiContent;")
            if anti_content:
                logger.info(f"✅ 获取到anti_content: {anti_content[:50]}...")
                self.current_anti_content = anti_content
                return anti_content
            else:
                logger.info("⚠️ 尚未拦截到anti_content")
                return None
        except Exception as e:
            logger.error(f"❌ 获取anti_content失败: {e}")
            return None
    
    def trigger_api_request(self):
        """触发API请求以获取anti_content"""
        logger.info("🔄 触发API请求...")
        
        try:
            # 方法1: 滚动页面触发加载
            logger.info("   方法1: 滚动页面...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # 方法2: 查找并点击分页按钮
            logger.info("   方法2: 查找分页按钮...")
            try:
                # 查找分页元素
                pagination_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "[class*='pagination'], [class*='page'], button, a, div[class*='btn']")
                
                for element in pagination_elements[:5]:  # 尝试前5个元素
                    try:
                        text = element.text.lower()
                        if any(keyword in text for keyword in ['2', '二', 'next', '下一页', '>']):
                            logger.info(f"   找到分页按钮: {element.text}")
                            element.click()
                            time.sleep(3)
                            break
                    except:
                        continue
            except:
                pass
            
            # 方法3: 模拟键盘操作
            logger.info("   方法3: 模拟键盘操作...")
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(1)
            actions.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(2)
            
            # 方法4: 点击筛选或排序
            logger.info("   方法4: 尝试点击筛选元素...")
            try:
                filter_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    "[class*='filter'], [class*='sort'], [class*='select'], [role='button']")
                
                for element in filter_elements[:3]:
                    try:
                        element.click()
                        time.sleep(1)
                        # 点击外部关闭
                        self.driver.find_element(By.TAG_NAME, 'body').click()
                        time.sleep(1)
                    except:
                        continue
            except:
                pass
            
            logger.info("✅ API请求触发完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 触发API请求失败: {e}")
            return False
    
    def fetch_page_via_browser(self, page: int):
        """通过浏览器获取单页数据"""
        logger.info(f"📥 通过浏览器获取第 {page} 页数据...")
        
        try:
            # 1. 确保有有效的anti_content
            if not self.current_anti_content:
                logger.info("   获取新的anti_content...")
                self.trigger_api_request()
                time.sleep(3)
                
                anti_content = self.get_current_anti_content()
                if not anti_content:
                    logger.error("❌ 无法获取anti_content")
                    return None
            
            # 2. 准备API请求
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
                "Cookie": "_nano_fp=Xpm8lpgJn0EjXqdaXo_eBA4AmspK5Wx4Oawm5ox~",
                "Anti-Content": self.current_anti_content
            }
            
            payload = {
                "page": page,
                "pageSize": 10
            }
            
            # 3. 发送请求
            response = self.session.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"❌ HTTP错误: {response.status_code}")
                
                # 如果错误是400，可能是anti_content过期
                if response.status_code == 400:
                    logger.info("   ⚠️ anti_content可能已过期，尝试获取新的...")
                    self.current_anti_content = None
                    return self.fetch_page_via_browser(page)
                
                return None
            
            data = response.json()
            
            if not data.get("success", False):
                error_code = data.get("errorCode")
                error_msg = data.get("errorMsg", "未知错误")
                logger.error(f"❌ API错误: {error_code} - {error_msg}")
                
                # 如果是400023错误，可能是anti_content问题
                if error_code == 400023:
                    logger.info("   ⚠️ anti_content无效，尝试获取新的...")
                    self.current_anti_content = None
                    return self.fetch_page_via_browser(page)
                
                return None
            
            # 4. 提取数据
            result = data.get("result", {})
            positions = result.get("list", [])
            total = result.get("total", 0)
            
            logger.info(f"   ✅ 成功获取 {len(positions)} 条数据")
            
            if positions and page == 1:
                first = positions[0]
                logger.info(f"   📋 示例: {first.get('name', 'N/A')} - {first.get('workLocation', 'N/A')}")
            
            return {
                "page": page,
                "page_size": 10,
                "total": total,
                "positions": positions,
                "raw_data": data
            }
            
        except Exception as e:
            logger.error(f"❌ 获取第 {page} 页失败: {e}")
            return None
    
    def fetch_all_pages(self, max_pages: int = None):
        """获取所有页数据"""
        logger.info("📊 开始获取所有页数据...")
        
        start_time = time.time()
        
        # 1. 获取第一页
        first_page = self.fetch_page_via_browser(1)
        if not first_page:
            logger.error("❌ 获取第一页失败")
            return []
        
        total_positions = int(first_page["total"])
        total_pages = (total_positions + 9) // 10
        
        logger.info(f"📊 数据统计:")
        logger.info(f"   总岗位数: {total_positions}")
        logger.info(f"   总页数: {total_pages}")
        
        # 确定要爬取的页数
        if max_pages:
            pages_to_fetch = min(total_pages, max_pages)
        else:
            pages_to_fetch = total_pages
        
        logger.info(f"   实际爬取: {pages_to_fetch} 页")
        
        # 收集第一页数据
        self.all_positions.extend(first_page["positions"])
        
        # 2. 获取剩余页
        for page in range(2, pages_to_fetch + 1):
            logger.info(f"\n📥 获取第 {page}/{pages_to_fetch} 页...")
            
            # 每5页重新获取一次anti_content
            if page % 5 == 0:
                logger.info("   🔄 每5页重新获取anti_content...")
                self.current_anti_content = None
                self.trigger_api_request()
                time.sleep(2)
                self.get_current_anti_content()
            
            page_data = self.fetch_page_via_browser(page)
            
            if page_data:
                self.all_positions.extend(page_data["positions"])
                logger.info(f"   ✅ 成功，累计 {len(self.all_positions)} 条")
            else:
                logger.warning(f"   ⚠️ 第 {page} 页获取失败，跳过")
            
            # 避免请求过快
            time.sleep(1.5)
        
        elapsed_time = time.time() - start_time
        logger.info(f"\n✅ 数据获取完成!")
        logger.info(f"   共获取 {len(self.all_positions)} 条记录")
        logger.info(f"   用时: {elapsed_time:.2f} 秒")
        
        return self.all_positions
    
    def process_data(self):
        """处理数据"""
        logger.info("🔧 处理数据...")
        
        processed_data = []
        
        for pos in self.all_positions:
            processed_pos = {
                "岗位ID": pos.get("code", ""),
                "岗位名称": pos.get("name", ""),
                "工作地点": pos.get("workLocation", ""),
                "岗位类别": pos.get("job", ""),
                "更新时间": pos.get("updateTime", ""),
                "更新时间戳": pos.get("updateDate", 0),
                "详情页URL": f"https://careers.pddglobalhr.com/jobs/{pos.get('code', '')}",
                "爬取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            processed_data.append(processed_pos)
        
        logger.info(f"✅ 数据处理完成，共 {len(processed_data)} 条记录")
        return processed_data
    
    def export_to_excel(self, data: List[Dict[str, Any]], filename: str = None):
        """导出到Excel"""
        if not data:
            logger.warning("⚠️ 没有数据需要导出")
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pdd_full_positions_{timestamp}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            logger.info(f"📤 导出 {len(data)} 条记录到Excel...")
            
            df = pd.DataFrame(data)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 主数据表
                df.to_excel(writer, sheet_name='所有岗位', index=False)
                
                # 统计表
                if '工作地点' in df.columns:
                    location_stats = df['工作地点'].value_counts().reset_index()
                    location_stats.columns = ['工作地点', '岗位数量']
                    location_stats.to_excel(writer, sheet_name='地点分布', index=False)
                
                if '岗位类别' in df.columns:
                    category_stats = df['岗位类别'].value_counts().reset_index()
                    category_stats.columns = ['岗位类别', '岗位数量']
                    category_stats.to_excel(writer, sheet_name='类别分布', index=False)
                
                # 数据摘要
                time_stats = pd.DataFrame({
                    '统计项': ['总记录数', '唯一岗位ID数', '数据源', '爬取时间', '爬取方式'],
                    '数值': [len(df), df['岗位ID'].nunique(), '拼多多招聘网站', 
                           datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '浏览器自动化']
                })
                time_stats.to_excel(writer, sheet_name='数据摘要', index=False)
            
            file_size = os.path.getsize(filepath)
            logger.info(f"✅ Excel导出成功")
            logger.info(f"   文件: {filepath}")
            logger.info(f"   大小: {file_size:,} 字节")
            logger.info(f"   工作表: 所有岗位、地点分布、类别分布、数据摘要")
            
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Excel导出失败: {e}")
            return ""
    
    def run_complete_crawl(self, max_pages: int = None):
        """运行完整爬取"""
        print("\n" + "="*70)
        print("🚀 完整浏览器自动化PDD爬取 - 开始执行")
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
            if not self.navigate_to_website():
                print("❌ 访问网站失败")
                self.close_browser()
                return False
            
            # 3. 设置网络拦截器
            print("\n📡 阶段3: 设置网络拦截器...")
            self.intercept_network_requests()
            
            # 4. 触发初始API请求获取第一个anti_content
            print("\n🔄 阶段4: 获取初始anti_content参数...")
            self.trigger_api_request()
            time.sleep(3)
            
            anti_content = self.get_current_anti_content()
            if anti_content:
                print(f"✅ 获取到初始anti_content: {anti_content[:50]}...")
            else:
                print("⚠️ 未获取到初始anti_content，继续尝试...")
            
            # 5. 获取所有数据
            print(f"\n📥 阶段5: 获取岗位数据...")
            positions = self.fetch_all_pages(max_pages=max_pages)
            
            if not positions:
                print("❌ 没有获取到数据")
                self.close_browser()
                return False
            
            # 6. 关闭浏览器（不再需要）
            print("\n🌐 阶段6: 关闭浏览器...")
            self.close_browser()
            
            # 7. 处理数据
            print("\n🔧 阶段7: 处理数据...")
            processed_data = self.process_data()
            
            # 8. 导出数据
            print("\n📤 阶段8: 导出数据到Excel...")
            excel_file = self.export_to_excel(processed_data)
            
            if not excel_file:
                print("❌ 导出失败")
                return False
            
            # 9. 生成报告
            total_time = time.time() - start_time
            
            print("\n" + "="*70)
            print("🎯 爬取完成报告")
            print("="*70)
            print(f"✅ 状态: 成功")
            print(f"⏱️  用时: {total_time:.2f} 秒")
            print(f"📊 记录数: {len(processed_data)} 条")
            print(f"📁 Excel文件: {excel_file}")
            print(f"📂 输出目录: {self.output_dir}")
            print("="*70)
            
            # 保存详细报告
            report = {
                "success": True,
                "execution_time": total_time,
                "total_records": len(processed_data),
                "excel_file": excel_file,
                "export_time": datetime.now().isoformat(),
                "output_directory": self.output_dir,
                "method": "full_browser_automation",
                "headless_mode": self.headless,
                "pages_crawled": len(self.all_positions) // 10,
                "anti_content_used": True
            }
            
            report_file = os.path.join(self.output_dir, "full_crawl_report.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"📄 详细报告: {report_file}")
            print(f"\n🎯 任务完成！完整Excel文档已生成: {excel_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ 爬取失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 确保浏览器被关闭
            self.close_browser()
            
            return False

def main():
    """主函数"""
    print("完整浏览器自动化PDD岗位数据爬取工具")
    print("="*70)
    print("使用Selenium模拟真实用户，爬取所有数据")
    print("="*70)
    
    # 配置参数
    headless = True  # 无头模式（后台运行）
    max_pages = 10   # 先测试10页，可以改为None爬取所有页
    
    print(f"\n🚀 配置参数:")
    print(f"   无头模式: {'是' if headless else '否'}")
    print(f"   最大页数: {max_pages if max_pages else '所有页'}")
    print("="*70)
    
    # 创建爬取器并运行
    crawler = FullBrowserPddCrawler(headless=headless)
    success = crawler.run_complete_crawl(max_pages=max_pages)
    
    if success:
        print("\n✅ 任务完成!")
        print("\n📋 下一步:")
        print("1. 打开Excel文件查看完整数据")
        print("2. 查看详细报告")
        print("3. 数据保存在output/pdd_full_browser/目录")
        return 0
    else:
        print("\n❌ 任务失败")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())