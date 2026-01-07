# 市场洞察模块 - 核心分析功能和算法设计

## 一、竞品追踪与分析

### 1.1 市场份额计算
```python
"""
算法目标: 计算某产品/企业在特定时间、区域的市场份额
输入: 产品ID、时间范围、区域、治疗领域
输出: 市场份额、排名、变化趋势
"""

def calculate_market_share(product_id, start_date, end_date, region=None, category=None):
    """
    市场份额计算算法

    核心逻辑:
    1. 查询目标产品销售额
    2. 查询同类产品总销售额
    3. 计算: 市场份额 = 产品销售额 / 同类总销售额 × 100%
    4. 计算排名和同比/环比变化
    """

    sql = f"""
    WITH target_product_sales AS (
        SELECT
            product_id,
            product_name,
            manufacturer_name,
            SUM(sales_amount) as total_sales
        FROM sales_data
        WHERE sale_date BETWEEN '{start_date}' AND '{end_date}'
            AND product_id = '{product_id}'
            {region_filter}
        GROUP BY product_id, product_name, manufacturer_name
    ),
    category_total_sales AS (
        SELECT
            SUM(sales_amount) as category_sales
        FROM sales_data
        WHERE sale_date BETWEEN '{start_date}' AND '{end_date}'
            AND category_l1 = '{category}'
            {region_filter}
    ),
    competitor_sales AS (
        SELECT
            product_id,
            product_name,
            manufacturer_name,
            SUM(sales_amount) as sales,
            RANK() OVER (ORDER BY SUM(sales_amount) DESC) as market_rank
        FROM sales_data
        WHERE sale_date BETWEEN '{start_date}' AND '{end_date}'
            AND category_l1 = '{category}'
            {region_filter}
        GROUP BY product_id, product_name, manufacturer_name
    )
    SELECT
        t.product_name,
        t.manufacturer_name,
        t.total_sales,
        c.category_sales,
        (t.total_sales / c.category_sales * 100) as market_share_pct,
        co.market_rank,
        co.market_rank - LAG(co.market_rank) OVER (ORDER BY sale_date) as rank_change
    FROM target_product_sales t
    CROSS JOIN category_total_sales c
    JOIN competitor_sales co ON t.product_id = co.product_id
    """

    return execute_query(sql)
```

### 1.2 竞品对比分析
```python
def competitor_benchmarking(product_ids, start_date, end_date, metrics):
    """
    多维度竞品对比

    对比维度:
    - 销售额增长率
    - 平均价格变化
    - 市场覆盖率(铺货率)
    - 医院渗透率
    - 区域分布
    """

    analysis_result = {
        'sales_growth': calculate_sales_growth(product_ids, start_date, end_date),
        'price_trend': analyze_price_trend(product_ids, start_date, end_date),
        'distribution_coverage': calculate_coverage(product_ids, end_date),
        'hospital_penetration': calculate_penetration(product_ids, end_date),
        'regional_distribution': analyze_regional_distribution(product_ids, start_date, end_date)
    }

    return analysis_result
```

---

## 二、智能销售预测

