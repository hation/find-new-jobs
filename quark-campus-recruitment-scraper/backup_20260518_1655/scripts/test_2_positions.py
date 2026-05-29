#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试处理第1页前2个岗位的真实数据
"""

import os
import sys
import time
import json
import re
from datetime import datetime

def log_info(msg: str):
    """记录信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def extract_position_id_from_url(url: str):
    """从URL提取positionId"""
    pattern = r'positionId=([^&]+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def extract_detail_fields_from_snapshot(snapshot_text: str, detail_url: str):
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

def test_first_2_positions():
    """测试第1页前2个岗位"""
    print("=" * 60)
    print("测试第1页前2个岗位的真实数据获取")
    print("=" * 60)
    
    results = []
    
    try:
        # 先点击剩余5个类别
        log_info("点击剩余5个类别筛选...")
        categories = [
            ("数据类", "e17"),
            ("市场拓展", "e19"),
            ("销售类", "e21"),
            ("游戏类", "e29"),
            ("金融类", "e31")
        ]
        
        for cat_name, ref in categories:
            try:
                from browser import browser
                browser(
                    action="act",
                    targetId="t5",
                    request={"kind": "click", "ref": ref}
                )
                log_info(f"点击: {cat_name}")
                time.sleep(1)
            except Exception as e:
                log_info(f"点击失败 {cat_name}: {str(e)}")
        
        # 等待筛选生效
        time.sleep(3)
        
        # 获取页面快照
        from browser import browser
        snapshot_result = browser(
            action="snapshot",
            targetId="t5",
            compact=True,
            maxChars=2000
        )
        
        snapshot_text = str(snapshot_result)
        log_info(f"页面快照获取成功，长度: {len(snapshot_text)} 字符")
        
        # 检查是否显示92个岗位
        if "92个岗位" in snapshot_text:
            log_info("✅ 筛选成功！显示92个岗位")
        else:
            log_info(f"⚠️  可能未正确筛选，显示: {snapshot_text.count('个岗位')}个岗位")
        
        # 提取前2个岗位信息
        lines = snapshot_text.split('\n')
        positions_found = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('千问事业部-'):
                positions_found.append(line)
                if len(positions_found) >= 2:
                    break
        
        log_info(f"找到 {len(positions_found)} 个岗位")
        
        # 处理前2个岗位
        for i, position_name in enumerate(positions_found[:2], 1):
            log_info(f"\n处理第{i}个岗位: {position_name[:40]}...")
            
            try:
                # 1. 点击岗位
                log_info("点击岗位...")
                click_result = browser(
                    action="act",
                    targetId="t5",
                    request={
                        "kind": "click",
                        "selector": f"text='{position_name}'"
                    }
                )
                
                log_info(f"点击结果: {click_result}")
                
                # 2. 等待详情页加载
                time.sleep(3)
                
                # 3. 获取详情页标签页
                tabs_result = browser(action="tabs")
                detail_tab = None
                detail_url = None
                
                if "tabs" in tabs_result:
                    for tab in tabs_result["tabs"]:
                        url = tab.get("url", "")
                        if "position-detail" in url and tab.get("tabId") != "t5":
                            detail_tab = tab.get("tabId")
                            detail_url = url
                            break
                
                if not detail_tab:
                    log_info("❌ 未找到详情页标签页")
                    results.append({
                        '序号': i,
                        '岗位名称': position_name,
                        '状态': '失败',
                        '错误': '未找到详情页'
                    })
                    continue
                
                log_info(f"详情页标签页: {detail_tab}, URL: {detail_url}")
                
                # 4. 获取详情页快照
                detail_snapshot = browser(
                    action="snapshot",
                    targetId=detail_tab,
                    compact=True,
                    maxChars=3000
                )
                
                detail_text = str(detail_snapshot)
                log_info(f"详情页快照长度: {len(detail_text)} 字符")
                
                # 5. 提取字段
                detail_fields = extract_detail_fields_from_snapshot(detail_text, detail_url)
                
                # 6. 创建结果
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
                
                log_info(f"✅ 第{i}个岗位处理完成")
                log_info(f"  岗位id: {result['岗位id']}")
                log_info(f"  所属部门: {result['所属部门']}")
                log_info(f"  学历: {result['学历']}")
                log_info(f"  工作年限: {result['工作年限']}")
                
                # 7. 关闭详情页标签页（切换回列表页）
                # 在实际中可能需要特定操作
                # 这里简单处理：切换回列表页
                browser(
                    action="act",
                    targetId="t5",
                    request={"kind": "click", "selector": "text='职位列表'"}
                )
                
                time.sleep(2)
                
            except Exception as e:
                log_info(f"❌ 处理失败: {str(e)}")
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
        output_file = os.path.join(output_dir, f"test_2_positions_{timestamp}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        log_info(f"\n✅ 结果保存到: {output_file}")
        
        # 打印总结
        success_count = sum(1 for r in results if r.get('状态') == '成功')
        
        print(f"\n📊 测试总结:")
        print(f"  总测试岗位: {len(results)}")
        print(f"  成功: {success_count}")
        print(f"  失败: {len(results) - success_count}")
        
        if success_count > 0:
            print(f"\n🔍 成功提取的字段:")
            for field in ['岗位id', '所属部门', '学历', '工作年限']:
                extracted = sum(1 for r in results if r.get('状态') == '成功' and r.get(field) not in ['未提取', None])
                print(f"  {field}: {extracted}/{success_count}")
        
        return results
        
    except Exception as e:
        log_info(f"❌ 整体测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """主函数"""
    print("\n🎯 测试目标:")
    print("  1. 应用7个类别筛选（产品、运营、数据、市场拓展、销售、游戏、金融）")
    print("  2. 获取第1页前2个岗位")
    print("  3. 点击进入详情页")
    print("  4. 提取详情页字段（岗位id、所属部门、学历、工作年限、职位描述、职位要求）")
    print("  5. 保存结果到文件")
    
    print("\n⚠️  注意事项:")
    print("  - 需要保持浏览器标签页打开")
    print("  - 可能会打开多个详情页标签页")
    print("  - 处理时间较长（约30秒/岗位）")
    
    results = test_first_2_positions()
    
    print("\n" + "=" * 60)
    if results and any(r.get('状态') == '成功' for r in results):
        print("✅ 测试成功!")
        print("   可以继续运行完整的第1-2页爬取")
    else:
        print("❌ 测试失败或部分失败")
        print("   请检查错误信息并调整配置")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    main()