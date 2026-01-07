"""
医疗效能优化模块 - 处方合理性分析与成本控制
"""

from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import random

security = HTTPBearer()
app = FastAPI(title="医疗效能优化API")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    from backend.app import verify_token as verify
    return verify(credentials)

# ============================================
# 数据模型
# ============================================

class PrescriptionAnalysis(BaseModel):
    prescription_id: str
    doctor_name: str
    department: str
    hospital_name: str
    patient_age: int
    diagnosis: str
    drugs: List[dict]
    rationality_score: float
    issues: List[str]
    suggestions: List[str]

class CostOptimization(BaseModel):
    hospital_name: str
    department: str
    current_cost: float
    optimized_cost: float
    savings: float
    savings_rate: float
    recommendations: List[str]

# ============================================
# 1. 处方合理性分析API
# ============================================

@app.get("/api/medical/prescription/analysis")
async def analyze_prescriptions(
    hospital_id: Optional[str] = None,
    department: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: str = Depends(verify_token)
):
    """
    处方合理性分析
    基于临床指南评估处方质量
    """
    prescriptions = [
        {
            "prescription_id": "RX20250107001",
            "doctor_name": "张医生",
            "department": "呼吸内科",
            "hospital_name": "北京协和医院",
            "patient_age": 45,
            "diagnosis": "急性支气管炎",
            "drugs": [
                {"name": "阿莫西林胶囊", "dose": "500mg", "frequency": "3次/日", "duration": "7天", "rational": True},
                {"name": "盐酸氨溴索口服液", "dose": "10ml", "frequency": "3次/日", "duration": "5天", "rational": True}
            ],
            "rationality_score": 95,
            "issues": [],
            "suggestions": ["处方符合指南,用药合理"]
        },
        {
            "prescription_id": "RX20250107002",
            "doctor_name": "李医生",
            "department": "心血管内科",
            "hospital_name": "上海瑞金医院",
            "patient_age": 62,
            "diagnosis": "高血压II级",
            "drugs": [
                {"name": "硝苯地平控释片", "dose": "30mg", "frequency": "1次/日", "duration": "30天", "rational": True},
                {"name": "阿司匹林肠溶片", "dose": "100mg", "frequency": "1次/日", "duration": "长期", "rational": True}
            ],
            "rationality_score": 98,
            "issues": [],
            "suggestions": ["规范用药,定期监测血压"]
        },
        {
            "prescription_id": "RX20250107003",
            "doctor_name": "王医生",
            "department": "儿科",
            "hospital_name": "广州中山医院",
            "patient_age": 5,
            "diagnosis": "上呼吸道感染",
            "drugs": [
                {"name": "阿莫西林颗粒", "dose": "125mg", "frequency": "3次/日", "duration": "5天", "rational": True},
                {"name": "布洛芬混悬液", "dose": "5ml", "frequency": "3次/日(必要时)", "duration": "3天", "rational": True},
                {"name": "头孢克肟分散片", "dose": "50mg", "frequency": "2次/日", "duration": "5天", "rational": False}
            ],
            "rationality_score": 72,
            "issues": ["重复用药:阿莫西林和头孢克肟均为抗生素", "儿童用药剂量偏高"],
            "suggestions": ["建议取消头孢克肟,单一抗生素治疗", "调整布洛芬剂量至3ml/次"]
        },
        {
            "prescription_id": "RX20250107004",
            "doctor_name": "刘医生",
            "department": "内分泌科",
            "hospital_name": "成都华西医院",
            "patient_age": 50,
            "diagnosis": "2型糖尿病",
            "drugs": [
                {"name": "二甲双胍缓释片", "dose": "500mg", "frequency": "2次/日", "duration": "长期", "rational": True},
                {"name": "胰岛素注射液", "dose": "10u", "frequency": "3次/日", "duration": "长期", "rational": True},
                {"name": "阿卡波糖片", "dose": "50mg", "frequency": "3次/日", "duration": "长期", "rational": True}
            ],
            "rationality_score": 92,
            "issues": ["三种降糖药联用,需密切监测血糖"],
            "suggestions": ["定期监测血糖,防止低血糖", "建议每3个月复查糖化血红蛋白"]
        }
    ]

    if hospital_id:
        prescriptions = [p for p in prescriptions if p["hospital_name"].find(hospital_id) != -1]
    if department:
        prescriptions = [p for p in prescriptions if p["department"] == department]

    return {"data": prescriptions}

