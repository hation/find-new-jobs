#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试脚本 - 只测试浏览器工具集成
目标：测试能否成功点击第1个岗位并获取详情页快照
"""

import json
import time
import random
import os
from datetime import datetime

def log_info(msg: str):
    """记录信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def log_success(msg: str):
    """记录成功信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"✅ [{timestamp}] {msg}")

def log_error(msg: str):
    """记录错误信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"❌ [{timestamp}] {msg}")

def random_delay(min_seconds: float = 2.0, max_seconds: float = 4.0) -> float:
    """随机延迟"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay

def test_browser_import():
    """测试浏览器工具导入"""
    print("=" * 60)
    print("🌐 测试浏览器工具导入")
    print("=" * 60)
    
    try:
        # 尝试导入浏览器工具
        from browser import browser
        log_success("浏览器工具导入成功")
        return browser
    except ImportError as e:
        log_error(f"浏览器工具导入失败: {e}")
        log_error("请确保在OpenClaw环境中运行此脚本")
        return None
    except Exception as e:
        log_error(f"导入异常: {e}")
        return None

def test_get_current_tabs(browser):
    """测试获取当前标签页"""
    print("\n" + "=" * 60)
    print("📋 测试获取当前标签页")
    print("=" * 60)
    
    try:
        log_info("获取当前所有标签页...")
        result = browser(action="tabs")
        
        if result and isinstance(result, dict):
            log_success(f"获取到标签页信息")
            
            # 解析标签页信息
            tabs = result.get('tabs', [])
            log_info(f"当前有 {len(tabs)} 个标签页")
            
            # 查找列表页标签页
            list_tab = None
            for tab in tabs:
                title = tab.get('title', '')
                url = tab.get('url', '')
                tab_id = tab.get('suggestedTargetId', '')
                
                log_info(f"标签页 {tab_id}: {title[:30]}...")
                
                if 'position-list' in url or '千问' in title:
                    list_tab = tab
                    log_success(f"找到列表页标签页: {tab_id} - {title}")
            
            if list_tab:
                return list_tab.get('suggestedTargetId', 't5')  # 默认t5
            else:
                log_warning("未找到列表页标签页，使用默认t5")
                return 't5'
        else:
            log_error("获取标签页失败")
            return None
            
    except Exception as e:
        log_error(f"获取标签页异常: {e}")
        return None

def test_get_list_snapshot(browser, list_tab_id: str):
    """测试获取列表页快照"""
    print("\n" + "=" * 60)
    print("📸 测试获取列表页快照")
    print("=" * 60)
    
    try:
        log_info(f"获取列表页 {list_tab_id} 快照...")
        
        result = browser(
            action="snapshot",
            targetId=list_tab_id,
            compact=True,
            maxChars=2000
        )
        
        if result and isinstance(result, str) and len(result) > 100:
            log_success(f"获取列表页快照成功，长度: {len(result)} 字符")
            
            # 简单分析快照内容
            lines = result.split('\n')
            log_info(f"快照包含 {len(lines)} 行")
            
            # 查找岗位信息
            position_count = 0
            for line in lines[:50]:  # 只检查前50行
                if '千问事业部-' in line or '阿里千问' in line:
                    position_count += 1
                    log_info(f"找到岗位: {line[:50]}...")
            
            log_info(f"共找到 {position_count} 个岗位")
            return result
        else:
            log_error(f"获取列表页快照失败: {result}")
            return None
            
    except Exception as e:
        log_error(f"获取快照异常: {e}")
        return None

def test_click_first_position(browser, list_tab_id: str, position_name: str):
    """测试点击第一个岗位"""
    print("\n" + "=" * 60)
    print("🖱️ 测试点击第一个岗位")
    print("=" * 60)
    
    try:
        log_info(f"点击岗位: {position_name}")
        
        # 随机延迟
        delay = random_delay(2.0, 3.0)
        log_info(f"随机延迟: {delay:.2f}秒")
        
        # 尝试点击
        result = browser(
            action="act",
            targetId=list_tab_id,
            request={"kind": "click", "selector": f"text='{position_name}'"}
        )
        
        if result and 'ok' in str(result):
            log_success("岗位点击成功")
            
            # 等待详情页加载
            log_info("等待详情页加载...")
            time.sleep(3)
            
            return True
        else:
            log_error(f"岗位点击失败: {result}")
            return False
            
    except Exception as e:
        log_error(f"点击岗位异常: {e}")
        return False

def test_get_detail_snapshot(browser):
    """测试获取详情页快照"""
    print("\n" + "=" * 60)
    print("📄 测试获取详情页快照")
    print("=" * 60)
    
    try:
        # 首先获取当前标签页，找到详情页
        log_info("获取当前标签页列表...")
        tabs_result = browser(action="tabs")
        
        if tabs_result and isinstance(tabs_result, dict):
            tabs = tabs_result.get('tabs', [])
            
            # 查找详情页标签页
            detail_tab = None
            for tab in tabs:
                title = tab.get('title', '')
                url = tab.get('url', '')
                tab_id = tab.get('suggestedTargetId', '')
                
                if 'position-detail' in url:
                    detail_tab = tab
                    log_success(f"找到详情页标签页: {tab_id} - {title}")
                    break
            
            if detail_tab:
                detail_tab_id = detail_tab.get('suggestedTargetId')
                
                # 获取详情页快照
                log_info(f"获取详情页 {detail_tab_id} 快照...")
                snapshot_result = browser(
                    action="snapshot",
                    targetId=detail_tab_id,
                    compact=True,
                    maxChars=4000
                )
                
                if snapshot_result and isinstance(snapshot_result, str):
                    log_success(f"获取详情页快照成功，长度: {len(snapshot_result)} 字符")
                    
                    # 检查是否包含关键字段
                    if '所属部门' in snapshot_result:
                        log_success("详情页包含'所属部门'字段")
                    if '学历' in snapshot_result:
                        log_success("详情页包含'学历'字段")
                    if '工作年限' in snapshot_result:
                        log_success("详情页包含'工作年限'字段")
                    if '职位描述' in snapshot_result:
                        log_success("详情页包含'职位描述'字段")
                    
                    return snapshot_result
                else:
                    log_error("获取详情页快照失败")
                    return None
            else:
                log_error("未找到详情页标签页")
                return None
        else:
            log_error("获取标签页列表失败")
            return None
            
    except Exception as e:
        log_error(f"获取详情页快照异常: {e}")
        return None

def extract_position_name_from_snapshot(snapshot: str) -> str:
    """从快照中提取第一个岗位名称"""
    if not snapshot:
        return "千问事业部-商业数据分析-信息流搜索业务-北京/广州"  # 默认
    
    lines = snapshot.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('千问事业部-') or line.startswith('阿里千问'):
            return line
    
    return "千问事业部-商业数据分析-信息流搜索业务-北京/广州"  # 默认

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始浏览器工具集成测试")
    print("=" * 60)
    
    # 测试1：导入浏览器工具
    browser = test_browser_import()
    if not browser:
        log_error("❌ 浏览器工具导入失败，测试终止")
        return False
    
    # 测试2：获取当前标签页
    list_tab_id = test_get_current_tabs(browser)
    if not list_tab_id:
        log_error("❌ 获取标签页失败，测试终止")
        return False
    
    # 测试3：获取列表页快照
    list_snapshot = test_get_list_snapshot(browser, list_tab_id)
    if not list_snapshot:
        log_error("❌ 获取列表页快照失败，测试终止")
        return False
    
    # 从快照中提取岗位名称
    position_name = extract_position_name_from_snapshot(list_snapshot)
    log_info(f"将测试点击的岗位: {position_name}")
    
    # 测试4：点击第一个岗位
    click_success = test_click_first_position(browser, list_tab_id, position_name)
    if not click_success:
        log_error("❌ 点击岗位失败")
        return False
    
    # 测试5：获取详情页快照
    detail_snapshot = test_get_detail_snapshot(browser)
    if not detail_snapshot:
        log_error("❌ 获取详情页快照失败")
        return False
    
    # 所有测试通过
    print("\n" + "=" * 60)
    print("🎉 所有浏览器工具测试通过！")
    print("=" * 60)
    
    print(f"\n✅ 已验证的功能:")
    print(f"   1. 浏览器工具导入 ✅")
    print(f"   2. 标签页管理 ✅")
    print(f"   3. 列表页快照获取 ✅")
    print(f"   4. 岗位点击 ✅")
    print(f"   5. 详情页快照获取 ✅")
    
    print(f"\n📝 下一步:")
    print(f"   1. 运行增强版爬取脚本 (actual_crawler_enhanced_with_browser.py)")
    print(f"   2. 处理第1页前3个岗位")
    print(f"   3. 验证完整的数据提取流程")
    
    return True

if __name__ == "__main__":
    try:
        success = run_all_tests()
        
        if success:
            print(f"\n💡 执行增强版爬取:")
            print(f"   cd ~/.openclaw/workspace/skills/quark-campus-recruitment-scraper/scripts")
            print(f"   python3 actual_crawler_enhanced_with_browser.py")
        else:
            print(f"\n⚠️ 浏览器工具测试失败，需要先解决问题")
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"\n\n❌ 测试执行异常: {e}")
        import traceback
        traceback.print_exc()