#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘快速爬取器
交互式获取签名并立即爬取
"""

import requests
import json
import os
from datetime import datetime

print("=" * 70)
print("🚀 快手招聘快速爬取器")
print("=" * 70)
print("说明: 签名有效期极短，请立即使用")
print()

# 基础配置
BASE_URL = "https://zhaopin.kuaishou.cn"
API_PATH = "/recruit/e/api/v1/open/positions/simple"
API_URL = BASE_URL + API_PATH

OUTPUT_DIR = "output/ks_quick"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 基础Cookie
BASE_COOKIE = "aliyungf_tc=62d111759197e609997a914760f88ccc44c00ef73b2f542817802af91250a937; accessproxy_session=01b7eac0ccce9f49aa335ac52039ec8a825379cdb3EAIiE3poYW9waW4ua3VhaXNob3UuY24KJGJiODA2NjMzLTVmODgtNGI5Yy1iM2QyLTBlMjEwZmI1NGEzZioVEhFVTkFVVEhPUklaRURfVVNFUgoAGLHJ1Of+Mw==; apdid=1e615e70-2858-4116-bd0e-5e461bd10eb4cc68ec35bc432b6780dc98e63f48cce7:1779186916:1; weblogger_did=web_754734862580340E"

def get_signature_from_user():
    """从用户获取签名"""
    print("📝 请从浏览器获取最新签名:")
    print("   1. 打开 https://zhaopin.kuaishou.cn")
    print("   2. 按F12打开开发者工具")
    print("   3. 切换到Network标签")
    print("   4. 刷新页面")
    print("   5. 找到API请求: positions/simple")
    print("   6. 复制 sign 和 signtimestamp")
    print()
    
    sign = input("请输入 sign: ").strip()
    signtimestamp = input("请输入 signtimestamp: ").strip()
    
    return sign, signtimestamp

def create_headers(sign, signtimestamp):
    """创建请求头"""
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Cookie": BASE_COOKIE,
        "Host": "zhaopin.kuaishou.cn",
        "Pragma": "no-cache",
        "Referer": "https://zhaopin.kuaishou.cn/",
        "Sec-Ch-Ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "sign": sign,
        "signtimestamp": signtimestamp
    }

def test_signature(sign, signtimestamp):
    """测试签名有效性"""
    print(f"🔍 测试签名: {signtimestamp}")
    
    headers = create_headers(sign, signtimestamp)
    params = {
        "pageNum": 1,
        "pageSize": 1,
        "positionCategoryCode": "J0005,J0004,J0013,J0006,J0014",
        "positionNatureCode": "C001",
        "recruitProject": "socialr",
        "workLocationCode": "domestic"
    }
    
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                print("✅ 签名有效！")
                return True
            else:
                print(f"❌ 签名无效: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def fetch_page(page_num, sign, signtimestamp, page_size=10):
    """获取单页数据"""
    print(f"📄 获取第 {page_num} 页...")
    
    headers = create_headers(sign, signtimestamp)
    params = {
        "pageNum": page_num,
        "pageSize": page_size,
        "positionCategoryCode": "J0005,J0004,J0013,J0006,J0014",
        "positionNatureCode": "C001",
        "recruitProject": "socialr",
        "workLocationCode": "domestic"
    }
    
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                result = data.get("result", {})
                positions = result.get('list', [])
                print(f"✅ 获取成功: {len(positions)} 个岗位")
                return data
            else:
                print(f"❌ API错误: {data.get('message')}")
                return None
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def save_position(position_data):
    """保存岗位数据"""
    position_id = str(position_data.get("id", "unknown"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 标准化数据
    standard_data = {
        "positionId": position_id,
        "positionName": position_data.get("name", ""),
        "workLocation": position_data.get("workLocationCode", ""),
        "positionCategory": position_data.get("positionCategoryCode", ""),
        "publishTime": position_data.get("updateTime", ""),
        "detailUrl": f"{BASE_URL}/position/{position_id}",
        "department": position_data.get("departmentCode", ""),
        "educationRequirement": position_data.get("educationLimitCode", ""),
        "workExperience": position_data.get("workExperienceCode", ""),
        "jobResponsibilities": position_data.get("description", ""),
        "jobRequirements": position_data.get("positionDemand", ""),
        "salaryRange": "",
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawlMode": "quick",
        "source": "kuaishou_quick"
    }
    
    filename = f"ks_position_{position_id}_{timestamp}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(standard_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 保存: {filename}")
        return filepath
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return None

def main():
    """主函数"""
    print("🔄 开始获取签名...")
    
    # 获取签名
    sign, signtimestamp = get_signature_from_user()
    
    if not sign or not signtimestamp:
        print("❌ 签名参数不能为空")
        return
    
    # 测试签名
    if not test_signature(sign, signtimestamp):
        print("❌ 签名无效，请重新获取")
        return
    
    print()
    print("✅ 签名有效，可以开始爬取！")
    print()
    
    # 询问爬取页数
    try:
        max_pages = int(input("请输入最大爬取页数（默认1）: ") or "1")
    except ValueError:
        print("⚠️ 输入无效，使用默认值1")
        max_pages = 1
    
    print()
    print(f"🚀 开始爬取 {max_pages} 页数据...")
    print()
    
    all_positions = []
    saved_files = []
    
    for page_num in range(1, max_pages + 1):
        print(f"📊 进度: {page_num}/{max_pages}")
        
        # 获取页面数据
        page_data = fetch_page(page_num, sign, signtimestamp, page_size=5)
        
        if not page_data:
            print(f"❌ 第 {page_num} 页获取失败")
            break
        
        result = page_data.get("result", {})
        positions = result.get('list', [])
        
        if not positions:
            print(f"⚠️ 第 {page_num} 页无数据")
            break
        
        # 保存每个岗位
        for position in positions:
            filepath = save_position(position)
            if filepath:
                saved_files.append(filepath)
            all_positions.append(position)
        
        print(f"✅ 第 {page_num} 页完成: {len(positions)} 个岗位")
        print()
        
        # 如果是第一页，显示统计信息
        if page_num == 1:
            total = result.get('total', 0)
            pages = result.get('pages', 0)
            print(f"📊 统计: {total} 个岗位，共 {pages} 页")
            print()
        
        # 如果不是最后一页，询问是否继续
        if page_num < max_pages:
            choice = input(f"是否继续获取第 {page_num + 1} 页？(y/N): ").strip().lower()
            if choice != 'y':
                print("⏹️ 用户选择停止")
                break
    
    # 显示结果
    print("=" * 60)
    print("🎉 爬取完成！")
    print(f"   获取岗位: {len(all_positions)} 个")
    print(f"   保存文件: {len(saved_files)} 个")
    print(f"   输出目录: {OUTPUT_DIR}")
    print()
    
    # 显示保存的文件
    if saved_files:
        print("📁 保存的文件:")
        for i, filepath in enumerate(saved_files[:5], 1):
            filename = os.path.basename(filepath)
            print(f"  {i}. {filename}")
        
        if len(saved_files) > 5:
            print(f"  ... 还有 {len(saved_files) - 5} 个文件")
    
    print("=" * 60)
    
    # 提供下一步建议
    print()
    print("💡 下一步:")
    print("  1. 查看数据: ls output/ks_quick/")
    print("  2. 查看文件内容: cat output/ks_quick/*.json | head -100")
    print("  3. 继续爬取: 重新运行此脚本")
    print("  4. 分析数据: 使用其他工具分析JSON文件")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("⏹️ 用户中断")
    except Exception as e:
        print(f"❌ 程序异常: {e}")