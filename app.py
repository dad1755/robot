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

# OpenAI API Key (Set your key here)
OPENAI_API_KEY = "your-api-key"

def get_screenshot():
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Install & setup ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Open Yahoo Finance EUR/USD chart
        url = "https://finance.yahoo.com/quote/EURUSD=X/chart"
        driver.get(url)
        time.sleep(5)  # Allow chart to load

        # Screenshot
        screenshot_path = "chart.png"
        driver.save_screenshot(screenshot_path)
        driver.quit()

        return screenshot_path

    except Exception as e:
        st.error(f"WebDriver Error: {e}")
        return None

def analyze_chart_with_ai(image_path):
    """Extracts text from the image and sends it to ChatGPT for analysis."""
    try:
        # Load image
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Extract text using Tesseract OCR
        extracted_text = pytesseract.image_to_string(gray)

        if not extracted_text.strip():
            return "⚠️ No readable text found in the chart."

        # Send to OpenAI API for analysis
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert financial analyst."},
                {"role": "user", "content": f"Analyze this forex chart data: {extracted_text}"}
            ]
        )

        return response["choices"][0]["message"]["content"]

    except Exception as e:
        return f"AI Analysis Error: {e}"

# Streamlit UI
st.title("📈 Automated Trading Signal Analyzer")

screenshot_file = get_screenshot()
if screenshot_file:
    st.image(screenshot_file, caption="Captured Chart Screenshot")
    
    # Analyze chart with AI
    analysis = analyze_chart_with_ai(screenshot_file)
    st.subheader("🔥 AI Analysis:")
    st.write(analysis)
else:
    st.error("⚠️ Failed to capture screenshot. Check WebDriver setup!")
