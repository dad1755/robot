import streamlit as st
import time
import pyautogui
import cv2
import pytesseract
import openai
import talib
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Set your ChatGPT API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to Capture Screenshot
def capture_screenshot(save_path, url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    
    time.sleep(5)  # Wait for the page to load

    screenshot = pyautogui.screenshot()
    screenshot.save(save_path)
    
    driver.quit()
    return save_path

# Extract Text & Numbers from Screenshot using OCR
def extract_text(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

# Analyze Market Trends using Technical Indicators
def analyze_market(data):
    prices = np.array([float(x) for x in data if x.replace('.', '', 1).isdigit()])
    if len(prices) < 5:
        return "Not enough data for analysis"

    sma = talib.SMA(prices, timeperiod=5)[-1]
    macd, signal, _ = talib.MACD(prices)
    macd_val, signal_val = macd[-1], signal[-1]

    if macd_val > signal_val and prices[-1] > sma:
        return "🔼 **BUY SIGNAL** - Uptrend detected!"
    elif macd_val < signal_val and prices[-1] < sma:
        return "🔽 **SELL SIGNAL** - Downtrend detected!"
    else:
        return "⏳ **HOLD** - No strong trend"

# Send Data to ChatGPT for Deeper Analysis
def chatgpt_analysis(text_data):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a professional financial market analyst."},
            {"role": "user", "content": f"Analyze this market data and provide a buy/sell recommendation: {text_data}"}
        ]
    )
    return response["choices"][0]["message"]["content"]

# Streamlit UI
st.title("📊 Automated Market Analysis - Yahoo Finance")

# Buttons to Capture Screenshots
if st.button("Capture 15m Chart Screenshot"):
    img_path_15m = capture_screenshot("chart_15m.png", "https://finance.yahoo.com")
    st.image(img_path_15m, caption="15m Chart Captured")
    extracted_text_15m = extract_text(img_path_15m)
    st.write("Extracted Data:", extracted_text_15m)

    # Get Market Analysis
    trend_analysis = analyze_market(extracted_text_15m.split())
    chatgpt_result = chatgpt_analysis(extracted_text_15m)
    
    st.write("📌 **Technical Analysis:**", trend_analysis)
    st.write("💡 **ChatGPT Insights:**", chatgpt_result)

if st.button("Capture 5m Chart Screenshot"):
    img_path_5m = capture_screenshot("chart_5m.png", "https://finance.yahoo.com")
    st.image(img_path_5m, caption="5m Chart Captured")
    extracted_text_5m = extract_text(img_path_5m)
    st.write("Extracted Data:", extracted_text_5m)

    # Get Market Analysis
    trend_analysis = analyze_market(extracted_text_5m.split())
    chatgpt_result = chatgpt_analysis(extracted_text_5m)
    
    st.write("📌 **Technical Analysis:**", trend_analysis)
    st.write("💡 **ChatGPT Insights:**", chatgpt_result)
