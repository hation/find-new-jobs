#!/usr/bin/env python3
"""
boss命令包装器
确保导出工具能正确调用boss命令
"""

import os
import sys
import subprocess

# boss命令的完整路径
BOSS_PATH = "/Users/xingan/Library/Python/3.12/bin/boss"

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
            stderr=f"执行失败: {e}"
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
        return f"获取失败: {result.stderr[:100]}"

if __name__ == "__main__":
    # 可以直接运行boss命令
    if len(sys.argv) > 1:
        result = run_boss_command(sys.argv[1:])
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
