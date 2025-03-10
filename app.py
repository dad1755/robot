import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import datetime
import io
from openai import OpenAI, OpenAIError

# ✅ Load OpenAI API Key securely
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ Missing OpenAI API Key. Please set it in .streamlit/secrets.toml or Streamlit Cloud secrets.")
    st.stop()

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ Function to fetch EUR/USD Forex Data
def fetch_forex_data(interval):
    try:
        data = yf.download("EURUSD=X", period="1d", interval=interval)
        return data if not data.empty else None
    except Exception as e:
        st.error(f"⚠️ Error fetching forex data: {e}")
        return None

# ✅ Function to save chart as an image
def save_chart_as_image(data, interval):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data.index, data["Close"], label="Close Price", color="blue")
    ax.set_title(f"EUR/USD Forex Chart ({interval})")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    ax.legend()
    
    # Save the chart as an image
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format="png")
    img_buf.seek(0)  # Move to the beginning of the file
    
    return img_buf

# ✅ Function to analyze forex chart with AI
def analyze_chart_with_ai(image_buf):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial analyst. Look at the forex chart and provide a BUY or SELL signal with key price levels."},
                {"role": "user", "content": "Analyze this forex chart and give a recommendation.", "image": image_buf}
            ]
        )
        return completion.choices[0].message.content

    except OpenAIError as e:
        return f"⚠️ AI Analysis Error: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected Error: {str(e)}"

# ✅ Streamlit UI
st.title("📈 EUR/USD Forex Signal Analyzer")

# ✅ Show success message for API key
st.success("✅ OpenAI API Key Loaded Successfully!")  

# Initialize session state for tracking updates
if "forex_data" not in st.session_state:
    st.session_state.forex_data = {}

if "analysis" not in st.session_state:
    st.session_state.analysis = {}

if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.datetime.now()

# ✅ Time remaining for next update (15 min interval)
update_interval = 900  # 15 minutes in seconds
time_since_update = (datetime.datetime.now() - st.session_state.last_update).total_seconds()
time_remaining = max(0, update_interval - time_since_update)

st.write(f"🔄 Next update in: {int(time_remaining // 60)} min {int(time_remaining % 60)} sec")

# ✅ Fetch and display forex data if time has elapsed
if time_since_update >= update_interval:
    st.session_state.forex_data.clear()
    st.session_state.analysis.clear()
    st.session_state.last_update = datetime.datetime.now()
    st.experimental_rerun()

# ✅ Fetch and analyze forex charts
intervals = {"15m": "15m", "5m": "5m"}
for label, interval in intervals.items():
    st.subheader(f"📊 EUR/USD {label} Chart")

    if interval not in st.session_state.forex_data:
        st.session_state.forex_data[interval] = fetch_forex_data(interval)

    forex_data = st.session_state.forex_data.get(interval)

    if forex_data is not None:
        img_buf = save_chart_as_image(forex_data, label)
        st.image(img_buf, caption=f"{label} Forex Chart", use_column_width=True)

        # ✅ AI Analysis
        st.subheader("🔥 AI Analysis:")
        if interval not in st.session_state.analysis:
            st.session_state.analysis[interval] = analyze_chart_with_ai(img_buf)

        st.write(st.session_state.analysis[interval])
    else:
        st.error(f"⚠️ Failed to fetch {label} forex data. Check Yahoo Finance API!")
