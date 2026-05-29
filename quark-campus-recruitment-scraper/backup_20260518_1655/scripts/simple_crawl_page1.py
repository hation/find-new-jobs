#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单爬取脚本 - 处理第1页前3个岗位的真实数据
直接在OpenClaw环境中运行
"""

import os
import json
import time
import re
from datetime import datetime

def log_info(msg: str):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def extract_position_id_from_url(url: str):
    pattern = r'positionId=([^&]+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def extract_detail_fields(snapshot_text: str, detail_url: str):
    """从详情页快照提取字段"""
    result = {
        '岗位id': extract_position_id_from_url(detail_url),
        '岗位详情链接': detail_url,
        '所属部门': '未提取',
        '学历': '未提取',
        '工作年限': '未提取',
        '职位描述': '未提取',
        '职位要求': '未提取'
    }
    
    lines = snapshot_text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # 提取所属部门
        if '所属部门:' in line:
            result['所属部门'] = line.split('所属部门:')[-1].strip()
        
        # 提取学历
        if '学历:' in line and '工作年限:' not in line:
            result['学历'] = line.split('学历:')[-1].strip()
        
        # 提取工作年限
        if '工作年限:' in line:
            result['工作年限'] = line.split('工作年限:')[-1].strip()
    
    # 提取职位描述
    desc_start = False
    desc_lines = []
    for line in lines:
        if '职位描述' in line:
            desc_start = True
            continue
        if '职位要求' in line:
            break
        if desc_start and line.strip():
            desc_lines.append(line.strip())
    
    if desc_lines:
        result['职位描述'] = ' '.join(desc_lines)
    
    # 提取职位要求
    req_start = False
    req_lines = []
    for line in lines:
        if '职位要求' in line:
            req_start = True
            continue
        if req_start and line.strip():
            req_lines.append(line.strip())
    
    if req_lines:
        result['职位要求'] = ' '.join(req_lines)
    
    return result

def main():
    print("=" * 60)
    print("简单爬取脚本 - 第1页前3个岗位")
    print("=" * 60)
    
    # 检查当前标签页
    log_info("检查浏览器标签页...")
    
    # 获取标签页列表
    from browser import browser as browser_tool
    
    tabs_result = browser_tool(action="tabs")
    if "tabs" not in tabs_result:
        print("❌ 无法获取标签页列表")
        return
    
    tabs = tabs_result["tabs"]
    print(f"✅ 当前标签页数量: {len(tabs)}")
    
    # 找到列表页标签页
    list_tab = None
    for tab in tabs:
        url = tab.get("url", "")
        if "position-list" in url:
            list_tab = tab
            break
    
    if not list_tab:
        print("❌ 未找到列表页标签页")
        return
    
    list_tab_id = list_tab.get("tabId")
    print(f"✅ 列表页标签页: {list_tab_id}")
    
    # 获取列表页快照
    log_info("获取列表页快照...")
    snapshot_result = browser_tool(
        action="snapshot",
        targetId=list_tab_id,
        compact=True,
        maxChars=1500
    )
    
    snapshot_text = str(snapshot_result)
    print(f"✅ 快照获取成功，长度: {len(snapshot_text)} 字符")
    
    # 检查筛选状态
    if "93个岗位" in snapshot_text:
        print("✅ 筛选条件已正确应用（93个岗位）")
    else:
        print("⚠️  筛选条件可能未正确应用")
    
    # 提取前3个岗位名称
    lines = snapshot_text.split('\n')
    positions = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('千问事业部-') and len(positions) < 3:
            positions.append(line)
    
    print(f"\n🎯 找到前3个岗位:")
    for i, pos in enumerate(positions, 1):
        print(f"  #{i} {pos}")
    
    # 处理这3个岗位
    results = []
    
    for i, position_name in enumerate(positions, 1):
        print(f"\n{'='*40}")
        print(f"处理第 {i} 个岗位: {position_name[:40]}...")
        print(f"{'='*40}")
        
        try:
            # 点击岗位
            log_info("点击岗位...")
            click_result = browser_tool(
                action="act",
                targetId=list_tab_id,
                request={
                    "kind": "click",
                    "selector": f"text='{position_name}'"
                }
            )
            
            print(f"✅ 点击结果: {click_result.get('ok', False)}")
            
            # 等待详情页加载
            time.sleep(3)
            
            # 获取新的标签页列表
            new_tabs_result = browser_tool(action="tabs")
            detail_tab = None
            detail_url = None
            
            if "tabs" in new_tabs_result:
                for tab in new_tabs_result["tabs"]:
                    url = tab.get("url", "")
                    if "position-detail" in url and tab.get("tabId") != list_tab_id:
                        detail_tab = tab.get("tabId")
                        detail_url = url
                        break
            
            if not detail_tab:
                print("❌ 未找到详情页标签页")
                results.append({
                    '序号': i,
                    '岗位名称': position_name,
                    '状态': '失败',
                    '错误': '未找到详情页'
                })
                continue
            
            print(f"✅ 详情页标签页: {detail_tab}")
            print(f"✅ 详情页URL: {detail_url}")
            
            # 获取详情页快照
            log_info("获取详情页快照...")
            detail_snapshot = browser_tool(
                action="snapshot",
                targetId=detail_tab,
                compact=True,
                maxChars=4000
            )
            
            detail_text = str(detail_snapshot)
            print(f"✅ 详情页快照长度: {len(detail_text)} 字符")
            
            # 提取字段
            detail_fields = extract_detail_fields(detail_text, detail_url)
            
            # 创建结果
            result = {
                '序号': i,
                '岗位名称': position_name,
                '状态': '成功',
                '岗位id': detail_fields['岗位id'],
                '所属部门': detail_fields['所属部门'],
                '学历': detail_fields['学历'],
                '工作年限': detail_fields['工作年限'],
                '职位描述_preview': detail_fields['职位描述'][:100] + '...' if detail_fields['职位描述'] != '未提取' and len(detail_fields['职位描述']) > 100 else detail_fields['职位描述'],
                '职位要求_preview': detail_fields['职位要求'][:100] + '...' if detail_fields['职位要求'] != '未提取' and len(detail_fields['职位要求']) > 100 else detail_fields['职位要求'],
                '详情页URL': detail_url,
                '处理时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            results.append(result)
            
            print(f"\n✅ 第{i}个岗位处理成功!")
            print(f"  岗位id: {result['岗位id']}")
            print(f"  所属部门: {result['所属部门']}")
            print(f"  学历: {result['学历']}")
            print(f"  工作年限: {result['工作年限']}")
            
            # 关闭详情页标签页（切换回列表页）
            try:
                browser_tool(
                    action="act",
                    targetId=list_tab_id,
                    request={"kind": "click", "selector": "text='职位列表'"}
                )
                time.sleep(2)
            except:
                print("⚠️  切换回列表页失败，继续处理")
            
        except Exception as e:
            print(f"❌ 处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            results.append({
                '序号': i,
                '岗位名称': position_name,
                '状态': '失败',
                '错误': str(e)
            })
    
    # 保存结果
    output_dir = "../output"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f"simple_crawl_page1_{timestamp}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ 结果保存到: {output_file}")
    
    # 总结
    success_count = sum(1 for r in results if r.get('状态') == '成功')
    
    print(f"\n📊 爬取总结:")
    print(f"  总测试岗位: {len(results)}")
    print(f"  成功: {success_count}")
    print(f"  失败: {len(results) - success_count}")
    
    if success_count > 0:
        print(f"\n🔍 成功提取的字段:")
        for field in ['岗位id', '所属部门', '学历', '工作年限']:
            extracted = sum(1 for r in results if r.get('状态') == '成功' and r.get(field) not in ['未提取', None])
            print(f"  {field}: {extracted}/{success_count}")
    
    print(f"\n💡 下一步:")
    print("  1. 查看生成的文件验证数据质量")
    print("  2. 调整字段提取逻辑（如果需要）")
    print("  3. 扩展到更多岗位和页面")
    
    return results

if __name__ == "__main__":
    main()