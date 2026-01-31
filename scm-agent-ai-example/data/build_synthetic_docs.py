import json
from pathlib import Path


DOC_SPECS = [
    ("scm_planning_overview.txt", "SCM Planning Overview", [
        "Demand planning aligns statistical forecasts with commercial inputs, promotions, and new product introductions.",
        "The S&OP cycle balances demand, supply, inventory, and financial targets with a monthly executive review.",
        "Master Production Scheduling translates the demand plan into time-phased build quantities and available-to-promise logic.",
        "MRP explodes the BOM to calculate gross requirements, net requirements, and planned order releases.",
        "Common planning KPIs include forecast accuracy, bias, and adherence to schedule.",
    ]),
    ("inventory_policy_playbook.txt", "Inventory Policy Playbook", [
        "Safety stock protects service level against demand variability and lead time variation.",
        "Reorder point is calculated as expected demand during lead time plus safety stock.",
        "Min-max policies maintain inventory between a minimum and maximum, often for C-class items.",
        "Cycle counting improves accuracy and reduces shrinkage by rotating counts by ABC classification.",
        "Inventory turnover and days of inventory on hand measure capital efficiency.",
    ]),
    ("logistics_network_design.txt", "Logistics Network Design", [
        "Network design evaluates plant and DC locations to minimize total landed cost and lead time.",
        "Cross docking reduces storage time by moving inbound freight directly to outbound lanes.",
        "Transportation mode selection balances cost, speed, and service levels across LTL and FTL.",
        "Incoterms define responsibility and risk transfer in global logistics.",
        "Last-mile delivery strategies optimize route density and customer experience.",
    ]),
    ("warehouse_operations.txt", "Warehouse Operations", [
        "WMS orchestrates inbound receiving, putaway, replenishment, and outbound picking.",
        "Slotting assigns fast movers to ergonomic locations to reduce travel time.",
        "Dock-to-stock time measures how quickly received goods are available for order fulfillment.",
        "Cycle time and labor productivity are monitored to sustain service levels.",
        "Quality checks reduce scrap and rework by catching issues at receiving.",
    ]),
    ("supplier_management.txt", "Supplier Management", [
        "Supplier lead time and on-time delivery are central to supply continuity.",
        "MOQ and lot size constraints affect inventory investment and schedule flexibility.",
        "Supplier scorecards include quality, responsiveness, and cost competitiveness.",
        "Dual sourcing reduces risk from single-supplier disruption.",
        "Collaborative planning with suppliers stabilizes production schedules.",
    ]),
    ("production_and_capacity.txt", "Production and Capacity", [
        "OEE combines availability, performance, and quality to measure manufacturing effectiveness.",
        "Takt time aligns production pace with customer demand.",
        "Bottleneck analysis identifies constraints that cap throughput.",
        "Capacity utilization and changeover time drive overall equipment efficiency.",
        "Scrap rate and yield track process capability.",
    ]),
    ("order_fulfillment.txt", "Order Fulfillment", [
        "Perfect order combines OTIF, damage-free, and documentation accuracy.",
        "Backorders indicate unmet demand and drive expediting costs.",
        "ATP helps customer service confirm feasible promise dates.",
        "Pick-pack-ship cycle time is a primary service metric for distribution centers.",
        "Returns management and reverse logistics protect margin and customer experience.",
    ]),
    ("inventory_optimization.txt", "Inventory Optimization", [
        "EOQ balances ordering costs with holding costs to determine optimal batch size.",
        "Safety stock can be set by service level targets using a z-score approach.",
        "Pipeline inventory covers demand during replenishment lead time.",
        "Cycle stock represents the average inventory due to batch ordering.",
        "Demand variability drives buffer stock requirements.",
    ]),
    ("transportation_strategy.txt", "Transportation Strategy", [
        "TMS optimizes routing, load building, and carrier selection.",
        "Fuel surcharge and accessorials affect total freight cost.",
        "Freight audit and payment ensure contract compliance.",
        "Cold chain processes maintain temperature control for perishables.",
        "Service level agreements define delivery time windows and penalties.",
    ]),
    ("planning_exceptions.txt", "Planning Exceptions", [
        "Expedite orders when customer priorities override standard lead time.",
        "Past-due orders require root-cause analysis and corrective action.",
        "Shortage reports highlight components that constrain production schedules.",
        "Allocation rules define fair distribution during supply shortages.",
        "Demand sensing uses near-real-time data to adjust forecasts.",
    ]),
    ("global_trade_and_compliance.txt", "Global Trade and Compliance", [
        "Trade compliance covers restricted party screening and export controls.",
        "Customs documentation must align with HS codes and declared values.",
        "DDP and DAP terms shift duty and delivery responsibility.",
        "Landed cost includes freight, duties, taxes, and handling fees.",
        "Broker performance affects clearance time and service.",
    ]),
    ("scm_analytics_kpis.txt", "SCM Analytics and KPIs", [
        "Fill rate measures the percent of customer demand fulfilled immediately from stock.",
        "OTIF measures the percent of orders delivered on time and in full.",
        "Forecast accuracy is often tracked with MAPE or WMAPE.",
        "Inventory accuracy compares system on-hand to physical count.",
        "Cash-to-cash cycle time links inventory, receivables, and payables.",
    ]),
]


def _expand_paragraphs(paragraphs, repeat=6):
    expanded = []
    for i in range(repeat):
        for p in paragraphs:
            expanded.append(f"{p} This guidance is reviewed quarterly to reflect changing business conditions.")
    return "\n\n".join(expanded)


def generate_docs(output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    for filename, title, paragraphs in DOC_SPECS:
        content = f"{title}\n\n{_expand_paragraphs(paragraphs)}\n"
        path = output_dir / filename
        path.write_text(content, encoding="utf-8")
        manifest.append({"file": filename, "title": title})

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    generate_docs(Path(__file__).parent / "enterprise_knowledge")
