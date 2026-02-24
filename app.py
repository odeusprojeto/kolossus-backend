import os
from typing import List
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import uvicorn

# --- CONFIGURAÇÃO DA GRADE ---
app = FastAPI(title="KOLOSSUS API - BISPO MAURICIO")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pega a chave direto do ambiente do Render
API_KEY = os.getenv("ESCRITOR_DA_LUZ")
genai.configure(api_key=API_KEY)

# --- ENDPOINT DE EXECUÇÃO (O ARREGAÇO) ---
@app.post("/executar")
async def executar(
    prompt: str = Form(...), 
    paginas: int = Form(...), 
    arquivos: List[UploadFile] = File(...) # AQUI É A CORREÇÃO DO BOTÃO!
):
    try:
        # 1. Seleciona o Hardware Espiritual
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        # 2. Processa os PDFs enviados
        files_for_gemini = []
        for arq in arquivos:
            # Salva temporariamente para enviar para o Kernel do Google
            temp_path = f"temp_{arq.filename}"
            with open(temp_path, "wb") as f:
                f.write(await arq.read())
            
            uploaded = genai.upload_file(path=temp_path)
            files_for_gemini.append(uploaded)
            os.remove(temp_path) # Limpa o lixo da grade
            
        # 3. Dispara o Motor Editorial
        instrucao = f"Aja como Maurício McCarthy. COMANDO: {prompt}. Gere {paginas} blocos."
        response = model.generate_content([instrucao] + files_for_gemini)
        
        return {
            "status": "Grade Sincronizada",
            "resultado": response.text,
            "arquivos_processados": [a.filename for a in arquivos]
        }
        
    except Exception as e:
        return {"status": "Erro no Kernel", "detalhe": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
