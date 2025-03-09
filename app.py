import os
import time
import streamlit as st
import numpy as np
import openai
import cv2
import pytesseract
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options



# Set up Selenium for taking screenshots
def get_screenshot(url, filename="screenshot.png"):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    time.sleep(5)  # Wait for page to load
    driver.save_screenshot(filename)
    driver.quit()
    return filename

# Image processing using OpenCV & OCR
def process_chart(filename):
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

# Send chart data to OpenAI for analysis
def analyze_chart(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Analyze this chart data and give trading signal:\n{text}"}]
    )
    return response["choices"][0]["message"]["content"]

# Streamlit UI
st.title("Automated Trading Signal Analyzer")
url = st.text_input("Enter Yahoo Finance Chart URL:", "https://finance.yahoo.com/")
if st.button("Analyze Chart"):
    screenshot_file = get_screenshot(url)
    chart_data = process_chart(screenshot_file)
    signal = analyze_chart(chart_data)
    st.image(screenshot_file, caption="Captured Chart", use_column_width=True)
    st.write("### Trading Signal")
    st.write(signal)
