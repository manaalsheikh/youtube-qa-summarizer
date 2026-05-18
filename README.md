# YouTube Video AI Summarizer & QA

A clean and efficient web application that summarizes YouTube videos and allows you to chat with the content. Powered by Streamlit and Groq's Llama 3 models.

## Features
- **Instant Summarization:** Get key takeaways from any YouTube video in seconds.
- **Interactive Chat:** Ask specific questions about the video content.
- **Reliable Transcripts:** Uses official transcripts with a robust fallback system.
- **Simple Setup:** Minimal files, easy to run locally.

## Setup

### 1. Clone the project
```bash
git clone <your-repo-url>
cd QA_Summarizer
```

### 2. Configuration
- Create a `.env` file in the root directory.
- Add your Groq API key:
  ```
  GROQ_API_KEY=your_api_key_here
  ```
- (Optional) Add a `cookies.txt` file in the root directory to help with YouTube transcript fetching.

### 3. Install & Run with `uv` (Recommended)
`uv` is an extremely fast Python package manager.

**Run the app directly:**
```bash
uv run streamlit run app.py
```
*This will automatically handle the environment and dependencies.*

---

### 4. Alternative: Manual Setup
If you prefer using standard `pip`:

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run the app:**
```bash
streamlit run app.py
```

## How to use
1. Launch the application.
2. Paste a YouTube video URL in the sidebar.
3. Click **Analyze Video**.
4. View the summary and start chatting with the AI about the video!
