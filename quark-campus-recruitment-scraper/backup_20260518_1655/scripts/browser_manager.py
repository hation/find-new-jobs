#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器交互管理器 - 处理标签页切换、点击、详情页获取
"""

import time
import random
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import json

def log_info(msg: str):
    """记录信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

class BrowserManager:
    """浏览器交互管理器"""
    
    def __init__(self):
        self.current_tab = None
        self.list_page_tab = None
        self.detail_tabs = []
        self.click_delay_range = (1, 3)  # 点击延迟范围（秒）
        self.page_load_wait = 2  # 页面加载等待时间（秒）
    
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
    
    def get_current_tab_info(self):
        """获取当前标签页信息（模拟）"""
        # 在实际实现中，这里会调用browser.tabs()获取真实标签页信息
        return {
            '当前标签页': self.current_tab,
            '列表页标签页': self.list_page_tab,
            '详情页标签页数量': len(self.detail_tabs)
        }
    
    def switch_to_list_page(self, tab_id: str):
        """切换到列表页标签页"""
        log_info(f"切换到列表页标签页: {tab_id}")
        self.current_tab = tab_id
        self.list_page_tab = tab_id
    
    def click_position_and_open_detail(self, click_target: str, position_name: str) -> Optional[str]:
        """
        点击岗位打开详情页（在新标签页）
        
        Args:
            click_target: 点击目标（ref或selector）
            position_name: 岗位名称（用于日志）
            
        Returns:
            新打开的详情页标签页ID，如果失败则返回None
        """
        log_info(f"点击岗位: {position_name[:30]}...")
        
        # 1. 随机延迟避免反爬
        self.random_delay()
        
        # 2. 点击岗位（在实际实现中，这里会调用browser.act()）
        log_info(f"执行点击: {click_target}")
        
        # 模拟点击成功，打开新标签页
        new_tab_id = f"detail_tab_{int(time.time())}_{random.randint(1000, 9999)}"
        self.detail_tabs.append(new_tab_id)
        
        # 3. 等待详情页加载
        self.wait_for_page_load()
        
        log_info(f"详情页打开成功，标签页ID: {new_tab_id}")
        return new_tab_id
    
    def switch_to_detail_tab(self, detail_tab_id: str):
        """切换到详情页标签页"""
        log_info(f"切换到详情页标签页: {detail_tab_id}")
        self.current_tab = detail_tab_id
    
    def get_detail_page_url(self, detail_tab_id: str) -> str:
        """获取详情页URL（模拟）"""
        # 在实际实现中，这里会调用browser.snapshot()或browser.tabs()获取真实URL
        # 模拟返回一个包含positionId的URL
        position_id = f"1000075{random.randint(10000, 99999)}"
        return f"https://talent.quark.cn/off-campus/position-detail?lang=zh&positionId={position_id}"
    
    def get_detail_page_snapshot(self, detail_tab_id: str) -> str:
        """获取详情页快照（模拟）"""
        # 在实际实现中，这里会调用browser.snapshot()获取真实快照
        position_id = f"1000075{random.randint(10000, 99999)}"
        
        # 模拟详情页内容
        mock_detail = f"""
职位详情
岗位名称: 千问事业部-AI Native 产品经理-北京
部门: 千问事业部-产品部
学历: 本科及以上
工作年限: 3-5年
工作地点: 北京

职位描述:
1. 负责AI Native产品的规划、设计和落地
2. 深入理解用户需求，制定产品迭代路线图
3. 与研发、设计、运营团队紧密合作，推动产品上线和迭代
4. 通过数据分析和用户反馈持续优化产品体验

职位要求:
1. 本科及以上学历，计算机、设计或相关专业优先
2. 3年以上互联网产品经理经验
3. 具备优秀的逻辑思维和数据分析能力
4. 熟悉AI技术发展趋势，对AI Native有深刻理解
5. 良好的沟通协调能力和团队合作精神

福利待遇:
- 具有竞争力的薪资和年终奖金
- 五险一金、补充医疗保险
- 年度体检、带薪年假
- 丰富的培训和发展机会

岗位ID: {position_id}
        """
        
        return mock_detail
    
    def close_detail_tab_and_return(self, detail_tab_id: str):
        """关闭详情页标签页并返回列表页"""
        log_info(f"关闭详情页标签页: {detail_tab_id}")
        
        # 从详情页标签列表中移除
        if detail_tab_id in self.detail_tabs:
            self.detail_tabs.remove(detail_tab_id)
        
        # 切换回列表页
        if self.list_page_tab:
            self.switch_to_list_page(self.list_page_tab)
            log_info("已切换回列表页")
        
        # 随机延迟，避免频繁操作
        self.random_delay()
    
    def batch_process_positions(self, position_links: List[Dict[str, Any]], 
                               max_positions: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        批量处理岗位详情页
        
        Args:
            position_links: 岗位链接信息列表
            max_positions: 最大处理数量（None表示全部）
            
        Returns:
            处理后的岗位数据列表
        """
        log_info(f"开始批量处理岗位详情页，共 {len(position_links)} 个岗位")
        
        results = []
        processed_count = 0
        
        for i, position in enumerate(position_links, 1):
            if max_positions and processed_count >= max_positions:
                log_info(f"已达到最大处理数量 {max_positions}，停止处理")
                break
            
            log_info(f"处理第 {i}/{len(position_links)} 个岗位: {position['岗位名称'][:40]}...")
            
            try:
                # 1. 点击打开详情页
                detail_tab_id = self.click_position_and_open_detail(
                    position['点击目标'], 
                    position['岗位名称']
                )
                
                if not detail_tab_id:
                    log_info(f"点击失败，跳过岗位: {position['岗位名称']}")
                    continue
                
                # 2. 切换到详情页
                self.switch_to_detail_tab(detail_tab_id)
                
                # 3. 获取详情页URL和快照
                detail_url = self.get_detail_page_url(detail_tab_id)
                detail_snapshot = self.get_detail_page_snapshot(detail_tab_id)
                
                # 4. 创建结果数据
                result = {
                    '序号': i,
                    '岗位名称': position['岗位名称'],
                    '点击目标': position['点击目标'],
                    '详情页标签页': detail_tab_id,
                    '详情页URL': detail_url,
                    '详情页快照长度': len(detail_snapshot),
                    '处理状态': '成功',
                    '处理时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                results.append(result)
                processed_count += 1
                
                # 5. 关闭详情页返回列表页
                self.close_detail_tab_and_return(detail_tab_id)
                
                log_info(f"✅ 第 {i} 个岗位处理完成")
                
            except Exception as e:
                log_info(f"❌ 处理失败: {str(e)}")
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

def test_browser_manager():
    """测试浏览器管理器"""
    print("=" * 60)
    print("浏览器交互管理器测试")
    print("=" * 60)
    
    # 创建管理器实例
    manager = BrowserManager()
    
    # 测试设置
    manager.set_click_delay(0.5, 1.5)
    
    # 模拟岗位链接数据
    test_position_links = [
        {
            '序号': 1,
            '岗位名称': '千问事业部-AI Native 产品经理-北京',
            '点击目标': 'text="千问事业部-AI Native 产品经理-北京"',
            '匹配策略': 'text_selector',
            '状态': '可点击'
        },
        {
            '序号': 2,
            '岗位名称': '千问事业部-AI 产品经理 - 千问语音Agent-北京/杭州',
            '点击目标': 'e55',
            '匹配策略': 'row_ref',
            '状态': '可点击'
        },
        {
            '序号': 3,
            '岗位名称': '千问事业部-用户产品经理-书旗小说APP',
            '点击目标': 'text="千问事业部-用户产品经理-书旗小说APP"',
            '匹配策略': 'text_selector',
            '状态': '可点击'
        }
    ]
    
    print("\n🔄 测试批量处理 (前2个岗位):")
    results = manager.batch_process_positions(test_position_links, max_positions=2)
    
    print("\n📋 处理结果:")
    for result in results:
        status_icon = '✅' if result['处理状态'] == '成功' else '❌'
        print(f"  {status_icon} #{result['序号']} {result['岗位名称'][:30]}...")
        print(f"    状态: {result['处理状态']}")
        if result['处理状态'] == '成功':
            print(f"    详情页URL: {result['详情页URL'][:50]}...")
            print(f"    详情页快照: {result['详情页快照长度']} 字符")
        else:
            print(f"    错误信息: {result.get('错误信息', '未知错误')}")
    
    print("\n💡 实际实现要点:")
    print("  1. 需要替换模拟函数为真实的browser工具调用")
    print("  2. 需要处理真实的标签页切换")
    print("  3. 需要获取真实的页面快照和URL")
    print("  4. 需要更完善的错误处理和重试机制")
    
    print("\n🔧 需要实现的真实函数:")
    print("  - browser.act(click, ref=...)  # 点击岗位")
    print("  - browser.tabs()  # 获取标签页列表")
    print("  - browser.snapshot(targetId=...)  # 获取页面快照")
    print("  - browser.open(url)  # 打开新页面")
    print("  - browser.close(tabId)  # 关闭标签页")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    
    return manager, results

if __name__ == "__main__":
    manager, results = test_browser_manager()