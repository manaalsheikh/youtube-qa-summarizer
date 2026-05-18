import streamlit as st
import os
import validators
from dotenv import load_dotenv
from summarizer import get_video_id,fetch_transcript,generate_summary,get_ai_response

# =============================================================================
# PART 1: GETTING STARTED
# =============================================================================

# Step 1: Look for the .env file and grab the secret API key so the AI can work.
load_dotenv()
api_key=os.getenv("GROQ_API_KEY")

# Step 2: Set up the webpage. Give it a title and make it stretch across the screen.
st.set_page_config(page_title="YouTube AI Summarizer",layout="wide")
st.title("🎬 YouTube AI Summarizer & Chat")

# =============================================================================
# PART 2: APP MEMORY
# =============================================================================
# Streamlit forgets everything when a button is clicked. 
# We use 'st.session_state' like a notepad to remember things while using the app.

# Remember the video's written words (transcript)
if "transcript" not in st.session_state:
    st.session_state.transcript=""
# Remember the AI's summary
if "summary" not in st.session_state:
    st.session_state.summary=""
# Remember our conversation with the AI
if "chat_history" not in st.session_state:
    st.session_state.chat_history=[]
# Remember which video we are looking at
if "video_id" not in st.session_state:
    st.session_state.video_id=""

# =============================================================================
# PART 3: THE SIDEBAR (User Inputs)
# =============================================================================
with st.sidebar:
    
    # Create a text box where the user can paste their YouTube link.
    video_url=st.text_input("Paste YouTube Link")
    
    # Create a big button that says "Analyze Video". If they click it, do the following:
    if st.button("Analyze Video"):
        
        # Check 1: Do we have an API key? If not, stop and show an error.
        if not api_key:
            st.error("API Key not found in .env file. Please add it to start.")
        
        # Check 2: Does the link look like a real website URL?
        elif not validators.url(video_url):
            st.error("Invalid URL. Please check the link.")
        
        # If everything is good, let's get to work!
        else:
            # Try to pull just the video ID out of the link.
            v_id=get_video_id(video_url)
            
            if v_id:
                # Show a spinning circle so the user knows we are working on it.
                with st.spinner("Processing..."):
                    
                    # Step 1: Download the text transcript of the video.
                    text=fetch_transcript(v_id)
                    
                    if text.startswith("Error"):
                        # If something broke during the download, show the error.
                        st.error(text)
                    else:
                        # Step 2: Save the text and video ID to our memory notepad.
                        st.session_state.transcript=text
                        st.session_state.video_id=v_id
                        
                        # Step 3: Ask the AI to write a summary of the text.
                        summary=generate_summary(text,api_key)
                        st.session_state.summary=summary
                        
                        # Step 4: Start the chat window, and make the AI's first message the summary.
                        st.session_state.chat_history=[
                            {"role":"assistant","content":f"**Summary of the video:**\n\n{summary}"}
                        ]
                        
                        # Step 5: Refresh the whole page to show our new results.
                        st.rerun()
            else:
                st.error("Could not find a video ID in that URL.")

    # Show a button to clear everything and start over, but only show it if we already have a transcript.
    if st.session_state.transcript:
        if st.button("Reset Everything"):
            # Erase the memory notepad and refresh the page.
            st.session_state.transcript=""
            st.session_state.summary=""
            st.session_state.chat_history=[]
            st.session_state.video_id=""
            st.rerun()

# =============================================================================
# PART 4: THE MAIN SCREEN
# =============================================================================

# If we have a transcript in memory, it means we are ready to show the results!
if st.session_state.transcript:
    
    # Split the screen down the middle into two columns.
    col1,col2=st.columns(2)
    
    # --- LEFT SIDE: Video and Transcript ---
    with col1:
        st.subheader("Video & Transcript")
        # Put the YouTube video player right on the screen.
        st.video(f"https://www.youtube.com/watch?v={st.session_state.video_id}")
        
        # Add a click-to-open box so the user can read the full text if they want to.
        with st.expander("Show Full Transcript"):
            st.write(st.session_state.transcript)
            
    # --- RIGHT SIDE: The AI Chat Box ---
    with col2:
        st.subheader("Chat with the AI")
        
        # Loop through our memory and print out all the past messages on the screen.
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Put a typing box at the bottom where the user can ask a new question.
        user_input=st.chat_input("Ask a question about the video...")
        
        # If the user typed something and hit enter...
        if user_input:
            # 1. Save their new question to the memory notepad.
            st.session_state.chat_history.append({"role":"user","content":user_input})
            
            # 2. Show a spinning circle while the AI thinks about the answer.
            with st.spinner("Thinking..."):
                # Give the AI the question, the transcript, and the summary, and get the answer.
                answer=get_ai_response(
                    user_input,
                    st.session_state.transcript,
                    st.session_state.summary,
                    api_key
                )
                # Save the AI's answer to the memory notepad.
                st.session_state.chat_history.append({"role":"assistant","content":answer})
            
            # 3. Refresh the page so the new messages appear and the typing box drops back to the bottom.
            st.rerun()

# If we don't have a transcript in memory, show the welcome screen instead.
else:
    st.info("Hello! Paste a YouTube link in the sidebar and click 'Analyze' to start.")
    st.write("""
    ### How it works:
    1. **Fetch:** We grab the transcript from the video.
    2. **Summarize:** AI gives you the key points.
    3. **Chat:** You ask questions about any detail you missed.
    """)
