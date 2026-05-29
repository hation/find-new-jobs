#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
夸克方案迁移脚本
将夸克校园招聘爬取方案迁移到其他公司招聘系统
"""

import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

class QuarkMigrationTool:
    """夸克方案迁移工具"""
    
    def __init__(self, source_dir: str = None):
        """
        初始化迁移工具
        
        Args:
            source_dir: 夸克项目源目录，默认为当前目录
        """
        if source_dir:
            self.source_dir = Path(source_dir)
        else:
            self.source_dir = Path(__file__).parent.parent
        
        # 定义源文件
        self.source_files = {
            "框架文件": [
                "quark_crawler.py",            # 统一入口
                "merge_to_excel.py",           # 数据导出
                "detailed_data_check.py",      # 数据检查
            ],
            "核心脚本": [
                "scripts/crawler_selector_optimized.py",  # 智能选择器
                "scripts/api_crawler_configurable.py",    # API爬取器（模板）
                "scripts/browser_crawler.py",             # 浏览器爬取器（模板）
            ],
            "配置模板": [
                "config/api_auth.json",        # API认证配置模板
            ],
            "文档模板": [
                "CHECKLIST.md",                # 检查清单模板
                "LESSONS_LEARNED.md",          # 教训记录模板
                "ARCHITECTURE.md",             # 架构文档模板
            ]
        }
        
        # 需要重命名的文件
        self.rename_mapping = {
            "quark_crawler.py": "company_crawler.py",
            "quark_": "company_"
        }
    
    def analyze_new_company(self, new_company_name: str) -> Dict[str, str]:
        """
        分析新公司需求
        
        Args:
            new_company_name: 新公司名称
            
        Returns:
            分析结果字典
        """
        print(f"🔍 分析新公司: {new_company_name}")
        print("=" * 60)
        
        analysis = {
            "company_name": new_company_name,
            "migration_steps": [],
            "customization_points": [],
            "estimated_effort": "中等"
        }
        
        # 询问用户关键信息
        print("\n📋 请回答以下问题来定制迁移方案:")
        
        questions = [
            ("公司招聘网站URL", "https://careers.example.com"),
            ("是否有公开API接口", "是/否"),
            ("是否需要登录认证", "是/否"),
            ("主要筛选条件", "技术类,产品类,运营类等"),
            ("数据字段需求", "岗位名称,工作地点,薪资范围等"),
        ]
        
        answers = {}
        for question, hint in questions:
            answer = input(f"  • {question} ({hint}): ").strip()
            answers[question] = answer
        
        # 基于回答生成分析
        if "是" in answers.get("是否有公开API接口", ""):
            analysis["migration_steps"].append("优先实现API方案")
            analysis["estimated_effort"] = "较低"
        else:
            analysis["migration_steps"].append("主要依赖浏览器方案")
            analysis["estimated_effort"] = "较高"
        
        if "是" in answers.get("是否需要登录认证", ""):
            analysis["customization_points"].append("需要定制认证逻辑")
        
        print(f"\n📊 分析完成: {analysis['estimated_effort']} 难度")
        return {**analysis, **answers}
    
    def create_migration_template(self, new_company_name: str, target_dir: str = None) -> Path:
        """
        创建迁移模板
        
        Args:
            new_company_name: 新公司名称
            target_dir: 目标目录，默认为新公司名称
            
        Returns:
            创建的模板目录路径
        """
        if not target_dir:
            # 生成安全目录名
            safe_name = "".join(c for c in new_company_name if c.isalnum() or c in (' ', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_').lower()
            target_dir = f"{safe_name}_recruitment_scraper"
        
        target_path = Path(target_dir)
        
        print(f"🚀 为 {new_company_name} 创建迁移模板...")
        print(f"   目标目录: {target_path}")
        
        # 创建目录结构
        dirs_to_create = [
            target_path,
            target_path / "scripts",
            target_path / "config",
            target_path / "output",
            target_path / "other",
            target_path / "other/scripts",
            target_path / "other/tests",
            target_path / "other/docs",
        ]
        
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ 创建目录: {dir_path}")
        
        # 复制文件并重命名
        copied_files = []
        
        for category, files in self.source_files.items():
            print(f"\n📁 复制 {category}:")
            
            for file_name in files:
                source_file = self.source_dir / file_name
                target_file = target_path / file_name
                
                if source_file.exists():
                    # 确保目标目录存在
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 重命名文件
                    new_name = target_file.name
                    for old, new in self.rename_mapping.items():
                        if old in new_name:
                            new_name = new_name.replace(old, new)
                    
                    target_file = target_file.parent / new_name
                    
                    # 复制文件
                    shutil.copy2(source_file, target_file)
                    
                    # 如果是核心文件，添加TODO标记
                    if "crawler" in file_name or "api" in file_name:
                        self._add_todo_markers(target_file, new_company_name)
                    
                    copied_files.append(str(target_file.relative_to(target_path)))
                    print(f"   ✅ 复制: {file_name} → {new_name}")
                else:
                    print(f"   ⚠️  跳过: {file_name} (源文件不存在)")
        
        # 创建配置文件
        self._create_config_template(target_path, new_company_name)
        
        # 创建迁移指南
        self._create_migration_guide(target_path, new_company_name, copied_files)
        
        print(f"\n🎉 迁移模板创建完成!")
        print(f"   位置: {target_path.absolute()}")
        print(f"   文件数: {len(copied_files)} 个")
        
        return target_path
    
    def _add_todo_markers(self, file_path: Path, new_company_name: str):
        """
        在需要定制的文件中添加TODO标记
        
        Args:
            file_path: 文件路径
            new_company_name: 新公司名称
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 添加TODO标记
            todo_marker = f"""# TODO: 为新公司 {new_company_name} 定制以下部分

# ==================== 需要定制的部分 ====================
# 1. 更新API端点或页面URL
# 2. 更新认证信息（CSRF令牌、Cookie等）
# 3. 更新请求参数
# 4. 更新数据字段映射
# 5. 更新页面元素选择器
# =====================================================

"""
            
            # 如果是Python文件，在import后添加TODO
            if file_path.suffix == '.py':
                lines = content.split('\n')
                import_end = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_end = i + 1
                    else:
                        break
                
                if import_end > 0:
                    new_content = '\n'.join(lines[:import_end]) + '\n\n' + todo_marker + '\n'.join(lines[import_end:])
                else:
                    new_content = todo_marker + content
            else:
                new_content = todo_marker + content
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
        except Exception as e:
            print(f"   ⚠️  添加TODO标记失败: {e}")
    
    def _create_config_template(self, target_path: Path, new_company_name: str):
        """
        创建配置文件模板
        
        Args:
            target_path: 目标目录
            new_company_name: 新公司名称
        """
        config_template = {
            "description": f"{new_company_name}招聘API认证配置文件",
            "last_updated": "请填写当前日期",
            "status": "pending_configuration",
            "company_name": new_company_name,
            "authentication": {
                "csrf_token": "TODO: 从浏览器获取CSRF令牌",
                "cookies": {
                    "SESSION": "TODO: 填写会话Cookie",
                    "XSRF-TOKEN": "TODO: 填写XSRF令牌"
                },
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Content-Type": "application/json",
                    "Referer": "TODO: 填写招聘网站URL"
                }
            },
            "api_endpoint": "TODO: 填写API端点URL",
            "parameters": {
                "page": 1,
                "size": 10,
                "categories": "TODO: 填写筛选类别"
            },
            "page_urls": {
                "list_page": "TODO: 填写列表页URL",
                "detail_page_template": "TODO: 填写详情页URL模板"
            },
            "validation": {
                "expected_total_positions": 0,
                "expected_page_size": 10,
                "expected_fields": [
                    "position_id",
                    "position_name",
                    "work_location",
                    "department",
                    "education_requirement",
                    "work_experience",
                    "salary_range",
                    "position_description",
                    "position_requirements",
                    "publish_date",
                    "application_deadline",
                    "company_info"
                ]
            },
            "notes": [
                "请根据实际情况填写TODO标记的内容",
                "认证信息可能需要定期更新",
                "如果API不可用，请使用浏览器方案"
            ]
        }
        
        config_file = target_path / "config" / "api_auth.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(config_template, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ 创建配置文件: {config_file.relative_to(target_path)}")
    
    def _create_migration_guide(self, target_path: Path, new_company_name: str, copied_files: List[str]):
        """
        创建迁移指南
        
        Args:
            target_path: 目标目录
            new_company_name: 新公司名称
            copied_files: 已复制的文件列表
        """
        guide_content = f"""# 🚀 {new_company_name}招聘爬取器迁移指南

## 📋 迁移完成情况

✅ **已复用的框架组件:**
```
{copied_files}
```

## 🛠️ 下一步定制工作

### 1. 配置认证信息
```bash
# 编辑配置文件
vim config/api_auth.json

# 需要填写的关键信息:
# - api_endpoint: API端点URL
# - csrf_token: CSRF令牌
# - cookies: 会话Cookie
# - headers: 请求头信息
```

### 2. 定制API爬取器
```bash
# 编辑API爬取器
vim scripts/api_crawler_configurable.py

# 需要修改的部分:
# - __init__: 更新API端点和参数
# - fetch_page: 更新请求逻辑
# - _parse_position_data: 更新数据字段映射
```

### 3. 定制浏览器爬取器
```bash
# 编辑浏览器爬取器
vim scripts/browser_crawler.py

# 需要修改的部分:
# - __init__: 更新页面URL和选择器
# - scrape_positions: 更新页面交互逻辑
# - _extract_position_details: 更新数据提取逻辑
```

### 4. 更新智能选择器
```bash
# 编辑智能选择器
vim scripts/crawler_selector_optimized.py

# 需要修改的部分:
# - 类名: QuarkCrawlerSelectorOptimized → NewCompanyCrawlerSelector
# - 导入: 更新爬取器导入路径
```

### 5. 更新统一入口
```bash
# 编辑统一入口
vim company_crawler.py

# 需要修改的部分:
# - 项目名称和描述
# - 默认参数设置
# - 帮助信息
```

## 🧪 测试步骤

### 第一步：测试配置文件
```bash
python3 -c "import json; import sys; data = json.load(open('config/api_auth.json')); print('配置检查:', 'TODO' not in str(data))"
```

### 第二步：测试API连接
```bash
python3 scripts/api_crawler_configurable.py
```

### 第三步：测试统一入口
```bash
# 查看帮助
python3 company_crawler.py --help

# 查看状态
python3 company_crawler.py --mode status

# 测试智能爬取
python3 company_crawler.py --mode smart --start 1 --end 1
```

## 📊 验证清单

- [ ] 配置文件填写完整
- [ ] API端点可访问
- [ ] 认证信息有效
- [ ] 数据字段映射正确
- [ ] 分页逻辑正常
- [ ] 错误处理完善
- [ ] 数据导出正常

## 🆘 遇到问题？

### 常见问题解决
1. **API连接失败**: 检查CSRF令牌和Cookie
2. **数据解析失败**: 检查响应结构和字段映射
3. **页面交互失败**: 检查选择器和页面结构
4. **分页逻辑错误**: 检查分页参数和总数计算

### 调试命令
```bash
# 测试API连接
python3 -c "from scripts.api_crawler_configurable import NewCompanyApiCrawlerConfigurable; c = NewCompanyApiCrawlerConfigurable(); print(c.test_api_connection())"

# 测试页面元素
python3 -c "from scripts.browser_crawler import NewCompanyCampusScraper; s = NewCompanyCampusScraper(); print(s.test_page_elements())"
```

## 📞 支持资源

- 夸克原始项目: {self.source_dir.absolute()}
- 迁移模板文档: {target_path}/MIGRATION_GUIDE.md
- 配置文件模板: config/api_auth.json

---

**迁移完成标志**: `python3 company_crawler.py --mode optimized` 能够成功爬取{new_company_name}的岗位数据

**开始时间**: 请填写开始日期
**预计完成**: 请填写预计完成日期
**实际完成**: 请填写实际完成日期
"""

        guide_file = target_path / "MIGRATION_GUIDE.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"   ✅ 创建迁移指南: {guide_file.relative_to(target_path)}")
    
    def generate_quick_start_script(self, target_path: Path):
        """
        生成快速启动脚本
        
        Args:
            target_path: 目标目录
        """
        script_content = """#!/usr/bin/env bash
# 快速启动脚本

echo "🚀 启动招聘爬取器..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "🔍 检查Python依赖..."
python3 -c "import requests, pandas, json" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装Python依赖..."
    pip3 install requests pandas --quiet
fi

# 显示帮助
echo ""
echo "📋 可用命令:"
echo "  1. python3 company_crawler.py --help          # 查看帮助"
echo "  2. python3 company_crawler.py --mode status   # 查看状态"
echo "  3. python3 company_crawler.py --mode smart    # 智能爬取"
echo "  4. python3 company_crawler.py --mode optimized # 优化爬取（推荐）"
echo "  5. python3 company_crawler.py --mode export   # 导出数据"
echo ""

# 默认运行优化模式
echo "🎯 推荐使用优化模式（失败后询问）"
read -p "是否开始爬取？(y/n): " choice

if [[ $choice == "y" || $choice == "Y" ]]; then
    python3 company_crawler.py --mode optimized
else
    echo "👋 已取消，请手动运行上述命令"
fi
"""

        script_file = target_path / "start.sh"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(script_file, 0o755)
        
        print(f"   ✅ 创建快速启动脚本: {script_file.relative_to(target_path)}")


