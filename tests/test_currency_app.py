import math

import pytest

import currency_converter_app as cca


def test_supported_currencies_and_convert():
    currs = cca.supported_currencies()
    assert "USD" in currs and "EUR" in currs

    rates = {"USD": 1.0, "EUR": 0.9, "GBP": 0.8}
    # USD -> EUR
    out = cca.convert(100, "USD", "EUR", rates)
    assert math.isclose(out, 90.0, rel_tol=1e-9)
    # EUR -> GBP
    out2 = cca.convert(90, "EUR", "GBP", rates)
    # EUR->base = 90/0.9 = 100 -> GBP = 100 * 0.8 = 80
    assert math.isclose(out2, 80.0, rel_tol=1e-9)


def test_convert_same_currency_returns_same():
    rates = {"USD": 1.0}
    assert cca.convert(50, "USD", "USD", rates) == 50


def test_convert_unsupported_raises():
    rates = {"USD": 1.0}
    with pytest.raises(ValueError):
        cca.convert(10, "USD", "XXX", rates)

