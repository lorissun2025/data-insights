/**
 * 医药市场洞察仪表盘 - 主界面组件
 * 技术栈: React 18 + TypeScript + ECharts 5 + Ant Design
 */

import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Select, DatePicker, Button, Spin } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import * as echarts from 'echarts';
import axios from 'axios';

const { RangePicker } = DatePicker;
const { Option } = Select;

interface DashboardProps {
  companyId: string;
}

interface KPICard {
  title: string;
  value: number;
  unit: string;
  growth: number;
  trend: 'up' | 'down';
}

const MarketInsightsDashboard: React.FC<DashboardProps> = ({ companyId }) => {
  // 状态管理
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState<[any, any]>([
    moment().subtract(12, 'months'),
    moment()
  ]);
  const [selectedProduct, setSelectedProduct] = useState<string>('all');

  // KPI数据
  const [kpis, setKpis] = useState<KPICard[]>([]);

  // 图表实例引用
  const salesTrendChartRef = React.useRef<HTMLDivElement>(null);
  const marketShareChartRef = React.useRef<HTMLDivElement>(null);
  const competitorChartRef = React.useRef<HTMLDivElement>(null);
  const regionalMapChartRef = React.useRef<HTMLDivElement>(null);

  // 获取仪表盘数据
  useEffect(() => {
    fetchDashboardData();
  }, [companyId, dateRange, selectedProduct]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/v1/dashboard/overview', {
        params: {
          company_id: companyId,
          date_range: '12m'
        }
      });

      setKpis(response.data.kpis);
      renderCharts(response.data);
    } catch (error) {
      console.error('获取数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 渲染所有图表
  const renderCharts = (data: any) => {
    renderSalesTrendChart(data.salesTrend);
    renderMarketShareChart(data.marketShare);
    renderCompetitorChart(data.competitorData);
    renderRegionalMapChart(data.regionalData);
  };

  /**
   * 图表1: 销售趋势图 (折线图 + 柱状图)
   */
  const renderSalesTrendChart = (trendData: any[]) => {
    const chart = echarts.init(salesTrendChartRef.current!);

    const option = {
      title: {
        text: '销售趋势',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        }
      },
      legend: {
        data: ['销售额', '销售量', '预测销售额'],
        top: 30
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: trendData.map((item: any) => item.month)
      },
      yAxis: [
        {
          type: 'value',
          name: '销售额 (万元)',
          position: 'left'
        },
        {
          type: 'value',
          name: '销售量 (万盒)',
          position: 'right'
        }
      ],
      series: [
        {
          name: '销售额',
          type: 'line',
          smooth: true,
          data: trendData.map((item: any) => item.sales_amount),
          itemStyle: {
            color: '#5470C6'
          },
          areaStyle: {
            opacity: 0.3
          }
        },
        {
          name: '销售量',
          type: 'bar',
          yAxisIndex: 1,
          data: trendData.map((item: any) => item.sales_quantity),
          itemStyle: {
            color: '#91CC75'
          }
        },
        {
          name: '预测销售额',
          type: 'line',
          smooth: true,
          data: trendData.map((item: any) => item.forecast_amount || null),
          lineStyle: {
            type: 'dashed'
          },
          itemStyle: {
            color: '#FAC858'
          }
        }
      ]
    };

    chart.setOption(option);

    // 响应式
    window.addEventListener('resize', () => chart.resize());
  };

  /**
   * 图表2: 市场份额趋势 (堆叠面积图)
   */
  const renderMarketShareChart = (marketShareData: any[]) => {
    const chart = echarts.init(marketShareChartRef.current!);

    const option = {
      title: {
        text: '市场份额变化趋势',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          label: {
            backgroundColor: '#6a7985'
          }
        }
      },
      legend: {
        data: marketShareData.map((item: any) => item.company_name),
        top: 30
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06']
      },
      yAxis: {
        type: 'value',
        name: '市场份额 (%)',
        max: 100
      },
      series: marketShareData.map((company: any) => ({
        name: company.company_name,
        type: 'line',
        smooth: true,
        stack: 'Total',
        areaStyle: {},
        emphasis: {
          focus: 'series'
        },
        data: company.market_share_history
      }))
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
  };

  /**
   * 图表3: 竞品对比雷达图
   */
  const renderCompetitorChart = (competitorData: any) => {
    const chart = echarts.init(competitorChartRef.current!);

    const option = {
      title: {
        text: '竞品综合对比',
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        data: competitorData.companies.map((c: any) => c.name),
        top: 30
      },
      radar: {
        indicator: [
          { name: '市场份额', max: 100 },
          { name: '增长率', max: 50 },
          { name: '价格竞争力', max: 100 },
          { name: '市场覆盖率', max: 100 },
          { name: '客户满意度', max: 100 },
          { name: '品牌影响力', max: 100 }
        ],
        shape: 'circle',
        splitNumber: 5,
        axisName: {
          color: '#6A7D8F'
        },
        splitLine: {
          lineStyle: {
            color: [
              'rgba(238, 197, 102, 0.1)',
              'rgba(238, 197, 102, 0.2)',
              'rgba(238, 197, 102, 0.4)',
              'rgba(238, 197, 102, 0.6)',
              'rgba(238, 197, 102, 0.8)',
              'rgba(238, 197, 102, 1)'
            ].reverse()
          }
        },
        splitArea: {
          show: false
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(238, 197, 102, 0.5)'
          }
        }
      },
      series: [
        {
          name: '竞品对比',
          type: 'radar',
          lineStyle: {
            width: 2
          },
          data: competitorData.companies.map((company: any) => ({
            value: company.scores,
            name: company.name,
            areaStyle: {
              opacity: 0.3
            }
          }))
        }
      ]
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
  };

  /**
   * 图表4: 区域市场热力图
   */
  const renderRegionalMapChart = (regionalData: any[]) => {
    const chart = echarts.init(regionalMapChartRef.current!);

    const option = {
      title: {
        text: '区域市场表现',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: params => {
          return `${params.name}<br/>销售额: ${params.value[1]}万元<br/>增长率: ${params.value[2]}%`;
        }
      },
      visualMap: {
        min: 0,
        max: 10000,
        left: 'left',
        top: 'bottom',
        text: ['高', '低'],
        calculable: true,
        inRange: {
          color: ['#50a3ba', '#eac736', '#d94e5d']
        }
      },
      grid: {
        right: '10%',
        top: '15%',
        bottom: '10%'
      },
      xAxis: {
        type: 'category',
        data: regionalData.map((item: any) => item.province),
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'category',
        data: ['增长迅速', '稳定增长', '持平', '下降'],
        axisLabel: {
          rotate: 0
        }
      },
      series: [
        {
          name: '区域表现',
          type: 'scatter',
          symbolSize: function (data: any) {
            return Math.sqrt(data[1]) / 3;
          },
          data: regionalData.map((item: any) => [
            item.province_index,
            item.growth_category_index,
            item.sales_amount,
            item.growth_rate
          ]),
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(120, 36, 50, 0.5)',
            shadowOffsetY: 5,
            color: params => {
              const growthRate = params.data[3];
              return growthRate > 20 ? '#ee6666' : growthRate > 10 ? '#5470c6' : '#91cc75';
            }
          },
          label: {
            show: true,
            formatter: params => params.data[0],
            position: 'top'
          }
        }
      ]
    };

    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
  };

  /**
   * KPI卡片组件
   */
  const KPICard: React.FC<KPICard> = ({ title, value, unit, growth, trend }) => (
    <Card className="kpi-card" style={{ marginBottom: 16 }}>
      <div className="kpi-title">{title}</div>
      <div className="kpi-value">
        <span className="value">{value.toLocaleString()}</span>
        <span className="unit">{unit}</span>
      </div>
      <div className={`kpi-growth ${trend === 'up' ? 'growth-up' : 'growth-down'}`}>
        {trend === 'up' ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
        <span>{Math.abs(growth).toFixed(2)}%</span>
        <span className="vs-previous">vs 上期</span>
      </div>
    </Card>
  );

  return (
    <div className="market-insights-dashboard">
      {/* 筛选工具栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col span={6}>
            <label>产品筛选:</label>
            <Select
              style={{ width: '100%' }}
              value={selectedProduct}
              onChange={setSelectedProduct}
            >
              <Option value="all">全部产品</Option>
              <Option value="prod001">阿莫西林胶囊</Option>
              <Option value="prod002">布洛芬缓释胶囊</Option>
              <Option value="prod003">奥美拉唑肠溶胶囊</Option>
            </Select>
          </Col>
          <Col span={8}>
            <label>时间范围:</label>
            <RangePicker
              style={{ width: '100%' }}
              value={dateRange}
              onChange={(dates: any) => setDateRange(dates)}
            />
          </Col>
          <Col span={4}>
            <Button type="primary" onClick={fetchDashboardData} loading={loading}>
              刷新数据
            </Button>
          </Col>
        </Row>
      </Card>

      <Spin spinning={loading}>
        {/* KPI总览卡片 */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <KPICard
              title="总销售额"
              value={kpis[0]?.value || 0}
              unit="万元"
              growth={kpis[0]?.growth || 0}
              trend={kpis[0]?.trend || 'up'}
            />
          </Col>
          <Col span={6}>
            <KPICard
              title="总销售量"
              value={kpis[1]?.value || 0}
              unit="万盒"
              growth={kpis[1]?.growth || 0}
              trend={kpis[1]?.trend || 'up'}
            />
          </Col>
          <Col span={6}>
            <KPICard
              title="市场份额"
              value={kpis[2]?.value || 0}
              unit="%"
              growth={kpis[2]?.growth || 0}
              trend={kpis[2]?.trend || 'up'}
            />
          </Col>
          <Col span={6}>
            <KPICard
              title="覆盖医院数"
              value={kpis[3]?.value || 0}
              unit="家"
              growth={kpis[3]?.growth || 0}
              trend={kpis[3]?.trend || 'up'}
            />
          </Col>
        </Row>

        {/* 第一行图表: 销售趋势 + 市场份额 */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={12}>
            <Card title="销售趋势" bordered={false}>
              <div ref={salesTrendChartRef} style={{ height: 350 }}></div>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="市场份额变化" bordered={false}>
              <div ref={marketShareChartRef} style={{ height: 350 }}></div>
            </Card>
          </Col>
        </Row>

        {/* 第二行图表: 竞品对比 + 区域热力图 */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={12}>
            <Card title="竞品综合对比" bordered={false}>
              <div ref={competitorChartRef} style={{ height: 350 }}></div>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="区域市场表现" bordered={false}>
              <div ref={regionalMapChartRef} style={{ height: 350 }}></div>
            </Card>
          </Col>
        </Row>

        {/* 机会识别列表 */}
        <Row gutter={16}>
          <Col span={24}>
            <Card title="市场机会识别" bordered={false}>
              <Table
                columns={[
                  { title: '区域', dataIndex: 'region', key: 'region' },
                  { title: '城市', dataIndex: 'city', key: 'city' },
                  { title: '市场规模', dataIndex: 'marketSize', key: 'marketSize', render: val => `${val}万元` },
                  { title: '增长率', dataIndex: 'growthRate', key: 'growthRate', render: val => `${val}%` },
                  { title: '竞争强度', dataIndex: 'competitorCount', key: 'competitorCount', render: val => `${val}家` },
                  { title: '渗透率', dataIndex: 'penetrationRate', key: 'penetrationRate', render: val => `${val}%` },
                  { title: '机会得分', dataIndex: 'score', key: 'score', render: val => <Progress percent={val} size="small" /> },
                  { title: '建议', dataIndex: 'recommendation', key: 'recommendation' }
                ]}
                dataSource={marketOpportunities}
                pagination={{ pageSize: 10 }}
              />
            </Card>
          </Col>
        </Row>
      </Spin>

      <style jsx>{`
        .market-insights-dashboard {
          padding: 24px;
          background: #f0f2f5;
          min-height: 100vh;
        }

        .kpi-card {
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .kpi-title {
          font-size: 14px;
          color: #8c8c8c;
          margin-bottom: 8px;
        }

        .kpi-value {
          display: flex;
          align-items: baseline;
          margin-bottom: 8px;
        }

        .kpi-value .value {
          font-size: 28px;
          font-weight: bold;
          color: #262626;
        }

        .kpi-value .unit {
          font-size: 14px;
          color: #8c8c8c;
          margin-left: 4px;
        }

        .kpi-growth {
          display: flex;
          align-items: center;
          font-size: 12px;
        }

        .kpi-growth.growth-up {
          color: #52c41a;
        }

        .kpi-growth.growth-down {
          color: #f5222d;
        }

        .vs-previous {
          color: #8c8c8c;
          margin-left: 4px;
        }
      `}</style>
    </div>
  );
};

export default MarketInsightsDashboard;
