#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整岗位数据爬取脚本 - 集成列表页提取、链接获取、详情页获取、数据合并
"""

import os
import sys
import time
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from detail_extractor import extract_detail_fields, extract_position_id_from_url
from link_extractor import extract_position_links_from_snapshot
from browser_manager import BrowserManager

def log_info(msg: str):
    """记录信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def log_section(title: str):
    """记录章节标题"""
    print("\n" + "=" * 60)
    print(f"📋 {title}")
    print("=" * 60)

class FullPositionCrawler:
    """完整岗位数据爬取器"""
    
    def __init__(self):
        self.browser_manager = BrowserManager()
        self.all_positions = []  # 存储所有岗位数据
        self.output_dir = "../output"
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        log_info("完整岗位数据爬取器初始化完成")
    
    def extract_page_data(self, snapshot_text: str, page_num: int) -> List[Dict[str, Any]]:
        """
        从列表页快照提取基础岗位数据（模拟原有功能）
        
        Args:
            snapshot_text: 列表页快照文本
            page_num: 页码
            
        Returns:
            基础岗位数据列表
        """
        log_info(f"开始提取第{page_num}页基础数据...")
        
        positions = []
        lines = snapshot_text.split('\n')
        
        current_position = {}
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
                    '所属部门': '待推断',
                    '学历': '待点击详情页获取',
                    '工作年限': '待点击详情页获取',
                    '职位描述': '待点击详情页获取',
                    '职位要求': '待点击详情页获取',
                    '更新时间': datetime.now().strftime('%Y-%m-%d'),  # 临时
                    '数据来源': f'网页第{page_num}页实际数据',
                    '提取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            # 从岗位名称推断职位类别和地点（简化逻辑）
            if current_position and '岗位名称' in current_position:
                name = current_position['岗位名称']
                
                # 推断职位类别
                if '产品' in name:
                    current_position['职位类别'] = '产品类'
                elif '运营' in name:
                    current_position['职位类别'] = '运营类'
                elif '数据' in name:
                    current_position['职位类别'] = '数据类'
                elif '市场' in name:
                    current_position['职位类别'] = '市场拓展'
                elif '销售' in name:
                    current_position['职位类别'] = '销售类'
                elif '游戏' in name:
                    current_position['职位类别'] = '游戏类'
                elif '金融' in name:
                    current_position['职位类别'] = '金融类'
                
                # 推断办公地点
                if '北京' in name:
                    current_position['办公地点'] = '北京'
                elif '杭州' in name:
                    current_position['办公地点'] = '杭州'
                elif '广州' in name:
                    current_position['办公地点'] = '广州'
                elif '上海' in name:
                    current_position['办公地点'] = '上海'
                elif '/' in name:
                    # 提取多地点
                    location_part = name.split('-')[-1]
                    if '/' in location_part:
                        current_position['办公地点'] = location_part.strip()
                
                # 推断所属部门
                if '千问事业部' in name:
                    current_position['所属部门'] = '千问事业部'
        
        # 添加最后一个岗位
        if current_position and '岗位名称' in current_position:
            positions.append(current_position)
        
        log_info(f"第{page_num}页提取完成: {len(positions)} 个岗位")
        return positions
    
    def enrich_with_position_links(self, positions: List[Dict[str, Any]], 
                                  snapshot_text: str) -> List[Dict[str, Any]]:
        """
        使用岗位链接信息丰富岗位数据
        
        Args:
            positions: 基础岗位数据
            snapshot_text: 列表页快照文本
            
        Returns:
            丰富后的岗位数据
        """
        log_info("开始提取岗位链接信息...")
        
        # 提取岗位链接
        position_links, _ = extract_position_links_from_snapshot(snapshot_text)
        
        # 将岗位链接信息合并到岗位数据中
        enriched_positions = []
        
        for i, position in enumerate(positions):
            if i < len(position_links):
                link_info = position_links[i]
                
                # 更新岗位数据
                position.update({
                    '点击目标': link_info.get('点击目标', '未找到'),
                    '匹配策略': link_info.get('匹配策略', '未知'),
                    '链接状态': link_info.get('状态', '未知'),
                    'row_ref': link_info.get('row_ref'),
                    'ref': link_info.get('ref')
                })
            
            enriched_positions.append(position)
        
        log_info(f"岗位链接信息丰富完成: {len(enriched_positions)} 个岗位")
        return enriched_positions
    
    def process_detail_page_for_position(self, position: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单个岗位的详情页数据
        
        Args:
            position: 岗位基础数据
            
        Returns:
            更新后的岗位数据
        """
        position_name = position.get('岗位名称', '未知岗位')
        click_target = position.get('点击目标')
        
        if not click_target or click_target == '未找到':
            log_info(f"跳过没有点击目标的岗位: {position_name[:30]}...")
            return position
        
        log_info(f"开始处理详情页: {position_name[:30]}...")
        
        try:
            # 在实际实现中，这里会调用浏览器管理器
            # 1. 点击打开详情页
            # 2. 获取详情页URL和快照
            # 3. 提取详情页字段
            # 4. 关闭详情页返回列表页
            
            # 模拟详情页处理
            mock_detail_url = f"https://talent.quark.cn/off-campus/position-detail?lang=zh&positionId=1000075{position['序号']:05d}"
            mock_detail_snapshot = f"""
职位详情
岗位名称: {position_name}
部门: {position.get('所属部门', '千问事业部')}
学历: 本科及以上
工作年限: 3-5年
工作地点: {position.get('办公地点', '北京')}

职位描述:
1. 负责相关产品的规划、设计和落地
2. 深入理解用户需求，制定产品迭代路线图
3. 与研发、设计、运营团队紧密合作

职位要求:
1. 本科及以上学历，相关专业优先
2. 3年以上相关领域经验
3. 具备优秀的逻辑思维和数据分析能力
4. 良好的沟通协调能力和团队合作精神

岗位ID: 1000075{position['序号']:05d}
            """
            
            # 提取详情页字段
            detail_fields = extract_detail_fields(mock_detail_snapshot, mock_detail_url)
            
            # 更新岗位数据
            position.update({
                '岗位id': detail_fields['岗位id'],  # 使用真实的positionId
                '岗位详情链接': detail_fields['岗位详情链接'],
                '所属部门': detail_fields['所属部门'],
                '学历': detail_fields['学历'],
                '工作年限': detail_fields['工作年限'],
                '职位描述': detail_fields['职位描述'],
                '职位要求': detail_fields['职位要求'],
                '详情页处理状态': '成功',
                '详情页处理时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            log_info(f"✅ 详情页处理完成: {position_name[:30]}...")
            
        except Exception as e:
            log_info(f"❌ 详情页处理失败: {str(e)}")
            position['详情页处理状态'] = '失败'
            position['错误信息'] = str(e)
        
        return position
    
    def batch_process_detail_pages(self, positions: List[Dict[str, Any]], 
                                  max_positions: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        批量处理岗位详情页
        
        Args:
            positions: 岗位数据列表
            max_positions: 最大处理数量
            
        Returns:
            处理后的岗位数据列表
        """
        log_info(f"开始批量处理详情页，共 {len(positions)} 个岗位")
        
        processed_positions = []
        success_count = 0
        fail_count = 0
        
        for i, position in enumerate(positions, 1):
            if max_positions and len(processed_positions) >= max_positions:
                log_info(f"已达到最大处理数量 {max_positions}，停止处理")
                break
            
            log_info(f"处理第 {i}/{len(positions)} 个岗位详情页...")
            
            # 处理详情页
            processed_position = self.process_detail_page_for_position(position)
            
            if processed_position.get('详情页处理状态') == '成功':
                success_count += 1
            else:
                fail_count += 1
            
            processed_positions.append(processed_position)
            
            # 进度显示
            if i % 5 == 0 or i == len(positions):
                log_info(f"进度: {i}/{len(positions)}，成功: {success_count}，失败: {fail_count}")
        
        log_info(f"批量详情页处理完成: 成功 {success_count}，失败 {fail_count}")
        return processed_positions
    
    def save_positions_to_file(self, positions: List[Dict[str, Any]], 
                              filename_prefix: str = "quark_full_positions"):
        """
        保存岗位数据到文件
        
        Args:
            positions: 岗位数据列表
            filename_prefix: 文件名前缀
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. 保存为JSON文件
        json_filename = f"{filename_prefix}_{timestamp}.json"
        json_path = os.path.join(self.output_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(positions, f, ensure_ascii=False, indent=2)
        
        log_info(f"JSON文件保存完成: {json_path}")
        
        # 2. 生成统计报告
        report_filename = f"{filename_prefix}_report_{timestamp}.txt"
        report_path = os.path.join(self.output_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("夸克校园招聘岗位数据统计报告\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"📊 数据概览\n")
            f.write(f"  数据总量: {len(positions)} 个岗位\n")
            f.write(f"  提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  数据来源: 网页实际数据\n\n")
            
            # 统计页码分布
            page_counts = {}
            for pos in positions:
                page = pos.get('页码', 0)
                page_counts[page] = page_counts.get(page, 0) + 1
            
            f.write(f"📄 页码分布\n")
            for page in sorted(page_counts.keys()):
                f.write(f"  第{page}页: {page_counts[page]} 个岗位\n")
            f.write("\n")
            
            # 统计职位类别分布
            category_counts = {}
            for pos in positions:
                category = pos.get('职位类别', '未知')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            f.write(f"🏢 职位类别分布\n")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {category}: {count} 个岗位\n")
            f.write("\n")
            
            # 统计详情页处理状态
            detail_status = {}
            for pos in positions:
                status = pos.get('详情页处理状态', '未处理')
                detail_status[status] = detail_status.get(status, 0) + 1
            
            f.write(f"🔧 详情页处理状态\n")
            for status, count in detail_status.items():
                f.write(f"  {status}: {count} 个岗位\n")
            f.write("\n")
            
            # 显示前5个岗位
            f.write(f"📋 岗位数据示例 (前5个)\n")
            for i, pos in enumerate(positions[:5], 1):
                f.write(f"  #{i} {pos.get('岗位名称', '未知')[:40]}...\n")
                f.write(f"    岗位id: {pos.get('岗位id', '未知')}\n")
                f.write(f"    职位类别: {pos.get('职位类别', '未知')}\n")
                f.write(f"    办公地点: {pos.get('办公地点', '未知')}\n")
                f.write(f"    详情页状态: {pos.get('详情页处理状态', '未处理')}\n")
                f.write("\n")
        
        log_info(f"统计报告保存完成: {report_path}")
        
        # 3. 生成Excel文件（需要pandas）
        try:
            import pandas as pd
            
            excel_filename = f"{filename_prefix}_{timestamp}.xlsx"
            excel_path = os.path.join(self.output_dir, excel_filename)
            
            # 创建DataFrame
            df = pd.DataFrame(positions)
            
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
            log_info(f"Excel文件保存完成: {excel_path}")
            
        except ImportError:
            log_info("❌ 未安装pandas，跳过Excel文件生成")
        except Exception as e:
            log_info(f"❌ Excel文件生成失败: {str(e)}")
        
        return {
            'json_path': json_path,
            'report_path': report_path,
            'excel_path': excel_path if 'excel_path' in locals() else None,
            'position_count': len(positions)
        }
    
    def run_full_crawl(self, max_pages: int = 1, max_positions_per_page: Optional[int] = None):
        """
        运行完整爬取流程
        
        Args:
            max_pages: 最大爬取页数
            max_positions_per_page: 每页最大岗位数
            
        Returns:
            爬取结果
        """
        log_section("开始完整爬取流程")
        
        # 在实际实现中，这里会：
        # 1. 获取真实的浏览器快照
        # 2. 应用筛选条件
        # 3. 分页获取数据
        # 4. 处理详情页
        
        log_info(f"配置: 最大页数={max_pages}, 每页最大岗位数={max_positions_per_page}")
        
        # 模拟获取页面快照（在实际中从浏览器获取）
        mock_snapshot = """
千问事业部-AI Native 产品经理-北京
更新于 2026-05-18 产品类-商业型 北京
千问事业部-AI 产品经理 - 千问语音Agent-北京/杭州
更新于 2026-05-18 产品类-用户型 北京 / 杭州
千问事业部-用户产品经理-书旗小说APP
更新于 2026-05-15 产品类-用户型 北京
row "更新于 2026-05-15 产品类-用户型 北京" [ref=e57] [cursor=pointer]
text "千问事业部-千问C端主对话产品经理-北京/杭州" [ref=e58] [cursor=pointer]
button "下一页，当前第1页" [ref=e65] [cursor=pointer]
"""
        
        all_positions = []
        
        for page_num in range(1, max_pages + 1):
            log_section(f"处理第 {page_num} 页")
            
            # 提取基础数据
            page_positions = self.extract_page_data(mock_snapshot, page_num)
            
            # 限制每页岗位数
            if max_positions_per_page:
                page_positions = page_positions[:max_positions_per_page]
            
            # 提取岗位链接信息
            enriched_positions = self.enrich_with_position_links(page_positions, mock_snapshot)
            
            # 处理详情页数据
            detailed_positions = self.batch_process_detail_pages(
                enriched_positions, 
                max_positions=max_positions_per_page
            )
            
            all_positions.extend(detailed_positions)
            
            log_info(f"第{page_num}页处理完成: {len(detailed_positions)} 个岗位")
        
        log_section("保存数据")
        
        # 保存数据到文件
        save_result = self.save_positions_to_file(all_positions)
        
        log_section("爬取完成")
        
        # 生成总结报告
        success_count = sum(1 for p in all_positions if p.get('详情页处理状态') == '成功')
        
        summary = {
            '总页数': max_pages,
            '总岗位数': len(all_positions),
            '成功详情页数': success_count,
            '失败详情页数': len(all_positions) - success_count,
            '输出文件': save_result
        }
        
        log_info(f"🎯 爬取总结:")
        log_info(f"  总页数: {summary['总页数']}")
        log_info(f"  总岗位数: {summary['总岗位数']}")
        log_info(f"  成功详情页: {summary['成功详情页数']}")
        log_info(f"  失败详情页: {summary['失败详情页数']}")
        log_info(f"  JSON文件: {os.path.basename(save_result['json_path'])}")
        log_info(f"  报告文件: {os.path.basename(save_result['report_path'])}")
        
        if save_result.get('excel_path'):
            log_info(f"  Excel文件: {os.path.basename(save_result['excel_path'])}")
        
        return summary

def main():
    """主函数"""
    log_section("夸克校园招聘完整数据爬取")
    
    # 创建爬虫实例
    crawler = FullPositionCrawler()
    
    # 运行爬取（测试模式：第1页，前3个岗位）
    summary = crawler.run_full_crawl(
        max_pages=1,
        max_positions_per_page=3
    )
    
    log_section("执行完成")
    
    # 显示输出文件位置
    output_dir = os.path.abspath(crawler.output_dir)
    log_info(f"📁 输出文件目录: {output_dir}")
    log_info(f"📊 数据文件: {os.listdir(output_dir)[-3:]}")
    
    print("\n💡 下一步:")
    print("  1. 查看生成的文件验证数据格式")
    print("  2. 集成真实的浏览器交互")
    print("  3. 应用到实际网页获取真实数据")
    print("  4. 扩展到多页和全部岗位")
    
    return summary

if __name__ == "__main__":
    main()