"""
智能供应链模块 - 库存优化与需求预测
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, timedelta
import numpy as np
import random

security = HTTPBearer()
app = FastAPI(title="智能供应链API")

# Token验证
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    from backend.app import verify_token as verify
    return verify(credentials)

# ============================================
# 数据模型
# ============================================

class InventoryItem(BaseModel):
    product_id: str
    product_name: str
    current_stock: int
    avg_daily_sales: float
    days_of_stock: int
    reorder_point: int
    status: str  # 'normal', 'low', 'out', 'overstock'

class DemandForecastRequest(BaseModel):
    product_id: str
    warehouse_id: str
    forecast_days: int = 30

class SupplyChainAlert(BaseModel):
    alert_type: str
    severity: str
    product_name: str
    warehouse: str
    message: str
    suggested_action: str

# ============================================
# 1. 库存监控API
# ============================================

@app.get("/api/supply-chain/inventory/status")
async def get_inventory_status(
    warehouse_id: Optional[str] = None,
    current_user: str = Depends(verify_token)
):
    """
    获取库存状态
    """
    products = [
        {
            "product_id": "prod001",
            "product_name": "阿莫西林胶囊 500mg",
            "current_stock": 15200,
            "avg_daily_sales": 520,
            "days_of_stock": 29,
            "reorder_point": 5000,
            "status": "normal",
            "warehouse": "华东仓"
        },
        {
            "product_id": "prod002",
            "product_name": "布洛芬缓释胶囊 300mg",
            "current_stock": 3200,
            "avg_daily_sales": 450,
            "days_of_stock": 7,
            "reorder_point": 8000,
            "status": "low",
            "warehouse": "华南仓"
        },
        {
            "product_id": "prod003",
            "product_name": "奥美拉唑肠溶胶囊 20mg",
            "current_stock": 0,
            "avg_daily_sales": 380,
            "days_of_stock": 0,
            "reorder_point": 6000,
            "status": "out",
            "warehouse": "华北仓"
        },
        {
            "product_id": "prod004",
            "product_name": "头孢克肟分散片 100mg",
            "current_stock": 45000,
            "avg_daily_sales": 320,
            "days_of_stock": 140,
            "reorder_point": 7000,
            "status": "overstock",
            "warehouse": "西南仓"
        },
        {
            "product_id": "prod005",
            "product_name": "盐酸二甲双胍缓释片",
            "current_stock": 18500,
            "avg_daily_sales": 680,
            "days_of_stock": 27,
            "reorder_point": 12000,
            "status": "normal",
            "warehouse": "华东仓"
        }
    ]

    if warehouse_id:
        products = [p for p in products if p["warehouse"] == warehouse_id]

    return {"data": products}

@app.get("/api/supply-chain/inventory/optimization")
async def get_inventory_optimization_suggestions(
    current_user: str = Depends(verify_token)
):
    """
    库存优化建议
    """
    suggestions = [
        {
            "product_name": "布洛芬缓释胶囊",
            "current_warehouse": "华南仓",
            "issue": "库存偏低",
            "days_until_stockout": 7,
            "suggested_action": "立即补货 15,000 盒",
            "reason": "当前库存仅可支撑7天,而补货周期为14天",
            "priority": "high",
            "estimated_cost_savings": "避免断货损失约 45万元"
        },
        {
            "product_name": "奥美拉唑肠溶胶囊",
            "current_warehouse": "华北仓",
            "issue": "缺货",
            "days_until_stockout": 0,
            "suggested_action": "紧急调货 5,000 盒",
            "reason": "已完全缺货,需从临近仓库紧急调拨",
            "priority": "critical",
            "estimated_cost_savings": "避免断货损失约 38万元"
        },
        {
            "product_name": "头孢克肟分散片",
            "current_warehouse": "西南仓",
            "issue": "库存积压",
            "excess_days": 110,
            "suggested_action": "调拨 35,000 盒至需求旺盛地区",
            "reason": "库存积压严重,资金占用成本高",
            "priority": "medium",
            "estimated_cost_savings": "减少资金占用成本约 12万元"
        },
        {
            "product_name": "阿莫西林胶囊",
            "current_warehouse": "华东仓",
            "issue": "库存健康",
            "days_of_stock": 29,
            "suggested_action": "维持现状,15天后安排补货",
            "reason": "库存水平合理",
            "priority": "low",
            "estimated_cost_savings": "优化库存成本约 3万元"
        }
    ]

    return {"data": suggestions}

# ============================================
# 2. 需求预测API
# ============================================

@app.post("/api/supply-chain/forecast/demand")
async def forecast_demand(
    request: DemandForecastRequest,
    current_user: str = Depends(verify_token)
):
    """
    需求预测 - 基于历史数据和季节性因素
    """
    # 生成未来30天的预测数据
    forecast_data = []
    base_date = datetime.now()

    # 模拟不同的需求模式
    trend = 100 + random.randint(-10, 20)  # 基础需求
    seasonality = [0.9, 0.95, 1.0, 1.05, 1.1, 1.08, 1.02, 0.98, 1.0, 1.03, 1.07, 1.12, 1.15, 1.1, 1.05, 1.02, 0.98, 0.95, 0.92, 0.9, 0.93, 0.97, 1.0, 1.05, 1.08, 1.1, 1.12, 1.08, 1.05, 1.02]

    for i in range(request.forecast_days):
        forecast_date = base_date + timedelta(days=i)

        # 添加随机波动
        noise = random.uniform(0.9, 1.1)
        demand = round(trend * seasonality[i % len(seasonality)] * noise)

        # 计算置信区间
        lower_bound = round(demand * 0.85)
        upper_bound = round(demand * 1.15)

        forecast_data.append({
            "date": forecast_date.strftime("%Y-%m-%d"),
            "forecast_demand": demand,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "confidence": 0.85
        })

    # 计算汇总统计
    total_demand = sum(d["forecast_demand"] for d in forecast_data)
    avg_daily_demand = total_demand / len(forecast_data)

    return {
        "product_id": request.product_id,
        "warehouse_id": request.warehouse_id,
        "forecast_period_days": request.forecast_days,
        "total_forecast_demand": total_demand,
        "avg_daily_demand": round(avg_daily_demand, 1),
        "peak_demand_day": max(forecast_data, key=lambda x: x["forecast_demand"]),
        "forecast_data": forecast_data
    }

@app.get("/api/supply-chain/forecast/accuracy")
async def get_forecast_accuracy(
    current_user: str = Depends(verify_token)
):
    """
    预测准确率统计
    """
    accuracy_stats = {
        "last_7_days": {
            "mape": 8.5,
            "forecast_accuracy": 91.5,
            "total_forecast": 15230,
            "actual_sales": 14890,
            "deviation": 340
        },
        "last_30_days": {
            "mape": 11.2,
            "forecast_accuracy": 88.8,
            "total_forecast": 65230,
            "actual_sales": 69850,
            "deviation": 4620
        },
        "last_90_days": {
            "mape": 13.5,
            "forecast_accuracy": 86.5,
            "total_forecast": 198500,
            "actual_sales": 212300,
            "deviation": 13800
        }
    }

    return accuracy_stats

# ============================================
# 3. 供应链告警API
# ============================================

@app.get("/api/supply-chain/alerts")
async def get_supply_chain_alerts(
    severity: Optional[str] = None,
    current_user: str = Depends(verify_token)
):
    """
    供应链实时告警
    """
    alerts = [
        {
            "alert_type": "stockout",
            "severity": "critical",
            "product_name": "奥美拉唑肠溶胶囊",
            "warehouse": "华北仓",
            "message": "产品已完全缺货",
            "suggested_action": "立即从临近仓库调货 5,000 盒",
            "created_at": "2025-01-07 09:30:00"
        },
        {
            "alert_type": "low_stock",
            "severity": "high",
            "product_name": "布洛芬缓释胶囊",
            "warehouse": "华南仓",
            "message": "库存仅剩7天,低于安全库存",
            "suggested_action": "安排紧急补货 15,000 盒",
            "created_at": "2025-01-07 08:15:00"
        },
        {
            "alert_type": "demand_spike",
            "severity": "medium",
            "product_name": "阿莫西林胶囊",
            "warehouse": "华东仓",
            "message": "近3天需求激增45%}",
            "suggested_action": "增加安全库存至20天",
            "created_at": "2025-01-06 14:20:00"
        },
        {
            "alert_type": "overstock",
            "severity": "low",
            "product_name": "头孢克肟分散片",
            "warehouse": "西南仓",
            "message": "库存积压140天,资金占用高",
            "suggested_action": "调拨至需求旺盛地区或暂停补货",
            "created_at": "2025-01-05 16:45:00"
        },
        {
            "alert_type": "shipment_delay",
            "severity": "high",
            "product_name": "盐酸二甲双胍缓释片",
            "warehouse": "华北仓",
            "message": "在途货物延误3天",
            "suggested_action": "联系物流商,准备备用供应商",
            "created_at": "2025-01-07 07:00:00"
        }
    ]

    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]

    return {"data": alerts, "total": len(alerts)}

# ============================================
# 4. 仓库绩效API
# ============================================

@app.get("/api/supply-chain/warehouse/performance")
async def get_warehouse_performance(
    current_user: str = Depends(verify_token)
):
    """
    仓库运营绩效
    """
    warehouses = [
        {
            "warehouse_name": "华东仓",
            "location": "上海",
            "total_products": 1520,
            "inventory_turnover_rate": 8.5,
            "fill_rate": 98.5,
            "avg_order fulfillment_time": 1.2,
            "stockout_rate": 1.5,
            "overstock_rate": 3.2,
            "accuracy": 99.2
        },
        {
            "warehouse_name": "华南仓",
            "location": "广州",
            "total_products": 1230,
            "inventory_turnover_rate": 7.8,
            "fill_rate": 97.2,
            "avg_order_fulfillment_time": 1.5,
            "stockout_rate": 2.8,
            "overstock_rate": 4.5,
            "accuracy": 98.5
        },
        {
            "warehouse_name": "华北仓",
            "location": "北京",
            "total_products": 1180,
            "inventory_turnover_rate": 6.9,
            "fill_rate": 95.8,
            "avg_order_fulfillment_time": 1.8,
            "stockout_rate": 4.2,
            "overstock_rate": 5.8,
            "accuracy": 97.3
        },
        {
            "warehouse_name": "西南仓",
            "location": "成都",
            "total_products": 890,
            "inventory_turnover_rate": 5.2,
            "fill_rate": 96.5,
            "avg_order_fulfillment_time": 2.1,
            "stockout_rate": 3.5,
            "overstock_rate": 8.9,
            "accuracy": 98.1
        }
    ]

    return {"data": warehouses}

# ============================================
# 5. 供应商管理API
# ============================================

@app.get("/api/supply-chain/suppliers/performance")
async def get_supplier_performance(
    current_user: str = Depends(verify_token)
):
    """
    供应商绩效评估
    """
    suppliers = [
        {
            "supplier_id": "sup001",
            "supplier_name": "华东制药有限公司",
            "on_time_delivery_rate": 96.5,
            "quality_rate": 99.2,
            "avg_lead_time_days": 12,
            "total_orders": 256,
            "total_amount": 8520,
            "performance_score": 94.5,
            "tier": "A"
        },
        {
            "supplier_id": "sup002",
            "supplier_name": "南方医药集团",
            "on_time_delivery_rate": 92.8,
            "quality_rate": 97.5,
            "avg_lead_time_days": 15,
            "total_orders": 189,
            "total_amount": 6230,
            "performance_score": 89.5,
            "tier": "B"
        },
        {
            "supplier_id": "sup003",
            "supplier_name": "北方生物制药",
            "on_time_delivery_rate": 88.5,
            "quality_rate": 95.8,
            "avg_lead_time_days": 18,
            "total_orders": 125,
            "total_amount": 3850,
            "performance_score": 82.3,
            "tier": "C"
        },
        {
            "supplier_id": "sup004",
            "supplier_name": "西南康德药业",
            "on_time_delivery_rate": 98.2,
            "quality_rate": 99.5,
            "avg_lead_time_days": 10,
            "total_orders": 312,
            "total_amount": 12580,
            "performance_score": 97.8,
            "tier": "A"
        }
    ]

    return {"data": suppliers}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
