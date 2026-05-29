#!/bin/bash
echo "🧪 最终解决方案测试脚本"
echo "=========================================="
echo "测试目的：验证 boss_fixed 是否能正确处理 __zp_stoken__ 过期问题"
echo ""

# 设置路径
export PATH="/Users/xingan/Library/Python/3.12/bin:$PATH"

# 创建测试目录
TEST_DIR="/tmp/boss_fixed_test_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TEST_DIR"
echo "📁 测试目录: $TEST_DIR"
echo ""

# 测试1：检查命令是否存在
echo "1. 🔍 检查命令是否存在..."
echo "------------------------------------------"
which boss_fixed
if [ $? -eq 0 ]; then
    echo "✅ boss_fixed 命令存在"
else
    echo "❌ boss_fixed 命令不存在"
    echo "   请检查: /Users/xingan/Library/Python/3.12/bin/boss_fixed"
    exit 1
fi

# 测试2：检查权限
echo ""
echo "2. 🔐 检查命令权限..."
echo "------------------------------------------"
ls -la /Users/xingan/Library/Python/3.12/bin/boss_fixed
if [ -x "/Users/xingan/Library/Python/3.12/bin/boss_fixed" ]; then
    echo "✅ 命令有执行权限"
else
    echo "❌ 命令无执行权限"
    chmod +x /Users/xingan/Library/Python/3.12/bin/boss_fixed
    echo "   已添加执行权限"
fi

# 测试3：检查当前状态
echo ""
echo "3. 📊 检查当前登录状态..."
echo "------------------------------------------"
boss_fixed status
STATUS_CODE=$?

if [ $STATUS_CODE -eq 0 ]; then
    echo "✅ 状态检查正常"
    CURRENT_STATUS="valid"
else
    echo "⚠️  状态检查异常"
    CURRENT_STATUS="invalid"
fi

# 测试4：测试搜索功能（带自动刷新）
echo ""
echo "4. 🔍 测试搜索功能（自动处理 __zp_stoken__）..."
echo "------------------------------------------"
echo "注意：如果 __zp_stoken__ 过期，boss_fixed 会自动尝试刷新"
echo ""

# 执行搜索
boss_fixed search "AI" --city "深圳" --page 1
SEARCH_CODE=$?

if [ $SEARCH_CODE -eq 0 ]; then
    echo "✅ 搜索成功"
    
    # 保存结果
    echo ""
    echo "5. 💾 保存测试结果..."
    echo "------------------------------------------"
    boss_fixed search "AI" --city "深圳" --page 1 --json > "$TEST_DIR/search_result.json"
    
    # 统计职位数量
    JOB_COUNT=$(cat "$TEST_DIR/search_result.json" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('ok'):
        jobs = data.get('data', {}).get('jobList', [])
        print(len(jobs))
    else:
        print(0)
except:
    print(0)
" 2>/dev/null)
    
    echo "📊 找到 $JOB_COUNT 个职位"
    echo "📁 结果保存到: $TEST_DIR/search_result.json"
    
    # 如果找到职位，测试详情功能
    if [ "$JOB_COUNT" -gt 0 ]; then
        echo ""
        echo "6. 📋 测试职位详情功能..."
        echo "------------------------------------------"
        
        # 获取第一个职位详情
        echo "获取第1个职位详情..."
        boss_fixed show 1 > "$TEST_DIR/job_1_detail.txt"
        echo "✅ 详情保存到: $TEST_DIR/job_1_detail.txt"
        
        if [ "$JOB_COUNT" -gt 1 ]; then
            echo "获取第2个职位详情..."
            boss_fixed show 2 > "$TEST_DIR/job_2_detail.txt"
            echo "✅ 详情保存到: $TEST_DIR/job_2_detail.txt"
        fi
    fi
else
    echo "❌ 搜索失败"
    echo ""
    echo "7. 🛠️ 故障诊断..."
    echo "------------------------------------------"
    
    # 诊断问题
    echo "a) 检查原始boss命令状态:"
    boss status 2>&1 | head -10
    
    echo ""
    echo "b) 建议修复步骤:"
    echo "   1. 执行: boss logout"
    echo "   2. 打开浏览器登录 https://www.zhipin.com"
    echo "   3. 执行: boss login --cookie-source chrome"
    echo "   4. 重新运行此测试脚本"
fi

# 生成测试报告
echo ""
echo "=========================================="
echo "📋 测试报告"
echo "------------------------------------------"
echo "测试时间: $(date)"
echo "测试目录: $TEST_DIR"
echo "当前状态: $CURRENT_STATUS"
echo "搜索测试: $(if [ $SEARCH_CODE -eq 0 ]; then echo '✅ 成功'; else echo '❌ 失败'; fi)"
if [ -f "$TEST_DIR/search_result.json" ]; then
    echo "职位数量: $JOB_COUNT"
    echo "详情文件:"
    ls -la "$TEST_DIR/"*.txt 2>/dev/null | awk '{print "  " $9 " (" $5 " bytes)"}'
fi

echo ""
echo "🔧 后续步骤:"
if [ $SEARCH_CODE -eq 0 ]; then
    echo "✅ 测试通过！可以开始使用 boss_fixed 命令"
    echo ""
    echo "📋 使用示例:"
    echo "  boss_fixed search AI --city 深圳 --page 1"
    echo "  boss_fixed show 1"
    echo "  boss_fixed status"
    echo ""
    echo "🚀 快速开始:"
    echo "  sh ~/.openclaw/workspace/quick_boss_fixed.sh"
else
    echo "❌ 需要先解决登录问题"
    echo ""
    echo "🛠️ 修复步骤:"
    echo "  1. boss logout"
    echo "  2. 浏览器登录 https://www.zhipin.com"
    echo "  3. boss login --cookie-source chrome"
    echo "  4. 重新运行此测试"
fi

echo ""
echo "📚 详细文档:"
echo "  ~/.openclaw/workspace/skills/job-search/SOLUTION_FINAL.md"
echo "  ~/.openclaw/workspace/BOSS_FIXED_README.md"
echo "=========================================="