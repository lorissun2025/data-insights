-- =====================================================
-- 医药市场洞察模块 - 数据库设计 (ClickHouse)
-- =====================================================

-- ============================================
-- 1. 销售数据表 (sales_data)
-- ============================================
CREATE TABLE IF NOT EXISTS sales_data (
    -- 主键和维度
    sale_id String COMMENT '销售记录ID',
    sale_date Date COMMENT '销售日期',
    sale_time DateTime COMMENT '销售时间戳',

    -- 产品维度
    product_id String COMMENT '产品ID',
    product_name String COMMENT '产品名称',
    generic_name String COMMENT '通用名',
    manufacturer_id String COMMENT '生产企业ID',
    manufacturer_name String COMMENT '生产企业名称',
    brand String COMMENT '品牌',
    dosage_form String COMMENT '剂型(片剂/注射剂等)',
    specification String COMMENT '规格',
    category_l1 String COMMENT '一级分类(治疗领域)',
    category_l2 String COMMENT '二级分类',
    category_l3 String COMMENT '三级分类',
    is_prescription_drug UInt8 COMMENT '是否处方药 1-是 0-否',
    is_otc UInt8 COMMENT '是否OTC 1-是 0-否',

    -- 销售维度
    seller_id String COMMENT '销售方ID(药企/流通商)',
    seller_name String COMMENT '销售方名称',
    seller_type String COMMENT '销售方类型(药企/流通商/药店)',
    sales_channel String COMMENT '销售渠道(医院/药店/电商)',
    sales_region String COMMENT '销售大区(华东/华南等)',
    sales_province String COMMENT '销售省份',
    sales_city String COMMENT '销售城市',
    sales_district String COMMENT '销售区县',

    -- 采购方维度
    buyer_id String COMMENT '采购方ID',
    buyer_name String COMMENT '采购方名称',
    buyer_type String COMMENT '采购方类型(医院/药店/诊所)',
    hospital_level String COMMENT '医院等级(三甲/二甲等)',
    hospital_type String COMMENT '医院类型(综合/专科)',

    -- 销售指标
    sales_quantity Decimal(18, 2) COMMENT '销售数量(最小单位)',
    sales_amount Decimal(18, 2) COMMENT '销售金额(元)',
    unit_price Decimal(18, 2) COMMENT '单价(元)',
    discount_amount Decimal(18, 2) COMMENT '折扣金额',
    actual_amount Decimal(18, 2) COMMENT '实际金额',

    -- 其他
    data_source String COMMENT '数据来源',
    create_time DateTime DEFAULT now() COMMENT '数据创建时间',
    update_time DateTime DEFAULT now() COMMENT '数据更新时间'
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(sale_date)
ORDER BY (sale_date, product_id, sales_province, sales_city)
SETTINGS index_granularity = 8192;

-- 创建索引以加速查询
-- ALTER TABLE sales_data ADD INDEX idx_product_name product_name TYPE minmax GRANULARITY 4;
-- ALTER TABLE sales_data ADD INDEX idx_manufacturer manufacturer_name TYPE minmax GRANULARITY 4;


-- ============================================
-- 2. 流通数据表 (distribution_data)
-- ============================================
CREATE TABLE IF NOT EXISTS distribution_data (
    -- 主键和维度
    dist_id String COMMENT '流通记录ID',
    dist_date Date COMMENT '流通日期',
    dist_time DateTime COMMENT '流通时间戳',

    -- 产品维度
    product_id String COMMENT '产品ID',
    product_name String COMMENT '产品名称',
    manufacturer_id String COMMENT '生产企业ID',
    manufacturer_name String COMMENT '生产企业名称',

    -- 流通链路
    upstream_id String COMMENT '上游企业ID',
    upstream_name String COMMENT '上游企业名称',
    upstream_type String COMMENT '上游类型',

    downstream_id String COMMENT '下游企业ID',
    downstream_name String COMMENT '下游企业名称',
    downstream_type String COMMENT '下游类型',

    -- 物流维度
    origin_province String COMMENT '发货省份',
    origin_city String COMMENT '发货城市',
    destination_province String COMMENT '收货省份',
    destination_city String COMMENT '收货城市',
    transport_type String COMMENT '运输方式',
    transport_distance Decimal(10, 2) COMMENT '运输距离(km)',

    -- 流通指标
    quantity Decimal(18, 2) COMMENT '流通数量',
    amount Decimal(18, 2) COMMENT '流通金额',
    logistics_cost Decimal(18, 2) COMMENT '物流成本',
    lead_time_days UInt16 COMMENT '在途天数',

    -- 其他
    batch_no String COMMENT '批次号',
    data_source String COMMENT '数据来源',
    create_time DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(dist_date)
ORDER BY (dist_date, product_id, origin_province, destination_province)
SETTINGS index_granularity = 8192;


-- ============================================
-- 3. 处方数据表 (prescription_data)
-- ============================================
CREATE TABLE IF NOT EXISTS prescription_data (
    -- 主键和维度
    prescription_id String COMMENT '处方ID',
    prescription_date Date COMMENT '处方日期',
    visit_time DateTime COMMENT '就诊时间',

    -- 患者维度(脱敏)
    patient_id_hash String COMMENT '患者ID(哈希加密)',
    patient_age UInt8 COMMENT '患者年龄',
    patient_gender UInt8 COMMENT '患者性别 1-男 2-女',
    patient_city String COMMENT '患者所在城市',
    insurance_type String COMMENT '医保类型(城镇职工/城乡居民/自费)',

    -- 医生维度
    doctor_id String COMMENT '医生ID',
    doctor_name String COMMENT '医生姓名',
    doctor_title String COMMENT '职称',
    department String COMMENT '科室',
    hospital_id String COMMENT '医院ID',
    hospital_name String COMMENT '医院名称',
    hospital_level String COMMENT '医院等级',
    hospital_province String COMMENT '医院所在省份',
    hospital_city String COMMENT '医院所在城市',

    -- 诊断维度
    diagnosis_code String COMMENT '诊断编码(ICD-10)',
    diagnosis_name String COMMENT '诊断名称',
    is_chronic_disease UInt8 COMMENT '是否慢性病',

    -- 处方药品(一对多，这里设计为明细表)
    drug_id String COMMENT '药品ID',
    drug_name String COMMENT '药品名称',
    generic_name String COMMENT '通用名',
    manufacturer String COMMENT '生产企业',
    dosage_form String COMMENT '剂型',
    specification String COMMENT '规格',
    quantity Decimal(10, 2) COMMENT '数量',
    days_supply UInt16 COMMENT '给药天数',
    dosage String COMMENT '用法用量',
    unit_price Decimal(18, 2) COMMENT '单价',
    total_amount Decimal(18, 2) COMMENT '总金额',

    -- 处方指标
    is_national_essential_drug UInt8 COMMENT '是否国家基本药物',
    is_reimbursable UInt8 COMMENT '是否医保报销',
    insurance_ratio Decimal(5, 2) COMMENT '医保报销比例(%)',

    -- 其他
    data_source String COMMENT '数据来源',
    create_time DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(prescription_date)
ORDER BY (prescription_date, hospital_id, doctor_id, drug_id)
SETTINGS index_granularity = 8192;


-- ============================================
-- 4. 患者数据表 (patient_data) - 已脱敏
-- ============================================
CREATE TABLE IF NOT EXISTS patient_data (
    -- 患者维度(脱敏)
    patient_id_hash String COMMENT '患者ID(哈希)',
    patient_age_group String COMMENT '年龄段(0-18/19-35/36-50/51-65/65+)',
    patient_gender UInt8 COMMENT '性别',
    patient_province String COMMENT '省份',
    patient_city String COMMENT '城市',
    patient_city_tier String COMMENT '城市等级(一线/二线/三线/四线及以下)',
    insurance_type String COMMENT '医保类型',

    -- 就诊记录(汇总指标)
    total_visits UInt32 COMMENT '总就诊次数',
    total_prescriptions UInt32 COMMENT '总处方数',
    total_amount Decimal(18, 2) COMMENT '总医疗费用',
    avg_amount_per_visit Decimal(18, 2) COMMENT '次均费用',

    -- 疾病维度
    primary_diagnosis String COMMENT '主要诊断',
    chronic_diseases Array(String) COMMENT '慢性病标签',
    is_chronic_patient UInt8 COMMENT '是否慢性病患者',

    -- 用药维度
    total_drugs_used UInt32 COMMENT '用药种类数',
    most_used_drug String COMMENT '最常使用药品',
    drug_categories Array(String) COMMENT '用药类别',

    -- 行为维度
    avg_days_between_visits Decimal(10, 2) COMMENT '平均就诊间隔(天)',
    compliance_score Decimal(5, 2) COMMENT '依从性评分(0-100)',

    -- 统计周期
    stat_month String COMMENT '统计月份(YYYYMM)',
    stat_quarter String COMMENT '统计季度(YYYYQQ)',
    stat_year String COMMENT '统计年份(YYYY)',

    update_time DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY stat_year
ORDER BY (stat_year, stat_month, patient_city, primary_diagnosis)
SETTINGS index_granularity = 8192;


-- ============================================
-- 5. 竞品数据聚合表 (competitor_analysis)
-- ============================================
CREATE TABLE IF NOT EXISTS competitor_analysis (
    -- 时间维度
    stat_date Date COMMENT '统计日期',
    stat_month String COMMENT '统计月份',
    stat_quarter String COMMENT '统计季度',
    stat_year String COMMENT '统计年份',

    -- 产品维度
    product_id String COMMENT '产品ID',
    product_name String COMMENT '产品名称',
    generic_name String COMMENT '通用名',
    category_l1 String COMMENT '一级分类',
    manufacturer_id String COMMENT '生产企业ID',
    manufacturer_name String COMMENT '生产企业名称',

    -- 区域维度
    region String COMMENT '大区',
    province String COMMENT '省份',
    city String COMMENT '城市',

    -- 市场指标
    total_sales_amount Decimal(18, 2) COMMENT '总销售额',
    total_sales_quantity Decimal(18, 2) COMMENT '总销售量',
    market_share Decimal(5, 2) COMMENT '市场份额(%)',
    market_share_rank UInt16 COMMENT '市场份额排名',
    mom_growth Decimal(8, 2) COMMENT '环比增长率(%)',
    yoy_growth Decimal(8, 2) COMMENT '同比增长率(%)',

    -- 竞争指标
    avg_price Decimal(18, 2) COMMENT '平均价格',
    price_vs_market_avg Decimal(5, 2) COMMENT 'vs市场均价(%)',
    distribution_coverage Decimal(5, 2) COMMENT '铺货率(%)',
    hospital_penetration UInt32 COMMENT '覆盖医院数',

    -- 更新时间
    update_time DateTime DEFAULT now()
)
ENGINE = AggregatingMergeTree()
PARTITION BY (stat_year, stat_month)
ORDER BY (stat_date, category_l1, manufacturer_id, province)
SETTINGS index_granularity = 8192;


-- ============================================
-- 6. 市场预测结果表 (market_forecast)
-- ============================================
CREATE TABLE IF NOT EXISTS market_forecast (
    -- 预测维度
    forecast_id String COMMENT '预测ID',
    forecast_date Date COMMENT '预测生成日期',
    model_name String COMMENT '预测模型名称',
    model_version String COMMENT '模型版本',

    -- 时间维度
    target_date Date COMMENT '预测目标日期',
    target_month String COMMENT '预测目标月份',
    target_quarter String COMMENT '预测目标季度',

    -- 产品维度
    product_id String COMMENT '产品ID',
    product_name String COMMENT '产品名称',
    category_l1 String COMMENT '一级分类',
    manufacturer_id String COMMENT '生产企业ID',

    -- 区域维度
    region String COMMENT '大区',
    province String COMMENT '省份',

    -- 预测结果
    forecast_sales_amount Decimal(18, 2) COMMENT '预测销售额',
    forecast_sales_quantity Decimal(18, 2) COMMENT '预测销售量',
    forecast_lower_bound Decimal(18, 2) COMMENT '预测下限(95%置信区间)',
    forecast_upper_bound Decimal(18, 2) COMMENT '预测上限(95%置信区间)',

    -- 模型指标
    prediction_confidence Decimal(5, 2) COMMENT '预测置信度(%)',
    model_accuracy Decimal(5, 2) COMMENT '历史准确率(%)',

    -- 其他
    create_time DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(target_date)
ORDER BY (target_date, product_id, province)
SETTINGS index_granularity = 8192;


-- ============================================
-- 7. 用户行为日志表 (user_behavior_log) - 用于产品优化
-- ============================================
CREATE TABLE IF NOT EXISTS user_behavior_log (
    log_id String COMMENT '日志ID',
    event_time DateTime COMMENT '事件时间',

    -- 用户维度
    user_id String COMMENT '用户ID',
    company_id String COMMENT '企业ID',
    user_role String COMMENT '用户角色',

    -- 事件维度
    event_type String COMMENT '事件类型(view/click/export/share)',
    page_name String COMMENT '页面名称',
    module_name String COMMENT '模块名称',

    -- 内容维度
    content_id String COMMENT '内容ID(产品ID/报告ID等)',
    content_type String COMMENT '内容类型',

    -- 其他
    ip_address String COMMENT 'IP地址',
    device_type String COMMENT '设备类型',
    user_agent String COMMENT '浏览器信息',

    create_time DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id, event_type)
SETTINGS index_granularity = 8192;


-- ============================================
-- 8. 数据更新日志表 (data_update_log)
-- ============================================
CREATE TABLE IF NOT EXISTS data_update_log (
    log_id String COMMENT '日志ID',
    table_name String COMMENT '表名',
    update_type String COMMENT '更新类型(insert/update/delete)',
    update_time DateTime DEFAULT now() COMMENT '更新时间',
    affected_rows UInt32 COMMENT '影响行数',
    data_source String COMMENT '数据来源',
    status String COMMENT '状态(success/failed)',
    error_msg String COMMENT '错误信息',
    duration_ms UInt32 COMMENT '耗时(毫秒)'
)
ENGINE = MergeTree()
ORDER BY update_time
SETTINGS index_granularity = 8192;


-- ============================================
-- 创建视图(方便查询)
-- ============================================

-- 销售趋势月度汇总视图
CREATE MATERIALIZED VIEW IF NOT EXISTS sales_monthly_summary_mv
ENGINE = AggregatingMergeTree()
PARTITION BY stat_year
ORDER BY (stat_year, stat_month, product_id, manufacturer_id)
POPULATE
AS SELECT
    toYear(sale_date) as stat_year,
    toYYYYMM(sale_date) as stat_month,
    product_id,
    product_name,
    manufacturer_id,
    manufacturer_name,
    category_l1,
    sumState(sales_amount) as total_sales_amount,
    sumState(sales_quantity) as total_sales_quantity,
    avgState(unit_price) as avg_unit_price,
    countState(sale_id) as transaction_count
FROM sales_data
GROUP BY stat_year, stat_month, product_id, product_name, manufacturer_id, manufacturer_name, category_l1;

-- 地区销售汇总视图
CREATE MATERIALIZED VIEW IF NOT EXISTS sales_region_summary_mv
ENGINE = AggregatingMergeTree()
PARTITION BY stat_year
ORDER BY (stat_year, stat_month, sales_province, sales_city, category_l1)
POPULATE
AS SELECT
    toYear(sale_date) as stat_year,
    toYYYYMM(sale_date) as stat_month,
    sales_province,
    sales_city,
    category_l1,
    sumState(sales_amount) as total_sales_amount,
    sumState(sales_quantity) as total_sales_quantity,
    countState(seller_id) as seller_count
FROM sales_data
GROUP BY stat_year, stat_month, sales_province, sales_city, category_l1;