### 2.1 时间序列预测 (ARIMA / Prophet)
```python
"""
算法目标: 预测未来1-12个月的销售趋势
适用场景: 稳定销售的历史产品
"""

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from fbprophet import Prophet

def forecast_sales_arima(product_id, forecast_periods=12):
    """
    基于ARIMA的时间序列预测

    步骤:
    1. 数据准备: 按月聚合历史销售数据
    2. 季节性分解: 识别趋势、季节性、残差
    3. 参数优化: 通过AIC选择最优(p,d,q)参数
    4. 模型训练: 拟合ARIMA模型
    5. 预测: 生成未来N期的预测值和置信区间
    6. 评估: 计算MAPE、RMSE等指标
    """

    # 1. 获取历史数据
    sql = f"""
    SELECT
        toStartOfMonth(sale_date) as month,
        SUM(sales_amount) as total_sales,
        SUM(sales_quantity) as total_quantity
    FROM sales_data
    WHERE product_id = '{product_id}'
        AND sale_date >= today() - INTERVAL 3 YEAR
    GROUP BY month
    ORDER BY month
    """
    df = pd.read_sql(sql, engine)

    # 2. 季节性分解
    from statsmodels.tsa.seasonal import seasonal_decompose
    decomposition = seasonal_decompose(df['total_sales'], model='multiplicative', period=12)

    # 3-4. ARIMA建模
    model = ARIMA(df['total_sales'], order=(1,1,1), seasonal_order=(1,1,1,12))
    fitted_model = model.fit()

    # 5. 预测
    forecast = fitted_model.forecast(steps=forecast_periods)
    confidence_interval = fitted_model.get_forecast(steps=forecast_periods).conf_int()

    # 6. 返回结果
    return {
        'forecast': forecast,
        'lower_bound': confidence_interval['lower total_sales'],
        'upper_bound': confidence_interval['upper total_sales'],
        'model_accuracy': calculate_mape(df['total_sales'], fitted_model.fittedvalues)
    }


def forecast_sales_prophet(product_id, forecast_periods=12):
    """
    基于Prophet的预测(支持节假日、突发事件)
    优势: 自动处理季节性、节假日效应、趋势变化点
    """

    # 获取数据
    df = pd.read_sql(sql, engine)
    df.columns = ['ds', 'y']

    # 创建并训练模型
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='multiplicative'
    )

    # 添加中国节假日
    model.add_country_holidays(country_name='CN')

    # 添加自定义季节性(如带量采购影响)
    model.add_seasonality(name='vbp_procurement', period=365, fourier_order=5)

    model.fit(df)

    # 生成未来时间框架
    future = model.make_future_dataframe(periods=forecast_periods, freq='M')

    # 预测
    forecast = model.predict(future)

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_periods)
```

### 2.2 机器学习预测 (XGBoost / LightGBM)
```python
"""
算法目标: 利用多特征进行精准预测
特征: 历史销售、季节、价格、竞品表现、政策因素、经济指标
"""

import xgboost as xgb
from sklearn.preprocessing import StandardScaler

def forecast_sales_ml(product_id, forecast_periods=12):
    """
    基于机器学习的销售预测

    特征工程:
    - 时间特征: 年、月、季度、是否节假日
    - 滞后特征: 过去1/3/6/12个月销量
    - 滚动统计: 3/6个月移动平均、标准差
    - 价格特征: 平均价格、价格变化率
    - 竞品特征: 竞品销量、市场份额
    - 政策特征: 是否带量采购、医保目录状态
    - 宏观特征: GDP增速、人口老龄化率
    """

    # 1. 准备特征数据集
    sql = f"""
    WITH features AS (
        SELECT
            toStartOfMonth(sale_date) as month,
            -- 时间特征
            toYear(sale_date) as year,
            toMonth(sale_date) as month,
            toQuarter(sale_date) as quarter,

            -- 滞后特征
            LAG(SUM(sales_amount), 1) OVER (ORDER BY toStartOfMonth(sale_date)) as lag_1m,
            LAG(SUM(sales_amount), 3) OVER (ORDER BY toStartOfMonth(sale_date)) as lag_3m,
            LAG(SUM(sales_amount), 6) OVER (ORDER BY toStartOfMonth(sale_date)) as lag_6m,
            LAG(SUM(sales_amount), 12) OVER (ORDER BY toStartOfMonth(sale_date)) as lag_12m,

            -- 滚动统计
            AVG(SUM(sales_amount)) OVER (
                ORDER BY toStartOfMonth(sale_date)
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ) as moving_avg_3m,

            -- 目标变量
            SUM(sales_amount) as sales_amount
        FROM sales_data
        WHERE product_id = '{product_id}'
        GROUP BY month, year, month, quarter
        ORDER BY month
    )
    SELECT * FROM features
    WHERE month >= today() - INTERVAL 3 YEAR
    """
    df = pd.read_sql(sql, engine)

    # 2. 特征工程
    df['is_holiday'] = df['month'].apply(is_holiday_month)
    df['price_change'] = df['unit_price'].pct_change()
    df['market_growth'] = df['total_market_size'].pct_change()

    # 3. 拆分训练集和测试集
    train = df[df['month'] < '2024-01-01']
    test = df[df['month'] >= '2024-01-01']

    feature_cols = ['year', 'month', 'quarter', 'lag_1m', 'lag_3m', 'lag_6m',
                   'moving_avg_3m', 'is_holiday', 'price_change']

    X_train = train[feature_cols]
    y_train = train['sales_amount']
    X_test = test[feature_cols]
    y_test = test['sales_amount']

    # 4. 训练XGBoost模型
    model = xgb.XGBRegressor(
        n_estimators=1000,
        max_depth=6,
        learning_rate=0.01,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        early_stopping_rounds=50,
        verbose=False
    )

    # 5. 特征重要性分析
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    # 6. 预测未来
    future_features = prepare_future_features(forecast_periods)
    forecast = model.predict(future_features[feature_cols])

    return {
        'forecast': forecast,
        'feature_importance': feature_importance,
        'model_accuracy': model.best_score
    }
```

