#!/usr/bin/env python3
"""
修复boss命令路径问题
确保导出工具能正确找到boss命令
"""

import os
import sys
import subprocess
from pathlib import Path

def find_boss_command():
    """查找boss命令的位置"""
    # 可能的boss命令安装位置
    possible_paths = [
        # macOS/Linux常见位置
        "/usr/local/bin/boss",
        "/usr/bin/boss", 
        "/bin/boss",
        # Python用户目录
        f"{Path.home()}/.local/bin/boss",
        f"{Path.home()}/Library/Python/3.12/bin/boss",  # 你的安装位置
        f"{Path.home()}/.pyenv/shims/boss",
        # Windows路径（如果需要）
        f"{Path.home()}/AppData/Local/Programs/Python/Python312/Scripts/boss.exe",
        f"{Path.home()}/AppData/Roaming/Python/Python312/Scripts/boss.exe",
    ]
    
    print("🔍 查找boss命令...")
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ 找到boss命令: {path}")
            return path
    
    # 尝试使用which命令查找
    try:
        result = subprocess.run(
            ["which", "boss"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode == 0:
            boss_path = result.stdout.strip()
            print(f"✅ 通过which找到boss命令: {boss_path}")
            return boss_path
    except Exception:
        pass
    
    # 尝试使用where命令（Windows）
    try:
        result = subprocess.run(
            ["where", "boss"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode == 0:
            boss_path = result.stdout.strip().split('\n')[0]
            print(f"✅ 通过where找到boss命令: {boss_path}")
            return boss_path
    except Exception:
        pass
    
    print("❌ 未找到boss命令")
    return None

def check_boss_working(boss_path):
    """检查boss命令是否工作正常"""
    if not boss_path:
        return False
    
    print(f"🔧 测试boss命令: {boss_path}")
    
    try:
        # 测试版本命令（最轻量）
        result = subprocess.run(
            [boss_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ boss命令工作正常: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ boss命令返回错误: {result.stderr[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ 执行boss命令失败: {e}")
        return False

def fix_export_tools(boss_path):
    """修复导出工具，添加boss命令路径"""
    if not boss_path:
        return False
    
    # 需要修复的文件列表
    files_to_fix = [
        "excel_export_with_description.py",
        "export_with_desc.py"
    ]
    
    print(f"\n🔧 修复导出工具...")
    
    for filename in files_to_fix:
        filepath = Path(__file__).parent / filename
        if not filepath.exists():
            print(f"⚠️  文件不存在: {filename}")
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找并替换boss命令调用
            old_patterns = [
                'cmd = f"boss',
                'cmd = f\'boss',
                'subprocess.run("boss',
                "subprocess.run('boss"
            ]
            
            modified = False
            for pattern in old_patterns:
                if pattern in content:
                    # 替换为使用完整路径
                    new_content = content.replace(
                        'cmd = f"boss',
                        f'cmd = f"{boss_path}'
                    ).replace(
                        "cmd = f'boss",
                        f"cmd = f'{boss_path}"
                    ).replace(
                        'subprocess.run("boss',
                        f'subprocess.run("{boss_path}'
                    ).replace(
                        "subprocess.run('boss",
                        f"subprocess.run('{boss_path}"
                    )
                    
                    if new_content != content:
                        content = new_content
                        modified = True
            
            if modified:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 已修复: {filename}")
            else:
                print(f"⚠️  无需修复: {filename}")
                
        except Exception as e:
            print(f"❌ 修复失败 {filename}: {e}")
    
    return True

def create_boss_wrapper(boss_path):
    """创建boss命令的包装脚本"""
    if not boss_path:
        return None
    
    wrapper_path = Path(__file__).parent / "boss_wrapper.py"
    
    wrapper_content = f'''#!/usr/bin/env python3
"""
boss命令包装器
确保导出工具能正确调用boss命令
"""

import os
import sys
import subprocess

# boss命令的完整路径
BOSS_PATH = "{boss_path}"

def run_boss_command(args, timeout=30):
    """运行boss命令"""
    cmd = [BOSS_PATH] + args
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8'
        )
        return result
    except Exception as e:
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=1,
            stdout="",
            stderr=f"执行失败: {{e}}"
        )

def get_job_description(job_id, security_id=None):
    """获取岗位描述（包装器函数）"""
    args = ["detail", job_id]
    if security_id:
        args.append(security_id)
    
    result = run_boss_command(args)
    if result.returncode == 0:
        return result.stdout
    else:
        return f"获取失败: {{result.stderr[:100]}}"

if __name__ == "__main__":
    # 可以直接运行boss命令
    if len(sys.argv) > 1:
        result = run_boss_command(sys.argv[1:])
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
'''
    
    try:
        with open(wrapper_path, 'w', encoding='utf-8') as f:
            f.write(wrapper_content)
        
        # 添加执行权限
        os.chmod(wrapper_path, 0o755)
        print(f"✅ 创建包装器: {wrapper_path}")
        return str(wrapper_path)
        
    except Exception as e:
        print(f"❌ 创建包装器失败: {e}")
        return None

def update_export_with_boss_wrapper(wrapper_path):
    """更新导出工具使用包装器"""
    if not wrapper_path:
        return False
    
    target_file = Path(__file__).parent / "excel_export_with_description.py"
    
    if not target_file.exists():
        print(f"❌ 目标文件不存在: {target_file}")
        return False
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换fetch_job_description方法
        old_method = '''
    def fetch_job_description(self, job_id: str, security_id: str = None) -> str:
        """
        获取岗位详细描述
        
        Args:
            job_id: 岗位ID (encryptJobId)
            security_id: 安全ID（可选）
        
        Returns:
            岗位描述文本
        """
        if not job_id:
            return "无法获取岗位ID"
            
        try:
            import subprocess
            
            # 使用boss-cli获取岗位详情
            cmd = f"boss detail {job_id}"
            if security_id:
                cmd = f"boss detail {job_id} {security_id}"
            
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                # 解析输出，提取岗位描述
                description = self._extract_description_from_output(result.stdout)
                return description if description else "未能获取详细描述"
            else:
                return f"获取失败: {result.stderr[:100]}"
                
        except Exception as e:
            return f"获取异常: {str(e)}"
'''
        
        new_method = f'''
    def fetch_job_description(self, job_id: str, security_id: str = None) -> str:
        """
        获取岗位详细描述
        
        Args:
            job_id: 岗位ID (encryptJobId)
            security_id: 安全ID（可选）
        
        Returns:
            岗位描述文本
        """
        if not job_id:
            return "无法获取岗位ID"
            
        try:
            # 使用boss包装器获取岗位详情
            wrapper_path = "{wrapper_path}"
            import subprocess
            import sys
            
            # 构建命令
            cmd = [sys.executable, wrapper_path, "detail", job_id]
            if security_id:
                cmd.append(security_id)
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                # 解析输出，提取岗位描述
                description = self._extract_description_from_output(result.stdout)
                return description if description else "未能获取详细描述"
            else:
                return f"获取失败: {{result.stderr[:100]}}"
                
        except Exception as e:
            return f"获取异常: {{str(e)}}"
'''
        
        if old_method in content:
            content = content.replace(old_method, new_method)
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已更新导出工具使用包装器")
            return True
        else:
            print(f"⚠️  未找到需要替换的方法")
            return False
            
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False

def main():
    print("🚀 修复boss命令路径问题")
    print("=" * 50)
    
    # 1. 查找boss命令
    boss_path = find_boss_command()
    
    if not boss_path:
        print("\n❌ 未找到boss命令，请先安装boss-cli:")
        print("python3 -m pip install --user git+https://github.com/zouzhifeng/boss-cli.git")
        return 1
    
    # 2. 检查boss命令是否工作
    if not check_boss_working(boss_path):
        print("\n❌ boss命令工作不正常，请检查安装")
        return 1
    
    # 3. 创建包装器
    print("\n📦 创建boss命令包装器...")
    wrapper_path = create_boss_wrapper(boss_path)
    
    if wrapper_path:
        # 4. 更新导出工具使用包装器
        print("\n🔄 更新导出工具...")
        if update_export_with_boss_wrapper(wrapper_path):
            print("✅ 导出工具已更新，现在使用包装器调用boss命令")
        else:
            print("⚠️  导出工具更新失败，将使用原始修复方式")
            # 回退到原始修复方式
            fix_export_tools(boss_path)
    else:
        print("⚠️  包装器创建失败，使用原始修复方式")
        fix_export_tools(boss_path)
    
    # 5. 创建环境变量设置脚本
    print("\n🌍 创建环境变量设置脚本...")
    env_script = Path(__file__).parent / "set_boss_env.sh"
    
    env_content = f'''#!/bin/bash
# 设置boss命令环境变量

# boss命令路径
export BOSS_PATH="{boss_path}"

# 添加到PATH
export PATH="{os.path.dirname(boss_path)}:$PATH"

# 测试boss命令
echo "BOSS_PATH: $BOSS_PATH"
echo "PATH中包含boss: {os.path.dirname(boss_path)}"
which boss || echo "boss命令未找到"
'''
    
    try:
        with open(env_script, 'w', encoding='utf-8') as f:
            f.write(env_content)
        os.chmod(env_script, 0o755)
        print(f"✅ 环境变量脚本: {env_script}")
        
        print(f"\n💡 使用前请设置环境变量:")
        print(f"  source {env_script}")
    except Exception as e:
        print(f"❌ 创建环境变量脚本失败: {e}")
    
    print("\n🎉 修复完成！")
    print("=" * 50)
    print(f"✅ boss命令路径: {boss_path}")
    if wrapper_path:
        print(f"✅ 包装器: {wrapper_path}")
    print(f"✅ 导出工具已修复")
    
    print(f"\n🔧 测试修复后的导出工具:")
    print(f"  python3 {Path(__file__).parent}/export_with_desc.py --help")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())