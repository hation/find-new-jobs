# 📋 示例文档：MEITUAN_CATEGORIES.md

**来源**: 美团招聘爬取项目
**创建时间**: 2026-05-22 09:56:10
**目的**: 作为夸克模板的参考示例

---

# 📊 美团招聘岗位类别详细说明

## 📋 类别配置更新

**重要更新**：根据用户说明，修正美团招聘岗位类别映射：

### **修正后的类别映射**
| 类别代码 | 类别名称 | 状态 | 说明 |
|----------|----------|------|------|
| **11002_-1** | **产品类** | ✅ 确认 | 产品类全部岗位 |
| **11003_-1** | **运营类** | ✅ 确认 | 运营类全部岗位 |
| **11005_-1** | **市场营销类** | 🔄 修正 | 原推测为"运营类" |
| **11007_-1** | **金融类** | 🔄 修正 | 原推测为"市场类" |
| **11010_1101001** | **销售、客服与支持类** | 🔄 修正 | 原推测为"数据类"，实际为销售部分 |

### **完整筛选URL**
```
https://zhaopin.meituan.com/web/social?cityList=001019002&jfJgList=11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001
```

## 🎯 各类别详细说明

### **1. 产品类 (11002_-1)**
- **包含岗位**: 产品经理、产品助理、产品运营、产品设计师等
- **技能要求**: 需求分析、原型设计、用户研究、数据分析
- **典型职责**: 产品规划、功能设计、用户增长、竞品分析
- **目标人群**: 有产品思维、用户体验意识、数据分析能力

### **2. 运营类 (11003_-1)**
- **包含岗位**: 用户运营、内容运营、活动运营、社区运营等
- **技能要求**: 数据分析、活动策划、用户增长、内容创作
- **典型职责**: 用户活跃度提升、内容生产分发、活动策划执行
- **目标人群**: 有运营思维、创意能力、执行能力

### **3. 市场营销类 (11005_-1)**
- **包含岗位**: 市场营销、品牌推广、市场策划、公关等
- **技能要求**: 市场分析、品牌策划、营销推广、媒体关系
- **典型职责**: 市场调研、品牌建设、营销活动、公关传播
- **目标人群**: 有市场敏感度、创意策划能力、沟通能力

### **4. 金融类 (11007_-1)**
- **包含岗位**: 金融产品、风险控制、投资分析、财务等
- **技能要求**: 金融知识、风险控制、数据分析、合规意识
- **典型职责**: 金融产品设计、风险评估、投资分析、财务规划
- **目标人群**: 有金融背景、风险意识、数据分析能力

### **5. 销售、客服与支持类 (11010_1101001)**
- **包含岗位**: 销售代表、客户经理、商务拓展、售前支持等
- **技能要求**: 销售技巧、客户关系、沟通能力、业务理解
- **典型职责**: 客户开发、销售达成、客户维护、商务谈判
- **目标人群**: 有销售经验、沟通能力、抗压能力

## ⚙️ 项目配置更新

### **环境变量** (`config/.env`)
```bash
# 类别代码映射（根据用户说明）
MEITUAN_CATEGORY_MAPPING="11002_-1:产品类,11003_-1:运营类,11005_-1:市场营销类,11007_-1:金融类,11010_1101001:销售、客服与支持类（销售部分）"
```

### **爬取器代码** (`src/meituan_crawler.py`)
```python
# 岗位类别映射（根据用户说明）
self.category_mapping = {
    "11002_-1": "产品类",
    "11003_-1": "运营类", 
    "11005_-1": "市场营销类",
    "11007_-1": "金融类",
    "11010_1101001": "销售、客服与支持类（销售部分）"
}
```

### **核心业务信息** (`memory-system/CORE_BUSINESS_INFO.md`)
```json
{
  "categories": [
    {"id": "11002_-1", "name": "产品类", "enabled": true, "description": "产品类全部岗位"},
    {"id": "11003_-1", "name": "运营类", "enabled": true, "description": "运营类全部岗位"},
    {"id": "11005_-1", "name": "市场营销类", "enabled": true, "description": "市场营销类全部岗位"},
    {"id": "11007_-1", "name": "金融类", "enabled": true, "description": "金融类全部岗位"},
    {"id": "11010_1101001", "name": "销售、客服与支持类", "enabled": true, "description": "销售、客服与支持类的销售部分"}
  ]
}
```

## 🔄 类别组合分析

