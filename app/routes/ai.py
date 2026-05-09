from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

from app.services.ai_validator import validar_texto
from app.services.firebase import db

router = APIRouter()


# =====================================================
# MODELOS
# =====================================================

class ValidateRequest(BaseModel):
    text: str


class SaveAIRequest(BaseModel):
    code: str
    input: str
    feedback: str


# =====================================================
# VALIDAR TEXTO
# =====================================================

@router.post("/validate")
def validate(data: ValidateRequest):

    result = validar_texto(data.text)

    return {
        "feedback": str(result)
    }


# =====================================================
# GUARDAR HISTORIAL IA
# =====================================================

@router.post("/save")
def save_ai(data: SaveAIRequest):

    if db is None:
        return {
            "status": "error",
            "message": "Firebase no disponible"
        }

    db.collection("ai_history").add({
        "code": data.code,
        "input": data.input,
        "feedback": data.feedback,
        "created_at": datetime.utcnow()
    })

    return {
        "status": "ok"
    }