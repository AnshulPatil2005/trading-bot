from kiteconnect import KiteTicker
from auth import kite
from strategy import check_bullish_rsi_divergence, check_bearish_rsi_divergence
import pandas as pd
import datetime
import threading
import time
import requests
import csv
import os
import json

# Zerodha token for NIFTY index spot
NIFTY_TOKEN = 256265
LOTSIZE = 75

# Load option symbols and tokens from file
with open("option_tokens.json", "r") as f:
    tokens = json.load(f)

ce_symbol = tokens["CE"]["symbol"]
pe_symbol = tokens["PE"]["symbol"]

# Telegram notifier
def send_telegram(msg):
    requests.get("https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage", params={
        "chat_id": "6756732013", "text": msg
    })

# Initialize candle and tick buffers
ticks = []
candles = pd.DataFrame(columns=["time", "open", "high", "low", "close"])

# WebSocket connection
kws = KiteTicker(kite.api_key, kite.access_token)

def on_ticks(ws, tick_data):
    global ticks
    for tick in tick_data:
        ticks.append(tick['last_price'])

def on_connect(ws, response):
    print("✅ WebSocket connected.")
    ws.subscribe([NIFTY_TOKEN])
    ws.set_mode(ws.MODE_LTP, [NIFTY_TOKEN])

# Log trade to CSV
def log_trade(timestamp, symbol, price, status):
    with open("trade_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["timestamp", "symbol", "price", "status"])
        writer.writerow([timestamp, symbol, price, status])

# Log candle to CSV
def log_candle(timestamp, o, h, l, c):
    with open("candle_data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["time", "open", "high", "low", "close"])
        writer.writerow([timestamp, o, h, l, c])

# Place market order
def place_order(symbol):
    try:
        ltp = kite.ltp([f"NFO:{symbol}"])[f"NFO:{symbol}"]["last_price"]
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=kite.EXCHANGE_NFO,
            tradingsymbol=symbol,
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            quantity=LOTSIZE,
            product=kite.PRODUCT_MIS,
            order_type=kite.ORDER_TYPE_MARKET
        )
        log_trade(datetime.datetime.now(), symbol, ltp, "Executed")
        send_telegram(f"✅ Order placed: {symbol} at ₹{ltp}")
        print(f"✅ Order placed: {symbol}")
    except Exception as e:
        send_telegram(f"❌ Order failed: {e}")
        log_trade(datetime.datetime.now(), symbol, "N/A", f"Failed: {e}")
        print(f"❌ Order failed: {e}")

# Build 1-minute candle and check signals
def generate_candle():
    global ticks, candles
    if not ticks:
        return
    o, h, l, c = ticks[0], max(ticks), min(ticks), ticks[-1]
    timestamp = datetime.datetime.now().replace(second=0, microsecond=0)
    candles.loc[len(candles)] = [timestamp, o, h, l, c]
    log_candle(timestamp, o, h, l, c)
    print(f"🕐 Candle: {timestamp.time()} | O: {o}, H: {h}, L: {l}, C: {c}")
    ticks = []

    if len(candles) >= 20:
        if check_bullish_rsi_divergence(candles):
            print("📈 Bullish RSI divergence detected.")
            place_order(ce_symbol)
        elif check_bearish_rsi_divergence(candles):
            print("📉 Bearish RSI divergence detected.")
            place_order(pe_symbol)

# Loop to build candle every minute
def run_candle_loop():
    while True:
        now = datetime.datetime.now()
        if now.hour == 15 and now.minute >= 30:
            send_telegram("🔚 Market closed. Bot shutting down.")
            print("🔚 Market closed. Bot shutting down.")
            break
        if now.second == 0:
            generate_candle()
        time.sleep(1)

# Register WebSocket callbacks
kws.on_ticks = on_ticks
kws.on_connect = on_connect

# Start WebSocket and candle loop
threading.Thread(target=kws.connect).start()
threading.Thread(target=run_candle_loop).start()
