# ==============================================================
# 🚀 main_chat.py
# --------------------------------------------------------------
# Ponto de entrada da API FastAPI do Assistente de Sustentação.
# Agora serve também a interface web (HTML + CSS + JS).
# ==============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.routes.chat_routes import router as chat_router
from app.routes.status_routes import router as status_router
import os

# ==============================================================
# ⚙️ Configuração principal
# ==============================================================
app = FastAPI(
    title="Assistente de Sustentação",
    description="API e interface web para análise de logs e saúde dos sistemas.",
    version="1.0.0"
)

# ==============================================================
# 🌐 CORS - Liberação para execução local, Cloud Run e bucket público (POC)
# ==============================================================
origins = [
    "http://127.0.0.1:5500",  # execução local via Live Server
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8080",
    "https://assistente-logs-chat-p62nlxrygq-uc.a.run.app",  # backend Cloud Run
    "https://storage.googleapis.com",                         # domínio genérico do bucket
    "https://storage.googleapis.com/chat-log-poc",             # bucket do front (ajuste conforme seu nome)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================
# 📁 Servindo arquivos estáticos (HTML, CSS, JS)
# ==============================================================
WEB_DIR = os.path.join(os.path.dirname(__file__), "web")
if not os.path.exists(WEB_DIR):
    os.makedirs(WEB_DIR)

app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")

# ==============================================================
# 🔗 Rotas principais (API)
# ==============================================================
app.include_router(chat_router)
app.include_router(status_router)

# ==============================================================
# 🌍 Página inicial (redireciona para interface web)
# ==============================================================
@app.get("/", include_in_schema=False)
async def serve_index():
    """
    Página inicial: retorna o index.html localizado em /app/web
    """
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Interface web não encontrada."}

# ==============================================================
# 🩺 Endpoint de status técnico
# ==============================================================
@app.get("/healthz")
async def health_check():
    """
    Verificação de saúde da API e da interface web.
    Retorna 200 OK se o serviço estiver operacional.
    """
    return {"status": "ok", "service": "assistente-logs-chat", "version": "1.0.0"}
