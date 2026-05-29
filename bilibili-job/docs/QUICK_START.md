# QUICK_START.md - B站招聘数据爬取器快速开始指南

## 🚀 5分钟快速开始

### **步骤1：环境准备**
```bash
# 1. 进入项目目录
cd /Users/xingan/.openclaw/workspace/skills/find_new_jobs/bilibili-job

# 2. 安装Python依赖（如果还没安装）
pip install -r requirements.txt

# 3. 验证环境
python3 --version  # 应该显示 Python 3.12.8
```

### **步骤2：配置检查**
```bash
# 1. 检查配置文件
ls -la config/

# 应该看到：
# - api_auth.json      # B站API配置
# - .env               # 环境变量配置
# - browser_config.json # 浏览器配置（可选）

# 2. 检查目录结构
ls -la data/bilibili/ output/bilibili/ logs/bilibili/
```

### **步骤3：运行功能测试**
```bash
# 运行完整的测试套件
python3 test_bilibili_crawler.py

# 期望结果：所有测试通过 ✅
```

### **步骤4：测试API连接**
```bash
# 运行API爬取器测试（只爬取第1页）
python3 src/bilibili_api_crawler.py

# 按照提示操作：
# 1. 选择测试第1页
# 2. 查看返回的数据样本
# 3. 选择是否继续爬取更多页
```

### **步骤5：使用智能爬取器**
```bash
# 运行智能爬取器（基于夸克框架）
python3 src/bilibili_smart_crawler.py

# 功能包括：
# 1. 自动测试API连接
# 2. 智能选择爬取策略
# 3. 数据导出到多种格式
# 4. 错误处理和用户交互
```

## 📊 数据爬取示例

### **爬取所有页数据**
```python
# 使用API爬取器爬取所有页
from src.bilibili_api_crawler import BilibiliAPICrawler

crawler = BilibiliAPICrawler("config/api_auth.json")
all_data = crawler.crawl_all_pages(max_pages=10)  # 爬取前10页
print(f"爬取到 {len(all_data)} 条数据")
```

### **导出数据到Excel**
```python
from src.bilibili_api_crawler import BilibiliAPICrawler
from framework.data_exporter import DataExporter

# 爬取数据
crawler = BilibiliAPICrawler("config/api_auth.json")
data = crawler.crawl_all_pages(max_pages=5)

# 导出数据
exporter = DataExporter()
result = exporter.export_data(
    data=data,
    format="excel",  # 也可以选择 "csv", "json", "all"
    company_name="bilibili"
)

if result["success"]:
    print(f"数据已导出到: {result['files']['excel']}")
```

## 🔧 配置说明

### **1. API配置 (`config/api_auth.json`)**
```json
{
  "bilibili": {
    "base_url": "https://jobs.bilibili.com",
    "api_endpoint": "/api/srs/position/positionList",
    "request_method": "POST",
    "request_headers": {
      "x-appkey": "ops.ehr-api.auth",
      "x-channel": "social",
      "user-agent": "Mozilla/5.0..."
    },
    "default_params": {
      "pageSize": 10,
      "pageNum": 1,
      "positionName": "",
      "postCode": ["03", "05", "11", "08", "07"],
      "postCodeList": ["03", "05", "11", "08", "07"],
      "workLocationList": [],
      "workTypeList": ["3"],
      "positionTypeList": ["3"],
      "deptCodeList": [],
      "recruitType": 0,
      "practiceTypes": [],
      "onlyHotRecruit": 0
    }
  }
}
```

### **2. 字段映射**
B站API返回的字段会自动映射到标准字段：

| B站字段 | 标准字段 | 说明 |
|---------|----------|------|
| `id` | `position_id` | 岗位ID |
| `positionName` | `title` | 岗位标题 |
| `postCodeName` | `category` | 岗位类别 |
| `workLocation` | `location` | 工作地点 |
| `pushTime` | `publish_time` | 发布时间 |
| `positionDescription` | `description` | 岗位描述 |

## 🛠️ 常见问题解决

### **问题1：API连接失败**
```
❌ 测试失败: HTTP错误: 403
```

**解决方案**:
1. 检查Cookie是否有效
2. 更新CSRF Token
3. 检查请求头是否完整

```bash
# 更新Cookie配置
vim config/api_auth.json
# 在authentication.cookie中更新最新的Cookie值
```

