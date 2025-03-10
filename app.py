import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import datetime
import io
import base64
from openai import OpenAI, OpenAIError

# Load OpenAI API Key
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ Missing OpenAI API Key. Please set it in .streamlit/secrets.toml or Streamlit Cloud secrets.")
    st.stop()

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# Fetch EUR/USD Forex Data
def fetch_forex_data(interval):
    try:
        data = yf.download("EURUSD=X", period="2d", interval=interval)
        return data if not data.empty else None
    except Exception as e:
        st.error(f"⚠️ Error fetching forex data: {e}")
        return None

# Save chart as an image and convert to Base64
def save_chart_as_base64(data, interval):
    # Remove weekends (Saturday=5, Sunday=6)
    data = data[data.index.dayofweek < 5]  
    
    fig, ax = plt.subplots(figsize=(10, 5))

    # Ensure x-axis only contains valid trading timestamps (no gaps)
    ax.plot(data.index, data["Close"], label="Close Price", color="blue")

    ax.set_title(f"EUR/USD Forex Chart ({interval})")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    ax.legend()
    
    # Format x-axis to remove weekend gaps
    ax.set_xticks(data.index)  # Only show actual trading timestamps
    ax.set_xticklabels([d.strftime("%Y-%m-%d %H:%M") for d in data.index], rotation=45, ha="right")

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format="png", bbox_inches="tight")  # Ensure full labels are visible
    img_buf.seek(0)

    # Convert image to Base64 string
    img_base64 = base64.b64encode(img_buf.getvalue()).decode("utf-8")
    
    return img_base64

# Analyze forex pattern with GPT-4 Vision
def analyze_chart_pattern(image_base64):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a professional forex trader. Analyze the forex chart image and suggest a BUY or SELL decision."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this EUR/USD forex chart and suggest a BUY or SELL decision based on pattern analysis."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                    ]
                }
            ],
        )

        tokens_used = response.usage.total_tokens  # ✅ Get token usage

        return f"📊 AI Analysis Result:\n\n{response.choices[0].message.content}\n\n⚡ Tokens Used: {tokens_used}"

    except OpenAIError as e:
        return f"⚠️ AI Analysis Error: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected Error: {str(e)}"

# Streamlit UI
st.title("📈 EUR/USD Forex Pattern Analyzer")

st.success("✅ OpenAI API Key Loaded Successfully!")  

# Session state for tracking updates
if "forex_data" not in st.session_state:
    st.session_state.forex_data = {}

if "analysis" not in st.session_state:
    st.session_state.analysis = {}

if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.datetime.now()

# Time remaining for next update (15 min interval)
update_interval = 900  
time_since_update = (datetime.datetime.now() - st.session_state.last_update).total_seconds()
time_remaining = max(0, update_interval - time_since_update)

st.write(f"🔄 Next update in: {int(time_remaining // 60)} min {int(time_remaining % 60)} sec")

# Fetch and display forex data if time has elapsed
if time_since_update >= update_interval:
    st.session_state.forex_data.clear()
    st.session_state.analysis.clear()
    st.session_state.last_update = datetime.datetime.now()
    st.experimental_rerun()

# Fetch and analyze forex charts
intervals = {"15m": "15m", "5m": "5m"}
for label, interval in intervals.items():
    st.subheader(f"📊 EUR/USD {label} Chart")

    if interval not in st.session_state.forex_data:
        st.session_state.forex_data[interval] = fetch_forex_data(interval)

    forex_data = st.session_state.forex_data.get(interval)

    if forex_data is not None:
        img_base64 = save_chart_as_base64(forex_data, label)
        st.image(io.BytesIO(base64.b64decode(img_base64)), caption=f"{label} Forex Chart", use_container_width=True)

        # AI Pattern Analysis
        st.subheader("🔥 AI Pattern Analysis:")
        if interval not in st.session_state.analysis:
            st.session_state.analysis[interval] = analyze_chart_pattern(img_base64)

        st.write(st.session_state.analysis[interval])
    else:
        st.error(f"⚠️ Failed to fetch {label} forex data. Check Yahoo Finance API!")
