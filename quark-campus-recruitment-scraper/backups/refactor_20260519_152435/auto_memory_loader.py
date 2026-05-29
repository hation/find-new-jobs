#!/usr/bin/env python3
# 🧠 夸克校园招聘爬取器 - 自动记忆加载器
# 版本: 1.0
# 创建时间: 2026-05-19T15:03:08.023545

import os
import json
import sys
from datetime import datetime
from pathlib import Path

class AutoMemoryLoader:
    """自动记忆加载器 - 加载项目的所有记忆文件"""
    
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).resolve()
        self.memory_files = {
            "architecture": "ARCHITECTURE.md",
            "checklist": "CHECKLIST.md", 
            "lessons": "LESSONS_LEARNED.md",
            "checkpoints": "memory_checkpoints.json",
            "config": "config/memory_config.json"
        }
        
        # 颜色输出
        self.colors = {
            "info": "\033[94m",
            "success": "\033[92m",
            "warning": "\033[93m",
            "error": "\033[91m",
            "reset": "\033[0m"
        }
    
    def print_colored(self, text, color_type="info"):
        """打印带颜色的文本"""
        color = self.colors.get(color_type, self.colors["info"])
        print(f"{color}{text}{self.colors['reset']}")
    
    def load_all_memory(self):
        """加载所有记忆文件"""
        print("🧠 自动记忆加载器")
        print("=" * 60)
        
        memory_data = {}
        loaded_count = 0
        total_files = len(self.memory_files)
        
        for key, filename in self.memory_files.items():
            filepath = self.project_root / filename
            
            if filepath.exists():
                try:
                    if filename.endswith('.json'):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            memory_data[key] = json.load(f)
                    else:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            memory_data[key] = f.read()
                    
                    loaded_count += 1
                    self.print_colored(f"✅ {key}: {filename}", "success")
                    
                    # 显示关键信息
                    if key == "checkpoints":
                        self._display_checkpoint_info(memory_data[key])
                    elif key == "config":
                        self._display_config_info(memory_data[key])
                        
                except Exception as e:
                    self.print_colored(f"❌ {key}: {filename} - 加载失败: {e}", "error")
            else:
                self.print_colored(f"⚠️  {key}: {filename} - 文件不存在", "warning")
        
        # 统计信息
        print("\n" + "=" * 60)
        self.print_colored(f"📊 加载统计: {loaded_count}/{total_files} 个文件", "info")
        
        if loaded_count == total_files:
            self.print_colored("🎉 所有记忆文件加载成功!", "success")
        elif loaded_count >= total_files * 0.7:
            self.print_colored("⚠️  部分记忆文件缺失，建议检查", "warning")
        else:
            self.print_colored("❌ 记忆文件严重缺失，需要重新初始化", "error")
        
        # 生成启动指令
        startup_command = self.generate_startup_command(memory_data)
        
        return {
            "status": "success" if loaded_count == total_files else "partial",
            "loaded_files": loaded_count,
            "total_files": total_files,
            "data": memory_data,
            "startup_command": startup_command
        }
    
    def _display_checkpoint_info(self, checkpoint_data):
        """显示检查点关键信息"""
        try:
            project_info = checkpoint_data.get("project_info", {})
            current_state = checkpoint_data.get("current_state", {})
            
            print(f"   📁 项目: {project_info.get('name', '未知')}")
            print(f"   🎯 待办: {current_state.get('next_action', '未设置')}")
            print(f"   📅 最后行动: {current_state.get('last_action_time', '未知')}")
            
            progress = current_state.get('progress', 0)
            if progress > 0:
                print(f"   📊 进度: {progress}%")
                
        except Exception as e:
            print(f"   ⚠️  检查点信息显示失败: {e}")
    
    def _display_config_info(self, config_data):
        """显示配置信息"""
        try:
            project_type = config_data.get("project_type", "未知")
            created_at = config_data.get("created_at", "未知")
            
            print(f"   🔧 类型: {project_type}")
            print(f"   🕐 创建: {created_at}")
            
        except Exception as e:
            print(f"   ⚠️  配置信息显示失败: {e}")
    
    def generate_startup_command(self, memory_data):
        """生成标准化启动指令"""
        project_name = "当前项目"
        next_action = "开始执行"
        
        try:
            project_name = memory_data.get("config", {}).get("project_name", project_name)
            next_action = memory_data.get("checkpoints", {}).get("current_state", {}).get("next_action", next_action)
        except:
            pass
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        command = f"""
🚀 基于记忆系统的标准化指令

📋 项目: {project_name}
🎯 待办: {next_action}
📅 当前时间: {current_time}

📝 执行命令:
执行{project_name}任务：步骤1验证记忆完整性，步骤2检查待办事项，步骤3{next_action}

💡 使用说明:
1. 复制上方指令发送给助手
2. 助手会基于记忆系统正确执行
3. 执行过程中会自动更新记忆状态
        """
        
        return command
    
    def update_checkpoint(self, action, result, details=None, lessons=None):
        """更新记忆检查点"""
        checkpoint_file = self.project_root / "memory_checkpoints.json"
        
        if not checkpoint_file.exists():
            self.print_colored("❌ 检查点文件不存在，无法更新", "error")
            return False
        
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoints = json.load(f)
            
            current_time = datetime.now().isoformat()
            
            # 更新当前状态
            if "current_state" not in checkpoints:
                checkpoints["current_state"] = {}
            
            checkpoints["current_state"]["last_action"] = action
            checkpoints["current_state"]["last_result"] = result
            checkpoints["current_state"]["last_action_time"] = current_time
            checkpoints["current_state"]["updated_at"] = current_time
            
            if details:
                checkpoints["current_state"]["last_details"] = details
            
            # 添加到历史记录
            if "checkpoint_history" not in checkpoints:
                checkpoints["checkpoint_history"] = []
            
            history_entry = {
                "timestamp": current_time,
                "action": action,
                "result": result,
                "details": details or "",
                "lessons": lessons or []
            }
            checkpoints["checkpoint_history"].append(history_entry)
            
            # 更新进度（如果提供了）
            if result == "completed" and "progress" in checkpoints["current_state"]:
                current_progress = checkpoints["current_state"].get("progress", 0)
                checkpoints["current_state"]["progress"] = min(current_progress + 10, 100)
            
            # 更新指标
            if "metrics" not in checkpoints:
                checkpoints["metrics"] = {}
            
            checkpoints["metrics"]["total_actions"] = checkpoints["metrics"].get("total_actions", 0) + 1
            checkpoints["metrics"]["last_updated"] = current_time
            
            # 保存
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoints, f, indent=2, ensure_ascii=False)
            
            self.print_colored(f"✅ 检查点已更新: {action}", "success")
            return True
            
        except Exception as e:
            self.print_colored(f"❌ 检查点更新失败: {e}", "error")
            return False

def main():
    """主函数"""
    # 获取项目根目录
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # 创建加载器实例
    loader = AutoMemoryLoader(project_root)
    
    # 加载所有记忆
    result = loader.load_all_memory()
    
    # 显示启动指令
    print("\n" + "=" * 60)
    print(result["startup_command"])
    
    # 建议
    print("\n💡 建议操作:")
    print("1. 复制上方指令发送给助手")
    print("2. 执行前阅读 CHECKLIST.md")
    print("3. 遇到错误时记录到 LESSONS_LEARNED.md")
    print("4. 定期更新 ARCHITECTURE.md")
    
    # 返回加载状态
    return 0 if result["status"] == "success" else 1

if __name__ == "__main__":
    sys.exit(main())