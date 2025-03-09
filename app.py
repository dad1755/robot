import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
from openai import OpenAI, OpenAIError

# ✅ Debugging: Check if API key is loaded correctly
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ Missing OpenAI API Key. Please set it in `.streamlit/secrets.toml` or Streamlit Cloud secrets.")
    st.stop()

# Load OpenAI API key securely from Streamlit secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# Function to fetch EUR/USD Forex Data
def fetch_forex_data(interval, period):
    try:
        data = yf.download("EURUSD=X", period=period, interval=interval)
        if data.empty:
            st.warning(f"⚠️ No data fetched for {interval}. API might be down.")
            return None
        return data
    except Exception as e:
        st.error(f"⚠️ Error fetching forex data: {e}")
        return None

# Streamlit UI
st.title("📈 EUR/USD Forex Chart")

# ✅ Debugging: Show a success message if API key is loaded correctly
st.success("✅ OpenAI API Key Loaded Successfully!")

# Fetch and display forex data
intervals = {
    "15m": {"interval": "15m", "period": "3h"},  # 15-minute candles for last 3 hours
    "5m": {"interval": "5m", "period": "1h"}     # 5-minute candles for last 1 hour
}

for label, config in intervals.items():
    st.subheader(f"📊 EUR/USD {label} Chart")
    forex_data = fetch_forex_data(config["interval"], config["period"])

    if forex_data is not None:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(forex_data.index, forex_data["Close"], label="Close Price", color="blue")

        ax.set_title(f"EUR/USD Forex Chart ({label})")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        ax.legend()
        st.pyplot(fig)
    else:
        st.error(f"⚠️ Failed to fetch {label} forex data. Check Yahoo Finance API!")
