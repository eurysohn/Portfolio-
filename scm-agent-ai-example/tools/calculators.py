from typing import Dict


def economic_order_quantity(annual_demand: float, order_cost: float, holding_cost: float) -> Dict:
    eoq = ((2 * annual_demand * order_cost) / holding_cost) ** 0.5
    return {"metric": "EOQ", "value": eoq}


def reorder_point(daily_demand: float, lead_time_days: float, safety_stock: float) -> Dict:
    return {
        "metric": "Reorder Point",
        "value": daily_demand * lead_time_days + safety_stock,
    }


def safety_stock(z_score: float, demand_std: float, lead_time_days: float) -> Dict:
    return {"metric": "Safety Stock", "value": z_score * demand_std * (lead_time_days ** 0.5)}


def fill_rate(filled_units: float, total_demand_units: float) -> Dict:
    rate = filled_units / total_demand_units if total_demand_units else 0.0
    return {"metric": "Fill Rate", "value": rate}


def otif(on_time: float, in_full: float) -> Dict:
    rate = on_time * in_full
    return {"metric": "OTIF", "value": rate}
