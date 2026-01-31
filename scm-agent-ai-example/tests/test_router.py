from agent.router import route_intent


def test_route_definition():
    intent, _ = route_intent("What is OTIF?")
    assert intent == "DEFINITION"


def test_route_calculation():
    intent, _ = route_intent("Calculate EOQ for demand 12000.")
    assert intent == "CALCULATION"


def test_route_inventory():
    intent, _ = route_intent("How do we improve inventory turnover?")
    assert intent == "INVENTORY"
