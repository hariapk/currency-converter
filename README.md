# Currency Converter

Simple Streamlit currency converter demo.

How to run:

```powershell
cd D:\Apps\currency-converter
pip install -r requirements.txt
streamlit run app.py
```

Notes:
- The app attempts to fetch live rates from `exchangerate.host` and will fall back to built-in sample rates if offline.
- The core conversion helpers (`get_rates`, `convert`) are safe to import in tests because the UI is in `run()`.
