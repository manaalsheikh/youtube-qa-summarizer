import os
from fastapi import FastAPI,Request,Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from utils import get_video_id,fetch_transcript,generate_summary,get_ai_response

load_dotenv()
api_key=os.getenv("GROQ_API_KEY")

app=FastAPI()
templates=Jinja2Templates(directory="templates")

@app.get("/")
async def home(request:Request):
    return templates.TemplateResponse("index.html",{"request":request})

@app.post("/analyze")
async def analyze(request:Request,url:str=Form(...)):
    v_id=get_video_id(url)
    if not v_id:
        return JSONResponse(content={"error":"Invalid YouTube URL"},status_code=400)
    
    text=fetch_transcript(v_id)
    if text.startswith("Error:"):
        return JSONResponse(content={"error":text},status_code=400)
    
    summary=generate_summary(text,api_key)
    return JSONResponse(content={
        "summary":summary,
        "video_id":v_id,
        "transcript":text
    })

@app.post("/chat")
async def chat(request:Request,question:str=Form(...),transcript:str=Form(...),summary:str=Form("")):
    response=get_ai_response(question,transcript,[],api_key,summary=summary)
    return JSONResponse(content={"response":response})

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8000)
