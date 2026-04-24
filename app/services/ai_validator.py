import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")


def validar_texto(texto: str):

    if not texto.strip():
        return "Texto vacío"

    prompt = f"""
    Eres un docente experto en pedagogía.
    
    Recuerda que debes analizar solo texto, si recibes un enlace o una imagen solo di "Imagen agregada, enlace recibido, segun corresponda".
    
    Quiero que des:

    - Un veredicto general
    - Observaciones concretas
    - Sugerencias puntuales respecto al contenido.

    IMPORTANTE:
    - NO reescribas todo el texto
    - Sé breve y claro
    - Se suave con las respuestas, no seas duro ni crítico, sé constructivo y empático.

    FORMATO:

    Veredicto: ...
    Observaciones: ...
    Sugerencias: ...
    

    Texto:
    {texto}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error IA: {str(e)}"