### 2.3 异常检测
```python
"""
算法目标: 识别销售异常(突增/突降/断货等)
适用场景: 实时监控、预警系统
"""

from sklearn.ensemble import IsolationForest
from scipy import stats

def detect_sales_anomalies(product_id, lookback_days=90):
    """
    销售异常检测

    方法1: 统计方法 (3-Sigma)
    - 判断标准: |实际值 - 均值| > 3 × 标准差

    方法2: 机器学习 (Isolation Forest)
    - 识别离群点

    方法3: 时间序列异常 (STL分解)
    - 残差超过阈值则判定为异常
    """

    sql = f"""
    SELECT
        sale_date,
        SUM(sales_amount) as daily_sales,
        SUM(sales_quantity) as daily_quantity
    FROM sales_data
    WHERE product_id = '{product_id}'
        AND sale_date >= today() - INTERVAL {lookback_days} DAY
    GROUP BY sale_date
    ORDER BY sale_date
    """
    df = pd.read_sql(sql, engine)

    # 方法1: 3-Sigma规则
    mean_sales = df['daily_sales'].mean()
    std_sales = df['daily_sales'].std()
    upper_bound = mean_sales + 3 * std_sales
    lower_bound = mean_sales - 3 * std_sales

    df['anomaly_3sigma'] = (
        (df['daily_sales'] > upper_bound) |
        (df['daily_sales'] < lower_bound)
    )

    # 方法2: Isolation Forest
    clf = IsolationForest(contamination=0.1, random_state=42)
    df['anomaly_iforest'] = clf.fit_predict(df[['daily_sales']]) == -1

    # 方法3: STL分解 + 残差检测
    from statsmodels.tsa.seasonal import STL
    stl = STL(df['daily_sales'], period=7)
    res = stl.fit()
    residuals = res.resid
    df['anomaly_stl'] = np.abs(residuals) > 2 * residuals.std()

    # 综合判断(多种方法都判定为异常)
    df['is_anomaly'] = (
        df['anomaly_3sigma'] |
        df['anomaly_iforest'] |
        df['anomaly_stl']
    )

    # 异常分类
    df.loc[df['is_anomaly'] & (df['daily_sales'] > upper_bound), 'anomaly_type'] = 'spike'
    df.loc[df['is_anomaly'] & (df['daily_sales'] < lower_bound), 'anomaly_type'] = 'drop'

    return df[df['is_anomaly']]
```

---

## 三、市场机会识别

