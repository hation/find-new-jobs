# 🚀 方案B技能实现标准文档

**目录**: `/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/`  
**版本**: 修复增强版 v2.6  
**创建时间**: 2026-05-16 12:50  
**标准依据**: 用户最初约定的方案B标准和实现要求

## 📋 **核心实现标准**

### **1. 目录结构标准**
```
scheme_b/
├── SKILL.md                    # 核心技能文档（必须完整）
├── scripts/                    # 实现脚本目录（必须分类清晰）
│   ├── 数据获取/              # 获取相关脚本
│   ├── Excel操作/             # Excel相关脚本  
│   ├── 工作流控制/            # 流程控制脚本
│   └── 工具脚本/              # 辅助工具脚本
├── data/                      # 测试数据目录
├── docs/                      # 文档目录
├── templates/                 # 模板文件目录（可选）
└── 快速启动脚本               # 一键启动脚本
```

### **2. 脚本命名标准**
- **前缀表示功能**：`fetch_`（获取）、`scheme_b_excel_`（Excel操作）、`complete_`（完整流程）
- **版本标识**：`_v2.py`、`_fixed.py`、`_optimized.py`
- **功能描述**：`_smart.py`（智能）、`_conservative.py`（保守）、`_simple.py`（简单）

### **3. 代码实现标准**
- **错误处理**：必须有完善的try-catch和错误日志
- **环境配置**：必须处理PATH和环境变量
- **格式兼容**：必须支持JSON和YAML格式
- **进度记录**：必须有完整的进度跟踪和记录

## 🔧 **脚本实现详情**

### **📁 数据获取脚本（8个）**

#### **1. `fetch_details_smart_v2.py`** ✅ **推荐使用**
**标准实现**：
- 智能错误检测：区分"职位不存在"和"token过期"
- 自动跳过失效security_id
- 分批获取，避免token过期
- 完整的进度记录和错误日志

**核心代码特点**：
```python
# 智能错误检测
if "已过期" in output_text or "环境异常" in output_text:
    return "token_expired"
elif "职位不存在" in output_text or "已失效" in output_text:
    return "job_not_found"
else:
    return "success"
```

#### **2. `fetch_details_conservative_v2.py`** ✅ **保守版本**
**标准实现**：
- 每次获取前检查token状态
- 更严格的错误处理
- 避免连续失败
- 适合网络不稳定环境

#### **3. `fetch_details_yaml_fixed.py`** ⚠️ **格式修复版**
**标准实现**：
- 支持YAML和JSON双格式解析
- 智能格式检测：先尝试JSON，失败后尝试YAML
- 保持数据完整性，不丢失任何信息

#### **4. `fetch_details_smart_skip.py`** 🔧 **智能跳过版**
**标准实现**：
- 自动跳过前3-5个可能失效的security_id
- 从中间位置开始获取
- 失效ID管理：记录已失效的security_id
- 准确错误诊断

#### **5. `fetch_details_optimized_v2.py`** ⚡ **优化版**
**标准实现**：
- 优化获取速度
- 减少不必要的检查
- 批量处理，提高效率

#### **6. `fetch_details_conservative.py`** 🐢 **原始保守版**
**标准实现**：
- 基础保守实现
- 简单直接，易于调试
- 适合测试和验证

#### **7. `fetch_details_simple.py`** 🎯 **简单版**
**标准实现**：
- 最简单的获取逻辑
- 适合快速测试
- 最小依赖

#### **8. `fetch_details_test.py`** 🧪 **测试版**
**标准实现**：
- 专门用于测试
- 包含各种测试用例
- 验证功能正确性

### **📊 Excel操作脚本（6个）**

#### **1. `scheme_b_excel_correct_merge_v2.py`** ✅ **推荐使用**
**标准实现**：
- 使用encryptId作为唯一标识
- 正确的字段映射：`postDescription` → `职位描述`
- 多策略匹配：encryptId直接匹配、职位名称唯一匹配
- 生成数据质量报告

#### **2. `scheme_b_excel_merge_fixed.py`** 🔧 **修复版**
**标准实现**：
- 修复字段映射错误
- 解决数据覆盖问题
- 确保数据完整性

#### **3. `scheme_b_excel_merge_simple.py`** 🎯 **简单版**
**标准实现**：
- 简单的Excel合并逻辑
- 适合小批量数据
- 快速执行

