#!/bin/bash

# 智能数据平台 - 快速部署脚本
# 用于快速在本地生成可分享的访问链接

echo "=========================================="
echo "智能数据平台 - 快速演示部署"
echo "=========================================="

# 检查ngrok是否安装
if ! command -v ngrok &> /dev/null; then
    echo "⚠️  ngrok未安装"
    echo ""
    echo "请选择安装方式:"
    echo "1. Homebrew (Mac):"
    echo "   brew install ngrok"
    echo ""
    echo "2. 下载安装:"
    echo "   访问 https://ngrok.com/download"
    echo ""
    exit 1
fi

# 启动后端服务
echo ""
echo "📦 步骤1: 启动后端服务..."
cd "$(dirname "$0")/backend"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install -r requirements.txt -q

# 启动主服务
echo "启动主服务 (端口8000)..."
python app.py > /dev/null 2>&1 &
MAIN_PID=$!
echo "主服务 PID: $MAIN_PID"

sleep 2

echo "✅ 后端服务启动成功!"

# 返回项目根目录
cd "$(dirname "$0")"

# 启动ngrok
echo ""
echo "📡 步骤2: 创建公网访问地址..."
echo ""

# 创建ngrok隧道
ngrok http 8000 --log=stdout &
NGROK_PID=$!

# 等待ngrok启动
sleep 3

echo ""
echo "=========================================="
echo "✅ 部署成功!"
echo "=========================================="
echo ""
echo "📍 访问地址已生成!"
echo ""
echo "请查看上面的ngrok输出,找到类似这样的地址:"
echo "   https://xxxx-xx-xx-xx-xx.ngrok-free.app"
echo ""
echo "📤 复制这个地址发给客户即可!"
echo ""
echo "🔑 登录信息:"
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "⏸️  按Ctrl+C停止服务"
echo "=========================================="
echo ""
echo "提示: ngrok免费版地址8小时内有效"
echo "      如需长期使用,请使用云服务器部署"
echo ""

# 保持脚本运行
trap "echo ''; echo '正在停止服务...'; kill $MAIN_PID $NGROK_PID 2>/dev/null; echo '服务已停止'; exit 0" INT TERM

while true; do
    sleep 1
done
