# ==============================================================
# 🚀 main_chat.py
# --------------------------------------------------------------
# Ponto de entrada da API FastAPI do Assistente de Sustentação.
# Fornece endpoints de chat (/chat), status (/status)
# e também serve a interface web estática (index.html).
# ==============================================================

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes.chat_routes import router as chat_router
from app.routes.status_routes import router as status_router

# ==============================================================
# ⚙️ Inicialização da aplicação
# ==============================================================

app = FastAPI(
    title="Assistente de Sustentação",
    description="API e interface web para análise de logs e saúde dos sistemas.",
    version="1.0.0"
)

# ==============================================================
# 🌐 Configuração de CORS (mantida para compatibilidade futura)
# ==============================================================

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "file://",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================
# 🧩 Montagem das rotas principais
# ==============================================================

app.include_router(chat_router)
app.include_router(status_router)

# ==============================================================
# 🖥️ Servindo a interface web estática
# --------------------------------------------------------------
# Espera encontrar o arquivo index.html e assets (CSS, JS, imagens)
# dentro do diretório "web" na raiz do projeto.
# ==============================================================

# Caminho absoluto da pasta "web"
WEB_DIR = os.path.join(os.path.dirname(__file__), "web")

# Monta a pasta de arquivos estáticos
if os.path.isdir(WEB_DIR):
    app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")
else:
    print("⚠️ Pasta 'web/' não encontrada. A interface web não será servida.")

# ==============================================================
# 🏠 Rota raiz — carrega automaticamente o index.html
# ==============================================================

@app.get("/", include_in_schema=False)
async def root():
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "Assistente de Sustentação ativo 🚀",
        "endpoints": ["/chat", "/status"]
    }