#### **4. `scheme_b_excel_exporter.py`** 📤 **导出版**
**标准实现**：
- 专门用于数据导出
- 支持多种格式
- 可定制输出

#### **5. `fix_excel_data.py`** 🛠️ **数据修复版**
**标准实现**：
- 修复Excel数据问题
- 标准化字段格式
- 清理无效数据

#### **6. `rename_excel_files.py`** 📝 **重命名版**
**标准实现**：
- 标准化文件命名
- 支持批量重命名
- 保持文件关联

### **🔄 工作流脚本（3个）**

#### **1. `complete_scheme_b_workflow.py`** ✅ **完整工作流**
**标准实现**：
- 一站式解决方案
- 包含所有步骤：登录→搜索→获取详情→合并Excel
- 完整的错误处理和恢复机制

#### **2. `scheme_b_auto_workflow.py`** 🤖 **自动工作流**
**标准实现**：
- 自动化执行
- 定时任务支持
- 无需人工干预

#### **3. `check_data_completeness.py`** 🔍 **数据检查**
**标准实现**：
- 检查数据完整性
- 验证ID匹配情况
- 生成质量报告

## 📁 **目录结构实现标准**

### **1. `scripts/` 目录结构**
```
scripts/
├── 数据获取/                  # 8个获取脚本
│   ├── fetch_details_smart_v2.py         # 智能获取（主推）
│   ├── fetch_details_conservative_v2.py  # 保守获取（备选）
│   ├── fetch_details_yaml_fixed.py       # YAML修复（特殊情况）
│   ├── fetch_details_smart_skip.py       # 智能跳过（失效ID处理）
│   ├── fetch_details_optimized_v2.py     # 优化获取（效率优先）
│   ├── fetch_details_conservative.py     # 原始保守（测试用）
│   ├── fetch_details_simple.py           # 简单获取（快速测试）
│   └── fetch_details_test.py             # 测试脚本（验证用）
├── Excel操作/                # 6个Excel脚本
│   ├── scheme_b_excel_correct_merge_v2.py # 正确合并（主推）
│   ├── scheme_b_excel_merge_fixed.py      # 修复合并（问题修复）
│   ├── scheme_b_excel_merge_simple.py     # 简单合并（小批量）
│   ├── scheme_b_excel_exporter.py         # 数据导出（输出）
│   ├── fix_excel_data.py                  # 数据修复（清理）
│   └── rename_excel_files.py              # 文件重命名（管理）
└── 工作流控制/              # 3个工作流脚本
    ├── complete_scheme_b_workflow.py      # 完整工作流（一站式）
    ├── scheme_b_auto_workflow.py          # 自动工作流（自动化）
    └── check_data_completeness.py         # 数据检查（验证）
```

### **2. `docs/` 目录文档标准**
```
docs/
├── README_下次继续.md        # 中断恢复指南
├── SCHEME_B_FULL_WORKFLOW.md # 完整工作流文档
├── 恢复执行检查清单.md       # 恢复执行检查项
└── 进度报告_暂停_20260515.md # 历史进度记录
```

### **3. 快速启动脚本标准**
- `quick_start.sh`：基础快速启动
- `quick_start_v2.sh`：增强版快速启动
- `恢复执行.sh`：中断后恢复执行

## 🎯 **核心实现原则**

### **原则1：encryptId为唯一标识**
```python
# 正确实现
search_encrypt_job_id = job_data['encryptJobId']  # 28字符
detail_encrypt_id = detail_data['data']['jobInfo']['encryptId']  # 28字符
assert search_encrypt_job_id == detail_encrypt_id  # 必须相等
```

### **原则2：security_id正确使用**
```python
# 搜索数据中的security_id（304字符）- 用于获取详情
search_security_id = job_data['securityId']  # 304字符，用于boss detail命令

# 详情数据中的securityId（416字符）- 详情内部标识，不用于匹配
detail_security_id = detail_data['data']['securityId']  # 416字符，仅内部使用

# 两者不同，不能混淆！
```

### **原则3：先获取详情，后合并Excel**
```python
# ✅ 正确流程
def correct_workflow():
    # 1. 批量获取详情
    fetch_multiple_details(security_ids)
    
    # 2. 验证获取完成
    verify_details_complete()
    
    # 3. 最后合并Excel
    merge_to_excel()

# ❌ 错误流程（禁止！）
def wrong_workflow():
    # 1. 获取几个详情
    fetch_some_details()
    
    # 2. 立即合并Excel（错误！）
    merge_to_excel()  # ❌ 不应该在这里合并
    
    # 3. 继续获取（数据不一致）
    fetch_more_details()
```

