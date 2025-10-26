# ==============================================================
# 🚀 main_chat.py
# --------------------------------------------------------------
# Ponto de entrada da API FastAPI do Assistente de Sustentação.
# Integra backend (chat) + frontend (interface HTML).
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
    title="Assistente de Sustentação IA",
    description="API e interface web para análise de logs e saúde dos sistemas.",
    version="1.0.0"
)

# ==============================================================
# 🌐 CORS (liberado para testes e uso local)
# ==============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # POC → libera tudo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================
# 🗂️ Configuração do diretório web
# ==============================================================
WEB_DIR = os.path.join(os.path.dirname(__file__), "web")
if not os.path.exists(WEB_DIR):
    os.makedirs(WEB_DIR)

app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")

# ==============================================================
# 🔗 Rotas principais da API
# ==============================================================
app.include_router(chat_router)
app.include_router(status_router)

# ==============================================================
# 🏠 Página inicial - abre interface web
# ==============================================================
@app.get("/", include_in_schema=False)
async def serve_index():
    """
    Página inicial: retorna o index.html da interface web
    """
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Interface web não encontrada."}

# ==============================================================
# 🩺 Healthcheck
# ==============================================================
@app.get("/healthz", include_in_schema=False)
async def health_check():
    return {"status": "ok", "service": "assistente-logs-chat", "version": "1.0.0"}