### 3.1 高增长潜力区域识别
```python
def identify_growth_opportunities(category_id, lookback_months=12):
    """
    识别高增长潜力的区域/产品

    评估维度:
    1. 增长率: CAGR连续3个月>20%
    2. 市场规模: 绝对规模>阈值
    3. 竞争强度: 竞品数量<阈值
    4. 渗透率: 当前渗透率<50%(有增长空间)

    综合得分 = 增长率得分 × 0.3 + 规模得分 × 0.2 +
               竞争得分 × 0.2 + 渗透空间得分 × 0.3
    """

    sql = f"""
    WITH regional_stats AS (
        SELECT
            sales_province,
            sales_city,
            category_l1,

            -- 增长率指标
            SUM(CASE WHEN sale_date >= today() - INTERVAL 3 MONTH
                THEN sales_amount ELSE 0 END) as sales_3m,
            SUM(CASE WHEN sale_date >= today() - INTERVAL 6 MONTH
                    AND sale_date < today() - INTERVAL 3 MONTH
                THEN sales_amount ELSE 0 END) as sales_prev_3m,

            -- 规模指标
            SUM(sales_amount) as total_sales,

            -- 竞争强度
            COUNT(DISTINCT manufacturer_id) as competitor_count,

            -- 渗透率
            COUNT(DISTINCT buyer_id) as covered_customers,
            (SELECT COUNT(DISTINCT buyer_id)
             FROM sales_data
             WHERE category_l1 = s.category_l1) as total_customers

        FROM sales_data s
        WHERE sale_date >= today() - INTERVAL {lookback_months} MONTH
            AND category_l1 = '{category_id}'
        GROUP BY sales_province, sales_city, category_l1
    )
    SELECT
        sales_province,
        sales_city,
        sales_3m / NULLIF(sales_prev_3m, 0) - 1 as growth_rate,
        total_sales,
        competitor_count,
        covered_customers / NULLIF(total_customers, 0) as penetration_rate,

        -- 综合得分计算
        (growth_rate * 0.3 +
         LOG10(total_sales) * 0.2 +
         (1 - competitor_count / 100.0) * 0.2 +
         (1 - penetration_rate) * 0.3) as opportunity_score

    FROM regional_stats
    WHERE growth_rate > 0.2  -- 增长率>20%
      AND total_sales > 1000000  -- 规模>100万
      AND competitor_count < 50  -- 竞品<50家
      AND penetration_rate < 0.5  -- 渗透率<50%
    ORDER BY opportunity_score DESC
    LIMIT 50
    """

    return pd.read_sql(sql, engine)
```

### 3.2 产品组合机会分析
```python
def analyze_product_portfolio_opportunities(company_id):
    """
    产品组合机会分析 (BCG矩阵改进版)

    分类维度:
    - 明星产品: 高增长 + 高份额 -> 继续投资
    - 现金牛产品: 低增长 + 高份额 -> 维持
    - 问题产品: 高增长 + 低份额 -> 决策点
    - 瘦狗产品: 低增长 + 低份额 -> 考虑退出

    新增维度:
    - 潜力产品: 低增长当前 + 高增长潜力(预测)
    """

    sql = f"""
    WITH product_metrics AS (
        SELECT
            product_id,
            product_name,
            manufacturer_id,

            -- 增长率
            (SUM(sales_amount) FILTER (
                WHERE sale_date >= today() - INTERVAL 6 MONTH
            ) / NULLIF(SUM(sales_amount) FILTER (
                WHERE sale_date >= today() - INTERVAL 12 MONTH
                    AND sale_date < today() - INTERVAL 6 MONTH
            ), 0) - 1) as growth_rate,

            -- 市场份额
            SUM(sales_amount) as product_sales,
            (SUM(sales_amount) / (
                SELECT SUM(sales_amount)
                FROM sales_data
                WHERE category_l1 = s.category_l1
            )) as market_share,

            -- 预测增长率
            f.forecast_growth_rate

        FROM sales_data s
        LEFT JOIN market_forecast f ON s.product_id = f.product_id
        WHERE manufacturer_id = '{company_id}'
          AND sale_date >= today() - INTERVAL 12 MONTH
        GROUP BY product_id, product_name, manufacturer_id, f.forecast_growth_rate
    )
    SELECT
        product_name,
        growth_rate,
        market_share,
        forecast_growth_rate,

        CASE
            WHEN growth_rate > 0.15 AND market_share > 0.1 THEN '明星产品'
            WHEN growth_rate < 0.1 AND market_share > 0.1 THEN '现金牛'
            WHEN growth_rate > 0.15 AND market_share < 0.05 THEN '问题产品'
            WHEN growth_rate < 0.1 AND market_share < 0.05 THEN '瘦狗产品'
            WHEN forecast_growth_rate > 0.2 THEN '潜力产品'
        END as bcg_category,

        -- 战略建议
        CASE
            WHEN growth_rate > 0.15 AND market_share > 0.1 THEN '继续投资，扩大优势'
            WHEN growth_rate < 0.1 AND market_share > 0.1 THEN '维持现状，收割利润'
            WHEN growth_rate > 0.15 AND market_share < 0.05 THEN '加大投入或退出'
            WHEN growth_rate < 0.1 AND market_share < 0.05 THEN '考虑退出'
            WHEN forecast_growth_rate > 0.2 THEN '提前布局，抢占先机'
        END as strategy

    FROM product_metrics
    ORDER BY
        CASE bcg_category
            WHEN '明星产品' THEN 1
            WHEN '现金牛' THEN 2
            WHEN '潜力产品' THEN 3
            WHEN '问题产品' THEN 4
            WHEN '瘦狗产品' THEN 5
        END
    """

    return pd.read_sql(sql, engine)
```

