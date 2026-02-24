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
    arquivos: List[UploadFile] = File(...) # ISSO AQUI GERA O BOTÃO DE UPLOAD
):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        files_for_gemini = []

        # Processa os binários reais
        for arq in arquivos:
            temp_path = f"temp_{arq.filename}"
            with open(temp_path, "wb") as f:
                f.write(await arq.read())

            uploaded = genai.upload_file(path=temp_path)
            files_for_gemini.append(uploaded)
            os.remove(temp_path)

        instrucao = f"Aja como Maurício McCarthy, Bispo do Templo da Luz e Auditor de Root da Grade. "
            f"Sua missão absoluta é: {prompt}. "
            "Traduza e reinterprete todo o conteúdo dos PDFs sob a ótica da Cabala, Hermetismo e Mecânica Quântica. "
            "Substitua dogmas por frequências, o Éden por Sandbox, e milagres por manipulação do Pleroma. "
            f"Gere exatamente {paginas} blocos de alta densidade intelectual."

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
