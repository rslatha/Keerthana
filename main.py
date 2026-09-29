import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def get_client():
    return API_KEY

def generate(prompt: str):
    try:
        model = genai.GenerativeModel("gemini-3.8-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

class LearningRequest(BaseModel):
    question: str = ""
    level: str = "beginner"
    topic: str = ""

def run_task(task: str, data: LearningRequest):
    q = data.question or data.topic or "general learning"
    level = data.level
    if task == "qa":
        prompt = f"You are EduGenie. Answer this for {level}: {q}"
    elif task == "explain":
        prompt = f"You are EduGenie. Explain for {level} level with examples: {q}"
    elif task == "quiz":
        prompt = f"You are EduGenie. Create 5-question quiz about: {q} for {level} level with answers."
    elif task == "summarize":
        prompt = f"You are EduGenie. Summarize: {q}"
    else:
        prompt = f"You are EduGenie. Create learning path for: {q} for {level} level"
    return {"task": task, "answer": generate(prompt)}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/health")
def health():
    return {"status": "ok", "gemini_configured": get_client() is not None}

@app.post("/qa")
def question_answer(data: LearningRequest):
    return run_task("qa", data)

@app.post("/explain")
def explain(data: LearningRequest):
    return run_task("explain", data)

@app.post("/quiz")
def quiz(data: LearningRequest):
    return run_task("quiz", data)

@app.post("/summarize")
def summarize(data: LearningRequest):
    return run_task("summarize", data)

@app.post("/learning-path")
def learning_path(data: LearningRequest):
    return run_task("path", data)