
import os
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List

# ------------------------------------------------------------
# CONFIGURAÇÃO DA API
# ------------------------------------------------------------

API_KEY = os.getenv("ESCRITOR_DA_LUZ")

if not API_KEY:
    raise ValueError("Defina a variável de ambiente ESCRITOR_DA_LUZ com sua API Key.")

genai.configure(api_key=API_KEY)

def selecionar_modelo():
    modelos = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
    prioridade = [
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest",
        "gemini-2.0-pro",
        "gemini-2.0-flash"
    ]
    for p in prioridade:
        for m in modelos:
            if p in m:
                return m
    return "models/gemini-1.5-pro"

MODELO_ATIVO = selecionar_modelo()

SYSTEM_INSTRUCTION = """
Produza exatamente o que o usuário pedir.
Se solicitar páginas, considere aproximadamente 800 palavras por página.
"""

model = genai.GenerativeModel(
    MODELO_ATIVO,
    system_instruction=SYSTEM_INSTRUCTION
)

app = FastAPI()

# ------------------------------------------------------------
# ENDPOINT PRINCIPAL
# ------------------------------------------------------------

@app.post("/executar")
async def executar(
    prompt: str = Form(...),
    paginas: int = Form(...),
    arquivos: List[UploadFile] = File(None)
):

    arquivos_enviados = []

    if arquivos:
        for arquivo in arquivos:
            contents = await arquivo.read()
            with open(arquivo.filename, "wb") as f:
                f.write(contents)

            uploaded = genai.upload_file(path=arquivo.filename)
            arquivos_enviados.append(uploaded)

    prompt_final = f"""
    INSTRUÇÃO DO USUÁRIO:
    {prompt}

    META: Produza aproximadamente {paginas} páginas completas.
    """

    try:
        response = model.generate_content([prompt_final] + arquivos_enviados)
        texto = response.text

        return JSONResponse(content={
            "modelo_usado": MODELO_ATIVO,
            "resultado": texto
        })

    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
