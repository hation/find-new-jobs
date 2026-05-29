#!/bin/bash
# 快手招聘简单爬取脚本
# 手动获取签名，立即爬取

echo "========================================"
echo "🚀 快手招聘简单爬取脚本"
echo "========================================"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 创建输出目录
OUTPUT_DIR="output/ks_simple"
mkdir -p "$OUTPUT_DIR"
LOG_FILE="logs/simple_crawl.log"
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="[$timestamp] $1"
    echo "$message"
    echo "$message" >> "$LOG_FILE"
}

log "🔍 开始快手招聘数据爬取"

# 显示操作指南
echo ""
echo "📝 操作指南:"
echo "   1. 打开浏览器访问: https://zhaopin.kuaishou.cn"
echo "   2. 按F12打开开发者工具"
echo "   3. 切换到Network标签"
echo "   4. 刷新页面"
echo "   5. 找到API请求: positions/simple"
echo "   6. 复制最新的 sign 和 signtimestamp"
echo "   7. 立即使用（有效期极短）"
echo ""

# 获取用户输入
read -p "请输入 sign: " SIGN
read -p "请输入 signtimestamp: " SIGNTIMESTAMP

if [ -z "$SIGN" ] || [ -z "$SIGNTIMESTAMP" ]; then
    log "❌ 签名参数不能为空"
    exit 1
fi

log "✅ 获取到签名参数"
log "   sign: ${SIGN:0:20}..."
log "   signtimestamp: $SIGNTIMESTAMP"

# 创建Python脚本
PYTHON_SCRIPT=$(cat <<EOF
#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime

# 签名参数
SIGN = "$SIGN"
SIGNTIMESTAMP = "$SIGNTIMESTAMP"

# 输出目录
OUTPUT_DIR = "$OUTPUT_DIR"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "aliyungf_tc=62d111759197e609997a914760f88ccc44c00ef73b2f542817802af91250a937; accessproxy_session=01b7eac0ccce9f49aa335ac52039ec8a825379cdb3EAIiE3poYW9waW4ua3VhaXNob3UuY24KJGJiODA2NjMzLTVmODgtNGI5Yy1iM2QyLTBlMjEwZmI1NGEzZioVEhFVTkFVVEhPUklaRURfVVNFUgoAGLHJ1Of+Mw==; apdid=1e615e70-2858-4116-bd0e-5e461bd10eb4cc68ec35bc432b6780dc98e63f48cce7:1779186916:1; weblogger_did=web_754734862580340E",
    "Host": "zhaopin.kuaishou.cn",
    "Pragma": "no-cache",
    "Referer": "https://zhaopin.kuaishou.cn/",
    "Sec-Ch-Ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"macOS\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "sign": SIGN,
    "signtimestamp": SIGNTIMESTAMP
}

# API配置
API_URL = "https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple"

print("🔍 测试签名有效性...")

# 测试签名
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
        else:
            print(f"❌ 签名无效: {data.get('message')}")
            exit(1)
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        exit(1)
        
except Exception as e:
    print(f"❌ 测试失败: {e}")
    exit(1)

print()
print("🚀 开始爬取数据...")

# 获取第一页数据
params["pageSize"] = 5  # 只取5条
response = requests.get(API_URL, params=params, headers=headers, timeout=30)

if response.status_code == 200:
    data = response.json()
    
    if data.get("code") == 0:
        result = data.get("result", {})
        positions = result.get("list", [])
        total = result.get("total", 0)
        pages = result.get("pages", 0)
        
        print(f"✅ 获取成功: {len(positions)} 个岗位")
        print(f"📊 统计: {total} 个岗位，共 {pages} 页")
        print()
        
        # 保存每个岗位
        saved_files = []
        
        for i, position in enumerate(positions, 1):
            print(f"📝 处理第 {i} 个岗位: {position.get('name', '未知')[:30]}...")
            
            # 标准化数据
            standard_data = {
                "positionId": str(position.get("id", "")),
                "positionName": position.get("name", ""),
                "workLocation": position.get("workLocationCode", ""),
                "positionCategory": position.get("positionCategoryCode", ""),
                "publishTime": position.get("updateTime", ""),
                "detailUrl": f"https://zhaopin.kuaishou.cn/position/{position.get('id', '')}",
                "department": position.get("departmentCode", ""),
                "educationRequirement": position.get("educationLimitCode", ""),
                "workExperience": position.get("workExperienceCode", ""),
                "jobResponsibilities": position.get("description", ""),
                "jobRequirements": position.get("positionDemand", ""),
                "salaryRange": "",
                "company": "快手",
                "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "crawlMode": "simple",
                "source": "kuaishou_simple",
                "signatureTimestamp": SIGNTIMESTAMP
            }
            
            # 保存文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            position_id = standard_data["positionId"]
            filename = f"ks_position_{position_id}_{timestamp}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(standard_data, f, ensure_ascii=False, indent=2)
                
                print(f"💾 保存: {filename}")
                saved_files.append(filepath)
            except Exception as e:
                print(f"❌ 保存失败: {e}")
        
        print()
        print("=" * 60)
        print("🎉 爬取完成！")
        print(f"   获取岗位: {len(positions)} 个")
        print(f"   保存文件: {len(saved_files)} 个")
        print(f"   输出目录: {OUTPUT_DIR}")
        print("=" * 60)
        
        # 显示第一个岗位详情
        if positions:
            first_position = positions[0]
            print()
            print("📄 第一个岗位详情:")
            print(f"   ID: {first_position.get('id')}")
            print(f"   名称: {first_position.get('name')}")
            print(f"   地点: {first_position.get('workLocationCode')}")
            print(f"   类别: {first_position.get('positionCategoryCode')}")
            print(f"   工作经验: {first_position.get('workExperienceCode')}")
            print()
    else:
        print(f"❌ API错误: {data.get('message')}")
else:
    print(f"❌ HTTP错误: {response.status_code}")
EOF
)

# 创建并运行Python脚本
echo "$PYTHON_SCRIPT" > /tmp/ks_crawl_temp.py
python3 /tmp/ks_crawl_temp.py

# 清理临时文件
rm -f /tmp/ks_crawl_temp.py

echo ""
echo "💡 下一步:"
echo "  1. 查看数据: ls $OUTPUT_DIR/"
echo "  2. 查看日志: cat $LOG_FILE"
echo "  3. 继续爬取: 重新运行此脚本"
echo "  4. 获取更多数据: 使用浏览器自动化方案"
echo ""
echo "========================================"
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"