### **当前组合特点**
1. **业务导向**: 产品、运营、市场、金融、销售
2. **覆盖全面**: 从产品设计到销售转化的完整链条
3. **互补性强**: 各类别相互支持，形成业务闭环
4. **人才需求**: 反映美团当前业务发展重点

### **数据爬取价值**
- **产品类**: 了解产品创新方向和用户需求
- **运营类**: 分析用户增长和活跃度策略
- **市场营销类**: 研究品牌建设和推广方式
- **金融类**: 洞察金融业务发展和风控要求
- **销售类**: 掌握销售策略和客户关系管理

## 📊 数据字段增强

### **添加类别详细信息**
```python
def enhance_position_with_category(self, position_data):
    """用类别信息增强岗位数据"""
    category_code = position_data.get("position_category_code")
    
    if category_code in self.category_mapping:
        position_data["category_name"] = self.category_mapping[category_code]
        position_data["category_group"] = self.get_category_group(category_code)
        position_data["category_description"] = self.get_category_description(category_code)
    
    return position_data

def get_category_group(self, category_code):
    """获取类别分组"""
    groups = {
        "11002_-1": "产品技术类",
        "11003_-1": "运营支持类", 
        "11005_-1": "市场营销类",
        "11007_-1": "金融业务类",
        "11010_1101001": "销售客服类"
    }
    return groups.get(category_code, "其他类")

def get_category_description(self, category_code):
    """获取类别详细描述"""
    descriptions = {
        "11002_-1": "负责产品规划、设计、优化和迭代",
        "11003_-1": "负责用户运营、内容运营、活动运营等",
        "11005_-1": "负责市场分析、品牌推广、营销策划",
        "11007_-1": "负责金融产品设计、风险控制、投资分析",
        "11010_1101001": "负责销售业务、客户关系、商务拓展"
    }
    return descriptions.get(category_code, "")
```

### **数据分析功能**
```python
def analyze_by_category(self, positions):
    """按类别分析岗位数据"""
    category_stats = {}
    
    for position in positions:
        category_code = position.get("position_category_code")
        category_name = position.get("category_name", "未知")
        
        if category_code not in category_stats:
            category_stats[category_code] = {
                "category_name": category_name,
                "count": 0,
                "departments": set(),
                "locations": set(),
                "avg_salary": [],
                "experience_levels": {}
            }
        
        stats = category_stats[category_code]
        stats["count"] += 1
        
        # 收集部门信息
        department = position.get("department")
        if department:
            stats["departments"].add(department)
        
        # 收集地点信息
        location = position.get("work_location")
        if location:
            stats["locations"].add(location)
        
        # 分析薪资（如果可用）
        salary = position.get("salary_range")
        if salary and "面议" not in salary:
            # 这里可以添加薪资解析逻辑
            pass
        
        # 分析经验要求
        experience = position.get("work_experience", "")
        if experience:
            stats["experience_levels"][experience] = stats["experience_levels"].get(experience, 0) + 1
    
    return category_stats
```

## 🚀 爬取策略优化

### **按类别分步爬取**
```python
def crawl_by_category(self, category_codes=None):
    """按类别分步爬取"""
    if category_codes is None:
        category_codes = list(self.category_mapping.keys())
    
    all_positions = []
    
    for category_code in category_codes:
        category_name = self.category_mapping.get(category_code, "未知")
        logger.info(f"📁 爬取{category_name}岗位数据...")
        
        # 构建类别特定URL
        url = f"{self.filter_url}?cityList={self.city_code}&jfJgList={category_code}"
        
        # 爬取数据
        positions = self.crawl_with_browser(url)
        
        # 添加类别标签
        for position in positions:
            position["position_category_code"] = category_code
            position["position_category_name"] = category_name
        
        all_positions.extend(positions)
        
        logger.info(f"✅ {category_name}: 获取到 {len(positions)} 个岗位")
        
        # 类别间延迟
        time.sleep(2)
    
    return all_positions
```

### **类别数据质量检查**
```python
def check_category_data_quality(self, positions):
    """检查类别数据质量"""
    quality_report = {
        "total_positions": len(positions),
        "categories_found": set(),
        "missing_category": 0,
        "category_distribution": {},
        "quality_score": 0
    }
    
    for position in positions:
        category_code = position.get("position_category_code")
        if category_code:
            quality_report["categories_found"].add(category_code)
            quality_report["category_distribution"][category_code] = \
                quality_report["category_distribution"].get(category_code, 0) + 1
        else:
            quality_report["missing_category"] += 1
    
    # 计算质量分数
    if positions:
        quality_report["quality_score"] = (len(positions) - quality_report["missing_category"]) / len(positions) * 100
    
    return quality_report
```

