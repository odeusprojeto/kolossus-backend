import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import uvicorn

# -----------------------------
# CONFIGURAÇÃO DA APLICAÇÃO
# -----------------------------
app = FastAPI(title="KOLOSSUS API - BISPO MAURICIO")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# CHAVE DE AMBIENTE (RENDER)
# -----------------------------
API_KEY = os.getenv("ESCRITOR_DA_LUZ")

if not API_KEY:
    raise ValueError("Variável de ambiente ESCRITOR_DA_LUZ não encontrada no Render.")

genai.configure(api_key=API_KEY)

# -----------------------------
# ENDPOINT PRINCIPAL
# -----------------------------
@app.post("/executar")
async def executar(
    prompt: str = Form(...),
    paginas: int = Form(...),
    arquivo: UploadFile = File(default=None)
):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")

        files_for_gemini = []

        # Processa arquivo se existir
        if arquivo:
            temp_path = f"temp_{arquivo.filename}"

            with open(temp_path, "wb") as f:
                f.write(await arquivo.read())

            uploaded = genai.upload_file(path=temp_path)
            files_for_gemini.append(uploaded)

            os.remove(temp_path)

        instrucao = f"Aja como Maurício McCarthy. COMANDO: {prompt}. Gere {paginas} blocos."

        response = model.generate_content([instrucao] + files_for_gemini)

        return {
            "status": "Grade Sincronizada",
            "resultado": response.text,
            "arquivo_processado": arquivo.filename if arquivo else None
        }

    except Exception as e:
        return {
            "status": "Erro no Kernel",
            "detalhe": str(e)
        }

# -----------------------------
# EXECUÇÃO LOCAL
# -----------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
