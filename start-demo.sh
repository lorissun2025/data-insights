#!/bin/bash

echo "=========================================="
echo "🚀 智能数据平台 - 演示启动脚本"
echo "=========================================="
echo ""

# 检查Node.js和npm
if command -v npm &> /dev/null; then
    echo "✅ 检测到npm,尝试使用localtunnel..."
    echo ""

    # 启动后端
    cd "$(dirname "$0")/backend"
    source venv/bin/activate

    echo "📦 启动后端服务..."
    python app.py > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "✅ 后端启动 (PID: $BACKEND_PID)"

    sleep 3

    # 检查后端是否启动成功
    if curl -s http://localhost:8000 > /dev/null; then
        echo "✅ 后端服务正常运行"
    else
        echo "❌ 后端启动失败,查看日志:"
        cat /tmp/backend.log
        exit 1
    fi

    # 安装并启动localtunnel
    echo ""
    echo "📡 安装localtunnel..."
    npm install -g localtunnel > /dev/null 2>&1

    if command -v lt &> /dev/null; then
        echo "✅ localtunnel安装成功"
        echo ""
        echo "=========================================="
        echo "🌐 创建公网访问地址..."
        echo "=========================================="
        echo ""

        # 启动localtunnel
        lt --port 8000 --subdomain data-insights-demo

    else
        echo "❌ localtunnel安装失败"
        echo ""
        echo "使用本地IP访问:"
        ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null
    fi

elif command -v node &> /dev/null; then
    echo "✅ 检测到Node.js,可以使用localtunnel"
    echo "请运行: npm install -g localtunnel"
    echo "然后运行: lt --port 8000"

else
    echo "⚠️  未检测到npm/Node.js"
    echo ""
    echo "📱 使用以下方案:"
    echo ""
    echo "方案1 - 局域网分享 (客户在同一WiFi):"
    LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
    if [ ! -z "$LOCAL_IP" ]; then
        echo "   客户访问: http://$LOCAL_IP:8000/docs"
    fi
    echo ""
    echo "方案2 - 手动下载ngrok:"
    echo "   1. 浏览器访问: https://ngrok.com/download"
    echo "   2. 下载Mac ARM版本"
    echo "   3. 解压后运行: ./ngrok http 8000"
    echo ""
    echo "方案3 - 录制演示视频:"
    echo "   按Cmd+Shift+5开始录屏"
fi

# 启动后端服务
cd "$(dirname "$0")/backend"
source venv/bin/activate

echo ""
echo "📦 启动后端服务..."
python app.py &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
echo ""
echo "=========================================="
echo "后端地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "=========================================="
echo ""
echo "按Ctrl+C停止服务"
echo ""

trap "kill $BACKEND_PID 2>/dev/null; echo '服务已停止'; exit 0" INT TERM

wait
