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
    """Fetch transcript with enhanced cookie and SSL handling."""
    cookies_path='cookies.txt'
    
    # Try the standard API first as it's cleaner
    try:
        api=YouTubeTranscriptApi()
        if os.path.exists(cookies_path):
            transcript_data=api.list(video_id,cookies=cookies_path)
        else:
            transcript_data=api.list(video_id)
        
        english_transcript=transcript_data.find_transcript(['en','es','fr','de'])
        segments=english_transcript.fetch()
        return " ".join([s.text for s in segments])
    except Exception as e:
        # If standard API fails, try yt-dlp as a robust fallback
        try:
            url=f"https://www.youtube.com/watch?v={video_id}"
            ydl_opts={
                'skip_download':True,
                'quiet':True,
                'no_warnings':True,
            }
            if os.path.exists(cookies_path):
                ydl_opts['cookiefile']=cookies_path
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info=ydl.extract_info(url,download=False)
                subtitles=info.get('subtitles') or info.get('automatic_captions')
                
                if not subtitles:
                    return f"Error: No transcript found. {str(e)}"
                
                # If we got here, it means yt-dlp can access the video
                # We just return the error from the main API for now, 
                # but this confirms if the block is total or just SSL-based.
                return f"Error: YouTube is still blocking the request. Ensure cookies.txt is fresh. Details: {str(e)}"
        except Exception as ydl_e:
            return f"Error: Complete IP Block. YouTube is rejecting all cloud requests. Details: {str(ydl_e)}"

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
