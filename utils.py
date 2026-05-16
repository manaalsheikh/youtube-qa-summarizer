import os
import re
import json
import html
import requests
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_video_id(url):
    reg=r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match=re.search(reg,url)
    return match.group(1) if match else None

def fetch_transcript(video_id):
    """Fetch a transcript from YouTube, with yt-dlp as a fallback."""
    errors=[]

    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        transcript=YouTubeTranscriptApi().fetch(video_id,languages=["en"])
        text=" ".join(snippet.text for snippet in transcript if snippet.text)
        if text.strip():
            return text
        errors.append("YouTubeTranscriptApi returned an empty transcript.")
    except Exception as e:
        errors.append(f"YouTubeTranscriptApi: {e}")

    try:
        return _fetch_transcript_with_ytdlp(video_id)
    except Exception as e:
        errors.append(f"yt-dlp: {e}")
        return f"Error: YouTube transcript fetching failed. {' | '.join(errors)}"

def _fetch_transcript_with_ytdlp(video_id):
    import yt_dlp

    url=f"https://www.youtube.com/watch?v={video_id}"
    cookies_path="cookies.txt"
    ydl_opts={
        "skip_download":True,
        "quiet":True,
        "no_warnings":True,
    }

    if os.path.exists(cookies_path):
        ydl_opts["cookiefile"]=cookies_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info=ydl.extract_info(url,download=False)

    caption=_select_caption(info.get("subtitles",{})) or _select_caption(info.get("automatic_captions",{}))
    if not caption:
        raise RuntimeError("No English subtitles or automatic captions were found.")

    response=requests.get(caption["url"],timeout=20)
    response.raise_for_status()

    if caption.get("ext")=="json3" or "json3" in caption["url"]:
        text=_parse_json3_caption(response.text)
    else:
        text=_parse_vtt_caption(response.text)

    if not text.strip():
        raise RuntimeError("Subtitle file was downloaded but no text could be parsed.")
    return text

def _select_caption(captions):
    tracks=captions.get("en") or captions.get("en-US") or captions.get("en-GB")
    if not tracks:
        return None

    for preferred_ext in ("json3","vtt"):
        for track in tracks:
            if track.get("ext")==preferred_ext and track.get("url"):
                return track

    return next((track for track in tracks if track.get("url")),None)

def _parse_json3_caption(payload):
    data=json.loads(payload)
    lines=[]
    for event in data.get("events",[]):
        parts=event.get("segs") or []
        line="".join(part.get("utf8","") for part in parts).strip()
        if line:
            lines.append(line)
    return _clean_caption_text(" ".join(lines))

def _parse_vtt_caption(payload):
    lines=[]
    for raw_line in payload.splitlines():
        line=raw_line.strip()
        if (
            not line
            or line.startswith(("WEBVTT","Kind:","Language:","NOTE"))
            or "-->" in line
            or re.fullmatch(r"\d+",line)
        ):
            continue
        lines.append(re.sub(r"<[^>]+>","",line))
    return _clean_caption_text(" ".join(lines))

def _clean_caption_text(text):
    text=html.unescape(text)
    text=re.sub(r"\s+"," ",text)
    return text.strip()

def generate_summary(text,api_key):
    if not api_key: return "API key missing."
    model=ChatGroq(api_key=api_key,model_name="llama-3.3-70b-versatile")
    prompt=ChatPromptTemplate.from_template("Summarize this: {transcript}")
    chain=prompt|model|StrOutputParser()
    return chain.invoke({"transcript":text})

def get_ai_response(user_query,transcript,history,api_key,summary=""):
    if not api_key: return "API key missing."
    model=ChatGroq(api_key=api_key,model_name="llama-3.3-70b-versatile")
    prompt=ChatPromptTemplate.from_template(
        "You are a helpful assistant in a YouTube summarizer and Q&A app.\n"
        "Answer the user's message directly.\n"
        "If the message is about the video, use the summary first, then the transcript for details.\n"
        "If the message is not related to the video or summary, answer from general knowledge.\n"
        "Never say the user did not ask a question. If the message is a fragment, topic, "
        "or command, infer the most useful intent and respond helpfully.\n"
        "Do not mention the summary or transcript unless the user asks about your source.\n\n"
        "Summary:\n{summary}\n\n"
        "Transcript:\n{transcript}\n\n"
        "User message:\n{question}"
    )
    chain=prompt|model|StrOutputParser()
    return chain.invoke({"summary":summary,"transcript":transcript,"question":user_query})
