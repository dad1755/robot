import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import openai
import numpy as np

# OpenAI API Key (Set your key here)
OPENAI_API_KEY = "your-api-key"

# Fetch EUR/USD Forex Data
def fetch_forex_data():
    try:
        data = yf.download("EURUSD=X", period="6mo", interval="1d")
        return data
    except Exception as e:
        return None

# Analyze Forex Trends with AI
def analyze_trends(data):
    if data is None or data.empty:
        return "⚠️ No data available for analysis."

    # Extract key stats
    latest_price = data["Close"].iloc[-1]
    price_change = latest_price - data["Close"].iloc[-2]
    trend = "uptrend 📈" if price_change > 0 else "downtrend 📉"

    # Send to OpenAI for analysis
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": f"Analyze this EUR/USD forex data: {data.tail(5)}. The latest trend is {trend}."}
        ]
    )
    
    return response["choices"][0]["message"]["content"]

# Streamlit UI
st.title("📈 Automated Trading Signal Analyzer")

# Fetch & display forex data
forex_data = fetch_forex_data()

if forex_data is not None and not forex_data.empty:
    st.subheader("📊 EUR/USD 6-Month Chart")

    # Plot forex chart
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(forex_data.index, forex_data["Close"], label="Close Price", color="blue")
    ax.set_title("EUR/USD Forex Chart (6 Months)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    st.pyplot(fig)

    # Analyze with AI
    st.subheader("🔥 AI Analysis:")
    analysis = analyze_trends(forex_data)
    st.write(analysis)
else:
    st.error("⚠️ Failed to fetch forex data. Check Yahoo Finance API!")

