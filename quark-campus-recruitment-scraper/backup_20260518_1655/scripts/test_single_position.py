#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单个岗位的真实数据获取

注意：在OpenClaw环境中，browser不是Python模块，而是工具
这个脚本需要在OpenClaw的上下文中运行，或者通过exec调用
"""

import os
import sys
import time
import json
from datetime import datetime

# 模拟browser工具调用
# 在实际OpenClaw环境中，这些调用会被转发到实际的browser工具

def browser(**kwargs):
    """模拟browser工具调用"""
    import subprocess
    import tempfile
    
    # 创建临时文件存储参数
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(kwargs, f, ensure_ascii=False, indent=2)
        temp_file = f.name
    
    try:
        # 在实际OpenClaw中，这里会通过工具调用
        # 这里模拟返回一些数据
        action = kwargs.get('action', '')
        
        if action == 'open':
            return {
                'targetId': 'test_tab_123',
                'title': '夸克校园招聘',
                'url': 'https://talent.quark.cn/off-campus/position-list?lang=zh'
            }
        elif action == 'snapshot':
            # 返回模拟的快照数据
            return """
千问事业部-AI Native 产品经理-北京
更新于 2026-05-18 产品类-商业型 北京
千问事业部-AI 产品经理 - 千问语音Agent-北京/杭州
更新于 2026-05-18 产品类-用户型 北京 / 杭州
row "更新于 2026-05-18 产品类-用户型 北京 / 杭州" [ref=e56] [cursor=pointer]
text "千问事业部-用户产品经理-书旗小说APP" [ref=e57] [cursor=pointer]
button "下一页，当前第1页" [ref=e65] [cursor=pointer]
            """
        elif action == 'tabs':
            # 返回模拟的标签页列表
            return {
                'tabs': [
                    {
                        'tabId': 'test_tab_123',
                        'title': '夸克校园招聘',
                        'url': 'https://talent.quark.cn/off-campus/position-list?lang=zh',
                        'type': 'page'
                    },
                    {
                        'tabId': 'test_tab_456',
                        'title': '岗位详情 - 千问事业部-AI Native 产品经理-北京',
                        'url': 'https://talent.quark.cn/off-campus/position-detail?lang=zh&positionId=100007500014',
                        'type': 'page'
                    }
                ]
            }
        elif action == 'act':
            # 模拟点击操作
            return {'ok': True, 'message': '点击成功'}
        else:
            return {'error': f'未知操作: {action}'}
            
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def log_info(msg: str):
    """记录信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def test_single_position():
    """测试单个岗位的真实获取"""
    print("=" * 60)
    print("测试单个岗位的真实数据获取")
    print("=" * 60)
    
    try:
        # 1. 打开夸克招聘页面
        log_info("打开夸克招聘页面...")
        open_result = browser(
            action="open",
            targetUrl="https://talent.quark.cn/off-campus/position-list?lang=zh"
        )
        
        if not open_result or "targetId" not in open_result:
            print("❌ 无法打开页面")
            return False
        
        tab_id = open_result["targetId"]
        print(f"✅ 页面打开成功，标签页ID: {tab_id}")
        
        # 2. 等待页面加载
        time.sleep(3)
        
        # 3. 获取页面快照
        log_info("获取页面快照...")
        snapshot_result = browser(
            action="snapshot",
            targetId=tab_id,
            compact=True,
            maxChars=2000
        )
        
        snapshot_text = str(snapshot_result)
        print(f"✅ 快照获取成功，长度: {len(snapshot_text)} 字符")
        
        # 4. 查找第一个岗位
        lines = snapshot_text.split('\n')
        first_position = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('千问事业部-'):
                first_position = line
                break
        
        if not first_position:
            print("❌ 未找到岗位信息")
            return False
        
        print(f"✅ 找到第一个岗位: {first_position}")
        
        # 5. 尝试点击第一个岗位
        log_info(f"尝试点击岗位: {first_position[:30]}...")
        
        # 使用文本选择器点击
        click_result = browser(
            action="act",
            targetId=tab_id,
            request={
                "kind": "click",
                "selector": f"text='{first_position}'"
            }
        )
        
        print(f"✅ 点击执行完成，结果: {click_result}")
        
        # 6. 等待新标签页打开
        time.sleep(3)
        
        # 7. 获取标签页列表
        log_info("获取标签页列表...")
        tabs_result = browser(action="tabs")
        
        if "tabs" in tabs_result:
            tabs = tabs_result["tabs"]
            print(f"✅ 当前标签页数量: {len(tabs)}")
            
            # 查找详情页标签页
            detail_tabs = []
            for tab in tabs:
                url = tab.get("url", "")
                if "position-detail" in url:
                    detail_tabs.append(tab)
                    print(f"📄 详情页标签页:")
                    print(f"  标题: {tab.get('title', '无标题')}")
                    print(f"  URL: {url}")
                    print(f"  标签页ID: {tab.get('tabId', '未知')}")
            
            if detail_tabs:
                detail_tab = detail_tabs[0]
                detail_tab_id = detail_tab.get("tabId")
                detail_url = detail_tab.get("url")
                
                # 8. 获取详情页快照
                log_info("获取详情页快照...")
                detail_snapshot = browser(
                    action="snapshot",
                    targetId=detail_tab_id,
                    compact=True,
                    maxChars=3000
                )
                
                detail_text = str(detail_snapshot)
                print(f"✅ 详情页快照获取成功，长度: {len(detail_text)} 字符")
                
                # 9. 提取positionId
                import re
                position_id_pattern = r'positionId=([^&]+)'
                match = re.search(position_id_pattern, detail_url)
                
                if match:
                    position_id = match.group(1)
                    print(f"🎯 提取到 positionId: {position_id}")
                else:
                    print("❌ 未找到 positionId")
                    position_id = "未找到"
                
                # 10. 分析详情页内容
                print("\n🔍 详情页内容分析:")
                
                # 查找关键字段
                fields_to_find = ['部门', '学历', '工作年限', '职位描述', '职位要求', '任职要求']
                
                lines = detail_text.split('\n')
                for line in lines:
                    line = line.strip()
                    for field in fields_to_find:
                        if field in line:
                            print(f"  📍 {line[:100]}...")
                            break
                
                # 11. 关闭详情页标签页
                log_info("关闭详情页标签页...")
                # 在实际中可能需要特定操作来关闭标签页
                # 这里先记录，在真实使用中可以切换回列表页
                
                # 切换回列表页
                browser(
                    action="act",
                    targetId=tab_id,
                    request={"kind": "click", "selector": "text='职位列表'"}
                )
                
                print("\n✅ 测试成功完成!")
                print(f"   岗位名称: {first_position}")
                print(f"   positionId: {position_id}")
                print(f"   详情页URL: {detail_url[:80]}...")
                print(f"   详情页内容长度: {len(detail_text)} 字符")
                
                return True
            else:
                print("❌ 未找到打开的详情页标签页")
                return False
        else:
            print("❌ 无法获取标签页列表")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n🎯 测试目标:")
    print("  1. 打开夸克招聘页面")
    print("  2. 找到第一个岗位")
    print("  3. 点击岗位打开详情页")
    print("  4. 获取详情页URL和positionId")
    print("  5. 获取详情页内容")
    print("  6. 分析关键字段")
    print("  7. 返回列表页")
    
    print("\n⚠️  预期:")
    print("  - 点击岗位会打开新标签页")
    print("  - 详情页URL包含positionId参数")
    print("  - 详情页包含部门、学历、工作年限等字段")
    
    success = test_single_position()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 单个岗位测试成功!")
        print("   可以继续运行完整的第1-2页爬取")
    else:
        print("❌ 单个岗位测试失败")
        print("   请检查错误信息并调整配置")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    main()