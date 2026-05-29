#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终的第1-2页真实数据爬取脚本
使用已验证的浏览器交互方法
"""

import os
import sys
import time
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

def log_info(msg: str):
    """记录信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def log_section(title: str):
    """记录章节标题"""
    print("\n" + "=" * 60)
    print(f"📋 {title}")
    print("=" * 60)

class RealDataCrawler:
    """真实数据爬取器 - 处理第1-2页"""
    
    def __init__(self):
        self.output_dir = "../output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 从环境变量获取配置
        self.max_positions_per_page = 5  # 每页最多处理岗位数
        self.click_delay = 2  # 点击延迟（秒）
        self.page_load_wait = 3  # 页面加载等待（秒）
        
        log_info("真实数据爬取器初始化完成")
    
    def extract_position_id_from_url(self, url: str) -> Optional[str]:
        """从URL提取positionId"""
        pattern = r'positionId=([^&]+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None
    
    def extract_detail_fields(self, snapshot_text: str, detail_url: str) -> Dict[str, Any]:
        """从详情页快照提取字段"""
        result = {
            '岗位id': self.extract_position_id_from_url(detail_url),
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
            if '所属部门:' in line and '阿里' in line:
                result['所属部门'] = '阿里集团'
            elif '所属部门:' in line:
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
            if desc_start and line.strip() and not line.startswith('1、'):
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
            if req_start and line.strip() and not line.startswith('1、'):
                req_lines.append(line.strip())
        
        if req_lines:
            result['职位要求'] = ' '.join(req_lines)
        
        return result
    
    def extract_page_positions(self, snapshot_text: str, page_num: int) -> List[Dict[str, Any]]:
        """从列表页快照提取岗位信息"""
        positions = []
        lines = snapshot_text.split('\n')
        
        current_position = None
        position_count = 0
        
        for line in lines:
            line = line.strip()
            
            # 查找岗位名称行
            if line.startswith('千问事业部-') or line.startswith('阿里千问') or line.startswith('千问事业群'):
                # 保存上一个岗位
                if current_position and '岗位名称' in current_position:
                    positions.append(current_position)
                
                position_count += 1
                current_position = {
                    '序号': position_count,
                    '岗位名称': line,
                    '页码': page_num,
                    '岗位id': f"quark_page{page_num}_{position_count:03d}",  # 临时ID
                    '岗位详情链接': '待提取',
                    '职位类别': '待提取',
                    '子类别': '待提取',
                    '办公地点': '待提取',
                    '所属部门': '待点击详情页获取',
                    '学历': '待点击详情页获取',
                    '工作年限': '待点击详情页获取',
                    '职位描述': '待点击详情页获取',
                    '职位要求': '待点击详情页获取',
                    '更新时间': '待提取',
                    '数据来源': f'网页第{page_num}页实际数据',
                    '提取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # 推断基础信息
                self._infer_basic_info(current_position, snapshot_text)
        
        # 添加最后一个岗位
        if current_position and '岗位名称' in current_position:
            positions.append(current_position)
        
        return positions
    
    def _infer_basic_info(self, position: Dict[str, Any], snapshot_text: str):
        """推断基础信息"""
        name = position['岗位名称']
        
        # 推断职位类别
        if '产品' in name:
            position['职位类别'] = '产品类'
            if 'AI' in name or 'Native' in name:
                position['子类别'] = 'AI产品'
            elif '用户' in name:
                position['子类别'] = '用户产品'
            elif '商业' in name:
                position['子类别'] = '商业产品'
            else:
                position['子类别'] = '产品经理'
        elif '运营' in name:
            position['职位类别'] = '运营类'
            if '用户增长' in name:
                position['子类别'] = '用户增长'
            elif '渠道' in name:
                position['子类别'] = '渠道运营'
            elif '广告' in name:
                position['子类别'] = '广告运营'
            else:
                position['子类别'] = '运营'
        elif '数据' in name:
            position['职位类别'] = '数据类'
            position['子类别'] = '数据分析'
        elif '市场' in name:
            position['职位类别'] = '市场拓展'
            position['子类别'] = '市场'
        elif '销售' in name:
            position['职位类别'] = '销售类'
            position['子类别'] = '销售'
        elif '游戏' in name:
            position['职位类别'] = '游戏类'
            position['子类别'] = '游戏'
        elif '金融' in name:
            position['职位类别'] = '金融类'
            position['子类别'] = '金融'
        
        # 推断办公地点
        if '北京' in name:
            position['办公地点'] = '北京'
        elif '杭州' in name:
            position['办公地点'] = '杭州'
        elif '广州' in name:
            position['办公地点'] = '广州'
        elif '上海' in name:
            position['办公地点'] = '上海'
        elif '深圳' in name:
            position['办公地点'] = '深圳'
        elif '/' in name:
            # 提取多地点
            parts = name.split('-')
            if parts and '/' in parts[-1]:
                position['办公地点'] = parts[-1].strip()
        
        # 推断所属部门
        if '千问事业部' in name:
            position['所属部门'] = '千问事业部'
        elif '阿里千问' in name:
            position['所属部门'] = '阿里千问'
    
    def process_position(self, position: Dict[str, Any], list_tab_id: str) -> Dict[str, Any]:
        """处理单个岗位的详情页"""
        position_name = position['岗位名称']
        log_info(f"处理岗位: {position_name[:40]}...")
        
        try:
            # 1. 点击岗位
            click_result = browser(
                action="act",
                targetId=list_tab_id,
                request={
                    "kind": "click",
                    "selector": f"text='{position_name}'"
                }
            )
            
            log_info(f"点击结果: {click_result.get('ok', False)}")
            
            # 2. 等待详情页加载
            time.sleep(self.page_load_wait)
            
            # 3. 获取标签页列表，找到详情页
            tabs_result = browser(action="tabs")
            detail_tab = None
            detail_url = None
            
            if "tabs" in tabs_result:
                for tab in tabs_result["tabs"]:
                    url = tab.get("url", "")
                    if "position-detail" in url and tab.get("tabId") != list_tab_id:
                        detail_tab = tab.get("tabId")
                        detail_url = url
                        break
            
            if not detail_tab:
                log_info("❌ 未找到详情页标签页")
                position['详情页处理状态'] = '失败'
                position['错误信息'] = '未找到详情页'
                return position
            
            log_info(f"详情页标签页: {detail_tab}")
            
            # 4. 获取详情页快照
            detail_snapshot = browser(
                action="snapshot",
                targetId=detail_tab,
                compact=True,
                maxChars=4000
            )
            
            detail_text = str(detail_snapshot)
            log_info(f"详情页快照长度: {len(detail_text)} 字符")
            
            # 5. 提取详情页字段
            detail_fields = self.extract_detail_fields(detail_text, detail_url)
            
            # 6. 更新岗位数据
            position.update({
                '岗位id': detail_fields['岗位id'],
                '岗位详情链接': detail_fields['岗位详情链接'],
                '所属部门': detail_fields['所属部门'],
                '学历': detail_fields['学历'],
                '工作年限': detail_fields['工作年限'],
                '职位描述': detail_fields['职位描述'],
                '职位要求': detail_fields['职位要求'],
                '详情页处理状态': '成功',
                '详情页处理时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            log_info(f"✅ 处理成功")
            log_info(f"  岗位id: {position['岗位id']}")
            log_info(f"  所属部门: {position['所属部门']}")
            log_info(f"  学历: {position['学历']}")
            log_info(f"  工作年限: {position['工作年限']}")
            
            # 7. 关闭详情页标签页（切换回列表页）
            # 在实际中，可能需要特定操作来关闭标签页
            # 这里简单处理：切换回列表页
            try:
                browser(
                    action="act",
                    targetId=list_tab_id,
                    request={"kind": "click", "selector": "text='职位列表'"}
                )
            except:
                log_info("切换回列表页失败，继续处理")
            
            # 8. 延迟避免反爬
            time.sleep(self.click_delay)
            
            return position
            
        except Exception as e:
            log_info(f"❌ 处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            position['详情页处理状态'] = '失败'
            position['错误信息'] = str(e)
            return position
    
    def process_page(self, list_tab_id: str, page_num: int, max_positions: Optional[int] = None) -> List[Dict[str, Any]]:
        """处理单个页面"""
        log_section(f"处理第 {page_num} 页")
        
        try:
            # 1. 获取页面快照
            snapshot_result = browser(
                action="snapshot",
                targetId=list_tab_id,
                compact=True,
                maxChars=2000
            )
            
            snapshot_text = str(snapshot_result)
            log_info(f"页面快照获取成功，长度: {len(snapshot_text)} 字符")
            
            # 2. 提取岗位信息
            positions = self.extract_page_positions(snapshot_text, page_num)
            
            # 限制处理数量
            if max_positions and len(positions) > max_positions:
                positions = positions[:max_positions]
                log_info(f"限制处理前 {max_positions} 个岗位")
            
            # 3. 处理每个岗位的详情页
            processed_positions = []
            success_count = 0
            
            for i, position in enumerate(positions, 1):
                log_info(f"\n[{i}/{len(positions)}] 处理岗位详情页...")
                
                processed_position = self.process_position(position, list_tab_id)
                processed_positions.append(processed_position)
                
                if processed_position.get('详情页处理状态') == '成功':
                    success_count += 1
            
            log_info(f"\n第{page_num}页处理完成: 成功 {success_count}/{len(positions)}")
            return processed_positions
            
        except Exception as e:
            log_info(f"❌ 处理第{page_num}页失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def save_results(self, all_positions: List[Dict[str, Any]]):
        """保存结果到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. JSON文件
        json_filename = f"quark_real_pages_1_2_{timestamp}.json"
        json_path = os.path.join(self.output_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_positions, f, ensure_ascii=False, indent=2)
        
        log_info(f"✅ JSON文件保存: {json_path}")
        
        # 2. 统计报告
        report_filename = f"quark_real_pages_1_2_report_{timestamp}.txt"
        report_path = os.path.join(self.output_dir, report_filename)
        
        success_count = sum(1 for p in all_positions if p.get('详情页处理状态') == '成功')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("夸克校园招聘真实数据统计报告（第1-2页）\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"📊 数据概览\n")
            f.write(f"  总岗位数: {len(all_positions)}\n")
            f.write(f"  成功详情页: {success_count}\n")
            f.write(f"  失败详情页: {len(all_positions) - success_count}\n")
            f.write(f"  提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  数据来源: 网页真实数据\n\n")
            
            # 页码分布
            page_counts = {}
            for pos in all_positions:
                page = pos.get('页码', 0)
                page_counts[page] = page_counts.get(page, 0) + 1
            
            f.write(f"📄 页码分布\n")
            for page in sorted(page_counts.keys()):
                f.write(f"  第{page}页: {page_counts[page]} 个岗位\n")
            f.write("\n")
            
            # 成功提取的字段
            f.write(f"🔧 详情页字段提取情况\n")
            fields_to_check = ['岗位id', '所属部门', '学历', '工作年限', '职位描述', '职位要求']
            for field in fields_to_check:
                extracted_count = sum(1 for p in all_positions 
                                    if p.get(field) and p.get(field) not in ['待提取', '待点击详情页获取', '未提取'])
                f.write(f"  {field}: {extracted_count}/{len(all_positions)} 已提取\n")
            f.write("\n")
            
            # 示例数据
            f.write(f"📋 数据示例（成功岗位）\n")
            success_positions = [p for p in all_positions if p.get('详情页处理状态') == '成功']
            for i, pos in enumerate(success_positions[:3], 1):
                f.write(f"  #{i} {pos.get('岗位名称', '未知')[:40]}...\n")
                f.write(f"    岗位id: {pos.get('岗位id', '未知')}\n")
                f.write(f"    职位类别: {pos.get('职位类别', '未知')}\n")
                f.write(f"    办公地点: {pos.get('办公地点', '未知')}\n")
                f.write(f"    所属部门: {pos.get('所属部门', '未知')}\n")
                f.write(f"    学历: {pos.get('学历', '未知')}\n")
                f.write(f"    工作年限: {pos.get('工作年限', '未知')}\n")
                f.write("\n")
        
        log_info(f"✅ 统计报告保存: {report_path}")
        
        # 3. 尝试保存为Excel（需要pandas）
        try:
            import pandas as pd
            
            excel_filename = f"quark_real_pages_1_2_{timestamp}.xlsx"
            excel_path = os.path.join(self.output_dir, excel_filename)
            
            # 创建DataFrame
            df = pd.DataFrame(all_positions)
            
            # 选择需要的列
            columns_order = [
                '序号', '页码', '岗位id', '岗位名称', '岗位详情链接',
                '职位类别', '子类别', '办公地点', '所属部门',
                '学历', '工作年限', '职位描述', '职位要求',
                '更新时间', '数据来源', '提取时间', '详情页处理状态'
            ]
            
            # 只保留存在的列
            existing_columns = [col for col in columns_order if col in df.columns]
            df = df[existing_columns]
            
            # 保存到Excel
            df.to_excel(excel_path, index=False)
            log_info(f"✅ Excel文件保存: {excel_path}")
            
            excel_saved = True
            
        except ImportError:
            log_info("❌ 未安装pandas，跳过Excel文件生成")
            excel_saved = False
            excel_path = None
        except Exception as e:
            log_info(f"❌ Excel文件生成失败: {str(e)}")
            excel_saved = False
            excel_path = None
        
        return {
            'json_path': json_path,
            'report_path': report_path,
            'excel_path': excel_path if excel_saved else None,
            'position_count': len(all_positions),
            'success_count': success_count
        }
    
    def run(self, max_positions_per_page: int = 3):
        """运行爬取"""
        log_section("开始真实数据爬取（第1-2页）")
        
        print(f"🔧 配置信息:")
        print(f"  目标页面: 第1页 + 第2页")
        print(f"  筛选条件: 7个类别（产品、运营、数据、市场拓展、销售、游戏、金融）")
        print(f"  目标岗位: 93个（筛选后实际数量）")
        print(f"  处理策略: 每页最多处理 {max_positions_per_page} 个岗位")
        print(f"  反爬策略: 点击延迟 {self.click_delay} 秒，页面加载等待 {self.page_load_wait} 秒")
        
        print(f"\n⚠️  注意事项:")
        print(f"  1. 需要保持浏览器窗口打开")
        print(f"  2. 可能会打开多个标签页")
        print(f"  3. 处理时间约 {max_positions_per_page * 2 * 10} 秒")
        print(f"  4. 如果失败，会自动跳过继续处理")
        
        all_positions = []
        
        try:
            # 假设列表页标签页ID是t5（根据之前的tabs结果）
            list_tab_id = "t5"
            
            # 处理第1页
            page1_positions = self.process_page(list_tab_id, 1, max_positions_per_page)
            all_positions.extend(page1_positions)
            
            # 尝试切换到第2页
            log_info("尝试切换到第2页...")
            try:
                # 点击下一页按钮
                browser(
                    action="act",
                    targetId=list_tab_id,
                    request={"kind": "click", "ref": "e65"}  # 根据快照，下一页按钮ref=e65
                )
                
                # 等待页面加载
                time.sleep(self.page_load_wait)
                
                # 处理第2页
                page2_positions = self.process_page(list_tab_id, 2, max_positions_per_page)
                all_positions.extend(page2_positions)
                
            except Exception as e:
                log_info(f"❌ 切换到第2页失败: {str(e)}")
                log_info("继续使用第1页数据...")
            
            # 保存结果
            log_section("保存爬取结果")
            save_result = self.save_results(all_positions)
            
            # 生成总结
            log_section("爬取完成")
            
            print(f"\n🎯 爬取总结:")
            print(f"  总页数: 2")
            print(f"  总岗位数: {save_result['position_count']}")
            print(f"  成功详情页: {save_result['success_count']}")
            print(f"  失败详情页: {save_result['position_count'] - save_result['success_count']}")
            print(f"  JSON文件: {os.path.basename(save_result['json_path'])}")
            print(f"  报告文件: {os.path.basename(save_result['report_path'])}")
            
            if save_result.get('excel_path'):
                print(f"  Excel文件: {os.path.basename(save_result['excel_path'])}")
            
            # 字段提取情况
            print(f"\n📊 数据字段提取情况:")
            fields = ['岗位id', '所属部门', '学历', '工作年限', '职位描述', '职位要求']
            for field in fields:
                extracted = sum(1 for p in all_positions 
                              if p.get(field) and p.get(field) not in ['待提取', '待点击详情页获取', '未提取'])
                print(f"  {field}: {extracted}/{save_result['position_count']} 已提取")
            
            return save_result
            
        except Exception as e:
            log_info(f"❌ 爬取失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """主函数"""
    log_section("夸克校园招聘真实数据爬取（第1-2页）")
    
    # 创建爬取器实例
    crawler = RealDataCrawler()
    
    # 运行爬取（处理每页最多3个岗位）
    result = crawler.run(max_positions_per_page=3)
    
    if result:
        log_section("执行成功")
        
        print(f"\n📁 输出文件目录:")
        output_dir = os.path.abspath(crawler.output_dir)
        print(f"  {output_dir}")
        
        print(f"\n📊 生成文件:")
        print(f"  JSON数据: {os.path.basename(result['json_path'])}")
        print(f"  统计报告: {os.path.basename(result['report_path'])}")
        if result.get('excel_path'):
            print(f"  Excel文件: {os.path.basename(result['excel_path'])}")
        
        print(f"\n💡 下一步:")
        print("  1. 查看生成的文件验证数据质量")
        print("  2. 调整字段提取逻辑（如果需要）")
        print("  3. 扩展到更多页面（第3-10页）")
        print("  4. 优化反爬策略和性能")
        
    else:
        log_section("执行失败")
        print("请检查错误信息并调整配置后重试")
    
    return result

if __name__ == "__main__":
    main()