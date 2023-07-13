from decimal import Decimal

import pytest
from shipping.transactions import TransactionProcessor


@pytest.mark.part1
def test_small_shipment_matches_lowest_small_package_price():
    transactions = [
        {"date": "2015-02-01", "package_size": "S", "carrier": "LP"},
        {"date": "2015-02-02", "package_size": "S", "carrier": "MR"},
    ]
    expected_prices = [
        {"reduced_price": Decimal("1.5"), "applied_discount": None},
        {"reduced_price": Decimal("1.5"), "applied_discount": Decimal("0.5")},
    ]
    _check_prices(transactions, expected_prices)


@pytest.mark.part1
def test_every_third_large_shipment_via_lp_should_be_free_once_per_month():

    transactions = [
        {"date": "2015-02-01", "package_size": "L", "carrier": "LP"},
        {"date": "2015-03-01", "package_size": "L", "carrier": "MR"},
        {"date": "2015-04-01", "package_size": "L", "carrier": "LP"},
        {"date": "2015-05-01", "package_size": "M", "carrier": "LP"},
        {"date": "2015-06-01", "package_size": "L", "carrier": "LP"},
        {"date": "2015-06-02", "package_size": "L", "carrier": "LP"},
        {"date": "2015-06-03", "package_size": "L", "carrier": "LP"},
        {"date": "2015-06-04", "package_size": "L", "carrier": "LP"},
    ]
    expected_prices = [
        {"reduced_price": Decimal("6.9"), "applied_discount": None},
        {"reduced_price": Decimal("4"), "applied_discount": None},
        {"reduced_price": Decimal("6.9"), "applied_discount": None},
        {"reduced_price": Decimal("4.9"), "applied_discount": None},
        {"reduced_price": Decimal("0"), "applied_discount": Decimal("6.9")},
        {"reduced_price": Decimal("6.9"), "applied_discount": None},
        {"reduced_price": Decimal("6.9"), "applied_discount": None},
        {"reduced_price": Decimal("6.9"), "applied_discount": None},
    ]

    _check_prices(transactions, expected_prices)


@pytest.mark.part1
def test_accumulated_discounts_cannot_exceed_10_eur_per_month():
    transactions = [
        {"date": "2015-02-01", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-02", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-06", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-09", "package_size": "L", "carrier": "LP"},
        {"date": "2015-02-09", "package_size": "L", "carrier": "LP"},
        {"date": "2015-02-09", "package_size": "L", "carrier": "LP"},
        {"date": "2015-02-10", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-10", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-15", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-17", "package_size": "S", "carrier": "MR"},
        {"date": "2015-02-18", "package_size": "S", "carrier": "MR"},
        {"date": "2015-03-01", "package_size": "S", "carrier": "MR"},
    ]
    expected_prices = [
        {"reduced_price": Decimal("1.50"), "applied_discount": Decimal("0.50")},
        {"reduced_price": Decimal("1.50"), "applied_discount": Decimal("0.50")},
        {"reduced_price": Decimal("1.50"), "applied_discount": Decimal("0.50")},
        {"reduced_price": Decimal("6.90"), "applied_discount": None},
        {"reduced_price": Decimal("6.90"), "applied_discount": None},
        {"reduced_price": Decimal("0"), "applied_discount": Decimal("6.90")},
        {"reduced_price": Decimal("1.50"), "applied_discount": Decimal("0.50")},
        {"reduced_price": Decimal("1.50"), "applied_discount": Decimal("0.50")},
        {"reduced_price": Decimal("1.50"), "applied_discount": Decimal("0.50")},
        {"reduced_price": Decimal("1.90"), "applied_discount": Decimal("0.10")},
        {"reduced_price": Decimal("2.00"), "applied_discount": None},
        {"reduced_price": Decimal("1.50"), "applied_discount": Decimal("0.50")},
    ]

    _check_prices(transactions, expected_prices)


def _check_prices(transactions, expected_prices):
    processor = TransactionProcessor()
    prices = [processor.process_transaction(t) for t in transactions]

    for i, (price, expected_price) in enumerate(zip(prices, expected_prices)):
        assert (
            price == expected_price
        ), f"Incorrect price for transaction with index {i}"
