import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import talib
from openai import OpenAI, OpenAIError

# ✅ Debugging: Check if API key is loaded correctly
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ Missing OpenAI API Key. Please set it in `.streamlit/secrets.toml` or Streamlit Cloud secrets.")
    st.stop()

# Load OpenAI API key securely from Streamlit secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# Function to fetch EUR/USD Forex Data
def fetch_forex_data(interval):
    try:
        data = yf.download("EURUSD=X", period="1d", interval=interval)
        return data if not data.empty else None
    except Exception as e:
        st.error(f"⚠️ Error fetching forex data: {e}")
        return None

# Function to add technical indicators
def add_indicators(data):
    data["SMA_50"] = talib.SMA(data["Close"], timeperiod=50)
    data["EMA_9"] = talib.EMA(data["Close"], timeperiod=9)
    data["RSI"] = talib.RSI(data["Close"], timeperiod=14)
    data["MACD"], data["MACD_Signal"], _ = talib.MACD(data["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
    data["Upper_BB"], data["Middle_BB"], data["Lower_BB"] = talib.BBANDS(data["Close"], timeperiod=20)
    data["ATR"] = talib.ATR(data["High"], data["Low"], data["Close"], timeperiod=14)
    return data

# Streamlit UI
st.title("📈 EUR/USD Forex Signal Analyzer")

# ✅ Debugging: Show a success message if API key is loaded correctly
st.success("✅ OpenAI API Key Loaded Successfully!")

# Fetch and display forex data
intervals = {"15m": "15m", "5m": "5m"}
for label, interval in intervals.items():
    st.subheader(f"📊 EUR/USD {label} Chart")
    forex_data = fetch_forex_data(interval)
    
    if forex_data is not None:
        forex_data = add_indicators(forex_data)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(forex_data.index, forex_data["Close"], label="Close Price", color="blue")
        ax.plot(forex_data.index, forex_data["SMA_50"], label="SMA 50", linestyle="--", color="orange")
        ax.plot(forex_data.index, forex_data["EMA_9"], label="EMA 9", linestyle="--", color="red")
        ax.fill_between(forex_data.index, forex_data["Lower_BB"], forex_data["Upper_BB"], color='gray', alpha=0.3, label="Bollinger Bands")
        ax.set_title(f"EUR/USD Forex Chart ({label})")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        ax.legend()
        st.pyplot(fig)
        
        # RSI Plot
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.plot(forex_data.index, forex_data["RSI"], label="RSI", color="purple")
        ax.axhline(70, linestyle="--", color="red", alpha=0.5)
        ax.axhline(30, linestyle="--", color="green", alpha=0.5)
        ax.set_title("Relative Strength Index (RSI)")
        st.pyplot(fig)
        
        # MACD Plot
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.plot(forex_data.index, forex_data["MACD"], label="MACD", color="blue")
        ax.plot(forex_data.index, forex_data["MACD_Signal"], label="Signal Line", color="red")
        ax.axhline(0, linestyle="--", color="gray", alpha=0.5)
        ax.set_title("MACD")
        st.pyplot(fig)
        
        # ATR Plot
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.plot(forex_data.index, forex_data["ATR"], label="ATR", color="black")
        ax.set_title("Average True Range (ATR)")
        st.pyplot(fig)
    else:
        st.error(f"⚠️ Failed to fetch {label} forex data. Check Yahoo Finance API!")
