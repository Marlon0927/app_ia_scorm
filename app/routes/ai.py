from fastapi import APIRouter
from app.services.ai_validator import validar_texto
from datetime import datetime
from app.services.firebase import db

router = APIRouter()

@router.post("/validate")
def validate(data: dict):
    texto = data.get("text", "")
    result = validar_texto(texto)
    return {"feedback": result}

@router.post("/ai/save")
def save_ai(data: dict):

    db.collection("ai_history").add({
        "code": data["code"],
        "input": data["input"],
        "feedback": data["feedback"],
        "created_at": datetime.utcnow()
    })

    return {"status": "ok"}