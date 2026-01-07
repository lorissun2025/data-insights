@echo off
REM 智能数据平台启动脚本 (Windows)

echo ==========================================
echo 智能数据平台 启动中...
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

REM 启动后端服务
echo.
echo ==========================================
echo 后端服务启动中...
echo ==========================================
echo 后端地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo 测试账号: admin / admin123
echo ==========================================
echo.
echo 请在浏览器中访问: frontend\login.html
echo 按 Ctrl+C 停止服务
echo.

python app.py

pause
