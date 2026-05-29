# 🚀 ks-job 快手招聘数据爬取器 - 快速开始指南

## 📋 项目概述

**ks-job** 是一个专门为**快手招聘数据爬取**定制的项目，基于夸克项目的完整架构，实现了快手官方API的数据爬取功能。

### **核心功能**
- ✅ **快手官方API爬取**: 使用 `https://zhaopin.kuaishou.cn` 官方API
- ✅ **智能分页处理**: 自动计算总页数，逐页爬取
- ✅ **12字段数据标准**: 统一的岗位数据格式
- ✅ **实时数据保存**: JSON文件即时保存，避免数据丢失
- ✅ **完整错误处理**: 网络重试、数据验证、进度跟踪
- ✅ **基于夸克经验**: 继承夸克项目的防错机制和最佳实践

## 🎯 快速开始

### **第一步：环境准备**
```bash
# 1. 进入项目目录
cd /Users/xingan/.openclaw/workspace/skills/find_new_jobs/ks-job

# 2. 安装Python依赖
pip3 install -r requirements.txt

# 3. 确保目录存在
mkdir -p logs output/ks_data backup
```

### **第二步：配置Cookie（关键步骤）**
快手API需要有效的Cookie认证，请按以下步骤获取：

1. **打开浏览器**访问: https://zhaopin.kuaishou.cn
2. **登录**快手招聘网站（如有需要）
3. **打开开发者工具** (F12)
4. **复制Cookie**值，包含以下字段：
   - `accessproxy_session`
   - `aliyungf_tc`
   - `apdid`
   - `weblogger_did`

5. **更新配置文件**:
```bash
# 编辑配置文件
vim config/.env

# 找到并更新以下行：
KS_COOKIE_PLACEHOLDER="aliyungf_tc=...; accessproxy_session=...; apdid=...; weblogger_did=..."
```

### **第三步：运行测试**
```bash
# 运行完整测试套件
python3 scripts/test_ks_crawler.py

# 或直接测试单页爬取
python3 src/ks_api_crawler.py
```

### **第四步：开始爬取**
```bash
# 方法1: 使用启动脚本（推荐）
chmod +x scripts/start_ks_crawler.sh
./scripts/start_ks_crawler.sh

# 方法2: 直接运行爬取器
python3 src/ks_api_crawler.py

# 方法3: 自定义参数爬取
python3 -c "
from src.ks_api_crawler import KsAPICrawler, load_config
config = load_config()
crawler = KsAPICrawler(config)
stats = crawler.crawl_and_save(max_pages=5)  # 爬取5页
print(f'爬取完成: {stats}')
"
```

## 📊 API信息概览

### **API地址**
```
https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple
```

### **核心参数**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `pageNum` | 页码 | 1 |
| `pageSize` | 每页数量 | 10 |
| `positionCategoryCode` | 岗位类别 | J0005,J0004,J0013,J0006,J0014 |
| `positionNatureCode` | 岗位性质 | C001（社招） |
| `recruitProject` | 招聘项目 | socialr |
| `workLocationCode` | 工作地点 | domestic（国内） |

### **认证要求**
- **Cookie认证**: 必须提供有效的Cookie
- **签名验证**: API需要 `sign` 和 `signtimestamp` 参数
- **Referer检查**: 需要设置正确的Referer头

## 📁 项目结构

```
ks-job/
├── 📚 知识层
│   ├── docs/                    # 项目文档
│   └── memory-system/          # 记忆系统
│
├── 🔧 框架层
│   ├── src/ks_api_crawler.py   # 快手API爬取器（核心）
│   ├── src/ks_crawler.py       # 示例爬取器（参考）
│   └── src/framework/          # 夸克框架组件
│
├── ⚙️ 配置层
│   ├── config/.env             # 环境配置（需更新Cookie）
│   ├── config/api_auth.json    # API配置模板
│   └── config/browser_config.json
│
├── 📊 数据层
│   ├── output/ks_data/         # 爬取数据（JSON格式）
│   ├── logs/                   # 日志文件
│   └── backup/                 # 数据备份
│
└── 🛠️ 工具层
    ├── scripts/start_ks_crawler.sh  # 启动脚本
    ├── scripts/test_ks_crawler.py   # 测试脚本
    └── requirements.txt         # Python依赖
```

