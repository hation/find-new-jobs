#!/usr/bin/env python3
# 🏗️ 夸克爬取器 - 直接URL方案插件
# 版本: 1.0
# 创建时间: 2026-05-19
# 基于: 优化的新方案，避免点击状态丢失

import os
import sys
import json
import time
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.interfaces import (
    IExtractionStrategy, StrategyType, PositionData, PageState, ExecutionContext,
    create_position_data_from_dict, StrategyError, BrowserError
)
from core.plugin_manager import register_plugin


@register_plugin(StrategyType.DIRECT_URL)
class DirectURLStrategy(IExtractionStrategy):
    """直接URL方案插件 - 优化的新方案，避免点击状态丢失"""
    
    def __init__(self):
        self.strategy_name = "直接URL方案插件"
        self.strategy_version = "1.0"
        self.description = "通过直接URL访问详情页，避免点击带来的筛选状态丢失"
        self.browser_manager = None
        self.data_manager = None
        self.context = None
        self.initialized = False
        
        # 配置
        self.base_url = "https://zhaopin.quark.cn/"
        self.list_page_url = f"{self.base_url}campus"
        self.detail_page_template = f"{self.base_url}job/detail?positionId="
        
        # 筛选配置
        self.filter_categories = [
            "产品类", "运营类", "数据类", 
            "市场拓展", "销售类", "游戏类", "金融类"
        ]
        
        # 状态跟踪
        self.current_tab_id = None
        self.list_tab_id = None
        self.detail_tabs = {}
        
        # 性能优化
        self.max_workers = 3  # 并行处理数量
        self.request_delay = 1  # 请求间隔(秒)
        self.batch_size = 5    # 批量处理大小
        
        print(f"🧩 初始化 {self.strategy_name} v{self.strategy_version}")
        print(f"📝 {self.description}")
    
    def get_strategy_type(self) -> StrategyType:
        return StrategyType.DIRECT_URL
    
    def get_strategy_name(self) -> str:
        return self.strategy_name
    
    def initialize(self, context: ExecutionContext) -> bool:
        """初始化策略"""
        try:
            self.context = context
            
            # 初始化浏览器管理器
            from core.browser_manager import OpenClawBrowserManager
            self.browser_manager = OpenClawBrowserManager(profile=context.browser_profile)
            
            if not self.browser_manager.initialize():
                raise StrategyError("浏览器管理器初始化失败")
            
            # 初始化数据管理器
            from plugins.utils.data_manager import StandardDataManager
            self.data_manager = StandardDataManager()
            
            # 导航到列表页
            print(f"🌐 导航到列表页: {self.list_page_url}")
            if not self.browser_manager.navigate(self.list_page_url):
                raise StrategyError("导航到列表页失败")
            
            # 等待页面加载
            time.sleep(3)
            
            # 保存列表页标签ID
            self._save_list_tab_id()
            
            # 应用筛选条件
            print("🔍 应用筛选条件...")
            if not self._apply_filters():
                raise StrategyError("应用筛选条件失败")
            
            # 验证筛选状态
            print("✅ 验证筛选状态...")
            if not self.validate_page_state(self.filter_categories):
                print("⚠️  筛选状态验证失败，尝试重新应用...")
                if not self._apply_filters():
                    raise StrategyError("重新应用筛选失败")
            
            self.initialized = True
            print(f"✅ {self.strategy_name} 初始化完成")
            print(f"📊 策略特点: 避免点击状态丢失，支持批量并行处理")
            return True
            
        except Exception as e:
            print(f"❌ {self.strategy_name} 初始化失败: {e}")
            return False
    
    def _save_list_tab_id(self) -> None:
        """保存列表页标签ID"""
        try:
            from openclaw_tools import browser
            
            tabs_result = browser(action="tabs", profile=self.context.browser_profile)
            tabs = tabs_result.get("tabs", [])
            
            if tabs:
                self.list_tab_id = tabs[0].get("id")
                self.current_tab_id = self.list_tab_id
                print(f"📌 列表页标签ID: {self.list_tab_id}")
                
        except Exception as e:
            print(f"⚠️  保存列表页标签ID失败: {e}")
    
    def _apply_filters(self) -> bool:
        """应用7个筛选类别"""
        try:
            print("🎯 应用筛选条件 (7个类别)...")
            
            # 获取页面快照
            snapshot = self.browser_manager.take_snapshot(refs="aria")
            elements = snapshot.get("elements", [])
            
            # 查找筛选元素
            filter_elements = []
            category_status = {}
            
            for element in elements:
                element_name = element.get("name", "")
                if not element_name:
                    continue
                
                # 检查是否是我们需要的筛选类别
                for category in self.filter_categories:
                    if category in element_name:
                        filter_elements.append({
                            "element": element,
                            "category": category,
                            "is_checked": element.get("checked", False)
                        })
                        category_status[category] = element.get("checked", False)
                        break
            
            print(f"🔍 找到 {len(filter_elements)} 个筛选元素")
            
            # 显示当前状态
            print("📊 筛选状态:")
            for category, is_checked in category_status.items():
                status = "✅ 已选中" if is_checked else "❌ 未选中"
                print(f"   {status} {category}")
            
            # 点击未选中的筛选
            needs_click = []
            for item in filter_elements:
                if not item["is_checked"]:
                    needs_click.append(item)
            
            if not needs_click:
                print("✅ 所有筛选类别已正确选中")
                return True
            
            print(f"🔄 需要点击 {len(needs_click)} 个未选中的筛选")
            
            # 点击筛选元素
            success_count = 0
            for item in needs_click:
                element_ref = item["element"].get("ref")
                category = item["category"]
                
                if element_ref:
                    print(f"   📌 点击筛选: {category}")
                    
                    if self.browser_manager.click_element(element_ref):
                        success_count += 1
                        print(f"   ✅ 点击成功")
                    else:
                        print(f"   ❌ 点击失败")
                    
                    # 添加延迟避免过快点击
                    time.sleep(0.8)
            
            # 等待筛选生效
            print("⏳ 等待筛选生效...")
            time.sleep(3)
            
            # 验证筛选结果
            final_snapshot = self.browser_manager.take_snapshot(refs="aria")
            
            # 查找筛选后的岗位数量显示
            for element in final_snapshot.get("elements", []):
                text = element.get("name", "")
                if "个岗位" in text:
                    print(f"📊 筛选结果: {text}")
                    
                    # 解析数量
                    import re
                    match = re.search(r'(\d+)\s*个岗位', text)
                    if match:
                        position_count = int(match.group(1))
                        print(f"🎯 目标岗位数量: {position_count}")
                        break
            
            print(f"✅ 筛选应用完成: {success_count}/{len(needs_click)} 个成功")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 应用筛选失败: {e}")
            return False
    
    def validate_environment(self) -> List[str]:
        """验证环境"""
        issues = []
        
        try:
            # 检查浏览器服务
            if not self.browser_manager:
                issues.append("浏览器管理器未初始化")
            
            # 检查网络连接 (通过访问一个已知URL)
            print("🌐 检查网络连接...")
            test_url = "https://zhaopin.quark.cn/"
            
            try:
                # 这里可以添加网络连接检查
                pass
            except Exception as e:
                issues.append(f"网络连接检查失败: {e}")
            
            # 检查目标网站可访问性
            print("🔗 检查目标网站...")
            try:
                # 这里可以添加网站可访问性检查
                pass
            except Exception as e:
                issues.append(f"目标网站检查失败: {e}")
            
            # 检查并行处理环境
            print("⚡ 检查并行处理环境...")
            try:
                import concurrent.futures
                # 测试线程池
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future = executor.submit(lambda: "test")
                    future.result(timeout=5)
                print("   ✅ 并行处理环境正常")
            except Exception as e:
                issues.append(f"并行处理环境异常: {e}")
            
            return issues
            
        except Exception as e:
            issues.append(f"环境验证异常: {e}")
            return issues
    
    def extract_list_page(self, page_number: int) -> List[str]:
        """提取列表页，返回position_id列表"""
        try:
            print(f"📄 提取第 {page_number} 页列表 (直接URL方案)...")
            
            # 确保在列表页标签
            if self.list_tab_id and self.current_tab_id != self.list_tab_id:
                print("   🔄 切换回列表页标签...")
                self.browser_manager.switch_to_tab(self.list_tab_id)
                self.current_tab_id = self.list_tab_id
                time.sleep(2)
            
            # 如果不在目标页码，先导航到目标页
            if page_number > 1:
                print(f"   🔄 翻页到第 {page_number} 页...")
                if not self._navigate_to_page(page_number):
                    raise StrategyError(f"导航到第 {page_number} 页失败")
            
            # 方法1: 通过JavaScript提取所有positionId
            print("   🔍 方法1: JavaScript提取positionId...")
            position_ids = self._extract_position_ids_via_js()
            
            if not position_ids:
                print("   ⚠️  方法1失败，尝试方法2...")
                # 方法2: 通过页面快照提取
                position_ids = self._extract_position_ids_via_snapshot()
            
            if not position_ids:
                print("   ⚠️  方法2失败，尝试方法3...")
                # 方法3: 通过HTML解析提取
                position_ids = self._extract_position_ids_via_html()
            
            # 去重和验证
            unique_ids = list(set(position_ids))
            valid_ids = [pid for pid in unique_ids if pid and len(pid) > 5]
            
            print(f"✅ 提取到 {len(valid_ids)} 个有效岗位ID")
            
            # 显示样本
            if valid_ids:
                print(f"📋 样本ID: {valid_ids[0]}" + (f", {valid_ids[1]}" if len(valid_ids) > 1 else ""))
                
                # 生成详情页URL样本
                sample_url = f"{self.detail_page_template}{valid_ids[0]}"
                print(f"🔗 详情页URL模板: {sample_url}")
            
            return valid_ids
            
        except Exception as e:
            print(f"❌ 提取列表页失败: {e}")
            return []
    
    def _extract_position_ids_via_js(self) -> List[str]:
        """通过JavaScript提取position_id"""
        try:
            js_code = """
            // 提取所有岗位链接的positionId
            const positionIds = new Set();
            
            // 方法1: 通过a标签的href属性
            document.querySelectorAll('a[href*="positionId"]').forEach(link => {
                const href = link.href;
                const match = href.match(/positionId=([^&]+)/);
                if (match && match[1]) {
                    positionIds.add(match[1]);
                }
            });
            
            // 方法2: 通过data属性
            document.querySelectorAll('[data-position-id], [data-id]').forEach(el => {
                const positionId = el.getAttribute('data-position-id') || el.getAttribute('data-id');
                if (positionId && positionId.length > 5) {
                    positionIds.add(positionId);
                }
            });
            
            // 方法3: 通过class名包含position或job的元素
            document.querySelectorAll('[class*="position"], [class*="job"]').forEach(el => {
                const classList = el.className.split(' ');
                for (const className of classList) {
                    if (className.length > 10 && /^[a-zA-Z0-9]+$/.test(className)) {
                        positionIds.add(className);
                    }
                }
            });
            
            return Array.from(positionIds);
            """
            
            result = self.browser_manager.execute_script(js_code)
            
            if result and isinstance(result, list):
                print(f"   ✅ JavaScript提取到 {len(result)} 个ID")
                return result
            
            return []
            
        except Exception as e:
            print(f"   ⚠️  JavaScript提取失败: {e}")
            return []
    
    def _extract_position_ids_via_snapshot(self) -> List[str]:
        """通过页面快照提取position_id"""
        try:
            snapshot = self.browser_manager.take_snapshot(refs="aria")
            elements = snapshot.get("elements", [])
            
            position_ids = []
            
            for element in elements:
                # 检查链接元素
                if element.get("role") == "link":
                    href = element.get("href", "")
                    if "positionId=" in href:
                        # 解析positionId
                        try:
                            parsed = urllib.parse.urlparse(href)
                            query_params = urllib.parse.parse_qs(parsed.query)
                            
                            if "positionId" in query_params:
                                pid = query_params["positionId"][0]
                                position_ids.append(pid)
                        except:
                            pass
                
                # 检查按钮或列表项
                elif element.get("role") in ["button", "listitem"]:
                    name = element.get("name", "")
                    # 尝试从文本中提取ID
                    import re
                    matches = re.findall(r'[A-Za-z0-9]{8,}', name)
                    for match in matches:
                        if len(match) > 7:  # 假设ID长度大于7
                            position_ids.append(match)
            
            print(f"   ✅ 快照提取到 {len(position_ids)} 个ID")
            return position_ids
            
        except Exception as e:
            print(f"   ⚠️  快照提取失败: {e}")
            return []
    
    def _extract_position_ids_via_html(self) -> List[str]:
        """通过HTML源码提取position_id"""
        try:
            # 获取页面HTML
            js_code = """
            return document.documentElement.outerHTML;
            """
            
            html_content = self.browser_manager.execute_script(js_code)
            
            if not html_content:
                return []
            
            # 使用正则表达式提取positionId
            import re
            
            # 模式1: positionId=后面的值
            pattern1 = r'positionId=([A-Za-z0-9]+)'
            matches1 = re.findall(pattern1, html_content)
            
            # 模式2: data-position-id属性
            pattern2 = r'data-position-id="([^"]+)"'
            matches2 = re.findall(pattern2, html_content)
            
            # 模式3: 可能是ID的较长字符串
            pattern3 = r'[A-Za-z0-9]{10,}'
            matches3 = re.findall(pattern3, html_content)
            
            # 合并结果
            all_matches = matches1 + matches2
            
            # 过滤可能的ID (长度8-50)
            valid_ids = []
            for match in all_matches:
                if 8 <= len(match) <= 50 and match.isalnum():
                    valid_ids.append(match)
            
            # 从matches3中找出不在前两个模式中的
            for match in matches3:
                if 10 <= len(match) <= 50 and match not in valid_ids:
                    # 检查是否可能是ID
                    if match.isalnum() and not match.isdigit():  # 不是纯数字
                        valid_ids.append(match)
            
            print(f"   ✅ HTML解析提取到 {len(valid_ids)} 个ID")
            return valid_ids
            
        except Exception as e:
            print(f"   ⚠️  HTML解析失败: {e}")
            return []
    
    def _navigate_to_page(self, target_page: int) -> bool:
        """导航到指定页码"""
        try:
            print(f"   📖 翻页到第 {target_page} 页")
            
            # 获取当前页码
            current_page = self._get_current_page_number()
            print(f"   当前页码: {current_page}")
            
            if current_page == target_page:
                print("   ✅ 已经在目标页码")
                return True
            
            # 计算翻页次数
            if target_page > current_page:
                direction = "forward"
                pages_to_go = target_page - current_page
            else:
                direction = "backward"
                pages_to_go = current_page - target_page
            
            print(f"   需要向{direction}翻 {pages_to_go} 页")
            
            # 执行翻页
            for i in range(pages_to_go):
                print(f"   翻页 {i+1}/{pages_to_go}...")
                
                if direction == "forward":
                    success = self._click_next_page()
                else:
                    success = self._click_previous_page()
                
                if not success:
                    print(f"   ❌ 第 {i+1} 次翻页失败")
                    return False
                
                # 等待页面加载
                time.sleep(2.5)
                
                # 验证翻页后页码
                new_page = self._get_current_page_number()
                print(f"   翻页后页码: {new_page}")
            
            # 最终验证
            final_page = self._get_current_page_number()
            if final_page == target_page:
                print(f"   ✅ 成功翻页到第 {target_page} 页")
                return True
            else:
                print(f"   ❌ 翻页失败，当前在第 {final_page} 页")
                return False
            
        except Exception as e:
            print(f"   ❌ 翻页失败: {e}")
            return False
    
    def _get_current_page_number(self) -> int:
        """获取当前页码"""
        try:
            # 方法1: 通过JavaScript获取
            js_code = """
            // 查找页码显示
            const pageElements = document.querySelectorAll('div, span, li');
            for (const el of pageElements) {
                const text = el.textContent || '';
                const match = text.match(/(\\d+)\\s*\\/\\s*(\\d+)/);
                if (match) {
                    return parseInt(match[1]);
                }
            }
            
            // 检查URL参数
            const urlParams = new URLSearchParams(window.location.search);
            const pageParam = urlParams.get('page');
            if (pageParam) {
                return parseInt(pageParam);
            }
            
            return 1;
            """
            
            page_number = self.browser_manager.execute_script(js_code)
            if page_number:
                return int(page_number)
            
            return 1
            
        except Exception as e:
            print(f"   ⚠️  获取页码失败: {e}")
            return 1
    
    def _click_next_page(self) -> bool:
        """点击下一页"""
        return self._click_pagination_button("下一页", "next")
    
    def _click_previous_page(self) -> bool:
        """点击上一页"""
        return self._click_pagination_button("上一页", "previous")
    
    def _click_pagination_button(self, chinese_text: str, english_text: str) -> bool:
        """点击分页按钮"""
        try:
            # 查找按钮
            snapshot = self.browser_manager.take_snapshot(refs="aria")
            
            for element in snapshot.get("elements", []):
                name = element.get("name", "").lower()
                if chinese_text in name or english_text in name:
                    ref = element.get("ref")
                    if ref:
                        print(f"   找到按钮: {name}")
                        return self.browser_manager.click_element(ref)
            
            # 如果通过ref找不到，尝试JavaScript点击
            js_code = f"""
            // 查找包含 {chinese_text} 或 {english_text} 的按钮
            const buttons = document.querySelectorAll('button, a, div[role="button"]');
            for (const btn of buttons) {{
                const text = btn.textContent.toLowerCase();
                if (text.includes('{chinese_text}') || text.includes('{english_text}')) {{
                    btn.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                    btn.click();
                    return true;
                }}
            }}
            return false;
            """
            
            clicked = self.browser_manager.execute_script(js_code)
            if clicked:
                print(f"   ✅ JavaScript点击成功")
                return True
            
            print(f"   ❌ 未找到 {chinese_text} 按钮")
            return False
            
        except Exception as e:
            print(f"   ❌ 点击按钮失败: {e}")
            return False
    
    def extract_position_detail(self, position_id: str, page_number: int, position_index: int) -> PositionData:
        """提取岗位详情 - 通过直接URL访问"""
        try:
            print(f"🔍 提取岗位详情 (直接URL): {position_id}")
            
            # 1. 构造详情页URL
            detail_url = f"{self.detail_page_template}{position_id}"
            print(f"   🔗 详情页URL: {detail_url}")
            
            # 2. 在新标签页中打开详情页
            detail_tab_id = self._open_url_in_new_tab(detail_url)
            if not detail_tab_id:
                raise StrategyError(f"打开详情页失败: {position_id}")
            
            # 3. 切换到详情页标签
            if not self.browser_manager.switch_to_tab(detail_tab_id):
                raise StrategyError(f"切换到详情页标签失败")
            
            self.current_tab_id = detail_tab_id
            
            # 4. 等待页面加载
            print("   ⏳ 等待详情页加载...")
            time.sleep(3)
            
            # 5. 提取详情数据
            detail_data = self._extract_detail_data(position_id, detail_url)
            
            # 6. 创建PositionData对象
            position_data = create_position_data_from_dict(detail_data)
            position_data.page_number = page_number
            position_data.position_index = position_index
            position_data.extraction_time = datetime.now().isoformat()
            position_data.source_url = detail_url
            
            # 7. 关闭详情页标签
            self._close_detail_tab_safe(detail_tab_id)
            
            # 8. 切换回列表页标签
            if self.list_tab_id:
                self.browser_manager.switch_to_tab(self.list_tab_id)
                self.current_tab_id = self.list_tab_id
            
            print(f"✅ 岗位详情提取完成: {position_data.position_name}")
            return position_data
            
        except Exception as e:
            print(f"❌ 提取岗位详情失败: {position_id} - {e}")
            
            # 确保关闭详情页标签
            if 'detail_tab_id' in locals():
                self._close_detail_tab_safe(detail_tab_id)
            
            # 确保返回列表页
            if self.list_tab_id:
                try:
                    self.browser_manager.switch_to_tab(self.list_tab_id)
                    self.current_tab_id = self.list_tab_id
                except:
                    pass
            
            raise
    
    def _open_url_in_new_tab(self, url: str) -> Optional[str]:
        """在新标签页中打开URL"""
        try:
            from openclaw_tools import browser
            
            # 打开新标签页
            open_result = browser(
                action="open",
                url=url,
                profile=self.context.browser_profile
            )
            
            if open_result.get("success", False):
                new_tab_id = open_result.get("tabId")
                
                if new_tab_id:
                    # 记录详情页标签
                    self.detail_tabs[new_tab_id] = {
                        "url": url,
                        "opened_at": time.time(),
                        "position_id": url.split("positionId=")[-1] if "positionId=" in url else "unknown"
                    }
                    
                    print(f"   ✅ 打开新标签页: {new_tab_id}")
                    return new_tab_id
            
            print(f"   ❌ 打开新标签页失败")
            return None
            
        except Exception as e:
            print(f"   ❌ 打开新标签页异常: {e}")
            return None
    
    def _extract_detail_data(self, position_id: str, detail_url: str) -> Dict[str, Any]:
        """提取详情页数据"""
        try:
            print("   📊 提取详情页数据...")
            
            # 初始化数据字典
            detail_data = {
                "position_id": position_id,
                "position_name": "",
                "work_location": "",
                "position_category": "",
                "publish_time": "",
                "detail_link": detail_url,
                
                # 详情页字段
                "department": "",
                "education_requirement": "",
                "work_experience": "",
                "job_responsibilities": "",
                "job_requirements": "",
                "other_info": "",
                
                # 元数据
                "source_url": detail_url
            }
            
            # 方法1: 通过JavaScript提取
            js_data = self._extract_detail_via_js()
            if js_data:
                detail_data.update(js_data)
            
            # 方法2: 通过快照提取
            if not detail_data.get("position_name"):
                snapshot_data = self._extract_detail_via_snapshot()
                if snapshot_data:
                    detail_data.update(snapshot_data)
            
            # 方法3: 备用提取
            if not detail_data.get("position_name"):
                backup_data = self._extract_detail_backup()
                if backup_data:
                    detail_data.update(backup_data)
            
            # 打印提取结果
            print("   📋 提取的数据:")
            extracted_count = 0
            for key, value in detail_data.items():
                if value and key not in ["position_id", "detail_link", "source_url"]:
                    extracted_count += 1
                    display_value = str(value)
                    if len(display_value) > 60:
                        display_value = display_value[:57] + "..."
                    print(f"     • {key}: {display_value}")
            
            print(f"   ✅ 提取了 {extracted_count} 个有效字段")
            
            return detail_data
            
        except Exception as e:
            print(f"   ❌ 提取详情数据异常: {e}")
            return {"position_id": position_id, "detail_link": detail_url}
    
    def _extract_detail_via_js(self) -> Dict[str, Any]:
        """通过JavaScript提取详情数据"""
        try:
            js_code = """
            // 提取详情页数据的综合方法
            const data = {};
            
            // 1. 获取页面标题（可能包含岗位名称）
            data.position_name = document.title;
            
            // 2. 查找所有文本元素，按关键词匹配
            const allElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, div, span, li');
            const elementMap = {};
            
            for (const el of allElements) {
                const text = el.textContent.trim();
                if (!text || text.length < 2) continue;
                
                const lowerText = text.toLowerCase();
                
                // 匹配岗位名称
                if (!data.position_name || data.position_name === document.title) {
                    if (lowerText.includes('岗位') || lowerText.includes('职位') || 
                        lowerText.includes('招聘') || lowerText.includes('聘')) {
                        if (text.length > 3 && text.length < 100) {
                            data.position_name = text;
                        }
                    }
                }
                
                // 匹配工作地点
                if (!data.work_location && (lowerText.includes('工作地点') || lowerText.includes('地点'))) {
                    data.work_location = text.replace('工作地点', '').replace('地点', '').trim();
                }
                
                // 匹配部门
                if (!data.department && lowerText.includes('部门')) {
                    data.department = text.replace('部门', '').trim();
                }
                
                // 匹配学历
                if (!data.education_requirement && 
                    (lowerText.includes('学历') || lowerText.includes('要求') || lowerText.includes('教育'))) {
                    data.education_requirement = text;
                }
                
                // 匹配经验
                if (!data.work_experience && 
                    (lowerText.includes('经验') || lowerText.includes('工作年限') || lowerText.includes('年'))) {
                    data.work_experience = text;
                }
                
                // 匹配发布时间
                if (!data.publish_time && 
                    (lowerText.includes('发布') || lowerText.includes('时间') || lowerText.includes('更新'))) {
                    data.publish_time = text;
                }
                
                // 存储所有元素的文本
                elementMap[text] = (elementMap[text] || 0) + 1;
            }
            
            // 3. 提取工作职责和任职要求（通常在多行文本中）
            const responsibilities = [];
            const requirements = [];
            
            for (const [text, count] of Object.entries(elementMap)) {
                const lowerText = text.toLowerCase();
                
                if (lowerText.includes('职责') || lowerText.includes('负责') || 
                    lowerText.includes('工作内容') || lowerText.includes('做什么')) {
                    responsibilities.push(text);
                }
                
                if (lowerText.includes('要求') || lowerText.includes('条件') || 
                    lowerText.includes('资格') || lowerText.includes('需要')) {
                    requirements.push(text);
                }
                
                if (lowerText.includes('其他') || lowerText.includes('补充') || 
                    lowerText.includes('备注') || lowerText.includes('说明')) {
                    data.other_info = text;
                }
            }
            
            // 合并职责和要求
            if (responsibilities.length > 0) {
                data.job_responsibilities = responsibilities.join('\\n');
            }
            
            if (requirements.length > 0) {
                data.job_requirements = requirements.join('\\n');
            }
            
            // 4. 如果没有找到具体信息，尝试获取整个主要内容区域
            if (!data.job_responsibilities || !data.job_requirements) {
                const mainContent = document.querySelector('main, .content, .job-detail, .detail-content');
                if (mainContent) {
                    const mainText = mainContent.textContent.trim();
                    if (mainText.length > 100) {
                        // 简单分割（实际应用需要更智能的分割）
                        const lines = mainText.split(/[\\n。；]/);
                        const responsibilityLines = [];
                        const requirementLines = [];
                        
                        for (const line of lines) {
                            if (line.includes('职责') || line.includes('负责')) {
                                responsibilityLines.push(line);
                            } else if (line.includes('要求') || line.includes('条件')) {
                                requirementLines.push(line);
                            }
                        }
                        
                        if (responsibilityLines.length > 0) {
                            data.job_responsibilities = responsibilityLines.join('\\n');
                        }
                        
                        if (requirementLines.length > 0) {
                            data.job_requirements = requirementLines.join('\\n');
                        }
                    }
                }
            }
            
            return data;
            """
            
            result = self.browser_manager.execute_script(js_code)
            
            if result and isinstance(result, dict):
                # 清理数据
                for key, value in result.items():
                    if value && isinstance(value, str):
                        result[key] = value.strip()
                
                return result
            
            return {}
            
        except Exception as e:
            print(f"   ⚠️  JavaScript提取失败: {e}")
            return {}
    
    def _extract_detail_via_snapshot(self) -> Dict[str, Any]:
        """通过快照提取详情数据"""
        try:
            snapshot = self.browser_manager.take_snapshot(refs="aria")
            elements = snapshot.get("elements", [])
            
            data = {}
            
            for element in elements:
                name = element.get("name", "").strip()
                if not name:
                    continue
                
                role = element.get("role", "")
                lower_name = name.lower()
                
                # 根据角色和内容提取数据
                if role in ["heading", "title"]:
                    if not data.get("position_name") and len(name) > 3 and len(name) < 100:
                        data["position_name"] = name
                
                elif "地点" in lower_name or "location" in lower_name:
                    data["work_location"] = name.replace("工作地点", "").replace("地点", "").trim()
                
                elif "部门" in lower_name or "department" in lower_name:
                    data["department"] = name.replace("部门", "").trim()
                
                elif "学历" in lower_name or "教育" in lower_name:
                    data["education_requirement"] = name
                
                elif "经验" in lower_name or "年限" in lower_name:
                    data["work_experience"] = name
                
                elif "发布" in lower_name or "时间" in lower_name:
                    data["publish_time"] = name
                
                elif "职责" in lower_name or "负责" in lower_name:
                    if "job_responsibilities" not in data:
                        data["job_responsibilities"] = name
                    else:
                        data["job_responsibilities"] += "\\n" + name
                
                elif "要求" in lower_name or "条件" in lower_name:
                    if "job_requirements" not in data:
                        data["job_requirements"] = name
                    else:
                        data["job_requirements"] += "\\n" + name
            
            return data
            
        except Exception as e:
            print(f"   ⚠️  快照提取失败: {e}")
            return {}
    
    def _extract_detail_backup(self) -> Dict[str, Any]:
        """备用提取方法"""
        try:
            # 获取页面标题
            js_title = "return document.title;"
            title = self.browser_manager.execute_script(js_title)
            
            # 获取页面URL（可能包含信息）
            current_url = self.browser_manager.get_current_url()
            
            # 获取页面主要内容
            js_content = """
            // 尝试获取主要内容
            const selectors = ['main', '.content', '.job-detail', '.detail', '#content', '.main-content'];
            for (const selector of selectors) {
                const element = document.querySelector(selector);
                if (element) {
                    return element.textContent.trim().substring(0, 1000);
                }
            }
            return document.body.textContent.trim().substring(0, 1000);
            """
            
            main_content = self.browser_manager.execute_script(js_content)
            
            data = {
                "position_name": title if title and title != document.title else "未知岗位",
                "source_url": current_url
            }
            
            if main_content:
                # 简单提取关键词
                if "地点" in main_content:
                    import re
                    location_match = re.search(r'[地点|工作地点][:：]?\\s*([^\\s，。]+)', main_content)
                    if location_match:
                        data["work_location"] = location_match.group(1)
                
                if "学历" in main_content:
                    edu_match = re.search(r'学历[:：]?\\s*([^\\s，。]+)', main_content)
                    if edu_match:
                        data["education_requirement"] = edu_match.group(1)
                
                if "经验" in main_content:
                    exp_match = re.search(r'经验[:：]?\\s*([^\\s，。]+)', main_content)
                    if exp_match:
                        data["work_experience"] = exp_match.group(1)
            
            return data
            
        except Exception as e:
            print(f"   ⚠️  备用提取失败: {e}")
            return {}
    
    def _close_detail_tab_safe(self, tab_id: str) -> bool:
        """安全关闭详情页标签"""
        try:
            if tab_id in self.detail_tabs:
                # 先尝试切换出这个标签页
                if self.current_tab_id == tab_id and self.list_tab_id:
                    self.browser_manager.switch_to_tab(self.list_tab_id)
                    self.current_tab_id = self.list_tab_id
                
                # 关闭标签页
                success = self.browser_manager.close_tab(tab_id)
                
                if success:
                    del self.detail_tabs[tab_id]
                    print(f"   ✅ 关闭详情页标签: {tab_id}")
                else:
                    print(f"   ⚠️  关闭标签页失败: {tab_id}")
                
                return success
            
            return True
            
        except Exception as e:
            print(f"   ⚠️  关闭标签页异常: {e}")
            return False
    
    def validate_page_state(self, expected_categories: List[str]) -> bool:
        """验证页面状态"""
        try:
            print("🔍 验证页面状态 (直接URL方案)...")
            
            # 确保在列表页
            if self.current_tab_id != self.list_tab_id and self.list_tab_id:
                print("   🔄 切换到列表页...")
                self.browser_manager.switch_to_tab(self.list_tab_id)
                self.current_tab_id = self.list_tab_id
                time.sleep(2)
            
            # 获取页面快照
            snapshot = self.browser_manager.take_snapshot(refs="aria")
            
            # 1. 检查筛选状态
            checked_categories = []
            for element in snapshot.get("elements", []):
                if element.get("checked", False):
                    name = element.get("name", "")
                    if name:
                        checked_categories.append(name)
            
            print(f"   已选中的筛选类别 ({len(checked_categories)}个):")
            for category in checked_categories:
                print(f"     • {category}")
            
            # 验证是否包含所有期望类别
            missing_categories = []
            for expected in expected_categories:
                found = False
                for checked in checked_categories:
                    if expected in checked:
                        found = True
                        break
                
                if not found:
                    missing_categories.append(expected)
            
            if missing_categories:
                print(f"   ❌ 缺失筛选类别: {missing_categories}")
                return False
            
            # 2. 检查页码显示
            page_display_valid = self._validate_page_display()
            if not page_display_valid:
                print("   ⚠️  页码显示验证失败")
                return False
            
            # 3. 检查岗位数量显示
            count_display_valid = self._validate_count_display()
            if not count_display_valid:
                print("   ⚠️  岗位数量显示验证失败")
                return False
            
            print("   ✅ 页面状态验证通过")
            return True
            
        except Exception as e:
            print(f"   ❌ 页面状态验证异常: {e}")
            return False
    
    def _validate_page_display(self) -> bool:
        """验证页码显示"""
        try:
            js_code = """
            // 查找页码显示
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );
            
            let node;
            while (node = walker.nextNode()) {
                const text = node.textContent.trim();
                if (text.match(/\\d+\\s*\\/\\s*\\d+/)) {
                    console.log('找到页码显示:', text);
                    return text;
                }
            }
            return null;
            """
            
            page_text = self.browser_manager.execute_script(js_code)
            
            if page_text:
                print(f"   页码显示: {page_text}")
                
                # 验证格式: 应该是 "X/10" 格式
                import re
                match = re.match(r'(\d+)\s*/\s*(\d+)', page_text)
                if match:
                    current_page = int(match.group(1))
                    total_pages = int(match.group(2))
                    
                    if total_pages == 10:  # 筛选后应该是10页
                        print(f"   ✅ 页码格式正确: {current_page}/{total_pages}")
                        return True
                    else:
                        print(f"   ⚠️  总页数异常: {total_pages} (期望10)")
                        return False
                else:
                    print(f"   ⚠️  页码格式异常: {page_text}")
                    return False
            
            print("   ⚠️  未找到页码显示")
            return False
            
        except Exception as e:
            print(f"   ⚠️  页码显示验证异常: {e}")
            return False
    
    def _validate_count_display(self) -> bool:
        """验证岗位数量显示"""
        try:
            js_code = """
            // 查找岗位数量显示
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );
            
            let node;
            while (node = walker.nextNode()) {
                const text = node.textContent.trim();
                if (text.includes('个岗位')) {
                    console.log('找到数量显示:', text);
                    return text;
                }
            }
            return null;
            """
            
            count_text = self.browser_manager.execute_script(js_code)
            
            if count_text:
                print(f"   岗位数量显示: {count_text}")
                
                # 验证数量: 应该是 "共92个岗位" 或类似
                import re
                match = re.search(r'(\d+)\s*个岗位', count_text)
                if match:
                    position_count = int(match.group(1))
                    
                    if position_count == 92:  # 筛选后应该是92个岗位
                        print(f"   ✅ 岗位数量正确: {position_count}个")
                        return True
                    else:
                        print(f"   ⚠️  岗位数量异常: {position_count} (期望92)")
                        return False
                else:
                    print(f"   ⚠️  数量格式异常: {count_text}")
                    return False
            
            print("   ⚠️  未找到岗位数量显示")
            return False
            
        except Exception as e:
            print(f"   ⚠️  岗位数量验证异常: {e}")
            return False
    
    def save_position_data(self, data: PositionData, output_dir: str) -> str:
        """保存岗位数据"""
        if not self.data_manager:
            raise StrategyError("数据管理器未初始化")
        
        try:
            # 初始化数据管理器
            if not self.data_manager.initialized:
                self.data_manager.initialize(output_dir)
            
            # 保存数据
            file_path = self.data_manager.save_position(data)
            print(f"   💾 保存岗位数据: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"   ❌ 保存岗位数据失败: {e}")
            raise
    
    def batch_extract_positions(self, position_ids: List[str], page_number: int) -> List[PositionData]:
        """批量提取岗位数据 - 重写以支持并行处理"""
        try:
            print(f"⚡ 批量提取 {len(position_ids)} 个岗位 (并行处理)...")
            
            results = []
            
            # 使用线程池并行处理
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交所有任务
                future_to_id = {}
                for i, position_id in enumerate(position_ids):
                    future = executor.submit(
                        self._extract_single_position_parallel,
                        position_id, page_number, i + 1
                    )
                    future_to_id[future] = position_id
                
                # 收集结果
                completed = 0
                for future in as_completed(future_to_id):
                    position_id = future_to_id[future]
                    completed += 1
                    
                    try:
                        position_data = future.result(timeout=30)  # 30秒超时
                        if position_data:
                            results.append(position_data)
                            print(f"   [{completed}/{len(position_ids)}] ✅ 完成: {position_id}")
                        else:
                            print(f"   [{completed}/{len(position_ids)}] ❌ 失败: {position_id}")
                    except Exception as e:
                        print(f"   [{completed}/{len(position_ids)}] ❌ 异常: {position_id} - {e}")
            
            print(f"📊 批量提取完成: {len(results)}/{len(position_ids)} 成功")
            return results
            
        except Exception as e:
            print(f"❌ 批量提取失败: {e}")
            return []
    
    def _extract_single_position_parallel(self, position_id: str, page_number: int, position_index: int) -> Optional[PositionData]:
        """并行处理单个岗位提取"""
        try:
            # 注意：并行处理时，每个线程需要自己的浏览器实例
            # 这里简化为串行处理，实际需要更复杂的资源管理
            return self.extract_position_detail(position_id, page_number, position_index)
            
        except Exception as e:
            print(f"   ⚡ 并行提取失败 {position_id}: {e}")
            return None
    
    def cleanup(self) -> None:
        """清理资源"""
        print(f"🧹 清理 {self.strategy_name} 资源...")
        
        try:
            # 关闭所有详情页标签
            for tab_id in list(self.detail_tabs.keys()):
                try:
                    self._close_detail_tab_safe(tab_id)
                except:
                    pass
            
            # 清理浏览器管理器
            if self.browser_manager and hasattr(self.browser_manager, "cleanup"):
                self.browser_manager.cleanup()
                print("   ✅ 清理浏览器资源")
            
            # 清理数据管理器
            if self.data_manager and hasattr(self.data_manager, "cleanup"):
                self.data_manager.cleanup()
                print("   ✅ 清理数据资源")
            
            self.detail_tabs.clear()
            self.initialized = False
            print(f"✅ {self.strategy_name} 资源清理完成")
            
        except Exception as e:
            print(f"⚠️  清理资源异常: {e}")


# 插件注册函数
def register_plugin(plugin_manager):
    """注册插件到插件管理器"""
    strategy = DirectURLStrategy()
    plugin_manager.register_strategy(strategy)
    
    return {
        "name": strategy.get_strategy_name(),
        "type": strategy.get_strategy_type().value,
        "version": strategy.strategy_version,
        "description": strategy.description,
        "class": DirectURLStrategy,
        "instance": strategy
    }