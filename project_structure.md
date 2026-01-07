# 市场洞察模块 - 项目结构

## 完整项目目录结构

```
pharma-market-insights/
├── backend/                        # 后端服务 (Python/FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI应用入口
│   │   ├── config.py               # 配置管理
│   │   ├── dependencies.py         # 依赖注入
│   │   │
│   │   ├── api/                    # API路由
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── market.py       # 市场分析相关接口
│   │   │   │   ├── forecast.py     # 销售预测相关接口
│   │   │   │   ├── opportunity.py  # 机会识别相关接口
│   │   │   │   ├── price.py        # 价格分析相关接口
│   │   │   │   ├── customer.py     # 客户洞察相关接口
│   │   │   │   └── dashboard.py    # 仪表盘相关接口
│   │   │   └── dependencies.py
│   │   │
│   │   ├── core/                   # 核心业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── market_analysis.py  # 市场分析算法
│   │   │   ├── forecasting.py      # 预测算法
│   │   │   ├── opportunity.py      # 机会识别算法
│   │   │   ├── price_analysis.py   # 价格分析算法
│   │   │   └── customer_insights.py # 客户洞察算法
│   │   │
│   │   ├── models/                 # 数据模型 (Pydantic)
│   │   │   ├── __init__.py
│   │   │   ├── market.py
│   │   │   ├── forecast.py
│   │   │   └── user.py
│   │   │
│   │   ├── db/                     # 数据库相关
│   │   │   ├── __init__.py
│   │   │   ├── clickhouse.py       # ClickHouse连接
│   │   │   ├── redis.py            # Redis连接
│   │   │   └── migrations/         # 数据库迁移脚本
│   │   │
│   │   ├── services/               # 服务层
│   │   │   ├── __init__.py
│   │   │   ├── data_service.py     # 数据服务
│   │   │   ├── cache_service.py    # 缓存服务
│   │   │   └── ml_service.py       # 机器学习服务
│   │   │
│   │   ├── utils/                  # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── date_utils.py
│   │   │   └── logger.py
│   │   │
│   │   └── tests/                  # 单元测试
│   │       ├── __init__.py
│   │       ├── test_api.py
│   │       └── test_forecasting.py
│   │
│   ├── requirements.txt            # Python依赖
│   ├── Dockerfile                  # Docker镜像
│   └── .env.example                # 环境变量示例
│
├── frontend/                       # 前端应用 (React + TypeScript)
│   ├── src/
│   │   ├── components/             # 公共组件
│   │   │   ├── KPICard.tsx
│   │   │   ├── DateRangePicker.tsx
│   │   │   └── Charts/
│   │   │       ├── SalesTrendChart.tsx
│   │   │       ├── MarketShareChart.tsx
│   │   │       └── RegionalMapChart.tsx
│   │   │
│   │   ├── pages/                  # 页面组件
│   │   │   ├── Dashboard.tsx       # 仪表盘主页
│   │   │   ├── MarketAnalysis.tsx  # 市场分析页
│   │   │   ├── Forecast.tsx        # 销售预测页
│   │   │   ├── Opportunity.tsx     # 机会识别页
│   │   │   ├── PriceAnalysis.tsx   # 价格分析页
│   │   │   └── CustomerInsights.tsx # 客户洞察页
│   │   │
│   │   ├── services/               # API服务
│   │   │   ├── api.ts             # Axios配置
│   │   │   ├── marketService.ts
│   │   │   └── forecastService.ts
│   │   │
│   │   ├── hooks/                  # 自定义Hooks
│   │   │   ├── useDashboardData.ts
│   │   │   └── useChartData.ts
│   │   │
│   │   ├── types/                  # TypeScript类型定义
│   │   │   ├── market.ts
│   │   │   └── forecast.ts
│   │   │
│   │   ├── utils/                  # 工具函数
│   │   │   ├── format.ts
│   │   │   └── chartOptions.ts
│   │   │
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── index.css
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── .env.example
│
├── ml/                            # 机器学习模型
│   ├── models/                     # 训练好的模型
│   │   ├── sales_forecast_arima.pkl
│   │   └── sales_forecast_xgboost.pkl
│   ├── notebooks/                  # Jupyter notebooks
│   │   ├── exploratory_analysis.ipynb
│   │   └── model_training.ipynb
│   ├── src/
│   │   ├── train_forecast_model.py
│   │   ├── train_anomaly_detection.py
│   │   └── predict.py
│   └── requirements.txt
│
├── infrastructure/                 # 基础设施配置
│   ├── docker-compose.yml          # Docker编排
│   ├── kubernetes/                 # K8s配置
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── terraform/                  # 基础设施即代码
│   └── airflow/                    # Airflow DAGs
│       └── dags/
│           ├── data_ingestion_dag.py
│           └── forecast_training_dag.py
│
├── data/                          # 数据脚本
│   ├── sql/                       # SQL脚本
│   │   ├── create_tables.sql
│   │   └── seed_data.sql
│   └── etl/                       # ETL脚本
│       ├── extract_sales_data.py
│       └── transform_data.py
│
├── docs/                          # 文档
│   ├── API.md                     # API文档
│   ├── DEPLOYMENT.md              # 部署文档
│   └── USER_GUIDE.md              # 用户手册
│
├── .gitignore
├── README.md
└── docker-compose.yml
```

## 快速启动

### 1. 使用Docker Compose启动

```bash
# 克隆项目
git clone https://github.com/your-org/pharma-market-insights.git
cd pharma-market-insights

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 2. 本地开发

#### 后端启动

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动FastAPI服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

#### ClickHouse启动

```bash
# Docker方式
docker run -d \
  --name clickhouse-server \
  -p 8123:8123 \
  -p 9000:9000 \
  --ulimit nofile=262144:262144 \
  clickhouse/clickhouse-server:latest

# 或使用brew安装 (macOS)
brew install clickhouse
brew services start clickhouse
```

## 环境变量配置

### backend/.env

```env
# ClickHouse配置
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=pharma_insights

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# API配置
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# 机器学习配置
ML_MODEL_PATH=/app/models
FORECAST_MODEL_TYPE=prophet

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/pharma-insights/app.log
```

### frontend/.env

```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENABLE_MOCK=false
```

## 依赖版本

### backend/requirements.txt

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
clickhouse-connect==0.6.23
redis==5.0.1
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
statsmodels==0.14.0
prophet==1.1.4
xgboost==2.0.2
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
celery==5.3.4
```

### frontend/package.json

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "antd": "^5.12.0",
    "echarts": "^5.4.3",
    "echarts-for-react": "^3.0.2",
    "axios": "^1.6.2",
    "dayjs": "^1.11.10",
    "lodash": "^4.17.21",
    "@types/react": "^18.2.42",
    "@types/react-dom": "^18.2.17",
    "typescript": "^5.3.2"
  }
}
```
