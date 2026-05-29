#!/bin/bash
# 设置boss命令环境变量

# boss命令路径
export BOSS_PATH="/Users/xingan/Library/Python/3.12/bin/boss"

# 添加到PATH
export PATH="/Users/xingan/Library/Python/3.12/bin:$PATH"

# 测试boss命令
echo "BOSS_PATH: $BOSS_PATH"
echo "PATH中包含boss: /Users/xingan/Library/Python/3.12/bin"
which boss || echo "boss命令未找到"
