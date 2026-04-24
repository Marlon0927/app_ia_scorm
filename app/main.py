import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routes import course, ai

# 👇 Crear directorios necesarios si no existen
DIRS_TO_CREATE = ["app/templates", "output", "uploads", "documents"]
for directory in DIRS_TO_CREATE:
    os.makedirs(directory, exist_ok=True)
    print(f"✅ Directorio asegurado: {directory}")

# 👇 PRIMERO se crea la app
app = FastAPI(
    title="Editor Educativo SCORM",
    description="Herramienta para crear y exportar cursos SCORM",
    version="1.0.0"
)

# 👇 CORS - permitir que el frontend se conecte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👇 Templates
try:
    templates = Jinja2Templates(directory="app/templates")
    print("✅ Templates cargadas correctamente")
except Exception as e:
    print(f"⚠️ Error cargando templates: {e}")
    templates = None

# 👇 Rutas de la API
app.include_router(course.router, prefix="/course")
app.include_router(ai.router, prefix="/ai")

# 👇 Endpoint raíz
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if templates is None:
        return "<h1>Editor Educativo - Templates no disponibles</h1>"
    
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        print(f"Error renderizando template: {e}")
        return f"<h1>Error: {str(e)}</h1>"

# 👇 Montar directorios estáticos
try:
    app.mount("/output", StaticFiles(directory="output"), name="output")
    print("✅ Static files /output montado")
except Exception as e:
    print(f"⚠️ Error montando /output: {e}")

try:
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    print("✅ Static files /uploads montado")
except Exception as e:
    print(f"⚠️ Error montando /uploads: {e}")

try:
    app.mount("/documents", StaticFiles(directory="documents"), name="documents")
    print("✅ Static files /documents montado")
except Exception as e:
    print(f"⚠️ Error montando /documents: {e}")

# 👇 Health check para Render
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": "1.0.0"
    }

print("\n✅ Aplicación iniciada correctamente")