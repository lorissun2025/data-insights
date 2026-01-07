# 快速启动指南

## 一键启动

### Mac/Linux 用户:
```bash
cd "/Users/sunsensen/claude code/智能数据平台"
./start.sh
```

### Windows 用户:
```bash
cd "C:\Users\sunsensen\claude code\智能数据平台"
start.bat
```

## 启动后访问

1. 等待后端服务启动(看到 "Uvicorn running on http://0.0.0.0:8000")

2. 在浏览器中访问:
   - **登录页面**: [frontend/login.html](frontend/login.html)
   - 或直接打开: [frontend/index.html](frontend/index.html) (自动跳转)

3. 使用测试账号登录:
   - 用户名: `admin`
   - 密码: `admin123`

## 访问各模块

登录后可访问以下页面:

- **市场洞察**: [dashboard.html](frontend/dashboard.html) - 主仪表盘
- **竞品分析**: [competitor.html](frontend/competitor.html)
- **销售预测**: [forecast.html](frontend/forecast.html)
- **客户洞察**: [customer.html](frontend/customer.html)
- **价格分析**: [price.html](frontend/price.html)

## API文档

后端启动后访问:
- Swagger文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc

## 注意事项

1. 首次运行会自动创建虚拟环境并安装依赖,可能需要几分钟
2. 确保端口8000未被占用
3. Token有效期24小时,过期后需重新登录
4. 所有页面采用深色科技风格设计

## 停止服务

在终端按 `Ctrl + C` 停止后端服务

## 技术支持

如有问题,请查看 [README.md](README.md) 获取更多信息
