from agent.router import route


def test_route_definition():
    result = route("What is OTIF?", ["OTIF"])
    assert result["intent"] == "DEFINITION"


def test_route_inventory():
    result = route("Explain safety stock policy", [])
    assert result["intent"] == "INVENTORY"
