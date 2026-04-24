from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.routes import course, ai

# 👇 PRIMERO se crea la app
app = FastAPI()

# 👇 luego templates
templates = Jinja2Templates(directory="app/templates")

# 👇 luego rutas
app.include_router(course.router, prefix="/course")
app.include_router(ai.router, prefix="/ai")

# 👇 luego endpoints
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

app.mount("/output", StaticFiles(directory="output"), name="output")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/documents", StaticFiles(directory="documents"), name="documents")