## 📈 业务洞察

### **当前类别组合分析**
1. **产品+运营+市场**: 完整的用户获取和留存链条
2. **金融类加入**: 反映美团在金融业务的发展
3. **销售类聚焦**: 重点关注销售转化环节
4. **技术类缺失**: 当前筛选未包含技术开发岗位

### **招聘趋势洞察**
- **产品运营并重**: 产品设计和用户运营同等重要
- **市场金融结合**: 市场营销和金融业务协同发展
- **销售专业化**: 销售岗位有专门分类和筛选
- **业务导向明显**: 所有类别都直接支持业务发展

## 🔧 配置验证

### **验证当前配置**
```bash
# 验证类别配置
cd "/Users/xingan/.openclaw/workspace/skills/find_new_jobs/meituan-job"
python3 -c "
from src.meituan_crawler import MeituanCrawler
crawler = MeituanCrawler()
print('📊 当前类别配置:')
for code, name in crawler.category_mapping.items():
    print(f'  {code}: {name}')
print(f'总计: {len(crawler.category_mapping)} 个类别')
"
```

### **生成类别报告**
```bash
# 生成详细的类别报告
python3 -c "
import json
from src.meituan_crawler import MeituanCrawler

crawler = MeituanCrawler()
report = {
    'company': '美团',
    'city_code': crawler.city_code,
    'city_name': '深圳',
    'categories': [],
    'total_categories': len(crawler.category_mapping),
    'filter_url': crawler.filter_url,
    'full_url': f'{crawler.filter_url}?cityList={crawler.city_code}&jfJgList={crawler.category_codes}'
}

for code, name in crawler.category_mapping.items():
    report['categories'].append({
        'code': code,
        'name': name,
        'in_url': code in crawler.category_codes,
        'description': '根据用户说明配置'
    })

print(json.dumps(report, ensure_ascii=False, indent=2))
"
```

## 📝 经验教训记录

### **本次修正的重要发现**
1. **不要依赖推测**: 类别代码含义需要实际验证
2. **及时更新配置**: 获得准确信息后立即更新所有文件
3. **创建详细文档**: 为每个类别创建说明文档
4. **添加验证机制**: 建立配置验证流程

### **添加到检查清单**
- [ ] 验证所有类别代码的实际含义
- [ ] 更新配置文件和文档中的类别信息
- [ ] 添加类别代码验证测试
- [ ] 记录类别发现的教训

### **改进措施**
1. 创建类别代码验证脚本
2. 添加配置验证机制
3. 建立代码映射的自动更新流程
4. 定期重新验证关键参数

## 🎯 立即使用

### **爬取当前配置的数据**
```bash
cd "/Users/xingan/.openclaw/workspace/skills/find_new_jobs/meituan-job"
python3 src/meituan_crawler.py --mode browser
```

### **测试单个类别**
```bash
# 测试产品类
python3 -c "
from src.meituan_crawler import MeituanCrawler
crawler = MeituanCrawler()
url = f'{crawler.filter_url}?cityList={crawler.city_code}&jfJgList=11002_-1'
print(f'产品类URL: {url}')
"
```

### **生成类别分析报告**
```bash
# 运行爬取后生成类别分析
cd "/Users/xingan/.openclaw/workspace/skills/find_new_jobs/meituan-job"
python3 -c "
import json
import glob

# 查找最新的数据文件
data_files = glob.glob('output/crawl_data/meituan_positions_*.json')
if data_files:
    latest_file = max(data_files, key=os.path.getctime)
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categories = {}
    for position in data.get('positions', []):
        category = position.get('position_category', '未知')
        categories[category] = categories.get(category, 0) + 1
    
    print('📊 岗位类别分布:')
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f'  {category}: {count} 个岗位')
else:
    print('❌ 没有找到数据文件')
"
```

---

**最后更新**: 2026-05-21  
**更新内容**: 根据用户说明修正岗位类别映射  
**维护人**: xingan  
**状态**: ✅ 已修正  

**当前爬取范围**: 深圳的产品类、运营类、市场营销类、金融类、销售类岗位