### **原则4：完善的错误处理**
```python
def standard_error_handling():
    try:
        # 主要逻辑
        result = execute_task()
        
        # 检查特定错误
        if "token过期" in result:
            log_error("token_expired", "需要重新登录")
            return "token_expired"
        elif "职位不存在" in result:
            log_error("job_not_found", "跳过该security_id")
            return "job_not_found"
        else:
            return "success"
            
    except json.JSONDecodeError as e:
        # 尝试YAML解析
        try:
            data = yaml.safe_load(result)
            return "success_yaml"
        except yaml.YAMLError:
            log_error("parse_failed", f"无法解析格式: {e}")
            return "parse_failed"
            
    except Exception as e:
        log_error("unexpected", f"未知错误: {e}")
        return "unexpected_error"
```

### **原则5：完整的进度记录**
```python
class ProgressTracker:
    def __init__(self):
        self.total = 0
        self.completed = 0
        self.failed = 0
        self.skipped = 0
        
    def record_success(self, security_id):
        self.completed += 1
        self._update_file(security_id, "success")
        
    def record_failure(self, security_id, reason):
        self.failed += 1
        self._update_file(security_id, f"failed: {reason}")
        
    def record_skip(self, security_id, reason):
        self.skipped += 1
        self._update_file(security_id, f"skipped: {reason}")
        
    def get_progress(self):
        return {
            "total": self.total,
            "completed": self.completed,
            "failed": self.failed,
            "skipped": self.skipped,
            "completion_rate": self.completed / self.total if self.total > 0 else 0
        }
```

## 📊 **数据质量标准**

### **质量指标**
1. **完整率**：> 50%的职位有完整详情
2. **匹配率**：100%的encryptId匹配
3. **重复率**：< 20%的重复文件
4. **错误率**：< 10%的获取失败

### **验证命令**
```bash
# 检查数据质量
python3 check_data_completeness.py

# 验证encryptId匹配
python3 -c "
import json
# 验证搜索和详情的encryptId匹配
"

# 检查进度
python3 -c "
# 计算完成率、失败率等
"
```

## 🔄 **工作流标准**

### **标准工作流**
```bash
# 1. 环境准备
export PATH="/Users/xingan/Library/Python/3.12/bin:$PATH"

# 2. 登录检查
boss status

# 3. 获取详情（推荐智能获取）
python3 fetch_details_smart_v2.py

# 4. 合并Excel（推荐正确合并）
python3 scheme_b_excel_correct_merge_v2.py

# 5. 质量检查
python3 check_data_completeness.py
```

### **快速启动工作流**
```bash
# 使用快速启动脚本
bash quick_start.sh

# 或使用完整工作流
python3 complete_scheme_b_workflow.py
```

### **恢复执行工作流**
```bash
# 中断后恢复
bash 恢复执行.sh

# 或手动恢复
python3 fetch_details_smart_skip.py  # 跳过失效ID
python3 scheme_b_excel_merge_fixed.py  # 修复合并
```

## 📝 **文档标准**

### **SKILL.md 文档结构**
1. **最新问题与解决方案**（顶部，及时更新）
2. **核心原则**（清晰明确）
3. **脚本功能说明**（详细完整）
4. **使用示例**（可复制执行）
5. **常见问题**（覆盖全面）
6. **更新历史**（记录变化）

### **快速使用指南标准**
- 必须包含：快速启动命令
- 必须包含：常见问题解决方法
- 必须包含：核心原则摘要
- 必须包含：联系方式或支持信息

## 🚀 **部署与维护标准**

### **部署检查清单**
- [ ] 所有脚本可执行权限正确
- [ ] 环境变量配置正确
- [ ] 依赖包已安装（pandas, yaml等）
- [ ] 测试数据可用
- [ ] 文档完整

### **维护标准**
- **定期检查**：每周检查数据质量
- **及时更新**：发现问题立即修复
- **版本控制**：重要变更记录版本
- **备份策略**：重要数据定期备份

---

**最后更新**: 2026-05-16 12:50  
**符合标准**: ✅ 完全按照用户最初约定的方案B标准和实现要求  
**验证状态**: ✅ 所有脚本符合标准，目录结构清晰，文档完整  
**维护承诺**: 持续按照此标准维护和更新方案B技能实现