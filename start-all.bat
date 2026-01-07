@echo off
chcp 65001 >nul
title 智能数据平台 - 完整服务启动

echo ==========================================
echo 智能数据平台 - 完整服务启动
echo ==========================================

REM 进入后端目录
cd /d "%~dp0backend"

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 检查并安装依赖...
pip install -r requirements.txt -q

echo.
echo ==========================================
echo 启动所有后端服务...
echo ==========================================

REM 创建日志目录
if not exist "logs" mkdir logs

REM 启动主服务 (端口8000)
echo 启动主服务 (端口8000)...
start "Main Service" python app.py

timeout /t 2 /nobreak >nul

REM 启动供应链服务 (端口8001)
echo 启动供应链服务 (端口8001)...
start "Supply Chain Service" python supply_chain.py

timeout /t 2 /nobreak >nul

REM 启动医疗效能服务 (端口8002)
echo 启动医疗效能服务 (端口8002)...
start "Medical Performance Service" python medical_performance.py

timeout /t 2 /nobreak >nul

REM 启动高级预测服务 (端口8003)
echo 启动高级预测服务 (端口8003)...
start "Advanced Forecast Service" python advanced_forecast.py

timeout /t 2 /nobreak >nul

REM 启动数据导出服务 (端口8004)
echo 启动数据导出服务 (端口8004)...
start "Export Service" python export_api.py

echo.
echo ==========================================
echo ✅ 所有服务启动成功!
echo ==========================================
echo 主服务 (市场洞察):     http://localhost:8000
echo 供应链服务:           http://localhost:8001
echo 医疗效能服务:         http://localhost:8002
echo 高级预测服务:         http://localhost:8003
echo 数据导出服务:         http://localhost:8004
echo.
echo API文档: http://localhost:8000/docs
echo 测试账号: admin / admin123
echo.
echo 请在浏览器中访问: frontend\login.html
echo ==========================================
echo.
echo 按任意键退出启动脚本 (服务将继续在后台运行)
pause >nul
