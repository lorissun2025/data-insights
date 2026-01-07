# 市场洞察模块 - API接口设计 (FastAPI)

from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
import uvicorn

app = FastAPI(
    title="医药市场洞察API",
    description="为药企、医疗机构提供市场分析、竞品追踪、销售预测等服务",
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

# ============================================
# 数据模型定义
# ============================================

class MarketShareRequest(BaseModel):
    product_id: str
    start_date: date
    end_date: date
    region: Optional[str] = None
    category: Optional[str] = None

class MarketShareResponse(BaseModel):
    product_name: str
    manufacturer_name: str
    total_sales: float
    category_sales: float
    market_share_pct: float
    market_rank: int
    rank_change: int
    mom_growth: float
    yoy_growth: float

class CompetitorComparisonRequest(BaseModel):
    product_ids: List[str]
    start_date: date
    end_date: date
    region: Optional[str] = None
    metrics: List[str] = ['sales_growth', 'price_trend', 'distribution_coverage']

class ForecastRequest(BaseModel):
    product_id: str
    forecast_periods: int = 12
    model_type: str = "arima"  # arima, prophet, xgboost

class ForecastResponse(BaseModel):
    product_id: str
    product_name: str
    forecast_data: List[dict]
    model_accuracy: float
    confidence_interval: bool

class OpportunityRequest(BaseModel):
    category_id: str
    lookback_months: int = 12
    min_growth_rate: float = 0.2
    min_market_size: float = 1000000

class PriceElasticityRequest(BaseModel):
    product_id: str
    start_date: date
    end_date: date

class HospitalProfileRequest(BaseModel):
    hospital_id: str
    analysis_period_months: int = 12

# ============================================
# 1. 市场份额与竞品分析API
# ============================================

@app.get("/api/v1/market/share", response_model=MarketShareResponse, tags=["市场分析"])
async def get_market_share(
    product_id: str = Query(..., description="产品ID"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    region: Optional[str] = Query(None, description="区域筛选"),
    category: Optional[str] = Query(None, description="治疗领域")
):
    """
    获取产品市场份额

    - **product_id**: 产品ID (必填)
    - **start_date**: 开始日期 (必填)
    - **end_date**: 结束日期 (必填)
    - **region**: 区域筛选 (可选)
    - **category**: 治疗领域 (可选)

    返回产品的市场份额、排名、增长率等关键指标
    """
    try:
        result = calculate_market_share(product_id, start_date, end_date, region, category)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/market/competitor-comparison", tags=["市场分析"])
async def get_competitor_comparison(params: CompetitorComparisonRequest):
    """
    竞品多维度对比分析

    对比维度包括:
    - 销售额增长率
    - 价格趋势
    - 市场覆盖率
    - 医院渗透率
    - 区域分布
    """
    result = competitor_benchmarking(
        params.product_ids,
        params.start_date,
        params.end_date,
        params.metrics
    )
    return result


@app.get("/api/v1/market/competitor-list", tags=["市场分析"])
async def get_competitor_list(
    category: str = Query(..., description="治疗领域"),
    region: Optional[str] = Query(None, description="区域筛选"),
    limit: int = Query(20, description="返回数量")
):
    """
    获取指定治疗领域的竞品列表

    返回该领域TOP N产品及其市场表现
    """
    sql = f"""
    SELECT
        product_id,
        product_name,
        manufacturer_name,
        SUM(sales_amount) as total_sales,
        SUM(sales_amount) / (SELECT SUM(sales_amount)
                            FROM sales_data
                            WHERE category_l1 = '{category}') as market_share,
        RANK() OVER (ORDER BY SUM(sales_amount) DESC) as rank
    FROM sales_data
    WHERE category_l1 = '{category}'
      AND sale_date >= today() - INTERVAL 12 MONTH
      {f"AND sales_province = '{region}'" if region else ""}
    GROUP BY product_id, product_name, manufacturer_name
    ORDER BY total_sales DESC
    LIMIT {limit}
    """
    return execute_query(sql)


# ============================================
# 2. 销售预测API
# ============================================

@app.post("/api/v1/forecast/sales", response_model=ForecastResponse, tags=["销售预测"])
async def forecast_sales(params: ForecastRequest):
    """
    销售预测

    支持多种预测模型:
    - **arima**: 适合稳定销售的产品
    - **prophet**: 适合有季节性、节假日效应的产品
    - **xgboost**: 适合多因素影响的复杂场景

    返回未来N个月的预测值及置信区间
    """
    if params.model_type == "arima":
        result = forecast_sales_arima(params.product_id, params.forecast_periods)
    elif params.model_type == "prophet":
        result = forecast_sales_prophet(params.product_id, params.forecast_periods)
    elif params.model_type == "xgboost":
        result = forecast_sales_ml(params.product_id, params.forecast_periods)
    else:
        raise HTTPException(status_code=400, detail="不支持的模型类型")

    return result


@app.get("/api/v1/forecast/accuracy", tags=["销售预测"])
async def get_forecast_accuracy(
    forecast_id: str = Query(..., description="预测ID")
):
    """
    获取预测模型的准确率

    对比预测值与实际值,计算MAPE、RMSE、MAE等指标
    """
    sql = f"""
    WITH forecast_vs_actual AS (
        SELECT
            f.target_date,
            f.forecast_sales_amount,
            f.forecast_lower_bound,
            f.forecast_upper_bound,
            COALESCE(SUM(s.sales_amount), 0) as actual_sales
        FROM market_forecast f
        LEFT JOIN sales_data s ON f.product_id = s.product_id
            AND f.target_date = toStartOfMonth(s.sale_date)
        WHERE f.forecast_id = '{forecast_id}'
            AND f.target_date <= today()
        GROUP BY f.target_date, f.forecast_sales_amount, f.forecast_lower_bound, f.forecast_upper_bound
    )
    SELECT
        AVG(ABS(actual_sales - forecast_sales_amount) / NULLIF(actual_sales, 0)) * 100 as mape_pct,
        SQRT(AVG(POWER(actual_sales - forecast_sales_amount, 2))) as rmse,
        AVG(ABS(actual_sales - forecast_sales_amount)) as mae
    FROM forecast_vs_actual
    """
    return execute_query(sql)


@app.get("/api/v1/anomaly/detection", tags=["销售预测"])
async def detect_anomalies(
    product_id: str = Query(..., description="产品ID"),
    lookback_days: int = Query(90, description="回溯天数")
):
    """
    销售异常检测

    识别以下异常:
    - 销售突增 (spike)
    - 销售突降 (drop)
    - 断货 (stockout)

    支持多种检测方法: 3-Sigma, Isolation Forest, STL
    """
    result = detect_sales_anomalies(product_id, lookback_days)
    return result


# ============================================
# 3. 市场机会识别API
# ============================================

@app.get("/api/v1/opportunity/high-growth", tags=["机会识别"])
async def get_high_growth_opportunities(params: OpportunityRequest):
    """
    识别高增长潜力的区域/产品

    评估维度:
    1. 增长率 (权重30%)
    2. 市场规模 (权重20%)
    3. 竞争强度 (权重20%)
    4. 渗透空间 (权重30%)
    """
    result = identify_growth_opportunities(
        params.category_id,
        params.lookback_months
    )
    return result


@app.get("/api/v1/opportunity/product-portfolio", tags=["机会识别"])
async def analyze_product_portfolio(
    company_id: str = Query(..., description="企业ID")
):
    """
    产品组合机会分析 (改进版BCG矩阵)

    分类:
    - 明星产品: 高增长 + 高份额
    - 现金牛: 低增长 + 高份额
    - 问题产品: 高增长 + 低份额
    - 瘦狗产品: 低增长 + 低份额
    - 潜力产品: 预测高增长
    """
    result = analyze_product_portfolio_opportunities(company_id)
    return result


@app.get("/api/v1/opportunity/white-space", tags=["机会识别"])
async def find_market_white_space(
    category: str = Query(..., description="治疗领域"),
    region: str = Query(..., description="区域")
):
    """
    发现市场空白点

    识别策略:
    1. 有需求但竞品少的品类
    2. 竞品渗透率低的区域
    3. 价格差异巨大的细分市场
    """
    sql = f"""
    WITH market_potential AS (
        SELECT
            category_l2,
            sales_province,
            COUNT(DISTINCT product_id) as product_count,
            SUM(sales_amount) as market_size,
            COUNT(DISTINCT buyer_id) as customer_count,
            (COUNT(DISTINCT buyer_id)::float / (
                SELECT COUNT(DISTINCT buyer_id)
                FROM sales_data
                WHERE sales_province = '{region}'
            )) as penetration_rate
        FROM sales_data
        WHERE category_l1 = '{category}'
          AND sales_province = '{region}'
          AND sale_date >= today() - INTERVAL 12 MONTH
        GROUP BY category_l2, sales_province
        HAVING market_size > 1000000
    )
    SELECT
        category_l2,
        market_size,
        product_count,
        penetration_rate,
        (market_size / NULLIF(product_count, 0)) as avg_sales_per_product,

        CASE
            WHEN product_count < 5 AND penetration_rate < 0.3 THEN '高潜力空白点'
            WHEN product_count < 10 AND penetration_rate < 0.5 THEN '中等潜力'
            ELSE '红海市场'
        END as opportunity_level

    FROM market_potential
    ORDER BY
        CASE opportunity_level
            WHEN '高潜力空白点' THEN 1
            WHEN '中等潜力' THEN 2
            ELSE 3
        END,
        market_size DESC
    """
    return execute_query(sql)


# ============================================
# 4. 价格分析API
# ============================================

@app.get("/api/v1/price/elasticity", tags=["价格分析"])
async def get_price_elasticity(params: PriceElasticityRequest):
    """
    计算价格弹性系数

    返回:
    - 弹性系数
    - 解读建议
    - 拟合优度
    - 月度弹性变化
    """
    result = calculate_price_elasticity(params.product_id)
    return result


@app.get("/api/v1/price/competition", tags=["价格分析"])
async def analyze_price_competition(
    product_ids: List[str] = Query(..., description="竞品ID列表"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期")
):
    """
    竞品价格对比分析

    返回:
    - 绝对价格水平
    - 相对价格(vs市场平均)
    - 价格排名
    - 价格变化趋势
    """
    result = analyze_price_competition(product_ids)
    return result


@app.get("/api/v1/price/trend", tags=["价格分析"])
async def get_price_trend(
    product_id: str = Query(..., description="产品ID"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    granularity: str = Query("month", description="聚合粒度: day/week/month")
):
    """
    价格趋势分析

    支持多时间粒度: 日、周、月
    """
    sql = f"""
    SELECT
        toStartOfMonth(sale_date) as month,
        AVG(unit_price) as avg_price,
        MIN(unit_price) as min_price,
        MAX(unit_price) as max_price,
        STDDEV(unit_price) as price_std,
        PERCENTILE(unit_price, 0.5) as median_price,

        -- 价格变化
        (AVG(unit_price) - LAG(AVG(unit_price)) OVER (ORDER BY toStartOfMonth(sale_date))) /
            NULLIF(LAG(AVG(unit_price)) OVER (ORDER BY toStartOfMonth(sale_date)), 0) as mom_change,

        SUM(sales_quantity) as sales_quantity

    FROM sales_data
    WHERE product_id = '{product_id}'
      AND sale_date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY month
    ORDER BY month
    """
    return execute_query(sql)


# ============================================
# 5. 客户画像API
# ============================================

@app.get("/api/v1/customer/hospital-profile", tags=["客户洞察"])
async def get_hospital_profile(params: HospitalProfileRequest):
    """
    医院采购画像分析

    返回医院的采购规模、偏好、行为特征、供应商结构等
    """
    result = create_hospital_profile(params.hospital_id)
    return result


@app.get("/api/v1/customer/hospital-segmentation", tags=["客户洞察"])
async def segment_hospitals(
    category: str = Query(..., description="治疗领域"),
    region: Optional[str] = Query(None, description="区域筛选")
):
    """
    医院客户分层

    使用RFM模型:
    - Recency: 最近采购时间
    - Frequency: 采购频率
    - Monetary: 采购金额

    分层: 高价值客户、主力客户、潜力客户、低价值客户
    """
    sql = f"""
    WITH hospital_rfm AS (
        SELECT
            buyer_id,
            buyer_name,
            hospital_level,

            -- Recency (天)
            DATEDIFF('day', MAX(sale_date), today()) as recency_days,

            -- Frequency (采购次数)
            COUNT(DISTINCT sale_date) as frequency,

            -- Monetary (采购金额)
            SUM(sales_amount) as monetary

        FROM sales_data
        WHERE category_l1 = '{category}'
          {f"AND sales_province = '{region}'" if region else ""}
          AND sale_date >= today() - INTERVAL 12 MONTH
        GROUP BY buyer_id, buyer_name, hospital_level
    ),
    rfm_scores AS (
        SELECT
            *,
            NTILE(4) OVER (ORDER BY recency_days DESC) as r_score,  -- 越小越好
            NTILE(4) OVER (ORDER BY frequency) as f_score,         -- 越大越好
            NTILE(4) OVER (ORDER BY monetary) as m_score           -- 越大越好
        FROM hospital_rfm
    )
    SELECT
        buyer_id,
        buyer_name,
        hospital_level,
        recency_days,
        frequency,
        monetary,
        r_score,
        f_score,
        m_score,
        r_score + f_score + m_score as rfm_total_score,

        CASE
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN '高价值客户'
            WHEN r_score >= 2 AND f_score >= 2 AND m_score >= 2 THEN '主力客户'
            WHEN m_score <= 2 AND frequency <= 2 THEN '低价值客户'
            ELSE '潜力客户'
        END as customer_segment

    FROM rfm_scores
    ORDER BY monetary DESC
    """
    return execute_query(sql)


@app.get("/api/v1/customer/doctor-prescription-pattern", tags=["客户洞察"])
async def analyze_doctor_pattern(
    doctor_id: str = Query(..., description="医生ID"),
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期")
):
    """
    医生处方行为分析

    分析维度:
    - 处方量趋势
    - 用药偏好(品牌/通用名)
    - 费效比
    - 合规性(指南符合度)
    """
    sql = f"""
    SELECT
        doctor_id,
        doctor_name,
        department,
        hospital_name,

        -- 处方量
        COUNT(DISTINCT prescription_id) as prescription_count,
        SUM(total_amount) as total_prescription_amount,
        AVG(total_amount) as avg_prescription_amount,

        -- 用药偏好
        SUM(CASE WHEN generic_name LIKE brand_name THEN 1 ELSE 0 END)::float /
            NULLIF(COUNT(*), 0) as generic_preference,

        -- 患者特征
        AVG(patient_age) as avg_patient_age,
        MODE() WITHIN GROUP (ORDER BY diagnosis_name) as primary_diagnosis,

        -- TOP 5 处方药品
        ARRAY_AGG(drug_name ORDER BY COUNT(*) DESC) FILTER (WHERE drug_name IS NOT NULL)[1:5] as top_drugs

    FROM prescription_data
    WHERE doctor_id = '{doctor_id}'
      AND prescription_date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY doctor_id, doctor_name, department, hospital_name
    """
    return execute_query(sql)


# ============================================
# 6. 仪表盘数据API
# ============================================

@app.get("/api/v1/dashboard/overview", tags=["仪表盘"])
async def get_dashboard_overview(
    company_id: str = Query(..., description="企业ID"),
    date_range: str = Query("12m", description="时间范围: 1m/3m/6m/12m")
):
    """
    市场洞察仪表盘 - 总览数据

    返回核心KPI和趋势图数据
    """
    period_map = {"1m": 1, "3m": 3, "6m": 6, "12m": 12}
    months = period_map.get(date_range, 12)

    sql = f"""
    WITH company_stats AS (
        SELECT
            -- 核心KPI
            SUM(sales_amount) as total_sales,
            SUM(sales_quantity) as total_quantity,
            COUNT(DISTINCT buyer_id) as customer_count,
            COUNT(DISTINCT product_id) as product_count,

            -- 对比上月
            (SUM(sales_amount) FILTER (
                WHERE sale_date >= today() - INTERVAL 1 MONTH
            ) / NULLIF(SUM(sales_amount) FILTER (
                WHERE sale_date >= today() - INTERVAL 2 MONTH
                    AND sale_date < today() - INTERVAL 1 MONTH
            ), 0) - 1) * 100 as mom_growth,

            -- 去年同期
            (SUM(sales_amount) FILTER (
                WHERE sale_date >= today() - INTERVAL {months} MONTH
            ) / NULLIF(SUM(sales_amount) FILTER (
                WHERE sale_date >= today() - INTERVAL {months * 2} MONTH
                    AND sale_date < today() - INTERVAL {months} MONTH
            ), 0) - 1) * 100 as yoy_growth

        FROM sales_data
        WHERE manufacturer_id = '{company_id}'
          AND sale_date >= today() - INTERVAL {months} MONTH
    ),
    top_products AS (
        SELECT
            product_name,
            SUM(sales_amount) as sales
        FROM sales_data
        WHERE manufacturer_id = '{company_id}'
          AND sale_date >= today() - INTERVAL {months} MONTH
        GROUP BY product_name
        ORDER BY sales DESC
        LIMIT 5
    ),
    sales_trend AS (
        SELECT
            toStartOfMonth(sale_date) as month,
            SUM(sales_amount) as sales_amount
        FROM sales_data
        WHERE manufacturer_id = '{company_id}'
          AND sale_date >= today() - INTERVAL {months} MONTH
        GROUP BY month
        ORDER BY month
    )
    SELECT * FROM company_stats, top_products, sales_trend
    """
    return execute_query(sql)


@app.get("/api/v1/dashboard/realtime-alerts", tags=["仪表盘"])
async def get_realtime_alerts(
    user_id: str = Query(..., description="用户ID")
):
    """
    实时预警信息

    预警类型:
    - 销售异常 (突增/突降/断货)
    - 竞品动态 (降价/新品)
    - 市场机会 (高增长区域)
    - 风险提示 (政策变化/供应问题)
    """
    sql = f"""
    WITH alerts AS (
        -- 销售异常预警
        SELECT
            '销售异常' as alert_type,
            'high' as severity,
            product_name || ' 在 ' || sales_city || ' 销售下降' || ROUND((1 - sales_growth) * 100) || '%' as message,
            sale_date as event_time
        FROM sales_anomaly_detection
        WHERE is_anomaly = true
          AND anomaly_type = 'drop'
          AND sale_date >= today() - INTERVAL 7 DAY

        UNION ALL

        -- 竞品降价预警
        SELECT
            '竞品动态' as alert_type,
            'medium' as severity,
            competitor_name || ' 在 ' || city || ' 降价 ' || ROUND(price_drop_pct) || '%' as message,
            detection_date as event_time
        FROM competitor_price_monitoring
        WHERE price_drop_pct > 10
          AND detection_date >= today() - INTERVAL 7 DAY

        ORDER BY event_time DESC
        LIMIT 20
    )
    SELECT * FROM alerts
    """
    return execute_query(sql)


# ============================================
# 辅助函数
# ============================================

def execute_query(sql: str):
    """
    执行SQL查询 (示例)
    实际项目中应该使用数据库连接池
    """
    import clickhouse_connect
    client = clickhouse_connect.get_client(
        host='localhost',
        port=8123,
        username='default',
        password='',
        database='pharma_insights'
    )
    result = client.query(sql)
    return result.named_results()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
