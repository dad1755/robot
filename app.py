import streamlit as st
import time
import numpy as np
import pytesseract
import openai
import cv2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Function to capture a screenshot from Yahoo Finance EUR/USD chart
def get_screenshot():
    url = "https://finance.yahoo.com/quote/EURUSD=X/chart"

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for headless mode
    chrome_options.add_argument("--no-sandbox")  # Required for cloud environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Avoid shared memory issues
    chrome_options.add_argument("--window-size=1920x1080")  # Ensure large capture

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)
        time.sleep(5)  # Wait for the chart to load

        screenshot_path = "chart_screenshot.png"
        driver.save_screenshot(screenshot_path)
        driver.quit()

        return screenshot_path
    except Exception as e:
        st.error(f"WebDriver Error: {e}")
        return None

# Function to analyze the chart using OpenAI
def analyze_chart(image_path):
    img = cv2.imread(image_path)
    text = pytesseract.image_to_string(img)  # Extract text from the chart

    # Send extracted text to ChatGPT for analysis
    openai.api_key = "YOUR_OPENAI_API_KEY"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Analyze this chart and give trading advice"},
                  {"role": "user", "content": text}]
    )
    
    return response["choices"][0]["message"]["content"]

# Streamlit UI
st.title("📈 Automated Trading Signal Analyzer")

if st.button("Capture and Analyze Chart"):
    with st.spinner("Fetching EUR/USD chart..."):
        screenshot_file = get_screenshot()

        if screenshot_file:
            st.image(screenshot_file, caption="Captured Chart", use_column_width=True)

            st.write("🔍 **Analyzing chart for trading signals...**")
            analysis_result = analyze_chart(screenshot_file)

            st.write("📊 **Trading Recommendation:**")
            st.success(analysis_result)
        else:
            st.error("⚠️ Failed to capture screenshot. Check WebDriver setup!")
