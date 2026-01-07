"""
智能数据平台 - 后端服务
FastAPI + JWT认证 + 模拟数据
"""

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta, date
import jwt
import uvicorn
import random
import json
from enum import Enum

# JWT配置
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

app = FastAPI(
    title="智能数据平台 API",
    description="医药市场洞察数据平台",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全认证
security = HTTPBearer()

# ============================================
# 数据模型
# ============================================

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: dict

class KPIMetric(BaseModel):
    title: str
    value: float
    unit: str
    growth: float
    trend: str  # 'up' or 'down'

class TrendData(BaseModel):
    month: str
    sales: float
    quantity: float

class CompetitorData(BaseModel):
    name: str
    market_share: float
    growth: float
    price: float

class OpportunityData(BaseModel):
    region: str
    city: str
    market_size: float
    growth_rate: float
    competitor_count: int
    penetration_rate: float
    score: float
    level: str

# ============================================
# 认证功能
# ============================================

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭证",
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期,请重新登录",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
        )

# ============================================
# API接口
# ============================================

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录

    测试账号: admin / admin123
    """
    # 验证用户名和密码
    if request.username == "admin" and request.password == "admin123":
        user_info = {
            "username": "admin",
            "full_name": "系统管理员",
            "role": "admin",
            "permissions": ["dashboard", "market", "competitor", "forecast", "customer", "price"]
        }

        access_token = create_access_token(
            data={"sub": request.username, "user_info": user_info}
        )

        return LoginResponse(
            access_token=access_token,
            user_info=user_info
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

@app.get("/api/auth/verify")
async def verify_auth(current_user: str = Depends(verify_token)):
    """验证Token有效性"""
    return {"valid": True, "username": current_user}

# ============================================
# 仪表盘数据
# ============================================

@app.get("/api/dashboard/kpi")
async def get_dashboard_kpi(current_user: str = Depends(verify_token)):
    """获取仪表盘KPI数据"""
    kpis = [
        {
            "title": "总销售额",
            "value": 128560,
            "unit": "万元",
            "growth": 15.8,
            "trend": "up"
        },
        {
            "title": "总销售量",
            "value": 8520,
            "unit": "万盒",
            "growth": 12.3,
            "trend": "up"
        },
        {
            "title": "市场份额",
            "value": 23.5,
            "unit": "%",
            "growth": 2.1,
            "trend": "up"
        },
        {
            "title": "覆盖医院数",
            "value": 3256,
            "unit": "家",
            "growth": -1.5,
            "trend": "down"
        }
    ]
    return {"data": kpis}

@app.get("/api/dashboard/sales-trend")
async def get_sales_trend(current_user: str = Depends(verify_token)):
    """获取销售趋势数据"""
    months = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06',
              '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12']

    data = {
        "months": months,
        "sales": [8500, 9200, 9800, 10500, 11200, 12000, 11500, 12200, 12800, 13500, 14200, 14800],
        "quantity": [580, 620, 680, 720, 780, 820, 790, 850, 890, 920, 960, 1000],
        "forecast": [None, None, None, None, None, None, None, None, None, None, 14200, 14800, 15500, 16200, 17000]
    }
    return data

@app.get("/api/dashboard/market-share")
async def get_market_share_trend(current_user: str = Depends(verify_token)):
    """获取市场份额趋势"""
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    data = {
        "quarters": quarters,
        "series": [
            {"name": "本公司", "data": [22, 23, 23.5, 24]},
            {"name": "竞品A", "data": [28, 27, 26.5, 26]},
            {"name": "竞品B", "data": [18, 19, 20, 21]},
            {"name": "其他", "data": [32, 31, 30, 29]}
        ]
    }
    return data

@app.get("/api/dashboard/opportunities")
async def get_opportunities(current_user: str = Depends(verify_token)):
    """获取市场机会数据"""
    opportunities = [
        {"region": "华东", "city": "杭州", "market_size": 8520, "growth_rate": 28.5, "competitor_count": 12, "penetration_rate": 35, "score": 92, "level": "高潜力"},
        {"region": "华南", "city": "深圳", "market_size": 12850, "growth_rate": 32.1, "competitor_count": 18, "penetration_rate": 42, "score": 88, "level": "高潜力"},
        {"region": "西南", "city": "成都", "market_size": 6580, "growth_rate": 24.3, "competitor_count": 8, "penetration_rate": 28, "score": 85, "level": "高潜力"},
        {"region": "华东", "city": "南京", "market_size": 9250, "growth_rate": 18.6, "competitor_count": 25, "penetration_rate": 55, "score": 72, "level": "中等"},
        {"region": "华北", "city": "天津", "market_size": 7820, "growth_rate": 15.2, "competitor_count": 32, "penetration_rate": 68, "score": 58, "level": "中等"},
        {"region": "华中", "city": "武汉", "market_size": 8950, "growth_rate": 12.8, "competitor_count": 38, "penetration_rate": 72, "score": 45, "level": "低"}
    ]
    return {"data": opportunities}

# ============================================
# 竞品分析
# ============================================

@app.get("/api/competitor/comparison")
async def get_competitor_comparison(current_user: str = Depends(verify_token)):
    """获取竞品对比数据"""
    data = {
        "indicators": ["市场份额", "增长率", "价格竞争力", "市场覆盖率", "客户满意度", "品牌影响力"],
        "series": [
            {
                "name": "本公司",
                "value": [85, 42, 78, 90, 82, 75]
            },
            {
                "name": "竞品A",
                "value": [92, 28, 65, 85, 78, 88]
            },
            {
                "name": "竞品B",
                "value": [75, 35, 82, 70, 85, 68]
            }
        ]
    }
    return data

@app.get("/api/competitor/regional")
async def get_competitor_regional(current_user: str = Depends(verify_token)):
    """获取区域竞品表现"""
    data = {
        "provinces": ['广东', '江苏', '浙江', '山东', '河南', '四川', '湖北', '福建', '湖南', '安徽'],
        "data": [
            ['广东', 3, 14800, 32],
            ['江苏', 2, 13200, 28],
            ['浙江', 2, 11500, 26],
            ['山东', 2, 10800, 22],
            ['河南', 1, 9200, 35],
            ['四川', 2, 8900, 30],
            ['湖北', 1, 8500, 28],
            ['福建', 1, 7800, 25],
            ['湖南', 1, 7200, 20],
            ['安徽', 1, 6800, 18]
        ]
    }
    return data

@app.get("/api/competitor/list")
async def get_competitor_list(current_user: str = Depends(verify_token)):
    """获取竞品列表"""
    competitors = [
        {"id": "comp001", "name": "竞品A制药", "market_share": 28.5, "growth": -3.2, "products": 15},
        {"id": "comp002", "name": "竞品B药业", "market_share": 21.3, "growth": 5.8, "products": 12},
        {"id": "comp003", "name": "竞品C医药", "market_share": 18.9, "growth": 8.5, "products": 9},
        {"id": "comp004", "name": "竞品D生物", "market_share": 15.2, "growth": -1.2, "products": 8},
        {"id": "comp005", "name": "竞品E制药", "market_share": 12.6, "growth": 12.3, "products": 6}
    ]
    return {"data": competitors}

# ============================================
# 销售预测
# ============================================

@app.get("/api/forecast/trend")
async def get_forecast_trend(current_user: str = Depends(verify_token)):
    """获取销售预测趋势"""
    months = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06',
              '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12',
              '2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06']

    data = {
        "months": months,
        "actual": [8500, 9200, 9800, 10500, 11200, 12000, 11500, 12200, 12800, 13500, 14200, 14800] + [None] * 6,
        "forecast": [None] * 9 + [13200, 13800, 14500, 15200, 15800, 16500, 17200, 17800, 18500],
        "lower_bound": [None] * 9 + [12500, 13000, 13600, 14200, 14800, 15400, 16000, 16600, 17200],
        "upper_bound": [None] * 9 + [13900, 14600, 15400, 16200, 16800, 17600, 18400, 19000, 19800]
    }
    return data

@app.get("/api/forecast/accuracy")
async def get_forecast_accuracy(current_user: str = Depends(verify_token)):
    """获取预测准确率"""
    data = {
        "models": [
            {"name": "ARIMA", "mape": 8.5, "rmse": 1250, "mae": 980},
            {"name": "Prophet", "mape": 7.2, "rmse": 1100, "mae": 850},
            {"name": "XGBoost", "mape": 6.8, "rmse": 1050, "mae": 820}
        ]
    }
    return data

# ============================================
# 客户洞察
# ============================================

@app.get("/api/customer/hospitals")
async def get_hospital_list(current_user: str = Depends(verify_token)):
    """获取医院客户列表"""
    hospitals = [
        {"id": "hosp001", "name": "北京协和医院", "level": "三甲", "province": "北京", "purchases": 1258, "amount": 5820},
        {"id": "hosp002", "name": "上海瑞金医院", "level": "三甲", "province": "上海", "purchases": 1156, "amount": 5230},
        {"id": "hosp003", "name": "广州中山医院", "level": "三甲", "province": "广东", "purchases": 1089, "amount": 4890},
        {"id": "hosp004", "name": "成都华西医院", "level": "三甲", "province": "四川", "purchases": 1024, "amount": 4560},
        {"id": "hosp005", "name": "武汉同济医院", "level": "三甲", "province": "湖北", "purchases": 956, "amount": 4120},
        {"id": "hosp006", "name": "西安西京医院", "level": "三甲", "province": "陕西", "purchases": 890, "amount": 3850},
        {"id": "hosp007", "name": "杭州市第一医院", "level": "三甲", "province": "浙江", "purchases": 785, "amount": 3240},
        {"id": "hosp008", "name": "南京市鼓楼医院", "level": "三甲", "province": "江苏", "purchases": 756, "amount": 3080}
    ]
    return {"data": hospitals}

@app.get("/api/customer/segmentation")
async def get_customer_segmentation(current_user: str = Depends(verify_token)):
    """获取客户分层分布"""
    data = {
        "segments": [
            {"name": "高价值客户", "count": 156, "amount": 25680, "color": "#3b82f6"},
            {"name": "主力客户", "count": 423, "amount": 48520, "color": "#8b5cf6"},
            {"name": "潜力客户", "count": 689, "amount": 18920, "color": "#06b6d4"},
            {"name": "低价值客户", "count": 1205, "amount": 8960, "color": "#64748b"}
        ]
    }
    return data

# ============================================
# 价格分析
# ============================================

@app.get("/api/price/trend")
async def get_price_trend(current_user: str = Depends(verify_token)):
    """获取价格趋势"""
    months = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06',
              '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12']

    data = {
        "months": months,
        "series": [
            {"name": "本公司", "data": [45.2, 45.5, 45.3, 45.8, 46.2, 46.5, 46.8, 47.2, 47.5, 47.8, 48.2, 48.5]},
            {"name": "竞品A", "data": [48.5, 48.2, 47.8, 47.5, 47.2, 46.8, 46.5, 46.2, 45.8, 45.5, 45.2, 45.0]},
            {"name": "竞品B", "data": [42.8, 43.2, 43.5, 43.8, 44.2, 44.5, 44.8, 45.2, 45.5, 45.8, 46.2, 46.5]},
            {"name": "市场平均", "data": [45.5, 45.6, 45.5, 45.7, 45.9, 46.0, 46.1, 46.3, 46.4, 46.5, 46.6, 46.7]}
        ]
    }
    return data

@app.get("/api/price/elasticity")
async def get_price_elasticity(current_user: str = Depends(verify_token)):
    """获取价格弹性分析"""
    data = {
        "products": [
            {"name": "阿莫西林胶囊", "elasticity": -1.25, "interpretation": "需求弹性较大,降价可显著提升销量"},
            {"name": "布洛芬缓释胶囊", "elasticity": -0.85, "interpretation": "需求弹性适中,价格调整需谨慎"},
            {"name": "奥美拉唑肠溶胶囊", "elasticity": -0.65, "interpretation": "需求弹性较小,品牌忠诚度高"}
        ]
    }
    return data

# ============================================
# 启动服务器
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("智能数据平台后端服务启动中...")
    print("=" * 60)
    print("服务地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("测试账号: admin / admin123")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
