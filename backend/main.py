
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
import shutil
import subprocess
import os

app = FastAPI()
PROCESS_SCRIPT = "backend/gemini.py"
CSV_INPUT = "produtos.csv"
CSV_OUTPUT = "produtos_saida.csv"
LOG_FILE = "processo.log"

@app.post("/upload/")
async def upload_csv(file: UploadFile):
    with open(CSV_INPUT, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Arquivo carregado com sucesso."}

@app.post("/start/")
async def start_process(api_key: str = Form(...)):
    subprocess.Popen(["python", PROCESS_SCRIPT], env={**os.environ, "API_KEY": api_key})
    return {"message": "Processamento iniciado."}

@app.get("/log/")
async def get_log():
    if os.path.exists(LOG_FILE):
        return PlainTextResponse(open(LOG_FILE, "r", encoding="utf-8").read())
    return PlainTextResponse("Nenhum log encontrado.")

@app.get("/download/")
async def download_csv():
    if os.path.exists(CSV_OUTPUT):
        return FileResponse(CSV_OUTPUT, filename="produtos_saida.csv")
    return PlainTextResponse("Nenhum arquivo de saída encontrado.")



# Servir a pasta frontend como estática
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

