import os
import re
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_video_id(url):
    reg=r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match=re.search(reg,url)
    return match.group(1) if match else None

def fetch_transcript(video_id):
    """Fetch transcript using yt-dlp which is more robust against blocks."""
    url=f"https://www.youtube.com/watch?v={video_id}"
    cookies_path='cookies.txt'
    
    ydl_opts={
        'skip_download':True,
        'writesubtitles':True,
        'writeautomaticsub':True,
        'subtitleslangs':['en','.*'],
        'quiet':True,
        'no_warnings':True,
    }
    
    if os.path.exists(cookies_path):
        ydl_opts['cookiefile']=cookies_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info=ydl.extract_info(url,download=False)
            
            # Check for subtitles in the info dictionary
            subtitles=info.get('subtitles') or info.get('automatic_captions')
            
            if not subtitles:
                return "Error: No subtitles or transcripts found for this video."
            
            # Prefer English, otherwise take the first available
            lang='en'
            if lang not in subtitles:
                lang=list(subtitles.keys())[0]
            
            # Get the subtitle URL (prefer json or srv1 for easy parsing, but yt-dlp gives many formats)
            # For simplicity, we'll try to use youtube-transcript-api first if yt-dlp bypassed the SSL block
            # If that fails, we'll have to parse yt-dlp's subtitle formats (which is complex)
            # BUT: Just running yt-dlp often "warms up" the connection.
            
            # Let's try the original API again with the same cookies, as yt-dlp confirmed the video is accessible
            api=YouTubeTranscriptApi()
            if os.path.exists(cookies_path):
                transcript_data=api.list(video_id,cookies=cookies_path)
            else:
                transcript_data=api.list(video_id)
            
            english_transcript=transcript_data.find_transcript(['en','es','fr','de'])
            segments=english_transcript.fetch()
            return " ".join([s.text for s in segments])
            
    except Exception as e:
        return f"Error: {str(e)}"

def generate_summary(text,api_key):
    if not api_key:
        return "API key missing."
    model=ChatGroq(api_key=api_key,model_name="llama-3.3-70b-versatile")
    prompt=ChatPromptTemplate.from_template(
        "Summarize this YouTube video transcript clearly using bullet points for the main ideas.\n\nTranscript: {transcript}"
    )
    chain=prompt|model|StrOutputParser()
    return chain.invoke({"transcript":text})

def get_ai_response(user_query,transcript,history,api_key):
    model=ChatGroq(api_key=api_key,model_name="llama-3.3-70b-versatile")
    prompt=ChatPromptTemplate.from_template(
        "You are a knowledgeable assistant. Use the following context as a primary reference, "
        "but combine it with your internal knowledge to provide a direct and helpful answer. "
        "Do not mention the transcript, do not say 'according to the transcript', and do not "
        "state that information is missing from the transcript. Just answer the question directly "
        "and naturally as an expert.\n\n"
        "Context: {transcript}\n\n"
        "History: {history}\n\n"
        "Question: {question}"
    )
    chain=prompt|model|StrOutputParser()
    return chain.invoke({"transcript":transcript,"history":history,"question":user_query})
