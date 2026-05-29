#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实数据爬取脚本 - 处理第1-2页数据，使用真实浏览器交互
"""

import os
import sys
import time
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_browser_manager import RealBrowserManager
from detail_extractor import extract_detail_fields
from link_extractor import extract_position_links_from_snapshot

def log_info(msg: str):
    """记录信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def log_section(title: str):
    """记录章节标题"""
    print("\n" + "=" * 60)
    print(f"📋 {title}")
    print("=" * 60)

class RealPageCrawler:
    """真实页面爬取器 - 处理第1-2页数据"""
    
    def __init__(self):
        self.browser_manager = RealBrowserManager()
        self.output_dir = "../output"
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        log_info("真实页面爬取器初始化完成")
    
    def apply_filters(self, tab_id: str) -> bool:
        """
        应用筛选条件（7个类别）
        
        Args:
            tab_id: 标签页ID
            
        Returns:
            是否成功应用筛选
        """
        from browser import browser
        
        log_info("开始应用筛选条件（7个类别）...")
        
        try:
            # 先获取当前页面快照，确认筛选状态
            snapshot = self.browser_manager.get_current_snapshot(tab_id)
            if not snapshot:
                log_info("无法获取页面快照")
                return False
            
            # 检查是否已经显示"92个岗位"
            if "92个岗位" in snapshot:
                log_info("✅ 筛选条件已正确应用（92个岗位）")
                return True
            
            # 如果未正确应用筛选，需要点击7个类别
            # 根据之前的分析，需要点击的类别ref:
            # 产品类: e68, 运营类: e78, 数据类: e98, 市场拓展: e108
            # 销售类: e118, 游戏类: e158, 金融类: e168
            
            category_refs = [
                ("产品类", "e68"),
                ("运营类", "e78"), 
                ("数据类", "e98"),
                ("市场拓展", "e108"),
                ("销售类", "e118"),
                ("游戏类", "e158"),
                ("金融类", "e168")
            ]
            
            for category_name, ref in category_refs:
                log_info(f"点击筛选: {category_name} (ref: {ref})")
                
                try:
                    # 点击筛选类别
                    browser(
                        action="act",
                        targetId=tab_id,
                        request={"kind": "click", "ref": ref}
                    )
                    
                    # 等待筛选生效
                    time.sleep(1)
                    
                except Exception as e:
                    log_info(f"点击筛选 {category_name} 失败: {str(e)}")
            
            # 等待筛选结果
            time.sleep(2)
            
            # 验证筛选结果
            snapshot_after = self.browser_manager.get_current_snapshot(tab_id)
            if snapshot_after and "92个岗位" in snapshot_after:
                log_info("✅ 筛选条件应用成功（92个岗位）")
                return True
            else:
                log_info("❌ 筛选条件可能未正确应用")
                return False
            
        except Exception as e:
            log_info(f"应用筛选条件失败: {str(e)}")
            return False
    
    def extract_page_data_from_snapshot(self, snapshot_text: str, page_num: int) -> List[Dict[str, Any]]:
        """
        从真实快照提取基础岗位数据
        
        Args:
            snapshot_text: 真实页面快照文本
            page_num: 页码
            
        Returns:
            基础岗位数据列表
        """
        log_info(f"开始提取第{page_num}页基础数据...")
        
        positions = []
        lines = snapshot_text.split('\n')
        
        current_position = None
        position_count = 0
        
        for line in lines:
            line = line.strip()
            
            # 查找岗位名称行（以"千问事业部-"或"阿里千问"开头）
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
                    '所属部门': '待推断',
                    '学历': '待点击详情页获取',
                    '工作年限': '待点击详情页获取',
                    '职位描述': '待点击详情页获取',
                    '职位要求': '待点击详情页获取',
                    '更新时间': self._extract_update_time(line, snapshot_text),
                    '数据来源': f'网页第{page_num}页实际数据',
                    '提取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # 从岗位名称推断基础信息
                self._infer_basic_info(current_position)
        
        # 添加最后一个岗位
        if current_position and '岗位名称' in current_position:
            positions.append(current_position)
        
        log_info(f"第{page_num}页提取完成: {len(positions)} 个岗位")
        return positions
    
    def _extract_update_time(self, position_line: str, snapshot_text: str) -> str:
        """从快照中提取更新时间"""
        # 在快照中查找包含"更新于"的行
        lines = snapshot_text.split('\n')
        
        for line in lines:
            if '更新于' in line and position_line in snapshot_text:
                # 提取日期部分
                date_pattern = r'更新于\s+(\d{4}-\d{2}-\d{2})'
                match = re.search(date_pattern, line)
                if match:
                    return match.group(1)
        
        return datetime.now().strftime('%Y-%m-%d')
    
    def _infer_basic_info(self, position: Dict[str, Any]):
        """从岗位名称推断基础信息"""
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
    
    def process_page(self, tab_id: str, page_num: int, max_positions: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        处理单个页面
        
        Args:
            tab_id: 标签页ID
            page_num: 页码
            max_positions: 最大处理岗位数
            
        Returns:
            处理后的岗位数据列表
        """
        log_section(f"处理第 {page_num} 页")
        
        try:
            # 1. 确保在正确的标签页
            self.browser_manager.switch_to_tab(tab_id)
            self.browser_manager.wait_for_page_load(2)
            
            # 2. 获取页面快照
            snapshot = self.browser_manager.get_current_snapshot(tab_id)
            if not snapshot:
                log_info("❌ 无法获取页面快照")
                return []
            
            log_info(f"页面快照获取成功，长度: {len(snapshot)} 字符")
            
            # 3. 提取基础岗位数据
            page_positions = self.extract_page_data_from_snapshot(snapshot, page_num)
            
            # 限制处理数量
            if max_positions and len(page_positions) > max_positions:
                page_positions = page_positions[:max_positions]
                log_info(f"限制处理前 {max_positions} 个岗位")
            
            # 4. 提取岗位链接信息
            position_links, _ = extract_position_links_from_snapshot(snapshot)
            
            # 5. 合并链接信息到岗位数据
            for i, position in enumerate(page_positions):
                if i < len(position_links):
                    link_info = position_links[i]
                    position.update({
                        '点击目标': link_info.get('点击目标', '未找到'),
                        '匹配策略': link_info.get('匹配策略', '未知'),
                        '链接状态': link_info.get('状态', '未知')
                    })
            
            # 6. 批量处理详情页
            detailed_positions = self.batch_process_details(page_positions, tab_id, max_positions)
            
            log_info(f"第{page_num}页处理完成: {len(detailed_positions)} 个岗位")
            return detailed_positions
            
        except Exception as e:
            log_info(f"❌ 处理第{page_num}页失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def batch_process_details(self, positions: List[Dict[str, Any]], 
                            list_tab_id: str,
                            max_positions: Optional[int] = None) -> List[Dict[str, Any]]:
        """批量处理详情页"""
        log_info(f"开始批量处理详情页，共 {len(positions)} 个岗位")
        
        # 使用真实浏览器管理器处理
        processed_results = self.browser_manager.batch_process_positions(
            positions,
            list_tab_id,
            max_positions=max_positions
        )
        
        # 将处理结果合并到岗位数据中
        detailed_positions = []
        
        for i, position in enumerate(positions):
            if i >= len(processed_results):
                # 如果没有处理结果，保留原始数据
                detailed_positions.append(position)
                continue
            
            result = processed_results[i]
            
            if result.get('处理状态') == '成功':
                # 更新岗位数据
                position.update({
                    '岗位id': result.get('岗位id', position.get('岗位id')),
                    '岗位详情链接': result.get('详情页URL', position.get('岗位详情链接')),
                    '所属部门': result.get('所属部门', position.get('所属部门')),
                    '学历': result.get('学历', position.get('学历')),
                    '工作年限': result.get('工作年限', position.get('工作年限')),
                    '职位描述': result.get('职位描述_preview', position.get('职位描述')).replace('_preview', ''),
                    '职位要求': result.get('职位要求_preview', position.get('职位要求')).replace('_preview', ''),
                    '详情页处理状态': '成功',
                    '详情页处理时间': result.get('处理时间')
                })
            else:
                position.update({
                    '详情页处理状态': '失败',
                    '错误信息': result.get('错误信息', '未知错误'),
                    '详情页处理时间': result.get('处理时间')
                })
            
            detailed_positions.append(position)
        
        # 统计成功率
        success_count = sum(1 for p in detailed_positions if p.get('详情页处理状态') == '成功')
        log_info(f"详情页处理完成: 成功 {success_count}/{len(detailed_positions)}")
        
        return detailed_positions
    
    def save_results(self, all_positions: List[Dict[str, Any]], 
                    filename_prefix: str = "quark_real_pages_1_2"):
        """保存结果到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. JSON文件
        json_filename = f"{filename_prefix}_{timestamp}.json"
        json_path = os.path.join(self.output_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_positions, f, ensure_ascii=False, indent=2)
        
        log_info(f"✅ JSON文件保存: {json_path}")
        
        # 2. 统计报告
        report_filename = f"{filename_prefix}_report_{timestamp}.txt"
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
            
            # 职位类别分布
            category_counts = {}
            for pos in all_positions:
                category = pos.get('职位类别', '未知')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            f.write(f"🏢 职位类别分布\n")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {category}: {count} 个岗位\n")
            f.write("\n")
            
            # 详情页字段提取情况
            f.write(f"🔧 详情页字段提取情况\n")
            fields_to_check = ['岗位id', '所属部门', '学历', '工作年限', '职位描述', '职位要求']
            for field in fields_to_check:
                extracted_count = sum(1 for p in all_positions 
                                    if p.get(field) and p.get(field) not in ['待提取', '待点击详情页获取', '未提取'])
                f.write(f"  {field}: {extracted_count}/{len(all_positions)} 已提取\n")
            f.write("\n")
            
            # 示例数据
            f.write(f"📋 数据示例（前3个成功岗位）\n")
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
        
        # 3. Excel文件
        try:
            excel_filename = f"{filename_prefix}_{timestamp}.xlsx"
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
            
        except Exception as e:
            log_info(f"❌ Excel文件保存失败: {str(e)}")
            excel_saved = False
            excel_path = None
        
        return {
            'json_path': json_path,
            'report_path': report_path,
            'excel_path': excel_path if excel_saved else None,
            'position_count': len(all_positions),
            'success_count': success_count
        }
    
    def run_crawl_pages_1_2(self, max_positions_per_page: int = 5):
        """
        运行第1-2页数据爬取
        
        Args:
            max_positions_per_page: 每页最大处理岗位数
        """
        log_section("开始爬取第1-2页真实数据")
        
        from browser import browser
        
        try:
            # 1. 打开或切换到夸克招聘页面
            log_info("打开夸克招聘页面...")
            open_result = browser(
                action="open",
                targetUrl="https://talent.quark.cn/off-campus/position-list?lang=zh"
            )
            
            if not open_result or "targetId" not in open_result:
                log_info("❌ 无法打开页面")
                return None
            
            tab_id = open_result["targetId"]
            log_info(f"页面打开成功，标签页ID: {tab_id}")
            
            # 2. 等待页面加载
            self.browser_manager.wait_for_page_load(3)
            
            # 3. 应用筛选条件
            if not self.apply_filters(tab_id):
                log_info("⚠️  筛选条件可能未正确应用，继续处理...")
            
            # 4. 处理第1页
            all_positions = []
            
            # 第1页
            page1_positions = self.process_page(tab_id, 1, max_positions_per_page)
            all_positions.extend(page1_positions)
            
            # 5. 切换到第2页
            log_info("切换到第2页...")
            try:
                # 点击下一页按钮
                browser(
                    action="act",
                    targetId=tab_id,
                    request={"kind": "click", "ref": "e65"}  # 根据之前的快照，下一页按钮ref=e65
                )
                
                # 等待页面加载
                self.browser_manager.wait_for_page_load(3)
                
                # 处理第2页
                page2_positions = self.process_page(tab_id, 2, max_positions_per_page)
                all_positions.extend(page2_positions)
                
            except Exception as e:
                log_info(f"❌ 切换到第2页失败: {str(e)}")
                log_info("继续处理第1页数据...")
            
            # 6. 保存结果
            log_section("保存爬取结果")
            save_result = self.save_results(all_positions)
            
            # 7. 生成总结报告
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
            
            # 显示数据字段情况
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
    
    print("🔧 配置信息:")
    print(f"  目标页面: 第1页 + 第2页")
    print(f"  筛选条件: 7个类别（产品、运营、数据、市场拓展、销售、游戏、金融）")
    print(f"  目标岗位: 92个（筛选后）")
    print(f"  处理策略: 每页最多处理5个岗位（测试模式）")
    print(f"  反爬策略: 随机延迟2-4秒，页面加载等待3秒")
    
    print("\n⚠️  注意事项:")
    print("  1. 需要保持浏览器窗口打开")
    print("  2. 可能会打开多个标签页")
    print("  3. 处理时间较长（约1-2分钟/岗位）")
    print("  4. 如果失败，会自动跳过继续处理下一个")
    
    # 创建爬取器实例
    crawler = RealPageCrawler()
    
    # 运行爬取
    result = crawler.run_crawl_pages_1_2(max_positions_per_page=5)
    
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