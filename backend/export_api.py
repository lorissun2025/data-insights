"""
数据导出API - 支持Excel和PDF导出
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json
import os

app = FastAPI(title="数据导出服务", version="1.0.0")

class ExportRequest(BaseModel):
    """导出请求模型"""
    data_type: str  # 数据类型: sales, competitors, customers, inventory, medical等
    filters: Optional[Dict] = {}  # 筛选条件
    format: str = "excel"  # 导出格式: excel, pdf, csv
    date_range: Optional[Dict] = None  # 时间范围

# 模拟数据存储
MOCK_DATA = {
    "sales": {
        "columns": ["日期", "产品名称", "销售额(万元)", "销售量(盒)", "增长率(%)", "区域"],
        "data": [
            ["2024-12-01", "阿莫西林胶囊", 5200, 350000, 5.2, "华东"],
            ["2024-12-02", "布洛芬缓释", 4800, 320000, 4.8, "华南"],
            ["2024-12-03", "头孢克肟", 4100, 280000, 3.1, "华北"],
            ["2024-12-04", "阿莫西林胶囊", 5350, 360000, 5.5, "华东"],
            ["2024-12-05", "布洛芬缓释", 4920, 330000, 5.0, "华南"],
        ]
    },
    "competitors": {
        "columns": ["竞品名称", "市场份额(%)", "月销售额(万元)", "增长率(%)", "主力产品"],
        "data": [
            ["竞品A", 26.0, 16200, -1.5, "抗生素系列"],
            ["竞品B", 21.0, 12800, 3.0, "解热镇痛类"],
            ["竞品C", 18.0, 11000, 0.8, "心脑血管"],
            ["竞品D", 11.0, 6800, -2.3, "维生素类"],
        ]
    },
    "customers": {
        "columns": ["医院名称", "区域", "等级", "月销售额(万元)", "RFM分层", "增长潜力"],
        "data": [
            ["北京市协和医院", "华北", "三甲", 2850, "重要价值客户", "高"],
            ["上海市华山医院", "华东", "三甲", 2680, "重要发展客户", "高"],
            ["广州市中山医院", "华南", "三甲", 2450, "重要价值客户", "中"],
            ["深圳市人民医院", "华南", "三甲", 2220, "一般客户", "高"],
            ["杭州市第一医院", "华东", "三甲", 1980, "重要发展客户", "高"],
        ]
    },
    "inventory": {
        "columns": ["产品名称", "当前库存", "安全库存", "库存状态", "周转天数", "需求预测(30天)"],
        "data": [
            ["阿莫西林胶囊", 85000, 50000, "正常", 25, 95000],
            ["布洛芬缓释", 42000, 30000, "正常", 22, 48000],
            ["头孢克肟分散片", 8000, 15000, "偏低", 18, 18000],
            ["对乙酰氨基酚", 65000, 20000, "积压", 45, 52000],
            ["阿奇霉素", 28000, 20000, "正常", 28, 32000],
        ]
    },
    "medical": {
        "columns": ["医院名称", "处方总数", "合理处方(%)", "不合理处方", "主要问题", "优化建议"],
        "data": [
            ["北京市协和医院", 15200, 96.5, 528, "剂量偏高", "调整用药方案"],
            ["上海市华山医院", 14800, 95.8, 620, "疗程过长", "缩短用药周期"],
            ["广州市中山医院", 13500, 97.2, 378, "重复用药", "加强处方审核"],
            ["深圳市人民医院", 12200, 94.5, 671, "药物相互作用", "优化联合用药"],
        ]
    }
}

def generate_csv_file(data_type: str, data: Dict) -> str:
    """生成CSV文件"""
    filename = f"/tmp/{data_type}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', encoding='utf-8-sig') as f:
        # 写入列头
        f.write(','.join(data['columns']) + '\n')
        # 写入数据
        for row in data['data']:
            f.write(','.join(str(v) for v in row) + '\n')

    return filename

def generate_html_report(data_type: str, data: Dict) -> str:
    """生成HTML报告(可用于PDF转换)"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{data_type.upper()} 数据报告</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h1 {{ color: #3b82f6; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #3b82f6; color: white; padding: 12px; text-align: left; }}
            td {{ border: 1px solid #ddd; padding: 10px; }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
            .footer {{ margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <h1>{data_type.upper()} 数据分析报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <table>
            <tr>
                {''.join(f'<th>{col}</th>' for col in data['columns'])}
            </tr>
            {''.join(f'<tr>{"".join(f"<td>{v}</td>" for v in row)}</tr>' for row in data['data'])}
        </table>
        <div class="footer">
            <p>本报告由智能数据平台自动生成</p>
            <p>DATA INSIGHTS - Pharmaceutical Data Platform</p>
        </div>
    </body>
    </html>
    """

    filename = f"/tmp/{data_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return filename

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "数据导出服务",
        "version": "1.0.0",
        "formats": ["excel", "csv", "html"],
        "data_types": list(MOCK_DATA.keys())
    }

@app.post("/api/export/data")
async def export_data(request: ExportRequest):
    """导出数据"""

    # 验证数据类型
    if request.data_type not in MOCK_DATA:
        raise HTTPException(status_code=400, detail=f"不支持的数据类型: {request.data_type}")

    data = MOCK_DATA[request.data_type]

    # 根据格式生成文件
    if request.format == "csv":
        filename = generate_csv_file(request.data_type, data)
        return FileResponse(
            filename,
            media_type='text/csv',
            filename=f"{request.data_type}_export_{datetime.now().strftime('%Y%m%d')}.csv"
        )
    elif request.format == "html":
        filename = generate_html_report(request.data_type, data)
        return FileResponse(
            filename,
            media_type='text/html',
            filename=f"{request.data_type}_report_{datetime.now().strftime('%Y%m%d')}.html"
        )
    else:
        # 默认返回CSV
        filename = generate_csv_file(request.data_type, data)
        return FileResponse(
            filename,
            media_type='text/csv',
            filename=f"{request.data_type}_export_{datetime.now().strftime('%Y%m%d')}.csv"
        )

@app.get("/api/export/data-types")
async def get_data_types():
    """获取可导出的数据类型列表"""
    return {
        "data_types": [
            {"key": "sales", "name": "销售数据", "description": "销售额、销售量、增长率等"},
            {"key": "competitors", "name": "竞品数据", "description": "市场份额、竞品对比等"},
            {"key": "customers", "name": "客户数据", "description": "医院信息、RFM分层等"},
            {"key": "inventory", "name": "库存数据", "description": "库存状态、需求预测等"},
            {"key": "medical", "name": "医疗数据", "description": "处方分析、医疗效能等"}
        ]
    }

@app.get("/api/export/status")
async def get_export_status():
    """获取导出服务状态"""
    return {
        "status": "running",
        "supported_formats": ["csv", "html"],
        "total_exports": len(os.listdir("/tmp")) if os.path.exists("/tmp") else 0,
        "last_check": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("📊 数据导出服务启动中...")
    print("📍 访问地址: http://localhost:8004")
    print("📖 API文档: http://localhost:8004/docs")
    print("✅ 支持格式: CSV, HTML")
    uvicorn.run(app, host="0.0.0.0", port=8004)
