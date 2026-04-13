from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AnomalyDetectionService:
    def __init__(self, cost_service):
        self.cost_service = cost_service
        self.threshold_percentage = 20.0
    
    def detect_anomalies(self, days: int = 30) -> List[Dict[str, Any]]:
        cost_data = self.cost_service.get_daily_cost_trend(days)
        daily_costs = cost_data.get("daily_costs", [])
        
        if len(daily_costs) < 8:
            return []
        
        anomalies = []
        
        for i in range(7, len(daily_costs)):
            current_day = daily_costs[i]
            current_date = current_day["date"]
            current_total = current_day["total"]
            
            rolling_sum = sum(d["total"] for d in daily_costs[i-7:i])
            rolling_average = rolling_sum / 7
            
            if rolling_average > 0:
                deviation_percentage = ((current_total - rolling_average) / rolling_average) * 100
                
                if deviation_percentage > self.threshold_percentage:
                    service_with_highest_cost = max(
                        current_day["costs"].items(),
                        key=lambda x: x[1]
                    )[0] if current_day["costs"] else "Unknown"
                    
                    anomalies.append({
                        "date": current_date,
                        "cost": current_total,
                        "average_cost": rolling_average,
                        "deviation_percentage": round(deviation_percentage, 2),
                        "affected_service": service_with_highest_cost,
                        "threshold_percentage": self.threshold_percentage
                    })
        
        return anomalies
    
    def get_rolling_average(self, daily_costs: List[Dict], window: int = 7) -> List[Dict[str, Any]]:
        if len(daily_costs) < window:
            return []
        
        averages = []
        for i in range(window - 1, len(daily_costs)):
            window_costs = daily_costs[i-window+1:i+1]
            avg = sum(d["total"] for d in window_costs) / window
            averages.append({
                "date": daily_costs[i]["date"],
                "average": round(avg, 2)
            })
        
        return averages

anomaly_service = AnomalyDetectionService(None)