### **问题2：数据为空**
```
⚠️ 第1页没有数据
```

**解决方案**:
1. 检查请求参数是否正确
2. 确认B站招聘网站是否有数据
3. 尝试不同的postCode参数

### **问题3：导出失败**
```
❌ 导出失败: Excel导出失败
```

**解决方案**:
1. 安装pandas和openpyxl
```bash
pip install pandas openpyxl
```

## 📈 数据验证

### **检查爬取的数据**
```bash
# 查看生成的数据文件
ls -la output/bilibili/

# 查看数据文件内容
cat output/bilibili/bilibili_jobs_*.json | head -100
```

### **数据完整性检查**
```python
from src.bilibili_api_crawler import BilibiliAPICrawler

crawler = BilibiliAPICrawler("config/api_auth.json")
data = crawler.crawl_all_pages(max_pages=2)

# 检查数据完整性
for job in data:
    required_fields = ["position_id", "title", "location", "category", "publish_time"]
    missing = [field for field in required_fields if not job.get(field)]
    if missing:
        print(f"⚠️ 岗位 {job.get('title')} 缺少字段: {missing}")
```

## 🚀 高级用法

### **定时爬取**
```bash
# 使用cron定时任务
crontab -e
# 添加以下行（每天凌晨2点爬取）
0 2 * * * cd /Users/xingan/.openclaw/workspace/skills/find_new_jobs/bilibili-job && python3 src/bilibili_api_crawler.py >> logs/cron.log 2>&1
```

### **数据监控**
```python
# 监控数据变化
from src.bilibili_api_crawler import BilibiliAPICrawler
import json
from datetime import datetime

crawler = BilibiliAPICrawler("config/api_auth.json")
today_data = crawler.crawl_all_pages(max_pages=5)

# 保存每日数据
timestamp = datetime.now().strftime("%Y%m%d")
with open(f"data/bilibili/daily_{timestamp}.json", "w") as f:
    json.dump(today_data, f, ensure_ascii=False, indent=2)
```

## 📚 相关文档

### **必须阅读的文档**
1. **架构设计**: `docs/ARCHITECTURE.md` - 项目整体架构
2. **检查清单**: `docs/CHECKLIST.md` - 53项防错检查
3. **业务知识**: `docs/BUSINESS_KNOWLEDGE_SYSTEM.md` - 业务知识体系
4. **教训记录**: `docs/LESSONS_LEARNED.md` - 历史问题和解决方案

### **业务信息**
1. **核心业务**: `memory-system/CORE_BUSINESS_INFO.md` - B站爬取业务目标
2. **每日记忆**: `memory-system/DAILY_MEMORY_TEMPLATE.md` - 日常记录模板

## 💡 提示和技巧

### **最佳实践**
1. **先测试后爬取**: 先用`bilibili_api_crawler.py`测试单页，确认正常后再爬取多页
2. **实时保存**: 数据会实时保存到`data/bilibili/raw/`目录，避免丢失
3. **错误处理**: 遇到错误会记录到日志，可以查看`logs/bilibili/`目录
4. **数据备份**: 导出的数据会保存到`output/bilibili/`目录，建议定期备份

### **性能优化**
1. **控制频率**: 默认每页间隔2秒，避免被封
2. **分批处理**: 大数据量时建议分批爬取和保存
3. **内存管理**: 大数据集时使用迭代器处理，避免内存溢出

## 🆘 技术支持

### **遇到问题怎么办？**
1. **查看日志**: `logs/bilibili/` 目录下的日志文件
2. **检查配置**: 确认`config/api_auth.json`配置正确
3. **运行测试**: `python3 test_bilibili_crawler.py` 检查所有功能
4. **查看文档**: 阅读相关文档寻找解决方案
5. **记录问题**: 在`docs/LESSONS_LEARNED.md`中记录问题和解决方案

### **紧急联系**
如果遇到紧急问题：
1. 检查网络连接
2. 验证B站网站是否可访问
3. 检查API端点是否变更
4. 查看是否有反爬虫机制

---

**🎉 现在你可以开始使用B站招聘数据爬取器了！**

开始你的第一个爬取任务：
```bash
cd /Users/xingan/.openclaw/workspace/skills/find_new_jobs/bilibili-job
python3 src/bilibili_api_crawler.py
```

祝你爬取顺利！ 🚀