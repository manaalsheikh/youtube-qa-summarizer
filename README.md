---
title: Youtube Summarizer QA Gradio
emoji: 🎥
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 4.19.2
app_file: gradio_app.py
pinned: false
license: mit
---

# YouTube Video Summarizer & QA

A high-performance web application that summarizes YouTube videos and allows users to ask questions about the content using the Groq API.

## Features
- **Two Interfaces**: Choose between Streamlit and Gradio.
- **Fast Summarization**: Powered by Groq's Llama 3.3 70B model.
- **Interactive QA**: Chat with the video content to find specific information.
- **Robust Fetching**: Uses `yt-dlp` and `cookies.txt` to ensure reliable transcript extraction.

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your `GROQ_API_KEY`.
4. Create a `cookies.txt` file from your YouTube session.

## Running the App
- **Streamlit Version**:
  ```bash
  streamlit run app.py
  ```
- **Gradio Version**:
  ```bash
  python gradio_app.py
  ```

## Deployment
This app is ready for **Streamlit Cloud** (using `app.py`) or **Hugging Face Spaces** (using `gradio_app.py`).
- For Hugging Face, set `sdk: gradio` and `app_file: gradio_app.py` in your README metadata.
- Remember to add your `GROQ_API_KEY` as a Secret.
