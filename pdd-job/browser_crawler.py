#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器自动化PDD爬取器
使用Selenium自动获取anti_content参数并爬取数据
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
from webdriver_manager.chrome import ChromeDriverManager

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BrowserPddCrawler:
    """浏览器自动化PDD爬取器"""
    
    def __init__(self, headless: bool = False):
        """
        初始化浏览器爬取器
        
        Args:
            headless: 是否使用无头模式
        """
        self.base_url = "https://careers.pddglobalhr.com/api/recruit/position/list"
        self.website_url = "https://careers.pddglobalhr.com/jobs"
        
        # 浏览器配置
        self.headless = headless
        self.driver = None
        
        # 会话
        self.session = requests.Session()
        
        # 输出目录
        self.output_dir = "output/pdd_browser"
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("🚀 浏览器爬取器初始化完成")
        logger.info(f"   网站URL: {self.website_url}")
        logger.info(f"   API端点: {self.base_url}")
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
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # 排除自动化标志
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 设置用户代理
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
    
    def get_anti_content_from_browser(self) -> Optional[str]:
        """
        从浏览器获取anti_content参数
        
        Returns:
            anti_content参数值，失败返回None
        """
        logger.info("🔍 从浏览器获取anti_content参数...")
        
        if not self.driver:
            logger.error("❌ 浏览器未初始化")
            return None
        
        try:
            # 访问网站
            logger.info(f"🌐 访问网站: {self.website_url}")
            self.driver.get(self.website_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info("✅ 页面加载完成")
            
            # 等待API请求
            logger.info("⏳ 等待API请求...")
            time.sleep(3)  # 给页面时间发送API请求
            
            # 获取网络日志
            logger.info("📡 获取网络请求日志...")
            
            # 执行JavaScript获取性能条目
            script = """
            return window.performance.getEntriesByType('resource')
                .filter(entry => entry.name.includes('/recruit/position/list'))
                .map(entry => ({
                    name: entry.name,
                    initiatorType: entry.initiatorType,
                    startTime: entry.startTime,
                    duration: entry.duration
                }));
            """
            
            resources = self.driver.execute_script(script)
            
            if resources:
                logger.info(f"✅ 找到 {len(resources)} 个API请求")
                for res in resources[:3]:  # 显示前3个
                    logger.info(f"   📡 {res['name']}")
            else:
                logger.warning("⚠️ 未找到API请求，尝试其他方法...")
            
            # 方法1: 从localStorage获取
            logger.info("🔧 方法1: 检查localStorage...")
            try:
                localStorage = self.driver.execute_script("return JSON.stringify(window.localStorage);")
                if "anti_content" in localStorage.lower():
                    logger.info("✅ 在localStorage中找到anti_content相关数据")
                    # 这里可以解析localStorage
            except:
                pass
            
            # 方法2: 从cookies获取
            logger.info("🍪 方法2: 检查cookies...")
            cookies = self.driver.get_cookies()
            logger.info(f"   找到 {len(cookies)} 个cookies")
            
            # 查找_nano_fp cookie
            nano_fp = None
            for cookie in cookies:
                if cookie['name'] == '_nano_fp':
                    nano_fp = cookie['value']
                    logger.info(f"   ✅ 找到_nano_fp: {nano_fp[:50]}...")
                    break
            
            if not nano_fp:
                logger.warning("⚠️ 未找到_nano_fp cookie")
            
            # 方法3: 尝试直接获取请求头
            logger.info("📋 方法3: 尝试获取请求头...")
            
            # 模拟点击分页或筛选以触发API请求
            try:
                # 尝试点击分页按钮
                pagination_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[class*='pagination'], [class*='page']")
                if pagination_buttons:
                    logger.info(f"   找到 {len(pagination_buttons)} 个分页元素")
                    # 可以尝试点击第二个分页按钮
                    if len(pagination_buttons) > 1:
                        logger.info("   尝试点击分页按钮触发API请求...")
                        try:
                            pagination_buttons[1].click()
                            time.sleep(2)
                        except:
                            pass
            except:
                pass
            
            # 等待更多请求
            time.sleep(2)
            
            # 再次检查资源
            resources = self.driver.execute_script(script)
            
            # 方法4: 使用JavaScript拦截网络请求
            logger.info("🛠️ 方法4: 使用JavaScript拦截网络请求...")
            
            intercept_script = """
            // 保存原始的fetch和XMLHttpRequest
            const originalFetch = window.fetch;
            const originalXHR = window.XMLHttpRequest.prototype.open;
            
            // 存储拦截到的请求
            window.interceptedRequests = [];
            
            // 拦截fetch请求
            window.fetch = function(...args) {
                const url = args[0];
                const options = args[1] || {};
                
                if (url && url.includes('/recruit/position/list')) {
                    console.log('拦截到fetch请求:', url, options);
                    window.interceptedRequests.push({
                        type: 'fetch',
                        url: url,
                        options: options
                    });
                    
                    // 检查headers中的Anti-Content
                    if (options.headers && options.headers['Anti-Content']) {
                        window.lastAntiContent = options.headers['Anti-Content'];
                    }
                }
                
                return originalFetch.apply(this, args);
            };
            
            // 拦截XMLHttpRequest请求
            window.XMLHttpRequest.prototype.open = function(method, url, ...args) {
                if (url && url.includes('/recruit/position/list')) {
                    console.log('拦截到XHR请求:', method, url);
                    window.interceptedRequests.push({
                        type: 'xhr',
                        method: method,
                        url: url
                    });
                    
                    // 监听send事件获取请求体
                    const originalSend = this.send;
                    this.send = function(body) {
                        if (body) {
                            try {
                                const parsed = JSON.parse(body);
                                if (parsed.anti_content) {
                                    window.lastAntiContent = parsed.anti_content;
                                }
                            } catch(e) {}
                        }
                        return originalSend.apply(this, arguments);
                    };
                }
                
                return originalXHR.apply(this, [method, url, ...args]);
            };
            
            return '拦截器已设置';
            """
            
            self.driver.execute_script(intercept_script)
            logger.info("✅ JavaScript拦截器已设置")
            
            # 等待拦截到请求
            logger.info("⏳ 等待拦截请求...")
            time.sleep(5)
            
            # 获取拦截到的anti_content
            anti_content = self.driver.execute_script("return window.lastAntiContent;")
            
            if anti_content:
                logger.info(f"✅ 成功获取anti_content参数: {anti_content[:50]}...")
                return anti_content
            
            # 如果以上方法都失败，尝试直接调用API
            logger.info("🔄 方法5: 尝试直接调用API...")
            
            # 获取当前cookies用于API请求
            cookies_dict = {c['name']: c['value'] for c in cookies}
            cookie_str = '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])
            
            # 尝试使用固定参数调用API
            test_payload = {
                "page": 1,
                "pageSize": 10
            }
            
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
                "Cookie": cookie_str
            }
            
            # 尝试调用API
            response = requests.post(
                self.base_url,
                headers=headers,
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    logger.info("✅ API调用成功（可能不需要anti_content）")
                    return ""  # 返回空字符串表示不需要anti_content
                else:
                    error_code = data.get("errorCode")
                    error_msg = data.get("errorMsg", "未知错误")
                    logger.warning(f"⚠️ API调用失败: {error_code} - {error_msg}")
            
            logger.error("❌ 无法获取anti_content参数")
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取anti_content失败: {e}")
            return None
    
    def fetch_with_anti_content(self, anti_content: str, page: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """
        使用anti_content获取数据
        
        Args:
            anti_content: anti_content参数
            page: 页码
            page_size: 每页大小
            
        Returns:
            响应数据
        """
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
        
        # 如果提供了anti_content，添加到请求头
        if anti_content:
            headers["Anti-Content"] = anti_content
        
        # 准备请求载荷
        payload = {
            "page": page,
            "pageSize": page_size
        }
        
        # 如果anti_content不是空字符串，也添加到请求体
        if anti_content and anti_content != "":
            payload["anti_content"] = anti_content
        
        try:
            logger.info(f"📥 获取第 {page} 页数据...")
            
            response = self.session.post(
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
            
            logger.info(f"   ✅ 成功获取 {len(positions)} 条数据，总计 {total} 条")
            
            if positions:
                first = positions[0]
                logger.info(f"   📋 示例: {first.get('name', 'N/A')} - {first.get('workLocation', 'N/A')}")
            
            return {
                "page": page,
                "page_size": page_size,
                "total": total,
                "positions": positions,
                "raw_data": data
            }
            
        except Exception as e:
            logger.error(f"❌ 获取第 {page} 页失败: {e}")
            return None
    
    def fetch_all_pages(self, anti_content: str, max_pages: int = 10) -> List[Dict[str, Any]]:
        """获取所有页数据"""
        all_positions = []
        
        # 先获取第一页了解总数据量
        first_page = self.fetch_with_anti_content(anti_content, page=1)
        if not first_page:
            logger.error("❌ 获取第一页失败，无法继续")
            return []
        
        total_positions = int(first_page["total"])
        page_size = int(first_page["page_size"])
        total_pages = (total_positions + page_size - 1) // page_size
        
        logger.info(f"📊 数据统计:")
        logger.info(f"   总岗位数: {total_positions}")
        logger.info(f"   每页大小: {page_size}")
        logger.info(f"   总页数: {total_pages}")
        logger.info(f"   实际爬取: {min(total_pages, max_pages)} 页")
        
        # 添加第一页数据
        all_positions.extend(first_page["positions"])
        
        # 获取剩余页
        pages_to_fetch = min(total_pages, max_pages)
        
        for page in range(2, pages_to_fetch + 1):
            logger.info(f"\n📥 获取第 {page}/{pages_to_fetch} 页...")
            
            page_data = self.fetch_with_anti_content(anti_content, page=page)
            if page_data:
                all_positions.extend(page_data["positions"])
            else:
                logger.warning(f"⚠️ 第 {page} 页获取失败，跳过")
            
            # 避免请求过快
            time.sleep(1)
        
        logger.info(f"\n✅ 数据获取完成，共 {len(all_positions)} 条记录")
        return all_positions
    
    def process_data(self, positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理数据"""
        processed = []
        
        for pos in positions:
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
            processed.append(processed_pos)
        
        return processed
    
    def export_to_excel(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """导出到Excel"""
        if not data:
            logger.warning("⚠️ 没有数据需要导出")
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pdd_positions_{timestamp}.xlsx"
        
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
                    '统计项': ['总记录数', '唯一岗位ID数', '数据源', '爬取时间'],
                    '数值': [len(df), df['岗位ID'].nunique(), '拼多多招聘网站', timestamp]
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
    
    def run_complete_crawl(self, max_pages: int = 10):
        """运行完整爬取"""
        print("\n" + "="*60)
        print("🚀 浏览器自动化PDD爬取 - 开始执行")
        print("="*60)
        
        start_time = time.time()
        
        try:
            # 1. 设置浏览器
            if not self.setup_browser():
                print("❌ 浏览器设置失败")
                return False
            
            # 2. 获取anti_content参数
            print("\n🔍 阶段1: 获取anti_content参数...")
            anti_content = self.get_anti_content_from_browser()
            
            if anti_content is None:
                print("❌ 无法获取anti_content参数")
                self.close_browser()
                return False
            
            print(f"✅ 获取到anti_content参数: {anti_content[:50]}..." if anti_content else "✅ API可能不需要anti_content参数")
            
            # 3. 关闭浏览器（不再需要）
            self.close_browser()
            
            # 4. 获取数据
            print("\n📥 阶段2: 获取岗位数据...")
            raw_positions = self.fetch_all_pages(anti_content, max_pages=max_pages)
            
            if not raw_positions:
                print("❌ 没有获取到数据")
                return False
            
            # 5. 处理数据
            print("\n🔧 阶段3: 处理数据...")
            processed_data = self.process_data(raw_positions)
            
            # 6. 导出数据
            print("\n📤 阶段4: 导出数据...")
            excel_file = self.export_to_excel(processed_data)
            
            if not excel_file:
                print("❌ 导出失败")
                return False
            
            # 7. 生成报告
            total_time = time.time() - start_time
            
            print("\n" + "="*60)
            print("🎯 爬取完成报告")
            print("="*60)
            print(f"✅ 状态: 成功")
            print(f"⏱️  用时: {total_time:.2f} 秒")
            print(f"📊 记录数: {len(processed_data)} 条")
            print(f"📁 Excel文件: {excel_file}")
            print(f"📂 输出目录: {self.output_dir}")
            print("="*60)
            
            # 保存详细报告
            report = {
                "success": True,
                "execution_time": total_time,
                "total_records": len(processed_data),
                "excel_file": excel_file,
                "export_time": datetime.now().isoformat(),
                "output_directory": self.output_dir,
                "method": "browser_automation",
                "anti_content_obtained": anti_content is not None
            }
            
            report_file = os.path.join(self.output_dir, "crawl_report.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"📄 详细报告: {report_file}")
            print(f"\n🎯 任务完成！Excel文档已生成: {excel_file}")
            
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
    print("浏览器自动化PDD岗位数据爬取工具")
    print("="*60)
    print("使用Selenium自动获取anti_content参数并爬取数据")
    print("="*60)
    
    # 询问是否使用无头模式
    print("\n🤖 浏览器模式选择:")
    print("   1. 有界面模式 (可见浏览器窗口)")
    print("   2. 无头模式 (后台运行，不可见)")
    
    choice = input("\n请选择模式 (1/2, 默认2): ").strip() or "2"
    headless = (choice == "2")
    
    # 询问爬取页数
    print("\n📄 请输入爬取页数 (默认5，建议1-20):")
    max_pages_input = input("最大页数: ").strip()
    
    try:
        max_pages = int(max_pages_input) if max_pages_input else 5
        if max_pages < 1:
            max_pages = 5
    except ValueError:
        print("⚠️ 输入无效，使用默认值5")
        max_pages = 5
    
    print(f"\n🚀 开始执行:")
    print(f"   模式: {'无头' if headless else '有界面'}")
    print(f"   最大页数: {max_pages}")
    print("="*60)
    
    # 创建爬取器并运行
    crawler = BrowserPddCrawler(headless=headless)
    success = crawler.run_complete_crawl(max_pages=max_pages)
    
    if success:
        print("\n✅ 任务完成!")
        print("\n📋 下一步:")
        print("1. 打开Excel文件查看数据")
        print("2. 查看详细报告")
        print("3. 数据保存在output/pdd_browser/目录")
        return 0
    else:
        print("\n❌ 任务失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    import sys
    sys.exit(exit_code)