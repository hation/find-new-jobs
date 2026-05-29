# 🏙️ 美团招聘城市代码映射

## 📋 重要更新

**关键纠正**：
- `cityList=001019002` 对应的是 **深圳**，不是北京
- 之前误识别为北京，现已修正 ✅

## 🗺️ 城市代码完整映射

### **已确认的城市代码**
| 城市代码 | 城市名称 | 状态 | 备注 |
|----------|----------|------|------|
| **001019002** | **深圳** | ✅ 已确认 | 当前项目使用 |
| 001019001 | 北京 | ⚠️ 待验证 | 推测为北京 |
| 001019003 | 上海 | ⚠️ 待验证 | 推测为上海 |
| 001019004 | 杭州 | ⚠️ 待验证 | 推测为杭州 |
| 001019005 | 广州 | ⚠️ 待验证 | 推测为广州 |
| 001019006 | 成都 | ⚠️ 待验证 | 推测为成都 |

### **使用示例**
```bash
# 深圳招聘
https://zhaopin.meituan.com/web/social?cityList=001019002

# 多城市组合（待验证）
https://zhaopin.meituan.com/web/social?cityList=001019002,001019001

# 当前项目使用的完整URL
https://zhaopin.meituan.com/web/social?cityList=001019002&jfJgList=11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001
```

## 🔍 如何验证城市代码

### **方法1：URL测试**
```bash
# 测试不同城市代码
curl -I "https://zhaopin.meituan.com/web/social?cityList=001019001"
curl -I "https://zhaopin.meituan.com/web/social?cityList=001019002"
curl -I "https://zhaopin.meituan.com/web/social?cityList=001019003"
```

### **方法2：浏览器开发者工具**
1. 打开美团招聘网站
2. 按F12打开开发者工具
3. 切换到Network标签
4. 选择不同城市筛选
5. 观察URL参数变化

### **方法3：爬取器测试**
```python
# 在meituan_crawler.py中添加测试代码
test_cities = ["001019001", "001019002", "001019003"]
for city_code in test_cities:
    url = f"https://zhaopin.meituan.com/web/social?cityList={city_code}"
    # 访问并解析页面标题/内容
```

## ⚙️ 项目配置更新

### **环境变量** (`config/.env`)
```bash
# 城市配置
MEITUAN_CITY_CODE="001019002"  # 深圳
MEITUAN_CITY_MAPPING="001019002:深圳,001019001:北京,001019003:上海,001019004:杭州,001019005:广州,001019006:成都"
```

### **爬取器代码** (`src/meituan_crawler.py`)
```python
# URL参数
self.city_code = "001019002"  # 深圳
self.city_mapping = {
    "001019002": "深圳",
    "001019001": "北京", 
    "001019003": "上海",
    "001019004": "杭州",
    "001019005": "广州",
    "001019006": "成都"
}
```

### **核心业务信息** (`memory-system/CORE_BUSINESS_INFO.md`)
```json
{
  "locations": [
    {"id": "001019002", "name": "深圳", "enabled": true},
    {"id": "001019001", "name": "北京", "enabled": false},
    {"id": "001019003", "name": "上海", "enabled": false},
    {"id": "001019004", "name": "杭州", "enabled": false},
    {"id": "001019005", "name": "广州", "enabled": false},
    {"id": "001019006", "name": "成都", "enabled": false}
  ]
}
```

## 🔄 多城市爬取支持

### **方案1：逐个城市爬取**
```python
def crawl_multiple_cities(self, city_codes):
    """爬取多个城市数据"""
    all_positions = []
    
    for city_code in city_codes:
        city_name = self.city_mapping.get(city_code, f"未知城市({city_code})")
        logger.info(f"🏙️ 爬取{city_name}的招聘数据...")
        
        # 构建城市特定URL
        url = f"{self.filter_url}?cityList={city_code}&jfJgList={self.category_codes}"
        
        # 爬取数据
        positions = self.crawl_with_browser(url)
        all_positions.extend(positions)
        
        # 添加城市标签
        for position in positions:
            position["city_code"] = city_code
            position["city_name"] = city_name
    
    return all_positions
```

