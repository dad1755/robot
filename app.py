import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from openai import OpenAI, OpenAIError
import os

# Load API Key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("⚠️ Missing OpenAI API Key. Set it as an environment variable.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Fetch EUR/USD Forex Data
def fetch_forex_data(interval):
    try:
        data = yf.download("EURUSD=X", period="1d", interval=interval)
        return data if not data.empty else None
    except Exception as e:
        st.error(f"⚠️ Error fetching forex data: {e}")
        return None

# Analyze Forex Trends with AI
def analyze_trends(data):
    if data is None or data.empty:
        return "⚠️ No data available for analysis."

    try:
        latest_price = data["Close"].iloc[-1]
        prev_price = data["Close"].iloc[-2]
        price_change = float(latest_price - prev_price)
        trend = "uptrend 📈" if price_change > 0 else "downtrend 📉"

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial analyst."},
                {"role": "user", "content": f"Analyze this EUR/USD forex data: {data.tail(5)}. The latest trend is {trend}."}
            ]
        )
        return completion.choices[0].message.content

    except OpenAIError as e:
        return f"⚠️ AI Analysis Error: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected Error: {str(e)}"

# Streamlit UI
st.title("📈 EUR/USD Forex Signal Analyzer")

# Fetch 15m and 5m forex data
intervals = {"15m": "15m", "5m": "5m"}
for label, interval in intervals.items():
    st.subheader(f"📊 EUR/USD {label} Chart")
    forex_data = fetch_forex_data(interval)

    if forex_data is not None:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(forex_data.index, forex_data["Close"], label="Close Price", color="blue")
        ax.set_title(f"EUR/USD Forex Chart ({label})")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        ax.legend()
        st.pyplot(fig)

        # AI Analysis
        st.subheader("🔥 AI Analysis:")
        analysis = analyze_trends(forex_data)
        st.write(analysis)
    else:
        st.error(f"⚠️ Failed to fetch {label} forex data. Check Yahoo Finance API!")
