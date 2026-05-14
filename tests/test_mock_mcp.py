import fasikl_assistant.mock_mcp as mock_mcp


def test_prescription_status_randomly_returns_one_known_status(monkeypatch):
    monkeypatch.setattr(mock_mcp.random, "choice", lambda options: options[1])

    assert mock_mcp.prescription_status() == "Prescription received and pending clinical review."


def test_supply_shipping_status_randomly_returns_one_known_status(monkeypatch):
    monkeypatch.setattr(mock_mcp.random, "choice", lambda options: options[2])

    assert mock_mcp.supply_shipping_status() == "Supply order is delayed and needs review."
