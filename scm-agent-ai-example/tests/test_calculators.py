from tools.calculators import economic_order_quantity, otif

def test_eoq():
    result = economic_order_quantity(annual_demand=1200, order_cost=50, holding_cost=5)
    assert result["metric"] == "EOQ"
    assert result["value"] == 154.92

def test_otif():
    result = otif(on_time=0.9, in_full=0.95)
    assert result["metric"] == "OTIF"
    assert result["value"] == "85.5%"