---

## 四、价格分析

### 4.1 价格弹性分析
```python
def calculate_price_elasticity(product_id):
    """
    计算价格弹性系数

    价格弹性 = 需求量变化率 / 价格变化率

    解释:
    - |弹性| > 1: 富有弹性(降价能显著提升销量)
    - |弹性| < 1: 缺乏弹性(价格变化对销量影响小)
    - |弹性| = 1: 单位弹性
    """

    sql = f"""
    WITH price_quantity_data AS (
        SELECT
            toStartOfMonth(sale_date) as month,
            AVG(unit_price) as avg_price,
            SUM(sales_quantity) as total_quantity,
            SUM(sales_amount) as total_amount
        FROM sales_data
        WHERE product_id = '{product_id}'
          AND sale_date >= today() - INTERVAL 2 YEAR
        GROUP BY month
        ORDER BY month
    )
    SELECT
        month,
        avg_price,
        total_quantity,

        -- 计算月度变化率
        (avg_price - LAG(avg_price) OVER (ORDER BY month)) /
            NULLIF(LAG(avg_price) OVER (ORDER BY month), 0) as price_change_pct,

        (total_quantity - LAG(total_quantity) OVER (ORDER BY month)) /
            NULLIF(LAG(total_quantity) OVER (ORDER BY month), 0) as quantity_change_pct

    FROM price_quantity_data
    """

    df = pd.read_sql(sql, engine)

    # 计算弹性系数
    df['price_elasticity'] = df['quantity_change_pct'] / df['price_change_pct']

    # 回归分析(更准确)
    from scipy.stats import linregress
    log_price = np.log(df['avg_price'])
    log_quantity = np.log(df['total_quantity'])
    slope, intercept, r_value, p_value, std_err = linregress(log_price, log_quantity)

    # 斜率即为价格弹性
    elasticity = slope

    return {
        'elasticity': elasticity,
        'interpretation': interpret_elasticity(elasticity),
        'r_squared': r_value ** 2,
        'monthly_elasticity': df[['month', 'price_elasticity']]
    }


def interpret_elasticity(elasticity):
    """
    解读价格弹性
    """
    if abs(elasticity) > 1.5:
        return "高度敏感 - 降价策略可能显著提升销量"
    elif abs(elasticity) > 1.0:
        return "中度敏感 - 价格是重要考虑因素"
    elif abs(elasticity) > 0.5:
        return "低度敏感 - 品牌忠诚度较高"
    else:
        return "极低敏感 - 可考虑提价策略"
```

