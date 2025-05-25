from kiteconnect import KiteConnect

api_key = "1f0vletbpc97y6fu"

# Load access token saved from login
with open("access_token.txt", "r") as f:
    access_token = f.read().strip()

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)
