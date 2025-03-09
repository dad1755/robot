import streamlit as st
import time
import cv2
import numpy as np
import openai
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Set OpenAI API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to Capture Screenshot using Selenium
def capture_screenshot(url, save_path):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    time.sleep(5)  # Wait for the page to load

    driver.save_screenshot(save_path)
    driver.quit()
    return save_path

# Preprocess the Image for Pattern Recognition
def preprocess_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    edges = cv2.Canny(image, 50, 150)  # Edge detection
    return edges

# Send Image to ChatGPT Vision API for Pattern Recognition
def analyze_chart_with_chatgpt(image_path):
    with open(image_path, "rb") as img_file:
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "system", "content": "You are a professional stock market analyst. Analyze the chart pattern and provide a buy/sell recommendation."},
                {"role": "user", "content": "What is the trend in this stock chart?"},
                {"role": "user", "content": {"image": img_file}}
            ]
        )
    return response["choices"][0]["message"]["content"]

# Streamlit UI
st.title("📊 Automated Stock Market Chart Analysis")

yahoo_finance_url = "https://finance.yahoo.com"

if st.button("Capture & Analyze Yahoo Finance Chart"):
    screenshot_path = capture_screenshot(yahoo_finance_url, "chart.png")
    edges = preprocess_image(screenshot_path)
    
    st.image(edges, caption="Processed Chart", channels="GRAY")

    with st.spinner("Analyzing chart pattern..."):
        analysis = analyze_chart_with_chatgpt(screenshot_path)
        st.write("📈 **Analysis Result:**")
        st.write(analysis)