## 🔧 核心功能说明

### **1. 数据字段映射**
我们的爬取器将快手API字段映射到12个标准字段：

| 标准字段 | 快手API字段 | 说明 |
|---------|------------|------|
| positionId | `id` | 岗位唯一ID |
| positionName | `name` | 岗位名称 |
| workLocation | `workLocationCode` | 工作地点代码 |
| positionCategory | `positionCategoryCode` | 岗位类别代码 |
| publishTime | `updateTime` | 更新时间 |
| detailUrl | 构造URL | `https://zhaopin.kuaishou.cn/position/{id}` |
| department | `departmentCode` | 部门代码 |
| educationRequirement | `educationLimitCode` | 学历要求代码 |
| workExperience | `workExperienceCode` | 工作经验代码 |
| jobResponsibilities | `description` | 工作职责 |
| jobRequirements | `positionDemand` | 任职要求 |
| salaryRange | 暂无 | 需要从其他接口获取 |

### **2. 数据保存格式**
每个岗位保存为独立的JSON文件：
```json
{
  "positionId": "30189",
  "positionName": "行业运营专家（生活服务方向）-【生活服务】",
  "workLocation": "Beijing",
  "positionCategory": "J0004",
  "publishTime": "2026-05-22T12:41:47.000+08:00",
  "detailUrl": "https://zhaopin.kuaishou.cn/position/30189",
  "department": "D15067",
  "educationRequirement": null,
  "workExperience": "5",
  "jobResponsibilities": "1. 行业全局规划与生态构建：深度挖掘生活服务行业增量机会...",
  "jobRequirements": "1、本科及以上学历，3年以上生活服务行业相关工作经验...",
  "salaryRange": "",
  "company": "快手",
  "crawlTime": "2026-05-22 16:45:30",
  "crawlMode": "api",
  "source": "kuaishou_api",
  "rawData": {
    "levels": ["E8", "E9"],
    "workLocationsCode": ["Beijing"],
    "recruitProjectCode": "socialr",
    "positionNatureCode": "C001",
    "channelCode": "official"
  }
}
```

### **3. 错误处理机制**
- **网络重试**: 最多3次重试，每次间隔5秒
- **API错误**: 处理快手API错误码（code ≠ 0）
- **数据验证**: 12字段完整性检查
- **断点续传**: 支持从失败点继续爬取

## 🚀 高级用法

### **自定义爬取参数**
```python
from src.ks_api_crawler import KsAPICrawler, load_config

# 加载配置
config = load_config()

# 自定义参数
config.update({
    "page_size": 20,  # 每页20条
    "position_category_codes": "J0005,J0004",  # 只爬取特定类别
    "max_retries": 5,  # 最多重试5次
    "timeout": 60,  # 超时60秒
})

# 创建爬取器
crawler = KsAPICrawler(config)

# 爬取指定页数
stats = crawler.crawl_and_save(max_pages=10)
```

### **批量处理数据**
```python
import os
import json
from datetime import datetime

# 读取所有爬取的数据文件
data_dir = "output/ks_data"
all_positions = []

for filename in os.listdir(data_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            position = json.load(f)
            all_positions.append(position)

print(f"共读取 {len(all_positions)} 个岗位数据")

# 数据分析示例
locations = {}
categories = {}
experiences = {}

for position in all_positions:
    # 统计工作地点
    location = position.get("workLocation", "未知")
    locations[location] = locations.get(location, 0) + 1
    
    # 统计岗位类别
    category = position.get("positionCategory", "未知")
    categories[category] = categories.get(category, 0) + 1
    
    # 统计工作经验
    experience = position.get("workExperience", "未知")
    experiences[experience] = experiences.get(experience, 0) + 1

print("\n📊 数据统计:")
print(f"工作地点分布: {locations}")
print(f"岗位类别分布: {categories}")
print(f"工作经验分布: {experiences}")
```

