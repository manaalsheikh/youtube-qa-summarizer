import streamlit as st
import os
import validators
from dotenv import load_dotenv
from utils import get_video_id,fetch_transcript,generate_summary,get_ai_response

# Load settings
load_dotenv()
api_key=os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

# App configuration
st.set_page_config(page_title="YouTube Video AI",layout="wide")

# Initialize session state for tracking data
if "transcript_text" not in st.session_state:
    st.session_state.transcript_text=""
if "messages" not in st.session_state:
    st.session_state.messages=[]
if "current_video_id" not in st.session_state:
    st.session_state.current_video_id=""

# UI Layout
st.title("YouTube Video Summarizer and QA")

with st.sidebar:
    st.header("Settings")
    video_url=st.text_input("YouTube URL",placeholder="Enter link here")
    
    if st.button("Analyze Video"):
        if not validators.url(video_url):
            st.error("Please provide a valid URL.")
        else:
            v_id=get_video_id(video_url)
            if v_id:
                with st.spinner("Fetching content..."):
                    text=fetch_transcript(v_id)
                    if text.startswith("Error:"):
                        st.error(text)
                    else:
                        st.session_state.transcript_text=text
                        st.session_state.current_video_id=v_id
                        
                        summary_result=generate_summary(text,api_key)
                        st.session_state.messages.append({"role":"assistant","content":f"Summary:\n{summary_result}"})
                        st.rerun()
            else:
                st.error("Invalid YouTube video ID.")

# Main content area
if st.session_state.transcript_text:
    st.video(f"https://www.youtube.com/watch?v={st.session_state.current_video_id}")
    
    st.subheader("Chat with this video")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input=st.chat_input("Ask a question about the video")
    if user_input:
        st.session_state.messages.append({"role":"user","content":user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response=get_ai_response(user_input,st.session_state.transcript_text,st.session_state.messages[:-1],api_key)
                st.markdown(response)
                st.session_state.messages.append({"role":"assistant","content":response})
else:
    st.info("Please enter a YouTube link in the sidebar to start.")
