# 方案B执行环境（迁移到技能目录）

## 📍 目录说明
- **源目录**: /Users/xingan/招聘数据/方案B_立即执行_20260515_010114
- **目标目录**: /Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output

## 📋 迁移内容
1. **核心数据文件**: all_security_ids_final.txt, fetched_security_ids.txt 等
2. **搜索结果**: search_page*.json 文件
3. **职位详情**: 职位详情/ 目录
4. **Excel文件**: 深圳_ai.xlsx 及备份

## 🚀 使用方法
1. 设置环境变量:
   ```bash
   export SCHEME_B_WORKSPACE="/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output"
   ```

2. 使用技能脚本:
   ```bash
   cd ~/.openclaw/workspace/skills/job-search/scheme_b
   python3 scripts/fetch_details_conservative_v2.py
   ```

## 📊 当前状态
- 总职位数: 150个
- 已获取详情: 68个 (45.3%)
- 未获取详情: 82个
- 目标: 达到75个 (50%)

## 🎯 下一步
继续获取详情直到达到50%完成率
