from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import openai
from fpdf import FPDF
import uuid
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
async def generate(request: Request, topic: str = Form(...)):
    prompt = f"Lütfen '{topic}' hakkında 1500 kelimelik, profesyonel ve bölümlere ayrılmış bir e-kitap yaz."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response['choices'][0]['message']['content']

    filename = f"{uuid.uuid4()}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)

    return templates.TemplateResponse("layout.html", {
        "request": request,
        "filename": filename
    })

@app.get("/download/{filename}")
async def download(filename: str):
    return FileResponse(path=filename, filename="e-kitap.pdf", media_type='application/pdf')
