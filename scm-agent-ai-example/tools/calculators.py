import math
from typing import Dict

def economic_order_quantity(annual_demand: float, order_cost: float, holding_cost: float) -> Dict:
    eoq = math.sqrt((2 * annual_demand * order_cost) / holding_cost)
    return {"metric": "EOQ", "value": round(eoq, 2)}

def reorder_point(daily_demand: float, lead_time_days: float, safety_stock: float) -> Dict:
    rop = (daily_demand * lead_time_days) + safety_stock
    return {"metric": "Reorder Point", "value": round(rop, 2)}

def safety_stock(z_score: float, demand_std: float, lead_time_days: float) -> Dict:
    ss = z_score * demand_std * math.sqrt(lead_time_days)
    return {"metric": "Safety Stock", "value": round(ss, 2)}

def fill_rate(filled_units: float, total_demand_units: float) -> Dict:
    fr = (filled_units / total_demand_units) * 100
    return {"metric": "Fill Rate", "value": f"{round(fr, 2)}%"}

def otif(on_time: float, in_full: float) -> Dict:
    otif_val = (on_time * in_full) * 100
    return {"metric": "OTIF", "value": f"{round(otif_val, 2)}%"}
