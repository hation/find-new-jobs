# 统一Excel导出框架快速启动指南
## 5分钟上手，完全匹配anti-job格式

**版本**: 1.0.0  
**最后更新**: 2026-05-22  
**目标**: 让新项目在5分钟内配置好统一Excel导出

---

## 🚀 **5分钟快速启动**

### **步骤1: 导入框架**
```python
# 在你的爬取器中添加
from framework.unified_excel_exporter import UnifiedExcelExporter
```

### **步骤2: 基本配置**
```python
# 最简单的配置
config = {
    "company_name": "你的公司名称",  # 必填
    "output_dir": "output/unified_excel"  # 可选，默认值
}

exporter = UnifiedExcelExporter(config)
```

### **步骤3: 导出数据**
```python
# positions是你的岗位数据列表
result = exporter.export_to_unified_excel(positions)

if result["success"]:
    print(f"✅ Excel导出成功: {result['file_path']}")
    print(f"   大小: {result['file_size_mb']:.2f} MB")
    print(f"   岗位: {result['total_positions']} 个")
    print(f"   工作表: {len(result['sheets_created'])} 个")
else:
    print(f"❌ 导出失败: {result.get('error')}")
```

### **步骤4: 验证输出**
```bash
# 检查生成的Excel文件
ls -la output/unified_excel/*.xlsx

# 打开文件验证
open output/unified_excel/你的公司_international_positions_*.xlsx
```

**完成！** 🎉 你的项目现在输出完全匹配anti-job格式的Excel文件。

---

## 📋 **完整配置示例**

### **基础配置（满足80%需求）**
```python
config = {
    "company_name": "京东",  # 公司名称
    "company_website": "https://zhaopin.jd.com",  # 招聘网站
    "output_dir": "output/jd_unified_excel",  # 输出目录
    
    # 质量配置
    "quality_config": {
        "min_completeness": 0.8,  # 最小数据完整率
        "auto_validation": True,  # 自动验证
        "generate_csv": True     # 同时生成CSV
    }
}
```

### **高级配置（自定义需求）**
```python
config = {
    "company_name": "蚂蚁集团",
    "company_website": "https://talent.antgroup.com",
    
    # 输出配置
    "output_dir": "output/ant_unified_excel",
    "naming_pattern": "{company}_recruitment_{timestamp}.xlsx",
    
    # 质量配置
    "quality_config": {
        "min_completeness": 0.9,  # 更高的质量要求
        "auto_validation": True,
        "generate_csv": True,
        "backup_failed": True     # 备份失败的数据
    },
    
    # Excel设置
    "excel_settings": {
        "include_sheets": [        # 包含的工作表
            "所有岗位",
            "地点分布", 
            "类别分布",
            "学历分布",
            "部门分布",
            "经验要求",
            "数据摘要"
        ],
        "auto_adjust_columns": True,  # 自动调整列宽
        "freeze_panes": True,         # 冻结首行
        "include_charts": False       # 不包含图表
    }
}
```

---

## 🔧 **集成到现有爬取器**

### **情况1: 新爬取器**
```python
class YourCrawler:
    def __init__(self):
        # 初始化导出器
        self.exporter = UnifiedExcelExporter({
            "company_name": "你的公司",
            "output_dir": "output/your_company"
        })
    
    def save_jobs(self, jobs):
        """保存岗位数据"""
        result = self.exporter.export_to_unified_excel(jobs)
        return result
```

### **情况2: 现有爬取器（jd-job风格）**
```python
def save_jobs_to_file(self, jobs, format="excel"):
    if format == "excel":
        # 使用统一导出器
        result = self.exporter.export_to_unified_excel(jobs)
        if result["success"]:
            return result["file_path"]
        else:
            raise Exception(f"导出失败: {result.get('error')}")
    # ... 其他格式处理
```

### **情况3: 现有爬取器（anti-job风格）**
```python
def export_positions(self, positions):
    """导出岗位数据"""
    # 使用统一导出器替代原有逻辑
    exporter = UnifiedExcelExporter({
        "company_name": self.company_name,
        "output_dir": self.output_dir
    })
    
    return exporter.export_to_unified_excel(positions)
```

---