def main():
    """主函数"""
    print("=" * 70)
    print("🚀 夸克招聘爬取方案迁移工具")
    print("📋 将夸克方案迁移到其他公司招聘系统")
    print("=" * 70)
    print()
    
    # 检查源目录
    source_dir = Path(__file__).parent.parent
    if not (source_dir / "quark_crawler.py").exists():
        print("❌ 错误：未找到夸克项目文件")
        print(f"   请确保在夸克项目目录中运行此脚本")
        print(f"   当前目录: {source_dir}")
        sys.exit(1)
    
    # 创建迁移工具
    migrator = QuarkMigrationTool(source_dir)
    
    # 获取新公司名称
    print("📝 请输入新公司名称:")
    print("   例如: 字节跳动、腾讯、阿里巴巴、华为等")
    new_company_name = input("公司名称: ").strip()
    
    if not new_company_name:
        print("❌ 公司名称不能为空")
        sys.exit(1)
    
    # 分析新公司需求
    analysis = migrator.analyze_new_company(new_company_name)
    
    # 确认是否继续
    print(f"\n⚠️  即将为 {new_company_name} 创建迁移模板")
    print(f"   预计难度: {analysis['estimated_effort']}")
    print(f"   需要定制: {len(analysis['customization_points'])} 个点")
    
    confirm = input("\n是否继续创建模板？(y/n): ").strip().lower()
    if confirm != 'y':
        print("👋 已取消迁移")
        sys.exit(0)
    
    # 创建迁移模板
    try:
        target_dir = migrator.create_migration_template(new_company_name)
        
        # 生成快速启动脚本
        migrator.generate_quick_start_script(target_dir)
        
        print("\n" + "=" * 70)
        print("🎉 迁移模板创建成功!")
        print("=" * 70)
        print()
        print("📋 下一步操作:")
        print(f"   1. 进入目录: cd {target_dir.name}")
        print(f"   2. 查看指南: cat MIGRATION_GUIDE.md")
        print(f"   3. 配置认证: vim config/api_auth.json")
        print(f"   4. 开始定制: 按照指南修改TODO标记")
        print(f"   5. 测试运行: ./start.sh")
        print()
        print("💡 提示:")
        print("   • 配置文件中的TODO标记需要全部填写")
        print("   • 可以先测试第1页数据")
        print("   • 遇到问题参考迁移指南")
        print()
        print("🚀 开始迁移之旅吧!")
        
    except Exception as e:
        print(f"❌ 创建迁移模板失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()