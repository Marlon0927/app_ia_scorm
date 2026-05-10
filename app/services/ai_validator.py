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
    Eres un docente experto en pedagogía y accesibilidad.

    Quiero que des:

    - Un veredicto general del texto agregado.
    - Observaciones concretas.
    - Sugerencias puntuales respecto al contenido.
    - Sugerentias de ACCESIBILIDAD para el texto analizado. (IMPORTANTE)
    - Finalmente, un texto sugerido que mejore el original, teniendo en cuenta las observaciones y sugerencias anteriores.
    - Este texto sugerido debe tener lineamientos de accesibilidad.

    IMPORTANTE:
    - NO reescribas todo el texto
    - Sé breve y claro
    - Se suave con las respuestas, no seas duro ni crítico, sé constructivo y empático.

    FORMATO:

    Veredicto: ...
    Observaciones: ...
    Sugerencias: ...
    Sugerencias de Accesibilidad: ...
    Texto Sugerido: ...
    

    Texto:
    {texto}
    """

    try:

        response = model.generate_content(prompt)

        # 🔥 FORZAR STRING
        if hasattr(response, "text"):
            return str(response.text)

        return str(response)

    except Exception as e:
        print("ERROR GEMINI:", e)
        return f"Error IA: {str(e)}"