from typing import Dict, List


def _repeat_section(title: str, sentences: List[str], repeats: int) -> str:
    blocks = []
    for i in range(repeats):
        blocks.append(f"{title} section {i + 1}. " + " ".join(sentences))
    return "\n\n".join(blocks)


def generate_synthetic_docs() -> List[Dict[str, str]]:
    docs = []
    docs.append(
        {
            "id": "scm_overview",
            "text": _repeat_section(
                "SCM overview",
                [
                    "Enterprise supply chain management aligns demand planning, inventory, procurement, manufacturing, logistics, and customer service.",
                    "A balanced scorecard tracks OTIF, fill rate, inventory turns, lead time, and cost-to-serve.",
                    "S&OP reconciles demand and supply plans, while MRP translates plans into material requirements.",
                    "Risk management and resilience planning consider supplier risk, geopolitical exposure, and alternate lanes.",
                ],
                20,
            ),
        }
    )
    docs.append(
        {
            "id": "demand_planning",
            "text": _repeat_section(
                "Demand planning",
                [
                    "Forecast accuracy is measured with MAPE and bias metrics.",
                    "Promotions, seasonality, and product life cycles are modeled to reduce stockouts and excess inventory.",
                    "Consensus forecasts feed the S&OP cycle for executive review and gap closure.",
                ],
                20,
            ),
        }
    )
    docs.append(
        {
            "id": "inventory_policy",
            "text": _repeat_section(
                "Inventory policy",
                [
                    "Safety stock is determined by demand variability and target service level.",
                    "Reorder point equals demand during lead time plus safety stock.",
                    "ABC classification sets different policies for high-value and low-value items.",
                    "Cycle counting improves inventory accuracy, which supports ATP reliability.",
                ],
                20,
            ),
        }
    )
    docs.append(
        {
            "id": "logistics_network",
            "text": _repeat_section(
                "Logistics and network design",
                [
                    "Transportation management optimizes mode selection, carrier performance, and freight cost per unit.",
                    "Network design determines DC placement and lane strategy.",
                    "Last mile delivery performance is tracked through on-time delivery and damage rate.",
                ],
                20,
            ),
        }
    )
    docs.append(
        {
            "id": "procurement_sourcing",
            "text": _repeat_section(
                "Procurement and sourcing",
                [
                    "Supplier OTIF, quality PPM, and lead time adherence are monitored.",
                    "MOQ and contract terms influence ordering frequency and working capital.",
                    "Dual sourcing mitigates risk and improves continuity of supply.",
                ],
                20,
            ),
        }
    )
    docs.append(
        {
            "id": "manufacturing_operations",
            "text": _repeat_section(
                "Manufacturing operations",
                [
                    "MRP explodes the bill of materials based on the master production schedule.",
                    "Capacity constraints drive finite scheduling and bottleneck management.",
                    "WIP, cycle time, OEE, and yield are core operational metrics.",
                ],
                20,
            ),
        }
    )
    return docs