### **方案2：并行爬取**
```python
import concurrent.futures

def crawl_cities_parallel(self, city_codes, max_workers=3):
    """并行爬取多个城市"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for city_code in city_codes:
            future = executor.submit(self.crawl_single_city, city_code)
            futures.append(future)
        
        # 收集结果
        all_positions = []
        for future in concurrent.futures.as_completed(futures):
            positions = future.result()
            all_positions.extend(positions)
    
    return all_positions
```

## 📊 数据字段增强

### **添加城市信息字段**
```python
position_data = {
    # ... 原有字段
    "city_code": city_code,  # 城市代码
    "city_name": city_name,  # 城市名称
    "is_multicity": len(city_codes) > 1,  # 是否多城市
    "crawl_scope": "single_city" if len(city_codes) == 1 else f"multi_city_{len(city_codes)}"
}
```

### **数据分组分析**
```python
def analyze_by_city(self, positions):
    """按城市分析数据"""
    city_stats = {}
    
    for position in positions:
        city_code = position.get("city_code")
        if city_code not in city_stats:
            city_stats[city_code] = {
                "city_name": position.get("city_name", "未知"),
                "count": 0,
                "categories": {},
                "departments": set()
            }
        
        stats = city_stats[city_code]
        stats["count"] += 1
        
        # 统计岗位类别
        category = position.get("position_category", "未知")
        stats["categories"][category] = stats["categories"].get(category, 0) + 1
        
        # 收集部门
        department = position.get("department")
        if department:
            stats["departments"].add(department)
    
    return city_stats
```

## 🚀 立即使用

### **爬取深圳数据（当前配置）**
```bash
python3 src/meituan_crawler.py --mode browser
```

### **测试其他城市**
```bash
# 修改配置后测试北京
sed -i '' 's/MEITUAN_CITY_CODE=\"001019002\"/MEITUAN_CITY_CODE=\"001019001\"/' config/.env
python3 src/meituan_crawler.py --mode test

# 恢复深圳配置
sed -i '' 's/MEITUAN_CITY_CODE=\"001019001\"/MEITUAN_CITY_CODE=\"001019002\"/' config/.env
```

### **多城市爬取示例**
```python
# 在Python中直接调用
from src.meituan_crawler import MeituanCrawler

crawler = MeituanCrawler()
city_codes = ["001019002", "001019001", "001019003"]  # 深圳、北京、上海
all_positions = crawler.crawl_multiple_cities(city_codes)
print(f"爬取完成，共获取 {len(all_positions)} 个岗位")
```

## 📝 经验教训

### **本次纠正的重要教训**
1. **不要假设代码含义**：`001019002` 看起来像北京代码，但实际是深圳
2. **必须实际验证**：所有代码映射都需要通过实际访问验证
3. **及时更新文档**：发现错误立即更新所有相关文档
4. **添加验证机制**：在代码中添加城市代码验证逻辑

### **添加到检查清单**
- [ ] 验证所有城市代码的实际对应关系
- [ ] 更新配置文件和文档中的城市信息
- [ ] 添加城市代码验证测试
- [ ] 记录城市代码发现的教训

### **改进措施**
1. 创建城市代码验证脚本
2. 添加配置验证机制
3. 建立代码映射的自动更新流程
4. 定期重新验证关键参数

## 🔮 未来规划

### **短期目标**
1. ✅ 修正深圳城市代码
2. ⬜ 验证其他城市代码
3. ⬜ 实现多城市爬取功能
4. ⬜ 添加城市数据分析

### **长期目标**
1. ⬜ 自动发现城市代码
2. ⬜ 建立完整的城市数据库
3. ⬜ 支持动态城市配置
4. ⬜ 实现智能城市选择

---

**最后更新**: 2026-05-21  
**更新内容**: 修正 `001019002` 为深圳（原误识别为北京）  
**维护人**: xingan  
**状态**: ✅ 已修正  

**重要提醒**: 所有城市代码都需要通过实际访问验证，不要依赖推测！