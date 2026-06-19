import os
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from openai import OpenAI
import PyPDF2

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def extract_text(pdf_path):
    text = ""

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            text += page.extract_text()

    return text


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={}
)


@app.post("/analyze", response_class=HTMLResponse)
async def analyze_resume(
    request: Request,
    resume: UploadFile = File(...)
):

    file_path = f"{UPLOAD_DIR}/{resume.filename}"

    with open(file_path, "wb") as f:
        f.write(await resume.read())

    resume_text = extract_text(file_path)

    prompt = f"""
    Analyze this resume.

    Resume:
    {resume_text}

    Provide:

    1. Summary
    2. Strengths
    3. Weaknesses
    4. Improvements
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result = response.choices[0].message.content

    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "result": result
    }
)

    # return templates.TemplateResponse(
    #     "index.html",
    #     {
    #         "request": request,
    #         "result": result
    #     }
    # )