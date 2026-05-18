import os
import re
import json
import html
import time
import random
import requests
from langchain_groq import ChatGroq


def get_video_id(url):
    # Step 1: We need the unique ID of the YouTube video.
    # This improved regex supports:
    # youtube.com/watch?v=
    # youtu.be/
    # youtube.com/embed/
    # youtube.com/shorts/
    pattern = r'(?:v=|youtu\.be\/|embed\/|shorts\/|\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None


def get_proxy_list():
    # Step 1: Get proxy/proxies from .env file.
    # Recommended .env format:
    # PROXIES=http://user:pass@ip1:port,http://user:pass@ip2:port
    proxies = os.getenv("PROXIES", "").strip()

    # Step 2: If multiple proxies exist, split them by comma.
    if proxies:
        return [proxy.strip() for proxy in proxies.split(",") if proxy.strip()]

    # Step 3: If only one proxy exists, use that.
    # Alternative .env format:
    # PROXY=http://user:pass@ip:port
    single_proxy = os.getenv("PROXY", "").strip()

    if single_proxy:
        return [single_proxy]

    # Step 4: If no proxy is found, return empty list.
    return []


def fetch_transcript(video_id):
    # Step 1: Try the easiest way first using youtube_transcript_api.
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        # Step 2: Load proxies from .env.
        proxy_list = get_proxy_list()

        # Step 3: Randomly select one proxy if available.
        proxy = random.choice(proxy_list) if proxy_list else None

        # Step 4: If proxy exists, use it with youtube_transcript_api.
        if proxy:
            data = YouTubeTranscriptApi.get_transcript(
                video_id,
                proxies={
                    "http": proxy,
                    "https": proxy
                }
            )
        else:
            data = YouTubeTranscriptApi.get_transcript(video_id)

        # Step 5: Join all transcript chunks into one paragraph.
        return " ".join([item["text"] for item in data])

    except Exception:
        # Step 6: If official transcript method fails, use yt-dlp fallback.
        return _fetch_with_ytdlp(video_id)


def _fetch_with_ytdlp(video_id):
    import yt_dlp

    # Step 1: Set up the YouTube link.
    url = f"https://www.youtube.com/watch?v={video_id}"

    # Step 2: Load proxy list from .env.
    proxy_list = get_proxy_list()

    # Step 3: Try multiple times because YouTube may block one proxy.
    last_error = ""

    for attempt in range(5):
        # Step 4: Pick a random proxy on every attempt.
        proxy = random.choice(proxy_list) if proxy_list else None

        # Step 5: yt-dlp settings.
        # skip_download=True means we only need subtitle/transcript, not video.
        options = {
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,

            # This User-Agent helps reduce bot detection.
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
            },

            # Small delay to avoid aggressive requests.
            "sleep_interval": 2,
            "max_sleep_interval": 5
        }

        # Step 6: Add proxy if available.
        if proxy:
            options["proxy"] = proxy

        # Step 7: Use cookies.txt if available.
        # Important: cookies.txt should be fresh and should not be public.
        if os.path.exists("cookies.txt"):
            options["cookiefile"] = "cookies.txt"

        try:
            # Step 8: Fetch video information from YouTube.
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)

            # Step 9: Find English subtitles or auto-generated captions.
            subtitles = (
                info.get("subtitles", {}).get("en")
                or info.get("automatic_captions", {}).get("en")
                or info.get("subtitles", {}).get("en-US")
                or info.get("automatic_captions", {}).get("en-US")
            )

            # Step 10: If no subtitles are found, stop here.
            if not subtitles:
                return "Error: No English subtitles found for this video."

            # Step 11: Get subtitle download URL.
            subtitle_url = subtitles[0]["url"]

            # Step 12: Download subtitle text using same proxy.
            response = requests.get(
                subtitle_url,
                proxies={"http": proxy, "https": proxy} if proxy else None,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
                },
                timeout=20
            )

            text = response.text

            # Step 13: If subtitle is JSON3 format, extract spoken words.
            if "events" in text:
                data = json.loads(text)
                lines = []

                for event in data.get("events", []):
                    for seg in event.get("segs", []):
                        lines.append(seg.get("utf8", ""))

                text = " ".join(lines)

            # Step 14: Clean transcript text.
            text = html.unescape(text)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()

            # Step 15: Return transcript if found.
            if text:
                return text

        except Exception as e:
            # Step 16: Save error and retry with another proxy.
            last_error = str(e)
            time.sleep(3)

    # Step 17: If all attempts fail, return final error.
    return f"Error fetching transcript after retries: {last_error}"


def generate_summary(transcript, api_key):
    # Step 1: Make sure we have API key.
    if not api_key:
        return "Please set your API key first."

    # Step 2: Initialize Groq model.
    llm = ChatGroq(api_key=api_key, model_name="llama-3.3-70b-versatile")

    # Step 3: Create summary prompt.
    prompt = (
        "Please summarize the following YouTube video transcript in simple bullet points. "
        "Focus on the main ideas and takeaways.\n\n"
        f"Transcript: {transcript}"
    )

    # Step 4: Generate summary.
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"


def get_ai_response(user_question, transcript, summary, api_key):
    # Step 1: Make sure we have API key.
    if not api_key:
        return "Please set your API key first."

    # Step 2: Initialize Groq model.
    llm = ChatGroq(api_key=api_key, model_name="llama-3.3-70b-versatile")

    # Step 3: Give AI full context.
    prompt = (
        "You are a helpful assistant. Use the video summary and transcript below to answer the user's question.\n\n"
        f"Summary: {summary}\n\n"
        f"Transcript: {transcript}\n\n"
        f"User Question: {user_question}"
    )

    # Step 4: Generate answer.
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"