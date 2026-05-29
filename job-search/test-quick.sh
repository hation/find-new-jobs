#!/bin/bash

echo "🧪 job-search GBrain 集成快速测试"
echo "========================================"

SKILL_DIR="/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search"

# 检查文件
echo "1. 检查文件..."
if [ -f "$SKILL_DIR/adapters/job-to-gbrain.js" ]; then
    echo "✅ 适配器文件存在"
else
    echo "❌ 适配器文件不存在"
    exit 1
fi

if [ -f "$SKILL_DIR/job-search-gbrain.js" ]; then
    echo "✅ 包装器文件存在"
else
    echo "❌ 包装器文件不存在"
    exit 1
fi

if [ -f "$SKILL_DIR/config/gbrain-config.json" ]; then
    echo "✅ 配置文件存在"
else
    echo "❌ 配置文件不存在"
    exit 1
fi

# 检查权限
echo ""
echo "2. 检查文件权限..."
chmod +x "$SKILL_DIR/adapters/job-to-gbrain.js" 2>/dev/null
chmod +x "$SKILL_DIR/job-search-gbrain.js" 2>/dev/null

if [ -x "$SKILL_DIR/adapters/job-to-gbrain.js" ]; then
    echo "✅ 适配器可执行"
else
    echo "❌ 适配器不可执行"
fi

if [ -x "$SKILL_DIR/job-search-gbrain.js" ]; then
    echo "✅ 包装器可执行"
else
    echo "❌ 包装器不可执行"
fi

# 测试适配器帮助
echo ""
echo "3. 测试适配器帮助..."
cd "$SKILL_DIR"
if node adapters/job-to-gbrain.js --help 2>&1 | grep -q "用法:"; then
    echo "✅ 适配器帮助命令正常"
else
    echo "❌ 适配器帮助命令异常"
    node adapters/job-to-gbrain.js --help
fi

# 测试包装器帮助
echo ""
echo "4. 测试包装器帮助..."
if node job-search-gbrain.js --help 2>&1 | grep -q "用法:"; then
    echo "✅ 包装器帮助命令正常"
else
    echo "❌ 包装器帮助命令异常"
    node job-search-gbrain.js --help
fi

# 测试配置命令
echo ""
echo "5. 测试配置命令..."
if node job-search-gbrain.js config 2>&1 | grep -q "gbrain"; then
    echo "✅ 配置命令正常"
else
    echo "❌ 配置命令异常"
fi

# 测试检查命令
echo ""
echo "6. 测试检查命令..."
if node job-search-gbrain.js check 2>&1 | grep -q "Node.js"; then
    echo "✅ 检查命令正常"
else
    echo "❌ 检查命令异常"
fi

# 创建测试招聘数据
echo ""
echo "7. 创建测试招聘数据..."
TEST_JOB_JSON='{
  "jobName": "AI开发工程师",
  "brandName": "腾讯科技",
  "salaryDesc": "25-40K",
  "jobExperience": "3-5年",
  "jobDegree": "本科",
  "cityName": "深圳",
  "brandScaleName": "10000人以上",
  "brandIndustryName": "互联网",
  "brandStageName": "已上市",
  "jobDescription": "负责AI相关产品的开发工作，要求有机器学习、深度学习相关经验。",
  "publishTime": "2026-05-26T10:30:00Z"
}'

echo "✅ 测试招聘数据已创建"

# 测试适配器处理
echo ""
echo "8. 测试适配器处理..."
if node adapters/job-to-gbrain.js process "$TEST_JOB_JSON" 2>&1 | grep -q "招聘数据已保存到 GBrain"; then
    echo "✅ 适配器处理测试通过"
else
    echo "⚠️  适配器处理测试可能有问题"
    node adapters/job-to-gbrain.js process "$TEST_JOB_JSON"
fi

# 测试包装器搜索
echo ""
echo "9. 测试包装器搜索..."
if node job-search-gbrain.js search "测试招聘" 2>&1 | grep -q "执行招聘搜索"; then
    echo "✅ 包装器搜索测试通过"
else
    echo "⚠️  包装器搜索测试可能有问题"
    node job-search-gbrain.js search "测试招聘"
fi

# 测试查询
echo ""
echo "10. 测试招聘历史查询..."
if gbrain query "测试招聘" 2>&1 | grep -q "招聘搜索"; then
    echo "✅ 招聘历史查询测试通过"
else
    echo "⚠️  招聘历史查询未找到结果，可能的原因:"
    echo "   - 数据未保存成功"
    echo "   - 需要等待索引更新"
    gbrain query "招聘"
fi

echo ""
echo "========================================"
echo "📊 快速测试完成"
echo ""
echo "🎯 建议的完整测试流程:"
echo "1. 配置 boss-cli 环境"
echo "2. 运行实际的 BOSS直聘搜索"
echo "3. 将搜索结果通过适配器保存"
echo "4. 验证招聘历史查询功能"
echo "5. 测试批量处理招聘数据"

echo ""
echo "⚠️  重要提示:"
echo "实际招聘搜索需要 boss-cli 工具"
echo "请确保已安装并配置 boss-cli"