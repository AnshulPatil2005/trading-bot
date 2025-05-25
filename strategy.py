import pandas as pd

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))

def check_bullish_rsi_divergence(df):
    if len(df) < 20:
        return False
    df = df.copy()
    df['rsi'] = calculate_rsi(df)
    recent = df.tail(5)
    return recent['close'].iloc[-1] > recent['close'].iloc[-3] and recent['rsi'].iloc[-1] < recent['rsi'].iloc[-3]

def check_bearish_rsi_divergence(df):
    if len(df) < 20:
        return False
    df = df.copy()
    df['rsi'] = calculate_rsi(df)
    recent = df.tail(5)
    return recent['close'].iloc[-1] < recent['close'].iloc[-3] and recent['rsi'].iloc[-1] > recent['rsi'].iloc[-3]
