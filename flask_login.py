from flask import Flask, request
from kiteconnect import KiteConnect
import requests, os, threading, time, webbrowser

TELEGRAM_TOKEN = ""#telegram token here
TELEGRAM_CHAT_ID = "6756732013"
api_key = ""#api key here
api_secret = ""#api secret here
# Make sure to replace with your actual API key and secret
access_token_file = "access_token.txt"

app = Flask(__name__)
kite = KiteConnect(api_key=api_key)

def send_telegram(text):
    try:
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                     params={"chat_id": TELEGRAM_CHAT_ID, "text": text})
    except:
        pass

@app.route("/")
def login():
    return f'<a href="{kite.login_url()}">Login with Zerodha</a>'

@app.route("/callback")
def callback():
    request_token = request.args.get("request_token")
    try:
        session = kite.generate_session(request_token, api_secret=api_secret)
        with open(access_token_file, "w") as f:
            f.write(session["access_token"]) # type: ignore
        send_telegram("✅ Access token saved. Bot ready.")
        return "<h2>✅ Login success. Access token saved.</h2>"
    except Exception as e:
        send_telegram(f"❌ Login failed: {e}")
        return f"<h2>❌ Login failed: {e}</h2>"

def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    if os.path.exists(access_token_file):
        os.remove(access_token_file)
    threading.Thread(target=open_browser).start()
    app.run(port=8000)
