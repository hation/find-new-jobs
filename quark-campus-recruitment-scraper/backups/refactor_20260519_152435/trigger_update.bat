@echo off
REM 夸克招聘爬取更新触发器 (Windows版本)
REM 手动触发更新检查清单和错误教训记录

echo =========================================
echo 🔄 夸克招聘爬取系统更新触发器
echo =========================================

REM 配置路径
set WORKSPACE_ROOT=%USERPROFILE%\.openclaw\workspace
set SKILL_DIR=%WORKSPACE_ROOT%\skills\quark-campus-recruitment-scraper
set SCRIPTS_DIR=%SKILL_DIR%\scripts

REM 1. 检查环境
echo.
echo 步骤1: 检查环境
if not exist "%SCRIPTS_DIR%" (
    echo ❌ 错误: 脚本目录不存在: %SCRIPTS_DIR%
    pause
    exit /b 1
)

cd /d "%SCRIPTS_DIR%" || (
    echo ❌ 错误: 无法进入脚本目录
    pause
    exit /b 1
)

REM 2. 检查Python环境
echo.
echo 步骤2: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ 错误: 未找到Python命令
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

for /f "tokens=*" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set "PYTHON_VERSION=%%v"
echo ✅ Python版本: %PYTHON_VERSION%

REM 3. 选择更新模式
echo.
echo 📋 选择更新模式:
echo 1. 快速更新 (只更新检查清单)
echo 2. 完整更新 (更新检查清单和错误教训)
echo 3. 分析模式 (生成分析报告)
echo 4. 全面模式 (运行所有更新和分析)
echo.

set /p mode="请选择模式 (1-4): "

if "%mode%"=="1" goto quick_update
if "%mode%"=="2" goto full_update
if "%mode%"=="3" goto analysis_mode
if "%mode%"=="4" goto comprehensive_mode

echo ❌ 错误: 无效的选择: %mode%
pause
exit /b 1

:quick_update
echo.
echo 执行快速更新模式
echo.
%PYTHON_CMD% error_detector.py
echo.
echo 快速更新完成
goto :show_status

:full_update
echo.
echo 执行完整更新模式
echo.
%PYTHON_CMD% error_detector.py
echo.
echo 错误检测完成，开始更新文件...
echo.

REM 检查错误报告
if exist "..\error_report.txt" (
    echo 📄 错误报告:
    type "..\error_report.txt"
    echo.
)

REM 备份检查清单
if exist "..\CHECKLIST.md" (
    set "timestamp=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
    set "timestamp=%timestamp: =0%"
    copy "..\CHECKLIST.md" "..\CHECKLIST.md.backup.%timestamp%" >nul
    echo ✅ 已备份检查清单
)

REM 备份错误教训记录
if exist "..\LESSONS_LEARNED.md" (
    set "timestamp=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
    set "timestamp=%timestamp: =0%"
    copy "..\LESSONS_LEARNED.md" "..\LESSONS_LEARNED.md.backup.%timestamp%" >nul
    echo ✅ 已备份错误教训记录
)

REM 运行自动更新
start /B %PYTHON_CMD% auto_updater.py
echo 🔄 更新进程已在后台启动
goto :show_status

:analysis_mode
echo.
echo 执行分析模式
echo.
%PYTHON_CMD% error_detector.py
echo.

REM 生成分析报告
set "timestamp=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "timestamp=%timestamp: =0%"
set "REPORT_FILE=..\analysis_report_%timestamp%.md"

(
echo # 夸克招聘爬取系统分析报告
echo 生成时间: %date% %time%
echo.
echo ## 📊 系统状态
echo.
echo ### 文件状态
) > "%REPORT_FILE%"

REM 检查文件状态
for %%f in ("..\CHECKLIST.md" "..\LESSONS_LEARNED.md" "..\errors_database.json") do (
    if exist %%~f (
        for %%s in (%%~f) do set "size=%%~zs"
        set /a "size_kb=(size+1023)/1024"
        echo - **%%~nxf**: !size_kb!KB, 最后修改: %%~tf >> "%REPORT_FILE%"
    ) else (
        echo - **%%~nxf**: 不存在 >> "%REPORT_FILE%"
    )
)

(
echo.
echo ### 执行统计
echo - 触发时间: %date% %time%
echo - 更新模式: 分析模式
echo - 脚本目录: %SCRIPTS_DIR%
echo.
echo ## 🎯 建议
echo.
echo ### 立即行动
echo 1. 检查所有备份文件
echo 2. 验证检查清单完整性
echo 3. 更新错误教训记录中的统计信息
echo.
echo ### 长期改进
echo 1. 实现自动错误检测
echo 2. 建立定期更新机制
echo 3. 优化错误预防策略
) >> "%REPORT_FILE%"

echo ✅ 分析报告已生成: %REPORT_FILE%
echo.
echo 📄 报告内容摘要:
type "%REPORT_FILE%" | findstr /C:"#" /C:"-" /C:"建议"
goto :show_status

:comprehensive_mode
echo.
echo 执行全面模式
echo.

REM 运行全面更新
start %PYTHON_CMD% auto_updater.py --full
echo 🚀 全面更新进程已启动
echo.
echo 📋 全面更新将执行以下任务:
echo 1. 错误检测与分析
echo 2. 检查清单更新
echo 3. 错误教训记录更新
echo 4. 生成详细分析报告
echo 5. 建立更新历史记录
echo.
echo 🔄 更新将在后台运行，请查看日志文件:
echo    - auto_updater.log (更新日志)
echo    - error_report.txt (错误报告)
echo    - analysis_report.md (分析报告)
echo.
echo 🔍 监控命令:
echo tail -f auto_updater.log
echo tail -f ..\error_report.txt
echo.
echo ✅ 全面更新已启动
goto :show_status

:show_status
echo.
echo =========================================
echo 🎯 更新触发器执行完成
echo =========================================

REM 显示更新后的文件状态
echo.
echo 📁 更新后文件状态:
echo ------------------

for %%f in ("..\CHECKLIST.md" "..\LESSONS_LEARNED.md") do (
    if exist %%~f (
        for %%s in (%%~f) do set "size=%%~zs"
        set /a "size_kb=(size+1023)/1024"
        for /f "usebackq tokens=1,2*" %%a in ("%%~f") do set /a "lines=%%a"
        echo %%~nxf: !size_kb!KB, !lines! 行
    )
)

REM 检查备份文件
set "backup_count=0"
for /f %%c in ('dir /b "..\*.backup.*" 2^>nul ^| find /c /v ""') do set "backup_count=%%c"

if %backup_count% gtr 0 (
    echo.
    echo 💾 备份文件: %backup_count% 个
    dir /b "..\*.backup.*" | findstr /v "^$" | head -5
    if %backup_count% gtr 5 (
        set /a "remaining=%backup_count% - 5"
        echo ... 还有 %remaining% 个
    )
)

echo.
echo 🚀 下次更新:
echo 1. 手动运行: trigger_update.bat
echo 2. 定时运行: 添加到计划任务
echo 3. 自动运行: 使用 auto_updater.py 调度器
echo =========================================

pause