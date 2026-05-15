# YouTube Video Summarizer & QA

A high-performance web application that summarizes YouTube videos and allows users to ask questions about the content using the Groq API.

## Features
- **Sleek Interface**: Built with Streamlit for a smooth user experience.
- **Fast Summarization**: Powered by Groq's Llama 3.3 70B model.
- **Interactive QA**: Chat with the video content to find specific information.
- **Robust Fetching**: Uses `yt-dlp` to ensure reliable transcript extraction.

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

## Deployment
This app is optimized for **Streamlit Cloud**.
- Add your `GROQ_API_KEY` in the **Secrets** section of your Streamlit Cloud dashboard.
- If you encounter blocks from YouTube, add a `cookies.txt` file to your repository (ensure it is ignored by git if it contains private data).
