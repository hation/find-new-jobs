# Excel导出模板 - 使用说明

## 🎯 概述

这是一个标准化的Excel导出模板，专门用于导出BOSS直聘的招聘数据到Excel格式。模板包含21个标准字段，自动生成统计分析报告，支持Excel一键打开。

## 📁 文件结构

```
job-search/scripts/
├── export_to_excel.py      # 核心导出类
├── quick_export.py         # 命令行工具
├── job_search_tool.py      # 主搜索工具
└── README_EXCEL_EXPORT.md  # 本说明文档
```

## 🚀 快速开始

### 方法1：使用命令行工具（推荐）
```bash
# 从JSON文件导出
python3 quick_export.py --json-file 你的数据.json

# 从文本文件导出（boss-cli原始输出）
python3 quick_export.py --text-file boss_output.txt

# 直接搜索并导出
python3 quick_export.py --search AI --city 深圳 --pages 5
```

### 方法2：在Python代码中使用
```python
from export_to_excel import ExcelExporter

# 创建导出器
exporter = ExcelExporter()

# 准备数据
jobs_data = [
    {
        'jobName': 'AI人工智能销售',
        'brandName': '某科技公司',
        'salaryDesc': '15-25K',
        # ... 其他字段
    }
]

# 导出Excel
output_files = exporter.export_jobs_to_excel(jobs_data)
print(f"导出完成: {output_files[0]}")
```

### 方法3：与主搜索工具集成
```bash
# 使用主搜索工具，指定输出格式为excel
python3 job_search_tool.py --city 深圳 --keyword AI --pages 5 --output-format excel
```

## 📋 标准字段说明

### 基础信息
1. **序号** - 自动编号
2. **岗位名称** - 岗位完整名称
3. **公司名称** - 公司全名
4. **薪资** - 薪资范围（如15-25K）
5. **经验要求** - 工作经验要求
6. **学历要求** - 学历要求

### 公司信息
7. **地区** - 工作地区
8. **公司规模** - 公司员工规模
9. **融资阶段** - 公司融资阶段
10. **福利待遇** - 公司福利

### 岗位要求
11. **技能要求** - 岗位技能要求
12. **岗位类型** - 岗位类型（全职/兼职/实习）

### Boss信息
13. **Boss姓名** - 招聘负责人
14. **Boss职位** - 招聘负责人职位
15. **在线状态** - Boss在线状态

### 搜索元数据
16. **搜索关键词** - 搜索关键词
17. **来源页数** - 搜索结果页码
18. **数据时间** - 数据获取时间

### 技术字段
19. **岗位ID** - 岗位唯一ID
20. **公司ID** - 公司唯一ID

## 📊 自动生成的分析报告

每次导出都会自动生成统计分析报告，包含：

### 1. 薪资分布分析
- 各薪资范围的岗位数量和占比
- 最高/最低薪资统计

### 2. 经验要求分析
- 不同经验要求的岗位分布
- "经验不限"岗位的比例

### 3. 地区分布分析
- 各地区的岗位集中度
- 热门工作区域

### 4. 公司规模分析
- 不同规模公司的招聘情况
- 大型公司 vs 创业公司

### 5. Excel使用指南
- 如何打开文件
- 数据筛选技巧
- 数据透视表教程

## 💡 最佳实践

### 1. 批量处理多个搜索
```bash
# 批量搜索多个关键词
for keyword in "AI" "人工智能" "机器学习" "深度学习"; do
    python3 quick_export.py --search "$keyword" --city 深圳 --pages 3
done
```

### 2. 定期数据归档
```bash
# 按月归档数据
tar -czf 招聘数据_$(date +%Y%m).tar.gz ~/招聘数据/Excel导出_*
```

### 3. 数据去重和分析
```python
# 使用pandas进行高级分析
import pandas as pd

# 读取导出的CSV文件
df = pd.read_csv('岗位数据_导出_20260514_170000.csv')

# 按薪资排序
df_sorted = df.sort_values('薪资', ascending=False)

# 按地区统计
area_stats = df.groupby('地区').size().sort_values(ascending=False)

# 按公司规模分析薪资
salary_by_size = df.groupby('公司规模')['薪资'].agg(['mean', 'count'])
```

