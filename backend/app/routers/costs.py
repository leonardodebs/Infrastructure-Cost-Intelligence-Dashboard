from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from calendar import monthrange
from app.routers.auth import get_current_user

router = APIRouter(prefix="/costs", tags=["Custos"])

@router.get("/dashboard")
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    from app.services.aws_cost import aws_cost_service
    
    today = datetime.utcnow()
    start_of_month = today.replace(day=1)
    
    cost_data = aws_cost_service.get_cost_and_usage(
        start_date=start_of_month.strftime("%Y-%m-%d"),
        end_date=today.strftime("%Y-%m-%d"),
        granularity="DAILY"
    )
    
    spend_by_service = aws_cost_service.get_spend_by_service(
        start_date=start_of_month.strftime("%Y-%m-%d"),
        end_date=today.strftime("%Y-%m-%d")
    )
    
    daily_trend = aws_cost_service.get_daily_cost_trend(30)
    
    top_resources = aws_cost_service.get_top_resources(5)
    
    return {
        "month_to_date": cost_data.get("month_to_date", 0),
        "spend_by_service": spend_by_service,
        "daily_trend": daily_trend.get("daily_costs", []),
        "top_resources": top_resources
    }

@router.get("/daily-trend")
async def get_daily_trend(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    from app.services.aws_cost import aws_cost_service
    
    trend = aws_cost_service.get_daily_cost_trend(days)
    return {"daily_costs": trend.get("daily_costs", [])}

@router.get("/by-service")
async def get_costs_by_service(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    from app.services.aws_cost import aws_cost_service
    
    if not start_date:
        start_date = datetime.utcnow().replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.utcnow().strftime("%Y-%m-%d")
    
    services = aws_cost_service.get_spend_by_service(start_date, end_date)
    return {"services": services}

@router.get("/anomalies")
async def get_anomalies(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    from app.services.anomaly import AnomalyDetectionService
    from app.services.aws_cost import aws_cost_service
    
    anomaly_service = AnomalyDetectionService(aws_cost_service)
    anomalies = anomaly_service.detect_anomalies(days)
    
    return {"anomalies": anomalies}

@router.get("/forecast")
async def get_forecast(current_user: dict = Depends(get_current_user)):
    from app.services.aws_cost import aws_cost_service
    
    today = datetime.utcnow()
    start_of_month = today.replace(day=1)
    days_in_month = monthrange(today.year, today.month)[1]
    days_passed = today.day
    
    cost_data = aws_cost_service.get_cost_and_usage(
        start_date=start_of_month.strftime("%Y-%m-%d"),
        end_date=today.strftime("%Y-%m-%d"),
        granularity="DAILY"
    )
    
    daily_costs = cost_data.get("daily_costs", [])
    if not daily_costs:
        return {"forecast": 0, "current_spend": 0, "daily_average": 0}
    
    current_spend = sum(d["total"] for d in daily_costs)
    daily_average = current_spend / days_passed if days_passed > 0 else 0
    
    remaining_days = days_in_month - days_passed
    projected_additional = daily_average * remaining_days
    forecast = current_spend + projected_additional
    
    return {
        "forecast": round(forecast, 2),
        "current_spend": round(current_spend, 2),
        "daily_average": round(daily_average, 2),
        "days_passed": days_passed,
        "days_in_month": days_in_month,
        "remaining_days": remaining_days
    }

@router.get("/tag-compliance")
async def get_tag_compliance(current_user: dict = Depends(get_current_user)):
    from app.services.tag_compliance import tag_compliance_service
    
    resources = tag_compliance_service.scan_tag_compliance()
    summary = tag_compliance_service.get_compliance_summary()
    
    return {
        "resources": resources,
        "summary": summary
    }

@router.get("/export-csv")
async def export_csv(current_user: dict = Depends(get_current_user)):
    from app.services.aws_cost import aws_cost_service
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    today = datetime.utcnow()
    start_of_month = today.replace(day=1)
    
    services = aws_cost_service.get_spend_by_service(
        start_date=start_of_month.strftime("%Y-%m-%d"),
        end_date=today.strftime("%Y-%m-%d")
    )
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Serviço", "Custo (USD)"])
    
    for service in services:
        writer.writerow([service["service"], service["cost"]])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=costs.csv"}
    )