@app.get("/api/medical/prescription/statistics")
async def get_prescription_statistics(
    current_user: str = Depends(verify_token)
):
    """
    处方统计概览
    """
    stats = {
        "total_prescriptions": 15230,
        "rational_prescriptions": 14580,
        "rationality_rate": 95.7,
        "avg_rationality_score": 92.5,
        "by_department": [
            {"department": "呼吸内科", "total": 2340, "rational": 2265, "rate": 96.8, "avg_score": 94.2},
            {"department": "心血管内科", "total": 3120, "rational": 3015, "rate": 96.6, "avg_score": 93.8},
            {"department": "内分泌科", "total": 1890, "rational": 1785, "rate": 94.4, "avg_score": 91.5},
            {"department": "儿科", "total": 2680, "rational": 2520, "rate": 94.0, "avg_score": 90.2},
            {"department": "消化内科", "total": 1560, "rational": 1510, "rate": 96.8, "avg_score": 94.5},
            {"department": "神经内科", "total": 1890, "rational": 1815, "rate": 96.0, "avg_score": 93.0},
            {"department": "急诊科", "total": 1750, "rational": 1670, "rate": 95.4, "avg_score": 92.0}
        ],
        "common_issues": [
            {"issue": "重复用药", "count": 185, "rate": 1.2},
            {"issue": "剂量不当", "count": 232, "rate": 1.5},
            {"issue": "疗程不当", "count": 158, "rate": 1.0},
            {"issue": "配伍禁忌", "count": 45, "rate": 0.3},
            {"issue": "超说明书用药", "count": 30, "rate": 0.2}
        ]
    }

    return stats

# ============================================
# 2. 成本优化API
# ============================================

@app.get("/api/medical/cost/optimization")
async def get_cost_optimization(
    hospital_id: Optional[str] = None,
    current_user: str = Depends(verify_token)
):
    """
    用药成本优化建议
    基于DRG/DIP支付标准
    """
    optimizations = [
        {
            "hospital_name": "北京协和医院",
            "department": "呼吸内科",
            "disease": "社区获得性肺炎",
            "current_cost": 8520,
            "optimized_cost": 6980,
            "savings": 1540,
            "savings_rate": 18.1,
            "recommendations": [
                "将莫西沙星(400mg)替换为左氧氟沙星(500mg),节省约680元",
                "调整抗生素疗程从10天缩短至7天,节省约420元",
                "优先使用国产仿制药替代原研药,节省约440元"
            ]
        },
        {
            "hospital_name": "上海瑞金医院",
            "department": "心血管内科",
            "disease": "高血压",
            "current_cost": 12350,
            "optimized_cost": 9850,
            "savings": 2500,
            "savings_rate": 20.2,
            "recommendations": [
                "优先选择氨氯地平替代硝苯地平控释片,节省约580元",
                "阿司匹林使用国产制剂,节省约320元",
                "常规检查优化,减少不必要的检查项目,节省约1600元"
            ]
        },
        {
            "hospital_name": "广州中山医院",
            "department": "内分泌科",
            "disease": "2型糖尿病",
            "current_cost": 15680,
            "optimized_cost": 12850,
            "savings": 2830,
            "savings_rate": 18.0,
            "recommendations": [
                "二甲双胍优先使用缓释片国产制剂,节省约450元",
                "胰岛素转为国产长效类似物,节省约1250元",
                "优化血糖监测频率,节省约1130元"
            ]
        }
    ]

    if hospital_id:
        optimizations = [o for o in optimizations if o["hospital_name"].find(hospital_id) != -1]

    return {"data": optimizations}

# ============================================
# 3. 患者流向分析API
# ============================================

@app.get("/api/medical/patient/flow")
async def get_patient_flow(
    region: Optional[str] = None,
    disease: Optional[str] = None,
    current_user: str = Depends(verify_token)
):
    """
    患者流向分析
    """
    patient_flow = {
        "total_patients": 15230,
        "flow_data": [
            {
                "from": "社区诊所",
                "to": "三甲医院",
                "count": 5230,
                "percentage": 34.3,
                "main_diseases": ["高血压", "糖尿病", "冠心病"]
            },
            {
                "from": "三甲医院",
                "to": "社区诊所",
                "count": 3120,
                "percentage": 20.5,
                "main_diseases": ["慢性病管理", "康复治疗"]
            },
            {
                "from": "下级医院",
                "to": "上级医院",
                "count": 4580,
                "percentage": 30.1,
                "main_diseases": ["肿瘤", "重症", "复杂手术"]
            },
            {
                "from": "上级医院",
                "to": "下级医院",
                "count": 2300,
                "percentage": 15.1,
                "main_diseases": ["康复", "慢病管理"]
            }
        ],
        "by_hospital_level": [
            {"level": "三级甲等", "inflow": 8920, "outflow": 2340},
            {"level": "三级乙等", "inflow": 4150, "outflow": 5120},
            {"level": "二级医院", "inflow": 1580, "outflow": 4890},
            {"level": "社区诊所", "inflow": 580, "outflow": 2880}
        ]
    }

    return patient_flow

