---
title: Youtube Summarizer QA
emoji: 🎥
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.35.0
app_file: app.py
pinned: false
license: mit
---

# YouTube Video Summarizer & QA

A high-performance web application that summarizes YouTube videos and allows users to ask questions about the content using the Groq API.

## Features
- **Sleek Interface**: Built with Streamlit for a smooth user experience.
- **Fast Summarization**: Powered by Groq's Llama 3.3 70B model.
- **Interactive QA**: Chat with the video content to find specific information.
- **Modular Design**: Separated UI and logic for easy maintenance.

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your `GROQ_API_KEY`.
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Hugging Face Deployment
When deploying to Hugging Face Spaces:
1. Choose the **Streamlit** SDK.
2. Add your `GROQ_API_KEY` as a **Secret** in the Space settings.
