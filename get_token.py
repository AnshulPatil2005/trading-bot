from datetime import datetime, timedelta
import json
from auth import kite  # Requires auth.py in the same folder

# 🗓️ Weekly expiry fetcher (next Thursday)
def get_next_weekly_expiry():
    today = datetime.now()
    weekday = today.weekday()
    expiry = today + timedelta(days=(3 - weekday)) if weekday <= 3 else today + timedelta(days=(10 - weekday))
    return expiry.strftime("%d%b").upper()

# 📈 Build ATM option symbol from NIFTY price
def get_atm_option_symbol(price, option_type="CE"):
    strike = round(price / 50) * 50
    expiry = get_next_weekly_expiry()
    return f"NIFTY{expiry}{strike}{option_type}"

# 🧾 Get token from Zerodha instrument list
def get_option_token(symbol):
    instruments = kite.instruments("NFO")
    for inst in instruments:
        if inst["tradingsymbol"] == symbol:
            return inst["instrument_token"]
    raise ValueError(f"Symbol {symbol} not found.")

# 🚀 Run this once daily before market open
if __name__ == "__main__":
    try:
        nifty_price = kite.ltp("NSE:NIFTY 50")["NSE:NIFTY 50"]["last_price"]
        ce_symbol = get_atm_option_symbol(nifty_price, "CE")
        pe_symbol = get_atm_option_symbol(nifty_price, "PE")

        ce_token = get_option_token(ce_symbol)
        pe_token = get_option_token(pe_symbol)

        data = {
            "CE": {"symbol": ce_symbol, "token": ce_token},
            "PE": {"symbol": pe_symbol, "token": pe_token}
        }

        with open("option_tokens.json", "w") as f:
            json.dump(data, f, indent=2)

        print("✅ Option tokens saved to option_tokens.json")
        print(json.dumps(data, indent=2))

    except Exception as e:
        print("❌ Error:", e)