## 📁 **数据格式要求**

### **最小数据要求**
```python
# 每个岗位至少包含这些字段
minimal_position = {
    "position_id": "JD001",          # 岗位ID
    "position_name": "软件工程师",    # 岗位名称
    "work_location": "北京",         # 工作地点
    "department": "技术部",          # 部门
    "job_type": "技术类"             # 岗位类别
}
```

### **完整数据示例**
```python
ideal_position = {
    # 基本信息
    "position_id": "JD001",
    "position_name": "软件工程师",
    "job_type": "技术类",
    "work_location": "北京",
    "publish_date": "2026-05-20",
    "department": "技术研发部",
    
    # 要求信息
    "education_requirement": "本科及以上学历",
    "work_experience": "3-5年工作经验",
    "position_requirements": "熟悉Python、Java等编程语言",
    "position_description": "负责后端系统开发和维护",
    
    # 附加信息
    "recruitment_number": "ZP260520001",
    "is_hot": 1,  # 是否热门
    "salary_range": "20-30k",  # 薪资范围（可选）
    "raw_data": {...}  # 原始数据（可选）
}
```

### **字段映射说明**
- **position_id**: 会自动映射到"岗位ID"
- **position_name**: 会自动映射到"岗位名称"
- **work_location**: 会自动映射到"工作地点"
- **department**: 会自动映射到"所属部门"
- **job_type**: 会自动映射到"岗位类别"和"类别名称"

**注意**: 即使字段名不同，框架也会自动映射。详见 `config/excel_column_mapping.yaml`

---

## 🚨 **常见问题快速解决**

### **问题1: 列名不是中文**
**症状**: Excel列名显示为英文（position_id, position_name等）  
**解决**: 确保使用 `UnifiedExcelExporter` 而不是旧的 `DataExporter`

### **问题2: 只有1个工作表**
**症状**: Excel文件只有"所有岗位"工作表  
**解决**: 检查配置中的 `include_sheets`，确保包含7个工作表

### **问题3: 数据清洗失败**
**症状**: 学历、经验字段显示原始文本  
**解决**: 确保字段名正确，或检查 `data_extractors.py` 的提取规则

### **问题4: 文件无法生成**
**症状**: 没有生成Excel文件  
**解决**: 检查输出目录权限，查看日志文件

---

## 📊 **输出验证**

### **自动验证**
框架会自动验证输出质量，你可以在结果中查看：
```python
result = exporter.export_to_unified_excel(positions)

print(f"质量状态: {result['quality_report']['status']}")
print(f"完整率: {result['quality_report']['completeness_percentage']}")
print(f"列匹配: {result['quality_report']['column_match_rate']}")
```

### **手动验证**
```bash
# 检查文件基本信息
python3 -c "
import pandas as pd
import sys

file_path = sys.argv[1]
df = pd.read_excel(file_path)

print(f'文件: {file_path}')
print(f'行数: {len(df)}')
print(f'列数: {len(df.columns)}')
print(f'列名: {list(df.columns)}')
" output/your_file.xlsx
```

### **格式对比**
```bash
# 对比两个Excel文件格式
python3 -c "
import pandas as pd

file1 = pd.read_excel('anti_job_output.xlsx')
file2 = pd.read_excel('your_output.xlsx')

print('列名对比:')
print(f'  anti-job: {len(file1.columns)}列')
print(f'  你的文件: {len(file2.columns)}列')

common_cols = set(file1.columns) & set(file2.columns)
print(f'共同列: {len(common_cols)}个')
print(f'差异列: {set(file1.columns) ^ set(file2.columns)}')
"
```

---

## 🔄 **从旧格式迁移**

### **一键转换**
```python
from framework.unified_excel_exporter import UnifiedExcelExporter

exporter = UnifiedExcelExporter({"company_name": "你的公司"})

# 转换旧格式Excel
result = exporter.convert_legacy_excel(
    legacy_file_path="output/old_format.xlsx",
    output_dir="output/converted"
)

if result["success"]:
    print(f"✅ 转换成功: {result['file_path']}")
```

### **批量转换**
```bash
# 使用脚本批量转换
python3 scripts/generate_unified_excel.py \
    --mode batch \
    --input "data/legacy_files" \
    --output "output/converted" \
    --company "你的公司"
```