### 4.2 价格竞争分析
```python
def analyze_price_competition(product_ids):
    """
    竞品价格对比分析

    分析维度:
    - 绝对价格水平
    - 价格变化趋势
    - 价格差异显著性
    - 价格战风险
    """

    sql = f"""
    WITH product_prices AS (
        SELECT
            product_id,
            product_name,
            manufacturer_name,
            toStartOfMonth(sale_date) as month,
            AVG(unit_price) as avg_price,
            SUM(sales_amount) as sales_amount
        FROM sales_data
        WHERE product_id IN ({','.join(product_ids)})
          AND sale_date >= today() - INTERVAL 12 MONTH
        GROUP BY product_id, product_name, manufacturer_name, month
    )
    SELECT
        product_id,
        product_name,
        manufacturer_name,
        month,
        avg_price,
        sales_amount,

        -- 计算相对价格(vs市场平均)
        avg_price / (SELECT AVG(avg_price) FROM product_prices pp WHERE pp.month = product_prices.month) as relative_price,

        -- 价格排名
        RANK() OVER (PARTITION BY month ORDER BY avg_price) as price_rank,

        -- 价格变化
        (avg_price - LAG(avg_price) OVER (PARTITION BY product_id ORDER BY month)) /
            NULLIF(LAG(avg_price) OVER (PARTITION BY product_id ORDER BY month), 0) as price_change_pct

    FROM product_prices
    ORDER BY month DESC, avg_price DESC
    """

    return pd.read_sql(sql, engine)
```

---

## 五、客户画像与细分

### 5.1 医院采购画像
```python
def create_hospital_profile(hospital_id):
    """
    医院采购画像分析

    维度:
    - 采购规模: 金额、品类数、供应商数
    - 采购偏好: 治疗领域、剂型、价段
    - 行为特征: 采购频率、议价能力、付款周期
    - 竞争态势: 主要供应商份额
    """

    sql = f"""
    WITH hospital_metrics AS (
        SELECT
            buyer_id,
            buyer_name,
            hospital_level,

            -- 采购规模
            COUNT(DISTINCT sale_date) as purchase_frequency,
            COUNT(DISTINCT product_id) as product_variety,
            COUNT(DISTINCT manufacturer_id) as supplier_count,
            SUM(sales_amount) as total_purchase_amount,
            AVG(sales_amount) as avg_purchase_amount,

            -- 采购偏好
            mode() WITHIN GROUP (ORDER BY category_l1) as preferred_category,
            mode() WITHIN GROUP (ORDER BY manufacturer_name) as preferred_supplier,

            -- 价格敏感度
            AVG(discount_amount / NULLIF(sales_amount, 0)) as avg_discount_rate,

            -- 采购集中度
            STDDEV(sales_amount) / AVG(sales_amount) as purchase_concentration

        FROM sales_data
        WHERE buyer_id = '{hospital_id}'
          AND sale_date >= today() - INTERVAL 12 MONTH
        GROUP BY buyer_id, buyer_name, hospital_level
    ),
    supplier_share AS (
        SELECT
            manufacturer_name,
            SUM(sales_amount) as supplier_amount,
            SUM(sales_amount) / (SELECT SUM(sales_amount) FROM sales_data WHERE buyer_id = '{hospital_id}') as share
        FROM sales_data
        WHERE buyer_id = '{hospital_id}'
          AND sale_date >= today() - INTERVAL 12 MONTH
        GROUP BY manufacturer_name
        ORDER BY supplier_amount DESC
        LIMIT 10
    )
    SELECT
        h.*,
        (SELECT ARRAY_agg(manufacturer_name || ':' || share::text)
         FROM supplier_share) as top_suppliers
    FROM hospital_metrics h
    """

    return pd.read_sql(sql, engine)
```

---

## 六、总结

### 核心算法模块清单

| 模块 | 算法 | 应用场景 | 数据需求 |
|------|------|---------|---------|
| **市场份额** | SQL聚合计算 | 竞品分析 | 销售数据 |
| **销售预测** | ARIMA/Prophet/XGBoost | 需求预测 | 历史12个月+数据 |
| **异常检测** | 3-Sigma/IsoForest/STL | 实时监控 | 最近90天数据 |
| **机会识别** | 多指标综合评分 | 战略规划 | 增长率+规模+竞争+渗透率 |
| **价格弹性** | 线性回归 | 定价策略 | 价格+销量时序数据 |
| **客户画像** | 聚类分析 | 精准营销 | 采购行为数据 |

### 性能优化建议

1. **数据预聚合**: 创建物化视图存储月度/季度汇总数据
2. **增量计算**: 只计算变化部分,避免全量重算
3. **缓存策略**: Redis缓存热门查询结果(TTL=1小时)
4. **并行计算**: 大规模分析使用Spark分布式计算
5. **异步任务**: 耗时分析任务放入Celery队列异步执行
