import os
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# =========================
# FIREBASE
# =========================

try:
    from app.firebase import db, bucket
    print("✅ Firebase importado correctamente")

except Exception as e:
    print("❌ ERROR IMPORTANDO FIREBASE")
    traceback.print_exc()
    raise


# =========================
# CREAR DIRECTORIOS
# =========================

DIRS_TO_CREATE = [
    "app/templates",
    "output",
    "uploads",
    "documents"
]

for directory in DIRS_TO_CREATE:
    os.makedirs(directory, exist_ok=True)
    print(f"✅ Directorio asegurado: {directory}")


# =========================
# FASTAPI
# =========================

app = FastAPI(
    title="Editor Educativo SCORM",
    description="Herramienta para crear y exportar cursos SCORM",
    version="1.0.0"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# TEMPLATES
# =========================

try:
    templates = Jinja2Templates(directory="app/templates")
    print("✅ Templates cargadas correctamente")

except Exception as e:
    print("❌ Error cargando templates")
    traceback.print_exc()
    templates = None


# =========================
# IMPORTAR ROUTERS
# =========================

try:
    from app.routes import course, ai

    app.include_router(course.router, prefix="/course")
    app.include_router(ai.router, prefix="/ai")

    print("✅ Routers cargados")

except Exception as e:
    print("❌ Error cargando routers")
    traceback.print_exc()
    raise


# =========================
# RUTA PRINCIPAL
# =========================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    if templates is None:
        return "<h1>Templates no disponibles</h1>"

    try:
        return templates.TemplateResponse(
            "index.html",
            {"request": request}
        )

    except Exception as e:
        traceback.print_exc()
        return f"<h1>Error renderizando template: {str(e)}</h1>"


# =========================
# STATIC FILES
# =========================

try:
    app.mount("/output", StaticFiles(directory="output"), name="output")
    print("✅ /output montado")

except Exception:
    traceback.print_exc()

try:
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    print("✅ /uploads montado")

except Exception:
    traceback.print_exc()

try:
    app.mount("/documents", StaticFiles(directory="documents"), name="documents")
    print("✅ /documents montado")

except Exception:
    traceback.print_exc()


# =========================
# HEALTH CHECK
# =========================

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


print("✅ Aplicación iniciada correctamente")