### **验证转换结果**
```bash
# 验证转换后的文件
python3 -c "
import pandas as pd

# 读取转换前后的文件
old_df = pd.read_excel('output/old_format.xlsx')
new_df = pd.read_excel('output/converted/your_company_*.xlsx', sheet_name='所有岗位')

print('转换验证:')
print(f'  旧文件行数: {len(old_df)}')
print(f'  新文件行数: {len(new_df)}')
print(f'  数据保留率: {len(new_df)/len(old_df)*100:.1f}%')
print(f'  新文件列数: {len(new_df.columns)} (标准: 16)')
"
```

---

## 📈 **性能优化**

### **大数据量处理**
```python
# 分批处理大数据
batch_size = 1000
all_results = []

for i in range(0, len(positions), batch_size):
    batch = positions[i:i+batch_size]
    result = exporter.export_to_unified_excel(
        batch,
        additional_info={"批次": f"{i//batch_size + 1}"}
    )
    all_results.append(result)
```

### **内存优化**
```python
# 使用生成器处理流式数据
def process_large_dataset(data_generator):
    """处理大型数据集"""
    exporter = UnifiedExcelExporter(config)
    
    batch = []
    for position in data_generator:
        batch.append(position)
        
        if len(batch) >= 1000:  # 每1000条处理一次
            result = exporter.export_to_unified_excel(batch)
            batch = []  # 清空批次
    
    # 处理剩余数据
    if batch:
        result = exporter.export_to_unified_excel(batch)
    
    return result
```

---

## 🎯 **最佳实践**

### **配置管理**
1. **环境变量**: 公司名称等敏感信息使用环境变量
2. **配置文件**: 复杂配置使用YAML配置文件
3. **版本控制**: 配置文件加入版本控制

### **错误处理**
```python
try:
    result = exporter.export_to_unified_excel(positions)
    
    if not result["success"]:
        # 记录错误并尝试恢复
        logger.error(f"导出失败: {result.get('error')}")
        
        # 尝试使用简化模式
        simple_config = {"company_name": config["company_name"]}
        simple_exporter = UnifiedExcelExporter(simple_config)
        result = simple_exporter.export_to_unified_excel(positions)
        
except Exception as e:
    logger.error(f"导出过程异常: {e}")
    # 保存原始数据到JSON作为备份
    with open("backup/raw_data.json", "w") as f:
        json.dump(positions, f)
```

### **日志记录**
```python
import logging

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/excel_export.log'),
        logging.StreamHandler()
    ]
)
```

---

## 📞 **获取帮助**

### **快速诊断命令**
```bash
# 检查框架是否正常工作
python3 -c "
from framework.unified_excel_exporter import UnifiedExcelExporter
print('✅ 框架导入成功')

exporter = UnifiedExcelExporter({'company_name': '测试'})
print('✅ 导出器创建成功')
"

# 检查依赖
python3 -c "
import pandas as pd
import openpyxl
print(f'pandas: {pd.__version__}')
print(f'openpyxl: {openpyxl.__version__}')
"

# 运行示例
python3 framework/unified_excel_exporter.py
```

### **检查清单**
```bash
# 运行完整检查
python3 scripts/generate_unified_excel.py \
    --config config/excel_column_mapping.yaml \
    --company "测试公司" \
    --input "template/framework/unified_excel_exporter.py" \
    --mode single
```

---

## 🎉 **恭喜！**

你已经成功配置了统一Excel导出框架。现在你的项目将：

1. ✅ **输出完全匹配anti-job格式的Excel文件**
2. ✅ **自动进行数据清洗和格式化**
3. ✅ **生成7个工作表（所有岗位+6个统计分析表）**
4. ✅ **自动验证数据质量**
5. ✅ **同时生成简化版CSV文件**

**下一步建议**:
1. **测试**: 使用你的实际数据测试导出
2. **验证**: 对比输出与anti-job的格式
3. **优化**: 根据需求调整配置
4. **文档**: 更新项目文档说明新的导出格式

**记住**: 统一的Excel格式让数据分析和处理变得简单一致！ 🚀