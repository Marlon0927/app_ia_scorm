import os
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# =========================================================
# CREAR DIRECTORIOS NECESARIOS
# =========================================================

DIRS_TO_CREATE = ["app/templates", "output", "uploads", "documents"]

for directory in DIRS_TO_CREATE:
    os.makedirs(directory, exist_ok=True)
    print(f"✅ Directorio asegurado: {directory}")

# =========================================================
# FIREBASE
# =========================================================

try:
    from app.services.firebase import db, bucket
    print("✅ Firebase importado correctamente")

except Exception as e:
    print("❌ ERROR IMPORTANDO FIREBASE")
    traceback.print_exc()

    db = None
    bucket = None

# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Editor Educativo SCORM",
    description="Herramienta para crear y exportar cursos SCORM",
    version="1.0.0"
)

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# TEMPLATES
# =========================================================

try:
    templates = Jinja2Templates(directory="app/templates")
    print("✅ Templates cargadas correctamente")

except Exception as e:
    print(f"⚠️ Error cargando templates: {e}")
    traceback.print_exc()
    templates = None

# =========================================================
# IMPORTAR RUTAS DESPUÉS DE FIREBASE
# =========================================================

try:
    from app.routes import course, ai

    app.include_router(course.router, prefix="/course")
    app.include_router(ai.router, prefix="/ai")

    print("✅ Rutas cargadas correctamente")

except Exception as e:
    print("❌ ERROR CARGANDO RUTAS")
    traceback.print_exc()

# =========================================================
# ROOT
# =========================================================

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
        print(f"❌ Error renderizando template: {e}")
        traceback.print_exc()

        return f"<h1>Error: {str(e)}</h1>"

# =========================================================
# STATIC FILES
# =========================================================

STATIC_DIRS = [
    ("/output", "output"),
    ("/uploads", "uploads"),
    ("/documents", "documents")
]

for route, directory in STATIC_DIRS:

    try:
        app.mount(route, StaticFiles(directory=directory), name=directory)
        print(f"✅ Static mounted: {route}")

    except Exception as e:
        print(f"⚠️ Error montando {route}: {e}")
        traceback.print_exc()

# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "firebase": db is not None
    }

# =========================================================
# STARTUP
# =========================================================

print("\n🚀 Aplicación iniciada correctamente")