## ⚠️ 注意事项

### **1. 法律合规**
- **尊重robots.txt**: 遵守网站爬取规则
- **控制爬取频率**: 避免对网站造成压力
- **合理使用数据**: 仅用于合法研究和分析目的
- **保护隐私**: 不爬取个人隐私信息

### **2. 技术限制**
- **Cookie有效期**: Cookie可能过期，需要定期更新
- **API变更**: 快手API可能变更，需要及时调整
- **反爬虫机制**: 注意签名验证和频率限制
- **数据完整性**: 某些字段可能为空（如薪资信息）

### **3. 最佳实践**
1. **先测试后爬取**: 先用测试模式验证功能
2. **分批次爬取**: 不要一次性爬取所有数据
3. **定期备份**: 重要数据定期备份
4. **记录日志**: 详细记录爬取过程和问题
5. **更新维护**: 定期检查API变更，更新代码

## 🔧 故障排除

### **常见问题及解决方案**

#### **问题1: Cookie无效或过期**
```
❌ API业务错误: code=403, message=认证失败
```
**解决方案**:
1. 重新访问 https://zhaopin.kuaishou.cn
2. 获取新的Cookie
3. 更新 config/.env 文件
4. 重新运行爬取器

#### **问题2: 网络连接失败**
```
❌ 网络请求失败: Connection timed out
```
**解决方案**:
1. 检查网络连接
2. 增加超时时间（config/.env 中设置）
3. 添加重试机制（已内置）
4. 使用代理服务器（如果需要）

#### **问题3: API响应格式变更**
```
❌ JSON解析失败: Expecting value: line 1 column 1 (char 0)
```
**解决方案**:
1. 检查API地址是否正确
2. 验证参数格式
3. 查看原始响应内容
4. 调整数据解析逻辑

#### **问题4: 数据字段缺失**
```
⚠️ 岗位 XXX 缺失字段: ['salaryRange', 'educationRequirement']
```
**解决方案**:
1. 检查字段映射配置（config/api_auth.json）
2. 验证API返回的数据结构
3. 调整字段提取逻辑
4. 添加默认值处理

## 📞 帮助和支持

### **文档参考**
- **架构设计**: `docs/ARCHITECTURE.md`
- **检查清单**: `docs/CHECKLIST.md`（53项标准检查）
- **教训记录**: `docs/LESSONS_LEARNED.md`
- **业务知识**: `docs/BUSINESS_KNOWLEDGE_SYSTEM.md`

### **调试命令**
```bash
# 查看实时日志
tail -f logs/ks_crawler.log

# 查看最新数据
ls -la output/ks_data/ | tail -10

# 检查配置文件
cat config/.env | grep -E "KS_|COOKIE"

# 运行单元测试
python3 -m pytest tests/ -v
```

### **联系支持**
- **问题反馈**: 记录到 `docs/LESSONS_LEARNED.md`
- **功能建议**: 更新 `memory-system/CORE_BUSINESS_INFO.md`
- **紧急问题**: 检查日志文件，分析错误信息

---

## 🎉 开始你的数据爬取之旅！

现在你已经了解了 ks-job 项目的所有功能和用法。接下来：

1. **✅ 配置Cookie** - 这是最关键的一步
2. **✅ 运行测试** - 验证功能是否正常
3. **✅ 开始爬取** - 从小规模测试开始
4. **✅ 分析数据** - 利用爬取的数据进行分析

**祝你项目顺利！有任何问题随时查阅本文档或查看日志文件。** 🚀

---

**最后更新**: 2026-05-22  
**项目状态**: ✅ 已实现快手API爬取功能  
**待完善**: 薪资信息获取、详情页爬取、数据分析报告