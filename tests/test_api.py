import pytest
from fastapi.testclient import TestClient
from shipping.api import build_app


@pytest.fixture
def client():
    return TestClient(build_app())


@pytest.mark.part2
def test_add_transaction(client):
    transactions = [
        {"date": "2015-02-01", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-02", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-03", "package_size": "L", "carrier": "LP"},
        {"date": "2015-02-05", "package_size": "S", "carrier": "LP"},
        {"date": "2015-02-06", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-06", "package_size": "L", "carrier": "LP"},
        {"date": "2015-02-07", "package_size": "L", "carrier": "MR"},
        {"date": "2015-02-08", "package_size": "M", "carrier": "MR"},
        {"date": "2015-02-09", "package_size": "L", "carrier": "LP"},
        {"date": "2015-02-10", "package_size": "L", "carrier": "LP"},
        {"date": "2015-02-10", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-10", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-11", "package_size": "L", "carrier": "LP"},
        {"date": "2015-02-12", "package_size": "M", "carrier": "MR"},
        {"date": "2015-02-13", "package_size": "M", "carrier": "LP"},
        {"date": "2015-02-15", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-17", "package_size": "L", "carrier": "LP"},
        {"date": "2015-02-17", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-24", "package_size": "L", "carrier": "LP"},
        {"date": "2015-03-01", "package_size": "S", "carrier": "MR"},
    ]
    expected_response_bodies = [
        {"reduced_price": "1.50", "applied_discount": "0.50"},
        {"reduced_price": "1.50", "applied_discount": "0.50"},
        {"reduced_price": "6.90", "applied_discount": None},
        {"reduced_price": "1.50", "applied_discount": None},
        {"reduced_price": "1.50", "applied_discount": "0.50"},
        {"reduced_price": "6.90", "applied_discount": None},
        {"reduced_price": "4.00", "applied_discount": None},
        {"reduced_price": "3.00", "applied_discount": None},
        {"reduced_price": "0.00", "applied_discount": "6.90"},
        {"reduced_price": "6.90", "applied_discount": None},
        {"reduced_price": "1.50", "applied_discount": "0.50"},
        {"reduced_price": "1.50", "applied_discount": "0.50"},
        {"reduced_price": "6.90", "applied_discount": None},
        {"reduced_price": "3.00", "applied_discount": None},
        {"reduced_price": "4.90", "applied_discount": None},
        {"reduced_price": "1.50", "applied_discount": "0.50"},
        {"reduced_price": "6.90", "applied_discount": None},
        {"reduced_price": "1.90", "applied_discount": "0.10"},
        {"reduced_price": "6.90", "applied_discount": None},
        {"reduced_price": "1.50", "applied_discount": "0.50"},
    ]
    responses = [client.post("/transactions", json=t) for t in transactions]
    for i, (r, expected_body) in enumerate(zip(responses, expected_response_bodies)):
        assert (
            r.status_code == 200
        ), f"POST /transactions for transaction with index {i} should respond with HTTP code 200"
        assert (
            r.json() == expected_body
        ), f"POST /transactions incorrect response for transaction index {i}"


@pytest.mark.part2
@pytest.mark.parametrize(
    "transaction,resp_status_code,resp_error_message,resp_text,resp_text_error_message",
    [
        (
            {"date": "2009-12-31", "package_size": "S", "carrier": "MR"},
            422,
            "POST /transactions should respond with HTTP code 422",
            "Transactions older than 2010 are not supported",
            "POST /transactions incorrect response",
        ),
        (
            {"date": "2010-01-01", "package_size": "S", "carrier": "MR"},
            200,
            "POST /transactions should respond with HTTP code 200",
            "",
            "POST /transactions incorrect response",
        ),
    ],
)
def test_date_validation(
    client,
    transaction,
    resp_status_code,
    resp_error_message,
    resp_text,
    resp_text_error_message,
):
    resp = client.post("/transactions", json=transaction)
    assert resp.status_code == resp_status_code, resp_error_message
    assert resp_text in resp.text, resp_text_error_message


@pytest.mark.part2
def test_get_carriers(client):
    resp = client.get("/carriers")
    assert resp.status_code == 200, "GET /carriers should respond with HTTP code 200"
    assert resp.json() == {
        "carriers": [{"code": "LP", "enabled": True}, {"code": "MR", "enabled": True}]
    }, "GET /carriers incorrect response"


@pytest.mark.part2
def test_configure_carriers(client):
    resp = client.post("/carriers", json={"code": "MonkeyExpress", "enabled": True})
    assert resp.status_code == 422, "POST /carriers should respond with HTTP code 422"

    resp = client.get("/carriers")
    assert resp.status_code == 200, "GET /carriers should respond with HTTP code 200"
    assert resp.json() == {
        "carriers": [{"code": "LP", "enabled": True}, {"code": "MR", "enabled": True}]
    }, "GET /carriers incorrect response"

    resp = client.post("/carriers", json={"code": "LP", "enabled": False})
    assert resp.status_code == 204, "POST /carriers should respond with HTTP code 204"

    resp = client.get("/carriers")
    assert resp.status_code == 200, "POST /carriers should respond with HTTP code 200"
    assert resp.json() == {
        "carriers": [{"code": "LP", "enabled": False}, {"code": "MR", "enabled": True}]
    }, "GET /carriers incorrect response"

    resp = client.post("/transactions", json={"date": "2015-02-01", "package_size": "S", "carrier": "LP"})
    assert (
        resp.status_code == 422
    ), "POST /transactions should respond with HTTP code 422"
    assert (
        "Carrier with code 'LP' is disabled" in resp.text
    ), "POST /transactions incorrect response"

    resp = client.post("/transactions", json={"date": "2015-02-01", "package_size": "S", "carrier": "MR"})
    assert (
        resp.status_code == 200
    ), "POST /transactions should respond with HTTP code 200"
    assert resp.json() == {
        "reduced_price": "2.00",
        "applied_discount": None,
    }, "Response body for post transaction is not as expected"
