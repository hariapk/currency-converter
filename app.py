"""Simple Streamlit currency converter app.

Features:
- Convert between a small set of currencies.
- Attempts to fetch live rates from exchangerate.host; falls back to built-in rates if offline.
- UI is created in the `run()` function so tests can import conversion helpers without requiring Streamlit.
"""
from typing import Dict

import json

try:
    import requests
except Exception:  # requests may not be installed in minimal environments
    requests = None

# A small fallback set of rates (relative to USD)
FALLBACK_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.80,
    "JPY": 150.0,
    "INR": 83.0,
    "CAD": 1.35,
    "AUD": 1.55,
}


def supported_currencies():
    return sorted(FALLBACK_RATES.keys())


def get_rates(base: str = "USD") -> Dict[str, float]:
    """Return a mapping currency -> rate relative to `base`.

    Attempts to fetch live rates from exchangerate.host; falls back to FALLBACK_RATES.
    """
    base = base.upper()
    # Try live fetch
    if requests is not None:
        try:
            url = f"https://api.exchangerate.host/latest?base={base}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                rates = data.get("rates")
                if isinstance(rates, dict) and rates:
                    return {k.upper(): float(v) for k, v in rates.items()}
        except Exception:
            # ignore and fall back
            pass

    # Fallback: compute relative to base from FALLBACK_RATES if possible
    base_rate = FALLBACK_RATES.get(base)
    if base_rate is None:
        # unknown base -> use USD as reference
        base_rate = FALLBACK_RATES["USD"]
    rates = {k: v / base_rate for k, v in FALLBACK_RATES.items()}
    return rates


def convert(amount: float, from_currency: str, to_currency: str, rates: Dict[str, float]) -> float:
    """Convert amount from one currency to another using provided rates mapping (rates are per 1 base currency).

    Example: if rates are relative to USD, to convert EUR->GBP: amount / rates['EUR'] * rates['GBP']
    """
    if amount is None:
        return 0.0
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    if from_currency == to_currency:
        return float(amount)
    if from_currency not in rates or to_currency not in rates:
        raise ValueError("Unsupported currency")
    # Convert amount to base, then to target
    base_amount = float(amount) / float(rates[from_currency])
    return base_amount * float(rates[to_currency])


def run():
    """Run the Streamlit UI. Kept in a function so imports don't require Streamlit when testing."""
    try:
        import streamlit as st
    except Exception:
        raise RuntimeError("Streamlit is required to run the app. Install with `pip install streamlit`.")

    st.set_page_config(page_title="Currency Converter", page_icon="💱", layout="centered")
    st.title("Currency Converter")

    cols = st.columns([1, 2, 1])
    from_amt = cols[1].number_input("Amount", value=100.0, step=1.0, format="%.2f")
    from_curr = cols[0].selectbox("From", supported_currencies(), index=0)
    to_curr = cols[2].selectbox("To", supported_currencies(), index=1)

    # Get rates relative to some base (USD)
    rates = get_rates("USD")

    try:
        result = convert(from_amt, from_curr, to_curr, rates)
        st.metric("Converted amount", f"{result:,.2f} {to_curr}")
    except Exception as e:
        st.error(str(e))

    st.markdown("---")
    st.write("Using these rates (relative to USD):")
    df = None
    try:
        import pandas as pd

        df = pd.DataFrame(list(rates.items()), columns=["Currency", "Rate (per USD)"]).sort_values("Currency")
        st.dataframe(df)
    except Exception:
        st.write(json.dumps(rates, indent=2))


if __name__ == "__main__":
    run()
