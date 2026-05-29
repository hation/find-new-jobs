#!/usr/bin/env python3
# 🏗️ 夸克爬取器 - 点击方案插件
# 版本: 1.0
# 创建时间: 2026-05-19
# 基于: 现有 actual_crawler.py 代码重构

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.interfaces import (
    IExtractionStrategy, StrategyType, PositionData, PageState, ExecutionContext,
    create_position_data_from_dict, StrategyError, BrowserError
)
from core.plugin_manager import register_plugin


@register_plugin(StrategyType.CLICK_BASED)
class ClickBasedStrategy(IExtractionStrategy):
    """点击方案插件 - 基于现有代码重构"""
    
    def __init__(self):
        self.strategy_name = "点击方案插件"
        self.strategy_version = "1.0"
        self.browser_manager = None
        self.data_manager = None
        self.context = None
        self.initialized = False
        
        # 配置
        self.base_url = "https://zhaopin.quark.cn/"
        self.list_page_url = f"{self.base_url}campus"
        self.detail_page_template = f"{self.base_url}job/detail"
        
        # 状态跟踪
        self.current_tab_id = None
        self.detail_tabs = {}
        self.filter_categories = [
            "产品类", "运营类", "数据类", 
            "市场拓展", "销售类", "游戏类", "金融类"
        ]
        
        print(f"🧩 初始化 {self.strategy_name} v{self.strategy_version}")
    
    def get_strategy_type(self) -> StrategyType:
        return StrategyType.CLICK_BASED
    
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
            return True
            
        except Exception as e:
            print(f"❌ {self.strategy_name} 初始化失败: {e}")
            return False
    
    def _apply_filters(self) -> bool:
        """应用7个筛选类别"""
        try:
            # 获取页面快照
            snapshot = self.browser_manager.take_snapshot(refs="aria")
            elements = snapshot.get("elements", [])
            
            # 查找筛选元素
            filter_elements = []
            for element in elements:
                if element.get("role") in ["checkbox", "button"]:
                    name = element.get("name", "")
                    if any(category in name for category in self.filter_categories):
                        filter_elements.append(element)
            
            print(f"🔍 找到 {len(filter_elements)} 个筛选元素")
            
            # 点击每个筛选元素
            for element in filter_elements:
                element_ref = element.get("ref")
                element_name = element.get("name", "未知")
                
                if element_ref:
                    print(f"   📌 点击筛选: {element_name}")
                    
                    # 检查是否已选中
                    is_checked = element.get("checked", False)
                    if not is_checked:
                        if not self.browser_manager.click_element(element_ref):
                            print(f"   ⚠️  点击失败: {element_name}")
                    
                    # 添加延迟避免过快点击
                    time.sleep(0.5)
            
            # 等待筛选生效
            time.sleep(2)
            
            # 验证筛选结果
            snapshot_after = self.browser_manager.take_snapshot(refs="aria")
            
            # 查找筛选后的岗位数量显示
            for element in snapshot_after.get("elements", []):
                if element.get("role") == "status" or element.get("role") == "alert":
                    text = element.get("name", "")
                    if "个岗位" in text:
                        print(f"   📊 筛选结果: {text}")
                        break
            
            return True
            
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
            
            # 检查网络连接
            print("🌐 检查网络连接...")
            # 这里可以添加网络检查逻辑
            
            # 检查目标网站可访问性
            print("🔗 检查目标网站...")
            # 这里可以添加网站可访问性检查
            
            return issues
            
        except Exception as e:
            issues.append(f"环境验证异常: {e}")
            return issues
    
    def extract_list_page(self, page_number: int) -> List[str]:
        """提取列表页，返回position_id列表"""
        try:
            print(f"📄 提取第 {page_number} 页列表...")
            
            # 如果不在目标页码，先导航到目标页
            if page_number > 1:
                print(f"   🔄 翻页到第 {page_number} 页...")
                if not self._navigate_to_page(page_number):
                    raise StrategyError(f"导航到第 {page_number} 页失败")
            
            # 获取页面快照
            snapshot = self.browser_manager.take_snapshot(refs="aria")
            elements = snapshot.get("elements", [])
            
            # 查找岗位元素
            position_ids = []
            position_elements = []
            
            for element in elements:
                if element.get("role") == "link" and "job" in element.get("name", "").lower():
                    position_elements.append(element)
            
            print(f"🔍 找到 {len(position_elements)} 个岗位元素")
            
            # 提取position_id
            for i, element in enumerate(position_elements):
                try:
                    # 从链接中提取position_id
                    href = element.get("href", "")
                    if "positionId=" in href:
                        # 解析position_id
                        import urllib.parse
                        parsed_url = urllib.parse.urlparse(href)
                        query_params = urllib.parse.parse_qs(parsed_url.query)
                        
                        if "positionId" in query_params:
                            position_id = query_params["positionId"][0]
                            position_ids.append(position_id)
                            print(f"   [{i+1}] 发现岗位: {position_id}")
                        else:
                            print(f"   ⚠️  无法解析position_id: {href}")
                    else:
                        # 尝试从元素属性中提取
                        element_name = element.get("name", "")
                        # 这里可以添加更多提取逻辑
                        print(f"   ⚠️  链接格式异常: {element_name[:50]}...")
                        
                except Exception as e:
                    print(f"   ❌ 提取岗位元素失败: {e}")
                    continue
            
            if not position_ids:
                print("⚠️  未找到任何岗位ID，尝试备用提取方法...")
                position_ids = self._extract_position_ids_backup(elements)
            
            print(f"✅ 提取到 {len(position_ids)} 个岗位ID")
            return position_ids
            
        except Exception as e:
            print(f"❌ 提取列表页失败: {e}")
            return []
    
    def _extract_position_ids_backup(self, elements: List[Dict[str, Any]]) -> List[str]:
        """备用方法提取position_id"""
        position_ids = []
        
        try:
            # 执行JavaScript提取
            js_code = """
            // 提取所有岗位链接
            const jobLinks = [];
            document.querySelectorAll('a[href*="positionId"]').forEach(link => {
                const href = link.href;
                const match = href.match(/positionId=([^&]+)/);
                if (match) {
                    jobLinks.push({
                        id: match[1],
                        text: link.textContent.trim()
                    });
                }
            });
            return jobLinks;
            """
            
            result = self.browser_manager.execute_script(js_code)
            
            if result:
                for item in result:
                    position_ids.append(item["id"])
                    print(f"   🔍 JavaScript提取: {item['id']} - {item['text'][:30]}...")
            
        except Exception as e:
            print(f"   ⚠️  JavaScript提取失败: {e}")
        
        return position_ids
    
    def _navigate_to_page(self, target_page: int) -> bool:
        """导航到指定页码"""
        try:
            print(f"   📖 尝试翻页到第 {target_page} 页")
            
            # 首先获取当前页码
            current_page = self._get_current_page_number()
            print(f"   当前页码: {current_page}")
            
            # 如果已经在目标页，直接返回
            if current_page == target_page:
                print("   ✅ 已经在目标页码")
                return True
            
            # 计算翻页方向
            if target_page > current_page:
                # 向前翻页
                pages_to_go = target_page - current_page
                print(f"   需要向前翻 {pages_to_go} 页")
                
                for _ in range(pages_to_go):
                    if not self._click_next_page():
                        return False
                    time.sleep(2)  # 等待页面加载
            
            else:
                # 向后翻页
                pages_to_go = current_page - target_page
                print(f"   需要向后翻 {pages_to_go} 页")
                
                for _ in range(pages_to_go):
                    if not self._click_previous_page():
                        return False
                    time.sleep(2)  # 等待页面加载
            
            # 验证最终页码
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
            # 执行JavaScript获取页码
            js_code = """
            // 查找页码显示元素
            const pageElements = document.querySelectorAll('[class*="page"], [class*="pagination"]');
            for (const el of pageElements) {
                const text = el.textContent;
                const match = text.match(/(\\d+)\\s*\\/\\s*(\\d+)/);
                if (match) {
                    return parseInt(match[1]);
                }
            }
            return 1;
            """
            
            page_number = self.browser_manager.execute_script(js_code)
            return int(page_number) if page_number else 1
            
        except Exception as e:
            print(f"   ⚠️  获取页码失败: {e}")
            return 1
    
    def _click_next_page(self) -> bool:
        """点击下一页"""
        try:
            # 查找下一页按钮
            snapshot = self.browser_manager.take_snapshot(refs="aria")
            
            for element in snapshot.get("elements", []):
                name = element.get("name", "").lower()
                if "下一页" in name or "next" in name:
                    ref = element.get("ref")
                    if ref:
                        return self.browser_manager.click_element(ref)
            
            print("   ⚠️  未找到下一页按钮")
            return False
            
        except Exception as e:
            print(f"   ❌ 点击下一页失败: {e}")
            return False
    
    def _click_previous_page(self) -> bool:
        """点击上一页"""
        try:
            # 查找上一页按钮
            snapshot = self.browser_manager.take_snapshot(refs="aria")
            
            for element in snapshot.get("elements", []):
                name = element.get("name", "").lower()
                if "上一页" in name or "previous" in name:
                    ref = element.get("ref")
                    if ref:
                        return self.browser_manager.click_element(ref)
            
            print("   ⚠️  未找到上一页按钮")
            return False
            
        except Exception as e:
            print(f"   ❌ 点击上一页失败: {e}")
            return False
    
    def extract_position_detail(self, position_id: str, page_number: int, position_index: int) -> PositionData:
        """提取岗位详情"""
        try:
            print(f"🔍 提取岗位详情: {position_id}")
            
            # 1. 点击岗位链接
            if not self._click_position_link(position_id):
                raise StrategyError(f"点击岗位链接失败: {position_id}")
            
            # 2. 等待详情页加载
            time.sleep(3)
            
            # 3. 切换到详情页标签
            if not self._switch_to_detail_tab():
                raise StrategyError("切换到详情页失败")
            
            # 4. 提取详情数据
            detail_data = self._extract_detail_data(position_id)
            
            # 5. 创建PositionData对象
            position_data = create_position_data_from_dict(detail_data)
            position_data.page_number = page_number
            position_data.position_index = position_index
            position_data.extraction_time = datetime.now().isoformat()
            
            # 6. 关闭详情页标签，返回列表页
            self._close_detail_tab_and_return()
            
            print(f"✅ 岗位详情提取完成: {position_data.position_name}")
            return position_data
            
        except Exception as e:
            print(f"❌ 提取岗位详情失败: {position_id} - {e}")
            raise
    
    def _click_position_link(self, position_id: str) -> bool:
        """点击岗位链接"""
        try:
            # 查找包含position_id的链接
            js_code = f"""
            // 查找包含 positionId={position_id} 的链接
            const targetLink = document.querySelector(`a[href*="positionId={position_id}"]`);
            if (targetLink) {{
                targetLink.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                return targetLink.getAttribute('href');
            }}
            return null;
            """
            
            href = self.browser_manager.execute_script(js_code)
            
            if href:
                # 执行JavaScript点击
                click_js = f"""
                const link = document.querySelector(`a[href*="positionId={position_id}"]`);
                if (link) {{
                    link.click();
                    return true;
                }}
                return false;
                """
                
                clicked = self.browser_manager.execute_script(click_js)
                if clicked:
                    print(f"   ✅ 点击岗位链接: {position_id}")
                    return True
            
            # 如果JavaScript点击失败，尝试通过ref点击
            print(f"   ⚠️  JavaScript点击失败，尝试通过ref点击...")
            snapshot = self.browser_manager.take_snapshot(refs="aria")
            
            for element in snapshot.get("elements", []):
                if element.get("role") == "link":
                    element_href = element.get("href", "")
                    if position_id in element_href:
                        ref = element.get("ref")
                        if ref:
                            return self.browser_manager.click_element(ref)
            
            print(f"   ❌ 未找到岗位链接: {position_id}")
            return False
            
        except Exception as e:
            print(f"   ❌ 点击岗位链接异常: {e}")
            return False
    
    def _switch_to_detail_tab(self) -> bool:
        """切换到详情页标签"""
        try:
            # 获取所有标签页
            from openclaw_tools import browser
            
            tabs_result = browser(action="tabs", profile=self.context.browser_profile)
            tabs = tabs_result.get("tabs", [])
            
            # 找到最新打开的标签页（应该是详情页）
            if len(tabs) > 1:
                # 假设最后一个标签页是详情页
                detail_tab = tabs[-1]
                detail_tab_id = detail_tab.get("id")
                
                if detail_tab_id:
                    # 切换到详情页
                    self.browser_manager.switch_to_tab(detail_tab_id)
                    self.current_tab_id = detail_tab_id
                    
                    # 记录详情页标签
                    self.detail_tabs[detail_tab_id] = {
                        "url": detail_tab.get("url", ""),
                        "title": detail_tab.get("title", ""),
                        "opened_at": time.time()
                    }
                    
                    print(f"   ✅ 切换到详情页标签: {detail_tab_id}")
                    return True
            
            print("   ⚠️  未找到详情页标签")
            return False
            
        except Exception as e:
            print(f"   ❌ 切换详情页标签异常: {e}")
            return False
    
    def _extract_detail_data(self, position_id: str) -> Dict[str, Any]:
        """提取详情页数据"""
        try:
            # 获取详情页快照
            snapshot = self.browser_manager.take_snapshot(refs="aria")
            
            # 提取数据
            detail_data = {
                "position_id": position_id,
                "position_name": "",
                "work_location": "",
                "position_category": "",
                "publish_time": "",
                "detail_link": self.browser_manager.get_current_url(),
                
                # 详情页字段
                "department": "",
                "education_requirement": "",
                "work_experience": "",
                "job_responsibilities": "",
                "job_requirements": "",
                "other_info": "",
                
                # 元数据
                "source_url": self.browser_manager.get_current_url()
            }
            
            # 提取具体字段
            elements = snapshot.get("elements", [])
            
            # 1. 提取岗位名称
            for element in elements:
                name = element.get("name", "")
                if "岗位名称" in name or "职位名称" in name:
                    # 查找相邻的元素
                    # 这里需要根据实际页面结构调整
                    pass
            
            # 2. 执行JavaScript提取完整数据
            js_code = """
            // 提取详情页数据
            const data = {};
            
            // 岗位名称
            const titleElement = document.querySelector('h1, .job-title, [class*="title"]');
            if (titleElement) {
                data.position_name = titleElement.textContent.trim();
            }
            
            // 工作地点
            const locationElements = document.querySelectorAll('[class*="location"], [class*="address"]');
            for (const el of locationElements) {
                if (el.textContent.includes('工作地点') || el.textContent.includes('地点')) {
                    data.work_location = el.textContent.replace('工作地点', '').replace('地点', '').trim();
                    break;
                }
            }
            
            // 发布时间
            const timeElements = document.querySelectorAll('[class*="time"], [class*="date"]');
            for (const el of timeElements) {
                if (el.textContent.includes('发布时间') || el.textContent.includes('发布于')) {
                    data.publish_time = el.textContent.replace('发布时间', '').replace('发布于', '').trim();
                    break;
                }
            }
            
            // 部门信息
            const departmentElements = document.querySelectorAll('[class*="department"], [class*="dept"]');
            for (const el of departmentElements) {
                data.department = el.textContent.trim();
                break;
            }
            
            // 学历要求
            const educationElements = document.querySelectorAll('[class*="education"], [class*="degree"]');
            for (const el of educationElements) {
                data.education_requirement = el.textContent.trim();
                break;
            }
            
            // 工作经验
            const experienceElements = document.querySelectorAll('[class*="experience"], [class*="work-year"]');
            for (const el of experienceElements) {
                data.work_experience = el.textContent.trim();
                break;
            }
            
            // 工作职责
            const responsibilityElements = document.querySelectorAll('[class*="responsibility"], [class*="duty"]');
            for (const el of responsibilityElements) {
                data.job_responsibilities = el.textContent.trim();
                break;
            }
            
            // 任职要求
            const requirementElements = document.querySelectorAll('[class*="requirement"], [class*="qualification"]');
            for (const el of requirementElements) {
                data.job_requirements = el.textContent.trim();
                break;
            }
            
            // 其他信息
            const otherElements = document.querySelectorAll('[class*="other"], [class*="additional"]');
            for (const el of otherElements) {
                data.other_info = el.textContent.trim();
                break;
            }
            
            return data;
            """
            
            js_data = self.browser_manager.execute_script(js_code)
            
            if js_data:
                detail_data.update(js_data)
            
            # 打印提取的数据
            print(f"   📊 提取的数据:")
            for key, value in detail_data.items():
                if value and key not in ["position_id", "detail_link", "source_url"]:
                    print(f"     • {key}: {value[:50]}..." if len(str(value)) > 50 else f"     • {key}: {value}")
            
            return detail_data
            
        except Exception as e:
            print(f"   ❌ 提取详情数据异常: {e}")
            return {"position_id": position_id}
    
    def _close_detail_tab_and_return(self) -> bool:
        """关闭详情页标签并返回列表页"""
        try:
            if self.current_tab_id in self.detail_tabs:
                # 关闭详情页标签
                self.browser_manager.close_tab(self.current_tab_id)
                del self.detail_tabs[self.current_tab_id]
                print(f"   ✅ 关闭详情页标签: {self.current_tab_id}")
            
            # 切换回列表页标签
            # 假设第一个标签页是列表页
            from openclaw_tools import browser
            
            tabs_result = browser(action="tabs", profile=self.context.browser_profile)
            tabs = tabs_result.get("tabs", [])
            
            if tabs:
                list_tab_id = tabs[0].get("id")
                if list_tab_id:
                    self.browser_manager.switch_to_tab(list_tab_id)
                    self.current_tab_id = list_tab_id
                    print(f"   ✅ 切换回列表页标签: {list_tab_id}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ 关闭详情页标签异常: {e}")
            return False
    
    def validate_page_state(self, expected_categories: List[str]) -> bool:
        """验证页面状态"""
        try:
            print("🔍 验证页面状态...")
            
            # 获取页面快照
            snapshot = self.browser_manager.take_snapshot(refs="aria")
            
            # 检查筛选状态
            checked_categories = []
            for element in snapshot.get("elements", []):
                if element.get("role") in ["checkbox", "button"] and element.get("checked", False):
                    name = element.get("name", "")
                    if name:
                        checked_categories.append(name)
            
            print(f"   已选中的筛选类别: {checked_categories}")
            
            # 验证是否包含所有期望的类别
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
            
            # 检查页码显示
            print("   检查页码显示...")
            page_display_valid = self._validate_page_display()
            
            if not page_display_valid:
                print("   ⚠️  页码显示验证失败")
                return False
            
            print("   ✅ 页面状态验证通过")
            return True
            
        except Exception as e:
            print(f"   ❌ 页面状态验证异常: {e}")
            return False
    
    def _validate_page_display(self) -> bool:
        """验证页码显示"""
        try:
            # 执行JavaScript检查页码显示
            js_code = """
            // 检查页码显示
            const pageElements = document.querySelectorAll('[class*="page"], [class*="pagination"]');
            let foundValidDisplay = false;
            
            for (const el of pageElements) {
                const text = el.textContent;
                if (text.includes('/') && text.match(/\\d+\\s*\\/\\s*\\d+/)) {
                    foundValidDisplay = true;
                    console.log('找到页码显示:', text);
                    break;
                }
            }
            
            // 检查岗位数量显示
            const countElements = document.querySelectorAll('[class*="count"], [class*="total"]');
            let foundCountDisplay = false;
            
            for (const el of countElements) {
                const text = el.textContent;
                if (text.includes('个岗位') || text.includes('职位')) {
                    foundCountDisplay = true;
                    console.log('找到数量显示:', text);
                    break;
                }
            }
            
            return foundValidDisplay && foundCountDisplay;
            """
            
            result = self.browser_manager.execute_script(js_code)
            return bool(result)
            
        except Exception as e:
            print(f"   ⚠️  页码显示验证异常: {e}")
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
    
    def cleanup(self) -> None:
        """清理资源"""
        print(f"🧹 清理 {self.strategy_name} 资源...")
        
        try:
            # 关闭所有详情页标签
            for tab_id in list(self.detail_tabs.keys()):
                try:
                    self.browser_manager.close_tab(tab_id)
                    print(f"   ✅ 关闭标签页: {tab_id}")
                except Exception as e:
                    print(f"   ⚠️  关闭标签页失败 {tab_id}: {e}")
            
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
    strategy = ClickBasedStrategy()
    plugin_manager.register_strategy(strategy)
    
    return {
        "name": strategy.get_strategy_name(),
        "type": strategy.get_strategy_type().value,
        "version": strategy.strategy_version,
        "class": ClickBasedStrategy,
        "instance": strategy
    }