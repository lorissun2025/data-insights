#!/bin/bash

# 智能数据平台 - 统一启动脚本
# 启动所有后端服务

echo "=========================================="
echo "智能数据平台 - 完整服务启动"
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

echo ""
echo "=========================================="
echo "启动所有后端服务..."
echo "=========================================="

# 创建日志目录
mkdir -p logs

# 启动主服务 (端口8000) - 市场洞察、竞品、预测、客户、价格
echo "启动主服务 (端口8000)..."
python app.py > logs/main.log 2>&1 &
MAIN_PID=$!
echo "主服务 PID: $MAIN_PID"

sleep 2

# 启动供应链服务 (端口8001)
echo "启动供应链服务 (端口8001)..."
python supply_chain.py > logs/supply_chain.log 2>&1 &
SUPPLY_PID=$!
echo "供应链服务 PID: $SUPPLY_PID"

sleep 2

# 启动医疗效能服务 (端口8002)
echo "启动医疗效能服务 (端口8002)..."
python medical_performance.py > logs/medical.log 2>&1 &
MEDICAL_PID=$!
echo "医疗效能服务 PID: $MEDICAL_PID"

sleep 2

# 启动高级预测服务 (端口8003)
echo "启动高级预测服务 (端口8003)..."
python advanced_forecast.py > logs/forecast.log 2>&1 &
FORECAST_PID=$!
echo "高级预测服务 PID: $FORECAST_PID"

sleep 2

# 启动数据导出服务 (端口8004)
echo "启动数据导出服务 (端口8004)..."
python export_api.py > logs/export.log 2>&1 &
EXPORT_PID=$!
echo "数据导出服务 PID: $EXPORT_PID"

echo ""
echo "=========================================="
echo "✅ 所有服务启动成功!"
echo "=========================================="
echo "主服务 (市场洞察):     http://localhost:8000"
echo "供应链服务:           http://localhost:8001"
echo "医疗效能服务:         http://localhost:8002"
echo "高级预测服务:         http://localhost:8003"
echo "数据导出服务:         http://localhost:8004"
echo ""
echo "API文档: http://localhost:8000/docs"
echo "测试账号: admin / admin123"
echo ""
echo "请在浏览器中访问: frontend/login.html"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "=========================================="

# 等待用户中断
trap "echo ''; echo '正在停止所有服务...'; kill $MAIN_PID $SUPPLY_PID $MEDICAL_PID $FORECAST_PID $EXPORT_PID 2>/dev/null; echo '所有服务已停止'; exit 0" INT TERM

# 保持脚本运行
while true; do
    sleep 1
done
