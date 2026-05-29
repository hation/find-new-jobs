#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实浏览器交互管理器 - 集成真实的 browser 工具调用
"""

import time
import random
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import json
import re

def log_info(msg: str):
    """记录信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

class RealBrowserManager:
    """真实浏览器交互管理器"""
    
    def __init__(self):
        self.current_tab_id = None
        self.list_page_tab_id = None
        self.detail_tabs = {}
        self.click_delay_range = (2, 4)  # 更保守的延迟范围，避免反爬
        self.page_load_wait = 3  # 页面加载等待时间
        
        log_info("真实浏览器管理器初始化完成")
    
    def set_click_delay(self, min_seconds: float, max_seconds: float):
        """设置点击延迟范围"""
        self.click_delay_range = (min_seconds, max_seconds)
        log_info(f"设置点击延迟范围: {min_seconds}-{max_seconds}秒")
    
    def random_delay(self):
        """随机延迟"""
        delay = random.uniform(*self.click_delay_range)
        log_info(f"随机延迟 {delay:.2f} 秒...")
        time.sleep(delay)
    
    def wait_for_page_load(self, custom_wait: Optional[float] = None):
        """等待页面加载"""
        wait_time = custom_wait or self.page_load_wait
        log_info(f"等待页面加载 {wait_time} 秒...")
        time.sleep(wait_time)
    
    def get_tabs_info(self) -> List[Dict[str, Any]]:
        """获取真实的标签页信息"""
        from browser import browser
        
        try:
            result = browser(action="tabs")
            if "tabs" in result:
                return result["tabs"]
            return []
        except Exception as e:
            log_info(f"获取标签页失败: {str(e)}")
            return []
    
    def switch_to_tab(self, tab_id: str) -> bool:
        """切换到指定标签页"""
        try:
            # 在实际浏览器工具中，可能需要通过其他方式切换标签页
            # 这里记录当前标签页ID
            self.current_tab_id = tab_id
            log_info(f"切换到标签页: {tab_id}")
            return True
        except Exception as e:
            log_info(f"切换标签页失败: {str(e)}")
            return False
    
    def get_current_snapshot(self, target_id: Optional[str] = None) -> Optional[str]:
        """获取当前页面的快照"""
        from browser import browser
        
        try:
            target = target_id or self.current_tab_id
            if not target:
                log_info("未指定目标标签页")
                return None
            
            snapshot_result = browser(
                action="snapshot",
                targetId=target,
                compact=True,
                maxChars=2000
            )
            
            if isinstance(snapshot_result, dict) and "content" in snapshot_result:
                return snapshot_result["content"]
            elif isinstance(snapshot_result, str):
                return snapshot_result
            
            return str(snapshot_result)
            
        except Exception as e:
            log_info(f"获取快照失败: {str(e)}")
            return None
    
    def click_position_and_open_detail(self, click_target: str, position_name: str) -> Optional[str]:
        """
        点击岗位打开详情页（使用真实 browser 工具）
        
        Args:
            click_target: 点击目标（ref或selector）
            position_name: 岗位名称
            
        Returns:
            新打开的详情页标签页ID
        """
        from browser import browser
        
        log_info(f"点击岗位: {position_name[:30]}...")
        
        try:
            # 1. 随机延迟避免反爬
            self.random_delay()
            
            # 2. 解析点击目标
            if click_target.startswith('text='):
                # 使用文本选择器
                selector = click_target[5:].strip("'\"")
                log_info(f"使用文本选择器: {selector[:50]}...")
                
                # 在实际中，可能需要使用不同的点击方式
                # 这里先尝试使用文本选择器
                click_config = {
                    "kind": "click",
                    "selector": f"text='{selector}'"
                }
            else:
                # 使用 ref
                log_info(f"使用 ref 点击: {click_target}")
                click_config = {
                    "kind": "click",
                    "ref": click_target
                }
            
            # 3. 执行点击
            log_info("执行点击操作...")
            click_result = browser(
                action="act",
                targetId=self.current_tab_id,
                request=click_config
            )
            
            if not click_result or "ok" not in str(click_result):
                log_info("点击可能未成功，等待新标签页...")
            
            # 4. 等待详情页加载
            self.wait_for_page_load()
            
            # 5. 获取新打开的标签页
            tabs = self.get_tabs_info()
            new_tabs = []
            
            for tab in tabs:
                tab_id = tab.get("tabId")
                url = tab.get("url", "")
                
                # 检查是否是详情页
                if "position-detail" in url and tab_id != self.current_tab_id:
                    if tab_id not in self.detail_tabs:
                        self.detail_tabs[tab_id] = {
                            "url": url,
                            "position_name": position_name,
                            "opened_time": datetime.now()
                        }
                        new_tabs.append(tab_id)
            
            if new_tabs:
                new_tab_id = new_tabs[0]
                log_info(f"详情页打开成功，标签页ID: {new_tab_id}")
                return new_tab_id
            else:
                log_info("未检测到新打开的详情页标签页")
                return None
                
        except Exception as e:
            log_info(f"点击岗位失败: {str(e)}")
            return None
    
    def get_detail_page_info(self, detail_tab_id: str) -> Dict[str, Any]:
        """获取详情页信息（URL和快照）"""
        from browser import browser
        
        log_info(f"获取详情页信息: {detail_tab_id}")
        
        try:
            # 1. 获取标签页URL
            tabs = self.get_tabs_info()
            detail_url = None
            
            for tab in tabs:
                if tab.get("tabId") == detail_tab_id:
                    detail_url = tab.get("url")
                    break
            
            if not detail_url:
                log_info(f"未找到详情页URL: {detail_tab_id}")
                return {"error": "未找到详情页URL"}
            
            # 2. 切换到详情页标签页
            self.switch_to_tab(detail_tab_id)
            self.wait_for_page_load(1)  # 短暂等待
            
            # 3. 获取详情页快照
            detail_snapshot = self.get_current_snapshot(detail_tab_id)
            
            if not detail_snapshot:
                log_info("获取详情页快照失败")
                return {
                    "url": detail_url,
                    "snapshot": None,
                    "error": "获取快照失败"
                }
            
            log_info(f"详情页信息获取成功，URL: {detail_url[:80]}...")
            log_info(f"详情页快照长度: {len(detail_snapshot)} 字符")
            
            return {
                "url": detail_url,
                "snapshot": detail_snapshot,
                "snapshot_length": len(detail_snapshot)
            }
            
        except Exception as e:
            log_info(f"获取详情页信息失败: {str(e)}")
            return {"error": str(e)}
    
    def close_detail_tab(self, detail_tab_id: str) -> bool:
        """关闭详情页标签页"""
        from browser import browser
        
        log_info(f"关闭详情页标签页: {detail_tab_id}")
        
        try:
            # 在实际浏览器工具中，关闭标签页可能需要特定操作
            # 这里先尝试切换到列表页，然后记录关闭
            
            # 切换回列表页
            if self.list_page_tab_id:
                self.switch_to_tab(self.list_page_tab_id)
                log_info(f"已切换回列表页: {self.list_page_tab_id}")
            
            # 从记录中移除
            if detail_tab_id in self.detail_tabs:
                del self.detail_tabs[detail_tab_id]
            
            # 随机延迟
            self.random_delay()
            
            return True
            
        except Exception as e:
            log_info(f"关闭标签页失败: {str(e)}")
            return False
    
    def batch_process_positions(self, position_links: List[Dict[str, Any]], 
                               list_page_tab_id: str,
                               max_positions: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        批量处理岗位详情页（真实浏览器交互）
        
        Args:
            position_links: 岗位链接信息列表
            list_page_tab_id: 列表页标签页ID
            max_positions: 最大处理数量
            
        Returns:
            处理后的详情页数据列表
        """
        from detail_extractor import extract_detail_fields
        
        log_info(f"开始批量处理岗位详情页，共 {len(position_links)} 个岗位")
        
        # 设置列表页
        self.list_page_tab_id = list_page_tab_id
        self.current_tab_id = list_page_tab_id
        
        results = []
        processed_count = 0
        
        for i, position in enumerate(position_links, 1):
            if max_positions and processed_count >= max_positions:
                log_info(f"已达到最大处理数量 {max_positions}，停止处理")
                break
            
            log_info(f"处理第 {i}/{len(position_links)} 个岗位: {position['岗位名称'][:40]}...")
            
            try:
                # 1. 确保在列表页
                if self.current_tab_id != list_page_tab_id:
                    self.switch_to_tab(list_page_tab_id)
                    self.wait_for_page_load(1)
                
                # 2. 点击打开详情页
                detail_tab_id = self.click_position_and_open_detail(
                    position['点击目标'], 
                    position['岗位名称']
                )
                
                if not detail_tab_id:
                    log_info(f"点击失败，跳过岗位: {position['岗位名称']}")
                    results.append({
                        '序号': i,
                        '岗位名称': position['岗位名称'],
                        '处理状态': '失败',
                        '错误信息': '点击失败',
                        '处理时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    continue
                
                # 3. 获取详情页信息
                detail_info = self.get_detail_page_info(detail_tab_id)
                
                if "error" in detail_info:
                    log_info(f"获取详情页信息失败: {detail_info['error']}")
                    results.append({
                        '序号': i,
                        '岗位名称': position['岗位名称'],
                        '处理状态': '失败',
                        '错误信息': detail_info['error'],
                        '处理时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    continue
                
                # 4. 提取详情页字段
                detail_fields = extract_detail_fields(
                    detail_info['snapshot'],
                    detail_info['url']
                )
                
                # 5. 创建结果数据
                result = {
                    '序号': i,
                    '岗位名称': position['岗位名称'],
                    '点击目标': position['点击目标'],
                    '详情页标签页': detail_tab_id,
                    '详情页URL': detail_info['url'],
                    '详情页快照长度': detail_info.get('snapshot_length', 0),
                    '岗位id': detail_fields.get('岗位id', '未提取'),
                    '所属部门': detail_fields.get('所属部门', '未提取'),
                    '学历': detail_fields.get('学历', '未提取'),
                    '工作年限': detail_fields.get('工作年限', '未提取'),
                    '职位描述_preview': detail_fields.get('职位描述', '未提取')[:100] + '...' if detail_fields.get('职位描述') and len(detail_fields['职位描述']) > 100 else detail_fields.get('职位描述', '未提取'),
                    '职位要求_preview': detail_fields.get('职位要求', '未提取')[:100] + '...' if detail_fields.get('职位要求') and len(detail_fields['职位要求']) > 100 else detail_fields.get('职位要求', '未提取'),
                    '处理状态': '成功',
                    '处理时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                results.append(result)
                processed_count += 1
                
                # 6. 关闭详情页返回列表页
                self.close_detail_tab(detail_tab_id)
                
                log_info(f"✅ 第 {i} 个岗位处理完成")
                log_info(f"  岗位id: {result['岗位id']}")
                log_info(f"  所属部门: {result['所属部门']}")
                log_info(f"  学历: {result['学历']}")
                log_info(f"  工作年限: {result['工作年限']}")
                
            except Exception as e:
                log_info(f"❌ 处理失败: {str(e)}")
                import traceback
                traceback.print_exc()
                
                error_result = {
                    '序号': i,
                    '岗位名称': position.get('岗位名称', '未知'),
                    '处理状态': '失败',
                    '错误信息': str(e),
                    '处理时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                results.append(error_result)
        
        log_info(f"批量处理完成，成功 {processed_count}/{len(position_links)} 个岗位")
        return results

def test_real_browser():
    """测试真实浏览器交互"""
    print("=" * 60)
    print("真实浏览器交互测试")
    print("=" * 60)
    
    try:
        # 创建管理器实例
        manager = RealBrowserManager()
        
        # 测试获取标签页
        log_info("测试获取标签页...")
        tabs = manager.get_tabs_info()
        
        print(f"\n📋 当前标签页 ({len(tabs)} 个):")
        for i, tab in enumerate(tabs[:3], 1):  # 显示前3个
            title = tab.get('title', '无标题')[:30]
            url = tab.get('url', '无URL')[:50]
            tab_id = tab.get('tabId', '未知')
            print(f"  #{i} {title}...")
            print(f"    URL: {url}...")
            print(f"    ID: {tab_id}")
        
        # 测试配置
        manager.set_click_delay(1, 2)
        
        print("\n💡 真实浏览器交互准备就绪")
        print("  可以开始处理真实的岗位详情页数据")
        
        return manager
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    manager = test_real_browser()