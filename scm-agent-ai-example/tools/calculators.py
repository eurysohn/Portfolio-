import math
import re


def _extract_numbers(text):
    return [float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+", text)]


def run_calculation(query):
    q = query.lower()
    numbers = _extract_numbers(q)

    if "eoq" in q or "economic order quantity" in q:
        if len(numbers) >= 3:
            demand, order_cost, holding_cost = numbers[:3]
            eoq = math.sqrt((2 * demand * order_cost) / holding_cost)
            return {
                "answer": f"EOQ = sqrt((2*{demand}*{order_cost})/{holding_cost}) = {eoq:.2f}",
                "confidence": 0.9,
            }
        return {
            "answer": "EOQ formula: sqrt((2 * D * S) / H). Provide D (annual demand), S (order cost), H (holding cost).",
            "confidence": 0.6,
        }

    if "reorder point" in q or "rop" in q:
        if len(numbers) >= 3:
            demand_rate, lead_time, safety_stock = numbers[:3]
            rop = demand_rate * lead_time + safety_stock
            return {
                "answer": f"ROP = {demand_rate}*{lead_time} + {safety_stock} = {rop:.2f}",
                "confidence": 0.85,
            }
        return {
            "answer": "ROP formula: demand during lead time + safety stock. Provide demand rate, lead time, and safety stock.",
            "confidence": 0.6,
        }

    if "takt" in q:
        if len(numbers) >= 2:
            available_time, demand = numbers[:2]
            takt = available_time / demand if demand != 0 else 0
            return {
                "answer": f"Takt Time = {available_time}/{demand} = {takt:.2f}",
                "confidence": 0.85,
            }
        return {
            "answer": "Takt Time formula: available time / customer demand. Provide available time and demand.",
            "confidence": 0.6,
        }

    if "fill rate" in q:
        if len(numbers) >= 2:
            shipped, ordered = numbers[:2]
            fill = (shipped / ordered) * 100 if ordered != 0 else 0
            return {
                "answer": f"Fill Rate = ({shipped}/{ordered})*100 = {fill:.2f}%",
                "confidence": 0.85,
            }
        return {
            "answer": "Fill Rate formula: units shipped immediately / units ordered * 100.",
            "confidence": 0.6,
        }

    if "on-time delivery" in q or "otd" in q:
        if len(numbers) >= 2:
            on_time, total = numbers[:2]
            otd = (on_time / total) * 100 if total != 0 else 0
            return {
                "answer": f"On-time Delivery = ({on_time}/{total})*100 = {otd:.2f}%",
                "confidence": 0.85,
            }
        return {
            "answer": "On-time Delivery formula: on-time shipments / total shipments * 100.",
            "confidence": 0.6,
        }

    return {
        "answer": "I can calculate EOQ, reorder point, takt time, fill rate, or on-time delivery. Provide the relevant numbers.",
        "confidence": 0.4,
    }
