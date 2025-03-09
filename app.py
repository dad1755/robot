import streamlit as st
import time
import cv2
import numpy as np
import openai
import pytesseract
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_screenshot():
    """Captures a screenshot of the EUR/USD chart from Yahoo Finance."""
    url = "https://finance.yahoo.com/quote/EURUSD=X/chart"  # Direct chart link
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(5)  # Wait for chart to load
        screenshot_path = "chart_screenshot.png"
        driver.save_screenshot(screenshot_path)
        driver.quit()
        return screenshot_path
    except Exception as e:
        driver.quit()
        st.error(f"Failed to capture screenshot: {e}")
        return None

def extract_chart_data(image_path):
    """Extracts price data from the chart screenshot using OCR."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

def analyze_chart_with_gpt(text_data):
    """Sends extracted data to ChatGPT for market trend analysis."""
    openai.api_key = "your-openai-api-key"  # Replace with your API key
    
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": "Analyze the given market data and provide a trading signal (BUY, SELL, HOLD)."},
            {"role": "user", "content": text_data}
        ]
    )
    return response["choices"][0]["message"]["content"]

# Streamlit UI
st.title("📈 Automated Trading Signal Analyzer")
if st.button("Capture & Analyze Chart"):
    screenshot_file = get_screenshot()
    if screenshot_file:
        st.image(screenshot_file, caption="Captured Chart", use_column_width=True)
        extracted_data = extract_chart_data(screenshot_file)
        trading_signal = analyze_chart_with_gpt(extracted_data)
        st.subheader("📊 Trading Signal:")
        st.write(trading_signal)
