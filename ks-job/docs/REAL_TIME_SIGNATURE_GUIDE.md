# 🚀 实时签名获取指南 - 快手招聘数据爬取

## 🔍 **问题分析**

测试发现：**快手API需要实时生成的签名参数**，签名有效期非常短（可能只有几秒到几分钟）。

### **已确认的信息**
1. ✅ **基础Cookie有效**: `accessproxy_session` 等Cookie字段有效
2. ✅ **API接口正常**: API地址和参数正确
3. ❌ **签名过期快**: `sign` 和 `signtimestamp` 需要实时生成

### **签名机制分析**
根据你提供的请求头，快手API需要：
- `sign`: 64位十六进制字符串（SHA256签名）
- `signtimestamp`: 13位时间戳（毫秒）

## 🎯 **解决方案**

### **方案A：浏览器实时获取（推荐）**
**步骤：**
1. **打开浏览器**访问: https://zhaopin.kuaishou.cn
2. **打开开发者工具** (F12)
3. **切换到Network标签**
4. **刷新页面**或点击"加载更多"
5. **找到API请求**: `positions/simple`
6. **复制实时签名**:
   - 在Headers中找到 `sign` 和 `signtimestamp`
   - 立即使用（有效期很短）

### **方案B：自动化获取（需要开发）**
**实现思路：**
1. 使用Playwright/Selenium打开浏览器
2. 自动访问快手招聘网站
3. 拦截API请求，提取签名
4. 使用签名发送数据请求

### **方案C：签名算法逆向（复杂）**
**需要分析：**
1. JavaScript代码中的签名生成逻辑
2. 签名算法的参数和密钥
3. 时间戳的生成规则

## 🚀 **立即开始爬取**

### **第一步：获取实时签名**
请按以下步骤操作：

```bash
# 1. 打开浏览器（Chrome/Firefox）
# 2. 访问: https://zhaopin.kuaishou.cn
# 3. 按F12打开开发者工具
# 4. 切换到Network标签
# 5. 刷新页面
# 6. 找到API请求: positions/simple
# 7. 复制最新的 sign 和 signtimestamp
```

### **第二步：更新爬取器**
我已经创建了智能爬取器，只需要你提供实时签名：

```python
# 在 src/ks_smart_crawler.py 中修改 _get_real_time_signature 方法
def _get_real_time_signature(self) -> Tuple[str, str]:
    """
    获取实时签名
    请在这里返回最新的 sign 和 signtimestamp
    """
    # 请替换为最新的签名参数
    current_sign = "540d4202e9f24585e677f861a0171e56893ae1f5a90558d5320c7a829acd648e"  # 替换为最新的sign
    current_timestamp = "1779440014248"  # 替换为最新的signtimestamp
    
    return current_sign, current_timestamp
```

### **第三步：运行爬取器**
```bash
# 1. 进入项目目录
cd /Users/xingan/.openclaw/workspace/skills/find_new_jobs/ks-job

# 2. 运行智能爬取器
python3 src/ks_smart_crawler.py

# 3. 选择测试模式验证
# 4. 开始完整爬取
```

## 📋 **快速测试脚本**

我已经创建了一个快速测试脚本，你可以直接使用：

```python
# test_real_time.py
import requests
import time

# 请在这里填入最新的签名参数
SIGN = "最新的sign值"
SIGNTIMESTAMP = "最新的signtimestamp值"

headers = {
    "sign": SIGN,
    "signtimestamp": SIGNTIMESTAMP,
    "Cookie": "aliyungf_tc=62d111759197e609997a914760f88ccc44c00ef73b2f542817802af91250a937; accessproxy_session=01b7eac0ccce9f49aa335ac52039ec8a825379cdb3EAIiE3poYW9waW4ua3VhaXNob3UuY24KJGJiODA2NjMzLTVmODgtNGI5Yy1iM2QyLTBlMjEwZmI1NGEzZioVEhFVTkBVVEhPUklaRURfVVNFUgoAGLHJ1Of+Mw==; apdid=1e615e70-2858-4116-bd0e-5e461bd10eb4cc68ec35bc432b6780dc98e63f48cce7:1779186916:1; weblogger_did=web_754734862580340E",
    "Referer": "https://zhaopin.kuaishou.cn/"
}

params = {
    "pageNum": 1,
    "pageSize": 5,
    "positionCategoryCode": "J0005,J0004,J0013,J0006,J0014",
    "positionNatureCode": "C001",
    "recruitProject": "socialr",
    "workLocationCode": "domestic"
}

response = requests.get(
    "https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple",
    params=params,
    headers=headers
)

print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")
```

## 🔧 **自动化方案实现**

如果你希望自动化获取签名，我已经准备好了浏览器自动化方案：

### **1. 安装依赖**
```bash
pip install playwright
python -m playwright install
```

### **2. 运行浏览器自动化爬取器**
```bash
python3 src/ks_browser_crawler.py
```

### **3. 浏览器自动化特点**
- ✅ 自动打开浏览器
- ✅ 实时获取Cookie和签名
- ✅ 自动发送API请求
- ✅ 处理数据并保存
- ✅ 无需手动获取签名

## 🎯 **立即行动建议**

### **如果你能获取实时签名：**
1. **立即获取**最新的 `sign` 和 `signtimestamp`
2. **运行测试**验证签名有效性
3. **开始爬取**完整数据

### **如果你希望自动化：**
1. **安装Playwright**依赖
2. **运行浏览器爬取器**
3. **监控爬取过程**

### **时间敏感性**
- ⏰ **签名有效期极短**（可能只有几秒）
- 🏃 **获取后立即使用**
- 🔄 **每页可能需要新签名**

## 📞 **快速帮助**

### **常见问题**
```
Q: 签名获取后立即过期？
A: 是的，需要立即使用。建议获取后1秒内使用。

Q: 每页都需要新签名吗？
A: 可能需要，建议每页重新获取。

Q: 如何批量获取签名？
A: 使用浏览器自动化方案。
```

### **调试命令**
```bash
# 测试网络连接
curl -I "https://zhaopin.kuaishou.cn"

# 查看当前时间戳（用于对比）
python3 -c "import time; print(int(time.time() * 1000))"

# 运行简化测试
python3 test_new_signature.py
```

## 🚀 **开始你的数据爬取！**

**现在你有三个选择：**

### **选择1：手动获取签名（最快）**
1. 打开浏览器获取实时签名
2. 更新 `src/ks_smart_crawler.py`
3. 立即开始爬取

### **选择2：浏览器自动化（最稳定）**
1. 安装Playwright
2. 运行 `src/ks_browser_crawler.py`
3. 自动爬取所有数据

### **选择3：混合方案**
1. 手动获取第一个签名
2. 测试API连通性
3. 决定后续方案

**请告诉我你的选择，我会立即协助你开始真实数据爬取！** 🎯

---

**最后更新**: 2026-05-22 17:00  
**关键发现**: 签名需要实时获取，有效期极短  
**推荐方案**: 浏览器自动化或快速手动获取  
**项目状态**: ✅ 爬取器就绪，等待实时签名