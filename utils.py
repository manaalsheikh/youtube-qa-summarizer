import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_video_id(url):
    reg=r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match=re.search(reg,url)
    return match.group(1) if match else None

def fetch_transcript(video_id):
    try:
        api=YouTubeTranscriptApi()
        cookies_path='cookies.txt'
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
