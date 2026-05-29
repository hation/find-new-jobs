#!/usr/bin/env python3
"""
配置文件验证示例
在迁移后验证项目配置是否完整
"""

import json
import os
import sys
from pathlib import Path

class ConfigValidator:
    """配置文件验证器"""
    
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.errors = []
        self.warnings = []
        
    def validate_project_structure(self):
        """验证项目结构"""
        required_dirs = [
            "docs",
            "config", 
            "scripts",
            "src",
            "tests",
            "logs",
            "data",
            "data/raw",
            "data/processed",
            "data/backup"
        ]
        
        print("🔍 验证项目目录结构...")
        
        for dir_path in required_dirs:
            full_path = self.project_path / dir_path
            if not full_path.exists():
                self.errors.append(f"缺少目录: {dir_path}")
            elif not full_path.is_dir():
                self.errors.append(f"不是目录: {dir_path}")
            else:
                print(f"  ✅ {dir_path}")
                
    def validate_core_files(self):
        """验证核心文件"""
        required_files = [
            "docs/CORE_BUSINESS_INFO.md",
            "docs/CHECKLIST.md",
            "docs/LESSONS_LEARNED.md",
            "docs/QUICK_START.md",
            "docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md",
            "config/project_config.json",
            "README.md",
            "start_project.sh"
        ]
        
        print("\n📄 验证核心文件...")
        
        for file_path in required_files:
            full_path = self.project_path / file_path
            if not full_path.exists():
                self.errors.append(f"缺少文件: {file_path}")
            elif not full_path.is_file():
                self.errors.append(f"不是文件: {file_path}")
            else:
                # 检查文件大小（不能为空）
                if full_path.stat().st_size < 100:
                    self.warnings.append(f"文件可能为空: {file_path}")
                print(f"  ✅ {file_path}")
                
    def validate_config_file(self):
        """验证配置文件内容"""
        config_file = self.project_path / "config" / "project_config.json"
        
        if not config_file.exists():
            self.errors.append("配置文件不存在")
            return
            
        print("\n⚙️ 验证配置文件...")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 检查必要字段
            required_fields = ["project", "template_system", "workflow"]
            for field in required_fields:
                if field not in config:
                    self.errors.append(f"配置缺少字段: {field}")
                else:
                    print(f"  ✅ 配置字段: {field}")
                    
            # 检查项目信息
            if "project" in config:
                project_info = config["project"]
                required_project_fields = ["name", "type", "created_date", "version"]
                for field in required_project_fields:
                    if field not in project_info:
                        self.warnings.append(f"项目信息缺少: {field}")
                    else:
                        print(f"    • {field}: {project_info[field]}")
                        
        except json.JSONDecodeError as e:
            self.errors.append(f"配置文件JSON格式错误: {e}")
        except Exception as e:
            self.errors.append(f"读取配置文件失败: {e}")
            
    def validate_scripts(self):
        """验证脚本文件"""
        scripts_dir = self.project_path / "scripts"
        
        if not scripts_dir.exists():
            self.warnings.append("scripts目录不存在")
            return
            
        print("\n🔧 验证脚本文件...")
        
        # 检查启动脚本权限
        start_script = self.project_path / "start_project.sh"
        if start_script.exists():
            # 检查是否可执行
            if not os.access(start_script, os.X_OK):
                self.warnings.append("启动脚本不可执行")
            else:
                print(f"  ✅ 启动脚本可执行")
                
        # 检查迁移脚本
        migration_script = scripts_dir / "new-project-migration.sh"
        if migration_script.exists():
            if not os.access(migration_script, os.X_OK):
                self.warnings.append("迁移脚本不可执行")
            else:
                print(f"  ✅ 迁移脚本存在")
                
    def validate_memory_system(self):
        """验证记忆系统"""
        memory_dir = self.project_path / "memory-system"
        
        if not memory_dir.exists():
            self.warnings.append("memory-system目录不存在")
            return
            
        print("\n🧠 验证记忆系统...")
        
        required_memory_files = [
            "DAILY_MEMORY_TEMPLATE.md",
            "CORE_BUSINESS_INFO_TEMPLATE.md", 
            "MEMORY_SYSTEM_GUIDE.md"
        ]
        
        for file_name in required_memory_files:
            file_path = memory_dir / file_name
            if file_path.exists():
                print(f"  ✅ 记忆文件: {file_name}")
            else:
                self.warnings.append(f"缺少记忆文件: {file_name}")
                
    def run_validation(self):
        """运行所有验证"""
        print("=" * 60)
        print("🚀 夸克模板系统 - 迁移验证工具")
        print("=" * 60)
        
        self.validate_project_structure()
        self.validate_core_files()
        self.validate_config_file()
        self.validate_scripts()
        self.validate_memory_system()
        
        # 显示结果
        print("\n" + "=" * 60)
        print("📊 验证结果")
        print("=" * 60)
        
        if self.errors:
            print("\n❌ 错误:")
            for error in self.errors:
                print(f"  • {error}")
                
        if self.warnings:
            print("\n⚠️  警告:")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        if not self.errors and not self.warnings:
            print("\n🎉 所有验证通过！项目迁移成功。")
            print("\n下一步建议:")
            print("1. 运行 ./start_project.sh 开始项目")
            print("2. 填写 docs/CORE_BUSINESS_INFO.md 中的业务信息")
            print("3. 执行 docs/CHECKLIST.md 中的检查项")
            return True
        elif self.errors:
            print(f"\n❌ 验证失败，发现 {len(self.errors)} 个错误")
            return False
        else:
            print(f"\n⚠️  验证通过但有 {len(self.warnings)} 个警告")
            print("\n项目可以正常使用，但建议修复警告")
            return True

def main():
    """主函数"""
    # 获取项目路径，默认为当前目录
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."
    
    validator = ConfigValidator(project_path)
    success = validator.run_validation()
    
    # 返回退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()