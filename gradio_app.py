import gradio as gr
import os
from dotenv import load_dotenv
from utils import get_video_id,fetch_transcript,generate_summary,get_ai_response

load_dotenv()
api_key=os.getenv("GROQ_API_KEY")

def process_video(url):
    video_id=get_video_id(url)
    if not video_id:
        return "Invalid YouTube URL.",None,""
    
    # Debug: Check if cookies exist
    if os.path.exists('cookies.txt'):
        print("✅ cookies.txt file found in root.")
    else:
        print("❌ cookies.txt NOT found in root.")
    
    transcript=fetch_transcript(video_id)
    if transcript.startswith("Error:"):
        return f"{transcript}\n\nStatus: {'Cookies Found' if os.path.exists('cookies.txt') else 'Cookies Missing'}",None,""
    
    summary=generate_summary(transcript,api_key)
    video_embed=f'<iframe width="100%" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
    
    return summary,video_embed,transcript

def chat_fn(message,history,transcript):
    if not transcript:
        return history+[("Please process a video first.","")]
    
    # Format history for LangChain if needed, but here we just pass it
    response=get_ai_response(message,transcript,history,api_key)
    history.append((message,response))
    return history

with gr.Blocks(title="YouTube Video AI") as demo:
    gr.Markdown("# YouTube Video Summarizer and QA")
    
    transcript_state=gr.State("")
    
    with gr.Row():
        with gr.Column(scale=1):
            url_input=gr.Textbox(label="YouTube URL",placeholder="Enter link here")
            btn=gr.Button("Analyze Video",variant="primary")
            video_output=gr.HTML()
        
        with gr.Column(scale=2):
            summary_output=gr.Textbox(label="Summary",lines=10)
            chatbot=gr.Chatbot(label="Chat with Video")
            msg=gr.Textbox(label="Ask a question")
            clear=gr.Button("Clear Chat")

    btn.click(process_video,inputs=url_input,outputs=[summary_output,video_output,transcript_state])
    msg.submit(chat_fn,inputs=[msg,chatbot,transcript_state],outputs=chatbot)
    msg.submit(lambda:gr.update(value=""),None,msg)
    clear.click(lambda:[],None,chatbot)

if __name__=="__main__":
    demo.launch()
