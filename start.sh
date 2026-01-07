#!/bin/bash

# 智能数据平台启动脚本

echo "=========================================="
echo "智能数据平台 启动中..."
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3,请先安装 Python3"
    exit 1
fi

# 进入后端目录
cd "$(dirname "$0")/backend"

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
pip install -r requirements.txt -q

# 启动后端服务
echo ""
echo "=========================================="
echo "后端服务启动中..."
echo "=========================================="
echo "后端地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "测试账号: admin / admin123"
echo "=========================================="
echo ""
echo "请在浏览器中访问: frontend/login.html"
echo "按 Ctrl+C 停止服务"
echo ""

python app.py