### 4. 趋势跟踪
```python
# 比较不同时期的数据
import glob
import pandas as pd

# 加载所有历史数据
all_files = glob.glob("~/招聘数据/Excel导出_*/岗位数据_导出_*.csv")
all_data = []

for file in all_files:
    df = pd.read_csv(file)
    df['导出日期'] = pd.to_datetime(file.split('_')[-2], format='%Y%m%d')
    all_data.append(df)

# 合并分析
combined_df = pd.concat(all_data, ignore_index=True)

# 分析薪资趋势
salary_trend = combined_df.groupby('导出日期')['薪资'].mean()
```

## 🔧 高级功能

### 自定义字段映射
```python
from export_to_excel import ExcelExporter

# 创建自定义字段映射
custom_columns = [
    ('岗位名称', 'jobName', '岗位名称'),
    ('公司名称', 'brandName', '公司名称'),
    ('薪资范围', 'salaryDesc', '薪资'),
    # 添加更多自定义字段...
]

# 创建导出器时指定字段
exporter = ExcelExporter()
exporter.STANDARD_COLUMNS = custom_columns
```

### 多城市合并导出
```python
# 合并多个城市的搜索结果
cities = ['深圳', '北京', '上海', '广州']
all_jobs = []

for city in cities:
    jobs = export_from_boss_cli('AI', city=city, pages=2)
    all_jobs.extend(jobs)

# 统一导出
exporter.export_jobs_to_excel(all_jobs)
```

### 数据质量检查
```python
# 检查数据完整性
def check_data_quality(jobs_data):
    missing_fields = {}
    
    for job in jobs_data:
        for required_field in ['jobName', 'brandName', 'salaryDesc']:
            if required_field not in job or not job[required_field]:
                missing_fields[required_field] = missing_fields.get(required_field, 0) + 1
    
    return missing_fields
```

## 🚨 故障排除

### 问题1：Excel打开乱码
**解决方案**：确保使用`utf-8-sig`编码保存CSV文件
```python
# 正确方式
with open('data.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
```

### 问题2：字段过长被截断
**解决方案**：调整字段长度限制
```python
# 在export_to_excel.py中修改
if isinstance(value, str) and len(value) > 500:  # 改为500字符
    value = value[:497] + '...'
```

### 问题3：缺少某些字段
**解决方案**：添加默认值
```python
# 在导出前填充缺失字段
for job in jobs_data:
    job.setdefault('skills', [])
    job.setdefault('welfareList', [])
    job.setdefault('areaDistrict', '未知地区')
```

## 📈 性能优化

### 大数据量处理
```python
# 分块处理大型数据集
def export_large_dataset(jobs_data, chunk_size=1000):
    for i in range(0, len(jobs_data), chunk_size):
        chunk = jobs_data[i:i + chunk_size]
        filename = f"岗位数据_第{i//chunk_size + 1}部分.csv"
        exporter.export_jobs_to_excel(chunk, filename=filename)
```

### 内存优化
```python
# 流式处理JSON文件
import ijson

def stream_json_data(file_path):
    """流式读取大型JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        parser = ijson.items(f, 'jobList.item')
        for job in parser:
            yield job
```

## 📞 技术支持

### 常见问题
1. **Q**: 导出的文件在哪里？
   **A**: 默认在`~/招聘数据/Excel导出_时间戳/`目录下

2. **Q**: 如何修改输出目录？
   **A**: 使用`--output-dir`参数或创建ExcelExporter时指定

3. **Q**: 可以导出哪些格式？
   **A**: 目前只支持CSV格式（Excel可打开）

4. **Q**: 如何添加自定义字段？
   **A**: 修改`STANDARD_COLUMNS`列表或创建子类

### 获取帮助
```bash
# 查看帮助
python3 quick_export.py --help

# 查看导出类文档
python3 -c "from export_to_excel import ExcelExporter; help(ExcelExporter)"

# 调试模式
python3 quick_export.py --search AI --city 深圳 --pages 1 --verbose
```

---

**最后更新**: 2026-05-14  
**版本**: v1.0  
**适用场景**: BOSS直聘数据导出、招聘数据分析、Excel格式转换