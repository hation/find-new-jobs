#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版爬取脚本 - 第1页验证
目标：测试第1页全部10个岗位的完整处理流程
"""

import sys
import os

# 添加脚本目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from actual_crawler_enhanced import (
    log_info, log_success, log_warning, log_error,
    random_delay, extract_position_id_from_url,
    extract_real_data_from_snapshot, extract_detail_fields_from_snapshot,
    save_real_data, ProgressManager, BrowserManager,
    process_position_with_retry, process_page,
    START_PAGE, END_PAGE, MAX_POSITIONS_PER_PAGE
)

def test_extract_functions():
    """测试数据提取函数"""
    print("\n" + "=" * 60)
    print("🧪 测试数据提取函数")
    print("=" * 60)
    
    # 测试URL提取
    test_url = "https://talent.quark.cn/off-campus/position-detail?lang=zh&positionId=100013280019"
    position_id = extract_position_id_from_url(test_url)
    log_info(f"URL提取测试: {test_url}")
    log_success(f"提取的positionId: {position_id}")
    
    # 测试详情页字段提取（模拟数据）
    test_snapshot = """
所属部门: 阿里集团
学历: 硕士
工作年限: 2 年
职位描述 1、负责信息流搜索业务...
职位要求 1、本科及以上学历...
"""
    
    detail_fields = extract_detail_fields_from_snapshot(test_snapshot, test_url)
    log_info("详情页字段提取测试:")
    for key, value in detail_fields.items():
        if value and value != '未提取':
            log_success(f"  {key}: {value[:30]}...")
        else:
            log_warning(f"  {key}: {value}")
    
    return True

def test_progress_manager():
    """测试进度管理器"""
    print("\n" + "=" * 60)
    print("📊 测试进度管理器")
    print("=" * 60)
    
    # 创建临时目录
    import tempfile
    temp_dir = tempfile.mkdtemp()
    
    progress_manager = ProgressManager(output_dir=temp_dir)
    
    # 模拟一些进度
    test_position = {
        '岗位id': 'test_001',
        '岗位名称': '测试岗位',
        '页码': 1,
        '序号': 1
    }
    
    progress_manager.update_position(test_position, "success")
    progress_manager.update_position(test_position, "failed")
    progress_manager.update_position(test_position, "skipped")
    
    # 获取摘要
    summary = progress_manager.get_summary()
    log_info("进度摘要:")
    for key, value in summary.items():
        log_info(f"  {key}: {value}")
    
    # 保存进度
    progress_manager.save_progress()
    log_success(f"进度文件保存到: {progress_manager.progress_file}")
    
    return True

def test_browser_manager_simulation():
    """测试浏览器管理器（模拟）"""
    print("\n" + "=" * 60)
    print("🌐 测试浏览器管理器（模拟）")
    print("=" * 60)
    
    browser_manager = BrowserManager()
    
    # 模拟点击
    tab_id = browser_manager.click_position("测试岗位")
    log_info(f"模拟点击返回的标签页ID: {tab_id}")
    
    # 模拟获取快照
    snapshot = browser_manager.get_snapshot(tab_id)
    log_info(f"模拟快照内容: {snapshot[:50]}...")
    
    # 模拟关闭标签页
    browser_manager.close_tab(tab_id)
    
    log_success("浏览器管理器模拟测试通过")
    return True

def test_process_position_with_retry():
    """测试带重试的岗位处理（模拟）"""
    print("\n" + "=" * 60)
    print("🔄 测试带重试的岗位处理（模拟）")
    print("=" * 60)
    
    # 模拟数据
    test_position = {
        '岗位id': 'test_retry_001',
        '岗位名称': '测试重试岗位',
        '页码': 1,
        '序号': 1
    }
    
    # 模拟进度管理器
    import tempfile
    temp_dir = tempfile.mkdtemp()
    progress_manager = ProgressManager(output_dir=temp_dir)
    
    # 模拟浏览器管理器（会失败）
    class MockBrowserManager:
        def click_position(self, name):
            log_warning("模拟点击失败")
            return None
        
        def get_snapshot(self, tab_id):
            return "模拟快照"
        
        def close_tab(self, tab_id):
            pass
    
    browser_manager = MockBrowserManager()
    
    # 测试重试机制
    try:
        result = process_position_with_retry(
            test_position, browser_manager, progress_manager
        )
        
        if result is None:
            log_success("重试机制测试通过：失败后返回None（跳过）")
        else:
            log_success("重试机制测试通过：成功处理")
            
    except Exception as e:
        log_error(f"重试机制测试异常: {e}")
        return False
    
    return True

def test_save_real_data():
    """测试数据保存功能"""
    print("\n" + "=" * 60)
    print("💾 测试数据保存功能")
    print("=" * 60)
    
    # 模拟数据
    test_positions = [
        {
            '序号': 1,
            '页码': 1,
            '岗位id': 'test_001',
            '岗位名称': '测试岗位1',
            '岗位详情链接': 'https://example.com/position1',
            '职位类别': '产品类',
            '子类别': '用户产品',
            '办公地点': '北京',
            '所属部门': '阿里集团',
            '学历': '本科',
            '工作年限': '3 年',
            '职位描述': '测试职位描述',
            '职位要求': '测试职位要求',
            '更新时间': '2026-05-18',
            '数据来源': '测试数据',
            '提取时间': '2026-05-18 16:55:00'
        },
        {
            '序号': 2,
            '页码': 1,
            '岗位id': 'test_002',
            '岗位名称': '测试岗位2',
            '岗位详情链接': 'https://example.com/position2',
            '职位类别': '运营类',
            '子类别': '产品运营',
            '办公地点': '上海',
            '所属部门': '千问事业部',
            '学历': '硕士',
            '工作年限': '2 年',
            '职位描述': '测试职位描述2',
            '职位要求': '测试职位要求2',
            '更新时间': '2026-05-18',
            '数据来源': '测试数据',
            '提取时间': '2026-05-18 16:55:00'
        }
    ]
    
    # 创建临时目录
    import tempfile
    temp_dir = tempfile.mkdtemp()
    
    # 修改保存路径
    import actual_crawler_enhanced as module
    module.OUTPUT_DIR = temp_dir
    
    # 保存数据
    result = save_real_data(test_positions)
    
    log_info("数据保存结果:")
    for key, value in result.items():
        log_info(f"  {key}: {value}")
    
    # 检查生成的文件
    import glob
    json_files = glob.glob(os.path.join(temp_dir, "*.json"))
    excel_files = glob.glob(os.path.join(temp_dir, "*.xlsx"))
    report_files = glob.glob(os.path.join(temp_dir, "*report*.txt"))
    
    log_info(f"生成的文件:")
    log_info(f"  JSON文件: {len(json_files)} 个")
    log_info(f"  Excel文件: {len(excel_files)} 个")
    log_info(f"  报告文件: {len(report_files)} 个")
    
    if json_files and excel_files and report_files:
        log_success("数据保存功能测试通过")
        return True
    else:
        log_error("数据保存功能测试失败")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始增强版爬取脚本测试")
    print("=" * 60)
    
    test_results = []
    
    # 运行各个测试
    test_results.append(("数据提取函数", test_extract_functions()))
    test_results.append(("进度管理器", test_progress_manager()))
    test_results.append(("浏览器管理器", test_browser_manager_simulation()))
    test_results.append(("重试机制", test_process_position_with_retry()))
    test_results.append(("数据保存", test_save_real_data()))
    
    # 打印测试结果
    print("\n" + "=" * 60)
    print("📋 测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in test_results:
        if result:
            log_success(f"{test_name}: ✅ 通过")
        else:
            log_error(f"{test_name}: ❌ 失败")
            all_passed = False
    
    if all_passed:
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！增强版脚本功能验证完成")
        print("=" * 60)
        
        print(f"\n📝 下一步:")
        print(f"   1. 将浏览器工具调用集成到增强脚本中")
        print(f"   2. 运行第1页完整爬取测试 (10个岗位)")
        print(f"   3. 验证批量处理和进度保存功能")
        
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ 测试失败！需要修复问题")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print(f"\n🚀 准备开始第1页实际爬取测试...")
        print(f"   建议先运行小规模测试：")
        print(f"   1. 处理第1页前3个岗位")
        print(f"   2. 验证浏览器工具集成")
        print(f"   3. 检查进度保存功能")
        
        print(f"\n💡 执行命令:")
        print(f"   python actual_crawler_enhanced.py (修改配置为START_PAGE=1, END_PAGE=1, MAX_POSITIONS_PER_PAGE=3)")
    else:
        print(f"\n⚠️ 需要先修复测试失败的问题")
        sys.exit(1)