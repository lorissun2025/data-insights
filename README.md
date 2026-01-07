# 智能数据平台 - 医药市场洞察系统

一个基于 FastAPI + Vue.js 的医药市场数据分析和可视化平台。

## 功能特性

- **登录认证**: JWT Token 认证机制
- **市场洞察仪表盘**: KPI指标、销售趋势、市场份额分析
- **竞品分析**: 多维度竞品对比、区域市场表现
- **销售预测**: AI模型预测、准确率评估
- **客户洞察**: 医院客户画像、RFM分层
- **价格分析**: 价格趋势、弹性系数分析

## 技术栈

### 后端
- FastAPI: Web框架
- JWT: 用户认证
- Pydantic: 数据验证

### 前端
- Vue.js 3: 前端框架
- ECharts 5: 数据可视化
- Axios: HTTP客户端

## 快速开始

### 方式一: 使用启动脚本 (推荐)

**Mac/Linux:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

### 方式二: 手动启动

**1. 安装依赖**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. 启动后端服务**
```bash
python backend/app.py
```

后端服务将在 http://localhost:8000 启动

**3. 访问前端**

在浏览器中打开: `frontend/login.html`

## 测试账号

- 用户名: `admin`
- 密码: `admin123`

## 项目结构

```
智能数据平台/
├── backend/
│   ├── app.py              # FastAPI应用
│   └── requirements.txt    # Python依赖
├── frontend/
│   ├── login.html          # 登录页面
│   ├── dashboard.html      # 市场洞察仪表盘
│   ├── competitor.html     # 竞品分析
│   ├── forecast.html       # 销售预测
│   ├── customer.html       # 客户洞察
│   ├── price.html          # 价格分析
│   └── styles.css          # 公共样式
├── start.sh                # Linux/Mac启动脚本
├── start.bat               # Windows启动脚本
└── README.md               # 项目说明
```

## API文档

启动后端服务后,访问: http://localhost:8000/docs

## 主要模块说明

### 1. 市场洞察仪表盘
- 总销售额、销售量、市场份额、覆盖医院数
- 销售趋势分析(折线图+柱状图)
- 市场份额变化(堆叠面积图)
- 竞品综合对比(雷达图)
- 区域市场表现(散点图)
- AI推荐市场机会

### 2. 竞品分析
- 竞品雷达图对比
- 区域市场表现
- 竞品列表及市场份额

### 3. 销售预测
- 销售趋势预测(含置信区间)
- 多模型准确率对比(ARIMA、Prophet、XGBoost)

### 4. 客户洞察
- 客户分层分布(饼图)
- 重点医院客户列表

### 5. 价格分析
- 价格趋势对比
- 价格弹性分析

## 设计风格

采用深色科技风格,体现数据公司的专业感和炫酷感:
- 深空蓝背景 (#0a0e27)
- 蓝紫渐变主色调
- 玻璃拟态效果(Glassmorphism)
- 霓虹发光效果
- 流畅的动画过渡

## 开发说明

### 添加新接口
在 `backend/app.py` 中添加新的路由和数据处理逻辑。

### 修改样式
所有页面共享 `frontend/styles.css`,可以在各页面中添加自定义样式。

### 数据模拟
当前使用模拟数据,实际项目需要:
1. 连接真实数据库(如ClickHouse)
2. 替换 `backend/app.py` 中的模拟数据函数
3. 根据实际数据结构调整前端展示

## 注意事项

1. Token有效期为24小时,过期后需重新登录
2. 所有API请求需要在Header中携带: `Authorization: Bearer <token>`
3. 前端默认连接 `http://localhost:8000`,如需修改请编辑HTML文件中的 `API_BASE`

## 许可证

MIT License
