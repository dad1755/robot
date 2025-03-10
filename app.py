import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import datetime
from openai import OpenAI, OpenAIError

# ✅ Check if API key is loaded correctly
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ Missing OpenAI API Key. Please set it in .streamlit/secrets.toml or Streamlit Cloud secrets.")
    st.stop()

# Load OpenAI API key securely from Streamlit secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Function to fetch EUR/USD Forex Data
def fetch_forex_data(interval):
    try:
        data = yf.download("EURUSD=X", period="1d", interval=interval)
        return data if not data.empty else None
    except Exception as e:
        st.error(f"⚠️ Error fetching forex data: {e}")
        return None

# Function to analyze forex trends with AI
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
                {"role": "system", "content": "You are a financial analyst. Based on chart patterns, just answer: BUY or SELL, with the exact price, where to close the order, or when to enter."},
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

# ✅ Show a success message if API key is loaded correctly
st.success("✅ OpenAI API Key Loaded Successfully!")  

# Initialize session state for tracking updates
if "forex_data" not in st.session_state:
    st.session_state.forex_data = {}

if "analysis" not in st.session_state:
    st.session_state.analysis = {}

if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.datetime.now()

# Time remaining for next update (15 minutes interval)
update_interval = 900  # 15 minutes in seconds
time_since_update = (datetime.datetime.now() - st.session_state.last_update).total_seconds()
time_remaining = max(0, update_interval - time_since_update)

st.write(f"🔄 Next update in: {int(time_remaining // 60)} min {int(time_remaining % 60)} sec")

# Auto-refresh logic
if time_since_update >= update_interval:
    st.session_state.forex_data.clear()
    st.session_state.analysis.clear()
    st.session_state.last_update = datetime.datetime.now()
    st.rerun()  # Safe way to trigger a rerun

# Fetch and display forex data
intervals = {"15m": "15m", "5m": "5m"}
for label, interval in intervals.items():
    st.subheader(f"📊 EUR/USD {label} Chart")

    if interval not in st.session_state.forex_data:
        st.session_state.forex_data[interval] = fetch_forex_data(interval)

    forex_data = st.session_state.forex_data.get(interval)

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
        if interval not in st.session_state.analysis:
            st.session_state.analysis[interval] = analyze_trends(forex_data)

        st.write(st.session_state.analysis[interval])
    else:
        st.error(f"⚠️ Failed to fetch {label} forex data. Check Yahoo Finance API!")

# Streamlit's built-in auto-refresh
st.rerun()  # Auto-refresh every 15 minutes
