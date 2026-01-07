#!/bin/bash

# 智能数据平台 - 简化版部署脚本
# 无需ngrok,使用本地网络

echo "=========================================="
echo "🚀 智能数据平台 - 快速启动"
echo "=========================================="

# 进入项目目录
cd "$(dirname "$0")"

# 步骤1: 启动后端服务
echo ""
echo "📦 步骤1: 启动后端服务..."
echo ""

cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "检查并安装依赖..."
pip install fastapi uvicorn python-jose -q > /dev/null 2>&1

# 启动主服务
echo "启动主服务 (端口8000)..."
python app.py &
MAIN_PID=$!

sleep 2

echo "✅ 后端服务启动成功! (PID: $MAIN_PID)"

# 返回项目根目录
cd ..

# 步骤2: 显示访问信息
echo ""
echo "=========================================="
echo "✅ 服务启动成功!"
echo "=========================================="
echo ""
echo "📍 本地访问地址:"
echo "   http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "💡 前端访问:"
echo "   在浏览器中打开: frontend/login.html"
echo ""
echo "🔑 登录信息:"
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "=========================================="
echo ""
echo "📱 给客户看的方式:"
echo ""
echo "方案A - 本地演示:"
echo "   1. 确保客户和你在同一WiFi网络"
echo "   2. 查看你的IP地址:"
echo ""

# 获取本地IP
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
if [ ! -z "$LOCAL_IP" ]; then
    echo "   你的IP: $LOCAL_IP"
    echo "   3. 让客户访问: http://$LOCAL_IP:8000"
else
    echo "   无法自动获取IP,请手动查看:"
    echo "   系统设置 -> 网络"
fi

echo ""
echo "方案B - 使用ngrok (需要安装):"
echo "   1. 安装ngrok: 访问 https://ngrok.com/download"
echo "   2. 解压并运行: ./ngrok http 8000"
echo "   3. 复制显示的https地址发给客户"
echo ""
echo "方案C - 截图/录屏:"
echo "   1. 访问 http://localhost:8000"
echo "   2. 使用系统截图工具: Cmd+Shift+4"
echo "   3. 或使用QuickTime录屏"
echo ""
echo "=========================================="
echo ""
echo "⏸️  按Ctrl+C停止服务"
echo ""

# 保持脚本运行
trap "echo ''; echo '正在停止服务...'; kill $MAIN_PID 2>/dev/null; echo '服务已停止'; exit 0" INT TERM

while true; do
    sleep 1
done
