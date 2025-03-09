import streamlit as st
import requests
import cv2
import numpy as np
import openai
import pytesseract
from PIL import Image
from io import BytesIO

# OpenAI API Key (Set your key here)
OPENAI_API_KEY = "your-api-key"

# Yahoo Finance Chart Image URL
YAHOO_CHART_URL = "https://chart.finance.yahoo.com/z?s=EURUSD=X&t=6m&q=l&l=on&z=l&p=m50,m200"

def fetch_chart():
    """Fetch the Yahoo Finance chart image directly."""
    try:
        response = requests.get(YAHOO_CHART_URL)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        return None

def analyze_chart_with_ai(image_data):
    """Extracts text from the image and sends it to ChatGPT for analysis."""
    try:
        # Load image
        image = Image.open(BytesIO(image_data))
        img_array = np.array(image)

        # Convert to grayscale for OCR
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Extract text using Tesseract OCR
        extracted_text = pytesseract.image_to_string(gray)

        if not extracted_text.strip():
            return "⚠️ No readable text found in the chart."

        # Send extracted data to OpenAI for analysis
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

chart_data = fetch_chart()
if chart_data:
    st.image(chart_data, caption="Captured Yahoo Finance Chart")
    
    # Analyze chart with AI
    analysis = analyze_chart_with_ai(chart_data)
    st.subheader("🔥 AI Analysis:")
    st.write(analysis)
else:
    st.error("⚠️ Failed to fetch chart. Check Yahoo Finance URL!")