# ============================================
# 4. 不良用药预警API
# ============================================

@app.get("/api/medical/alerts")
async def get_medical_alerts(
    severity: Optional[str] = None,
    current_user: str = Depends(verify_token)
):
    """
    不良用药预警
    """
    alerts = [
        {
            "alert_type": "drug_interaction",
            "severity": "critical",
            "doctor": "王医生",
            "hospital": "广州中山医院",
            "department": "儿科",
            "message": "检测到潜在药物相互作用",
            "details": "阿莫西林与头孢克肟联用可能导致抗生素相关性腹泻",
            "suggestion": "建议取消其中一种抗生素,避免重复用药",
            "created_at": "2025-01-07 10:30:00"
        },
        {
            "alert_type": "dose_warning",
            "severity": "high",
            "doctor": "李医生",
            "hospital": "上海瑞金医院",
            "department": "老年科",
            "message": "药物剂量偏高",
            "details": "85岁患者使用常规成人剂量布洛芬,可能导致肾损伤",
            "suggestion": "建议减半剂量或改用对乙酰氨基酚",
            "created_at": "2025-01-07 09:45:00"
        },
        {
            "alert_type": "contraindication",
            "severity": "critical",
            "doctor": "张医生",
            "hospital": "北京协和医院",
            "department": "心血管内科",
            "message": "存在禁忌症",
            "details": "患者有消化道溃疡史,处方中含阿司匹林",
            "suggestion": "建议改用氯吡格雷或停用抗血小板药物",
            "created_at": "2025-01-07 09:15:00"
        },
        {
            "alert_type": "off_label_use",
            "severity": "medium",
            "doctor": "刘医生",
            "hospital": "成都华西医院",
            "department": "神经内科",
            "message": "超说明书用药",
            "details": "使用该药物用于非批准适应症",
            "suggestion": "需签署知情同意书,并做好病历记录",
            "created_at": "2025-01-07 08:50:00"
        },
        {
            "alert_type": "duration_warning",
            "severity": "medium",
            "doctor": "陈医生",
            "hospital": "杭州第一医院",
            "department": "呼吸内科",
            "message": "用药疗程过长",
            "details": "抗生素疗程超过14天,可能增加耐药性",
            "suggestion": "建议重新评估,适时停药或降阶梯治疗",
            "created_at": "2025-01-07 08:20:00"
        }
    ]

    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]

    return {"data": alerts, "total": len(alerts)}

# ============================================
# 5. DRG/DIP绩效分析API
# ============================================

@app.get("/api/medical/drg/performance")
async def get_drg_performance(
    hospital_id: Optional[str] = None,
    current_user: str = Depends(verify_token)
):
    """
    DRG/DIP绩效分析
    """
    performance = {
        "summary": {
            "total_cases": 5230,
            "avg_cost": 12580,
            "avg_stay_days": 8.5,
            "cost_efficiency": 92.5,
            "quality_score": 94.2
        },
        "by_drg_group": [
            {
                "drg_code": "DRG101",
                "drg_name": "呼吸系统感染",
                "cases": 890,
                "avg_cost": 8520,
                "std_cost": 8200,
                "cost_variance": 3.9,
                "avg_stay": 6.5,
                "quality_score": 95.5
            },
            {
                "drg_code": "DRG201",
                "drg_name": "心血管疾病",
                "cases": 1250,
                "avg_cost": 15680,
                "std_cost": 15200,
                "cost_variance": 3.2,
                "avg_stay": 9.2,
                "quality_score": 93.8
            },
            {
                "drg_code": "DRG301",
                "drg_name": "内分泌疾病",
                "cases": 680,
                "avg_cost": 12350,
                "std_cost": 11800,
                "cost_variance": 4.7,
                "avg_stay": 7.8,
                "quality_score": 94.5
            },
            {
                "drg_code": "DRG401",
                "drg_name": "消化系统疾病",
                "cases": 756,
                "avg_cost": 11200,
                "std_cost": 10800,
                "cost_variance": 3.7,
                "avg_stay": 7.2,
                "quality_score": 95.2
            }
        ],
        "high_cost_cases": [
            {
                "case_id": "CASE001",
                "drg": "DRG201",
                "cost": 45820,
                "std_cost": 15200,
                "variance": 201.4,
                "reason": "并发症多,使用高价耗材",
                "stay_days": 25
            },
            {
                "case_id": "CASE002",
                "drg": "DRG101",
                "cost": 32560,
                "std_cost": 8200,
                "variance": 297.0,
                "reason": "重症感染,ICU治疗",
                "stay_days": 18
            }
        ]
    }

    return performance

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
