from auth import kite
from datetime import datetime, timedelta

# 🗓️ Get next Thursday's expiry in Zerodha format (e.g., "29MAY")
def get_next_weekly_expiry():
    today = datetime.now()
    weekday = today.weekday()
    if weekday <= 3:
        expiry = today + timedelta(days=(3 - weekday))
    else:
        expiry = today + timedelta(days=(7 - weekday + 3))
    return expiry.strftime("%d%b").upper()

# 🔧 Create option symbol dynamically from price + expiry
def get_atm_option_symbol(current_price, option_type="CE"):
    strike = round(current_price / 50) * 50
    expiry = get_next_weekly_expiry()
    return f"NIFTY{expiry}{strike}{option_type}"

# 🔁 Fetch token for given symbol
def get_option_token(symbol):
    instruments = kite.instruments("NFO")
    for inst in instruments:
        if inst["tradingsymbol"] == symbol:
            return inst["instrument_token"]
    raise ValueError(f"Symbol {symbol} not found.")
