@echo off
chcp 65001 >nul
echo [36m🚀 夸克校园招聘API爬取器启动[0m
echo ==========================================

REM 检查Python环境
echo [33m🔍 检查Python环境...[0m
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Python未安装，请先安装Python3
        pause
        exit /b 1
    ) else (
        set PYTHON=python3
    )
) else (
    set PYTHON=python
)

echo ✅ Python环境正常

REM 获取脚本目录
set "SCRIPT_DIR=%~dp0"
echo 📁 项目目录: %SCRIPT_DIR%

REM 检查依赖
echo 🔍 检查Python依赖...
if exist "%SCRIPT_DIR%requirements.txt" (
    echo 📦 检查并安装依赖...
    %PYTHON% -m pip install -r "%SCRIPT_DIR%requirements.txt" --quiet
) else (
    echo ⚠️  未找到requirements.txt，跳过依赖检查
)

REM 检查配置文件
echo 🔧 检查配置文件...
if not exist "%SCRIPT_DIR%config.yaml" (
    echo ⚠️  未找到config.yaml，使用默认配置
    echo 💡 提示：可以创建config.yaml来自定义配置
)

REM 创建必要的目录
echo 📁 创建必要目录...
if not exist "%SCRIPT_DIR%output\positions" mkdir "%SCRIPT_DIR%output\positions"
if not exist "%SCRIPT_DIR%output\backups" mkdir "%SCRIPT_DIR%output\backups"
if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs"

REM 运行主程序
echo ==========================================
echo 📋 使用智能选择器：默认API优先，支持切换到浏览器模式
echo 💡 如需强制模式，请使用:
echo    --force-api     强制使用API模式
echo    --force-browser 强制使用浏览器模式
echo    --mode mixed    混合模式
echo ==========================================
echo 🚀 启动智能爬取系统...

cd /d "%SCRIPT_DIR%"
%PYTHON% scripts\main.py %*

REM 检查执行结果
if errorlevel 1 (
    echo ==========================================
    echo ❌ 执行失败，请检查日志
    echo 📄 查看日志: %SCRIPT_DIR%logs\quark_crawler_*.log
    echo ==========================================
    pause
    exit /b 1
) else (
    echo ==========================================
    echo ✅ 执行成功！
    echo 📁 数据保存在: %SCRIPT_DIR%output\positions\
    echo 📄 日志保存在: %SCRIPT_DIR%logs\
    echo ==========================================
)

pause